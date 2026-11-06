from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from nanobot.agent.loop import AgentLoop
from nanobot.bus.events import InboundMessage
from nanobot.bus.queue import MessageBus
from nanobot.config.loader import get_config_path, set_config_path
from nanobot.providers.base import LLMProvider, LLMResponse


class _DummyProvider(LLMProvider):
    async def chat(self, messages, tools=None, model=None, max_tokens=4096, temperature=0.7, reasoning_effort=None):
        return LLMResponse(content="ok")

    def get_default_model(self) -> str:
        return "anthropic/claude-opus-4-5"


@pytest.fixture
def config_near_models(tmp_path: Path):
    original = get_config_path()
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    (tmp_path / "models").write_text(
        "# allowed models\nanthropic/claude-opus-4-5\nopenai/gpt-4o-mini\n",
        encoding="utf-8",
    )
    set_config_path(cfg)
    yield cfg
    set_config_path(original)


@pytest.mark.asyncio
async def test_model_command_sets_and_resets_session_model(tmp_path, config_near_models):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)

    set_resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model openai/gpt-4o-mini")
    )
    assert "Model switched" in set_resp.content

    show_resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model")
    )
    assert "openai/gpt-4o-mini" in show_resp.content
    assert "session override" in show_resp.content
    assert "Models source:" in show_resp.content

    reset_resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model reset")
    )
    assert "Session model reset" in reset_resp.content


@pytest.mark.asyncio
async def test_model_command_accepts_models_outside_display_list(tmp_path, config_near_models):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)

    resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model anthropic/claude-3-5-sonnet")
    )

    assert "Model switched" in resp.content


@pytest.mark.asyncio
async def test_new_command_clears_model_override(tmp_path, config_near_models):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)
    session = loop.sessions.get_or_create("cli:c")
    session.metadata["model"] = "openai/gpt-4o-mini"

    await loop._process_message(InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/new"))

    refreshed = loop.sessions.get_or_create("cli:c")
    assert "model" not in refreshed.metadata


@pytest.mark.asyncio
async def test_model_show_reports_read_error_for_invalid_json_allowlist(tmp_path):
    original = get_config_path()
    cfg = tmp_path / "config.json"
    cfg.write_text("{}", encoding="utf-8")
    (tmp_path / "models.json").write_text("{bad json", encoding="utf-8")
    set_config_path(cfg)
    try:
        loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)
        resp = await loop._process_message(InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model"))
        assert "Warning: Failed to read model list" in resp.content
    finally:
        set_config_path(original)


@pytest.mark.asyncio
async def test_regular_messages_use_session_model_override(tmp_path):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)
    session = loop.sessions.get_or_create("cli:c")
    session.metadata["model"] = "openai/gpt-4o-mini"

    loop._run_agent_loop = AsyncMock(return_value=("ok", [], []))

    await loop._process_message(InboundMessage(channel="cli", sender_id="u", chat_id="c", content="hello"))

    assert loop._run_agent_loop.await_count == 1
    assert loop._run_agent_loop.await_args.kwargs["model"] == "openai/gpt-4o-mini"


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["gemini-3.8-flash", "google/gemini-3.5-flash"])
@pytest.mark.parametrize("scope", ["", "global "])
async def test_model_command_preserves_exact_id_and_passes_it_to_provider(
    tmp_path, config_near_models, model, scope,
):
    provider = _DummyProvider()
    provider.chat = AsyncMock(return_value=LLMResponse(content="ok"))
    loop = AgentLoop(bus=MessageBus(), provider=provider, workspace=tmp_path)
    response = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content=f"/model {scope}{model}")
    )
    assert model in response.content

    # Reload from disk: both session and global overrides must survive a restart.
    loop = AgentLoop(bus=MessageBus(), provider=provider, workspace=tmp_path)
    session = loop.sessions.get_or_create("cli:c")
    assert loop._resolve_session_model(session) == model
    other = loop.sessions.get_or_create("cli:other")
    assert loop._resolve_session_model(other) == (model if scope else loop.model)
    await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="hello")
    )
    provider.chat.assert_awaited_once()
    assert provider.chat.await_args.kwargs["model"] == model


@pytest.mark.asyncio
@pytest.mark.parametrize("scope", ["", "global "])
@pytest.mark.parametrize("model", ["gemini flash", "google/gemini\tflash", "gemini\nflash"])
async def test_invalid_model_does_not_change_existing_overrides(
    tmp_path, config_near_models, scope, model,
):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)
    session = loop.sessions.get_or_create("cli:c")
    session.metadata["model"] = "google/gemini-3.5-flash"
    loop.sessions.save(session)
    loop._set_global_model("global-model")
    response = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content=f"/model {scope}{model}")
    )
    assert ("Usage:" if scope else "Invalid model name") in response.content
    assert session.metadata["model"] == "google/gemini-3.5-flash"
    assert loop._get_global_model() == "global-model"


@pytest.mark.asyncio
@pytest.mark.parametrize("reset", ["reset", "clear", "default"])
async def test_model_override_priority_and_reset(tmp_path, config_near_models, reset):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)

    async def command(text):
        return await loop._process_message(
            InboundMessage(channel="cli", sender_id="u", chat_id="c", content=text)
        )

    await command("/model global gemini-3.8-flash")
    await command("/model google/gemini-3.5-flash")
    session = loop.sessions.get_or_create("cli:c")
    assert loop._resolve_session_model(session) == "google/gemini-3.5-flash"
    await command(f"/model {reset}")
    assert loop._resolve_session_model(session) == "gemini-3.8-flash"
    await command(f"/model global {reset}")
    assert loop._resolve_session_model(session) == loop.model
    assert not (tmp_path / "global_model").exists()
