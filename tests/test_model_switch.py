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
    assert "chat override" in show_resp.content
    assert "Models source:" in show_resp.content

    reset_resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model reset")
    )
    assert "Model reset to default" in reset_resp.content


@pytest.mark.asyncio
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
async def test_model_command_allows_temporary_model_outside_allowlist(tmp_path, config_near_models):

 codex/implement-dynamic-model-switching-in-bot-ki1ptz
async def test_model_command_allows_temporary_model_outside_allowlist(tmp_path, config_near_models):

 codex/implement-dynamic-model-switching-in-bot-c42t1p
async def test_model_command_allows_temporary_model_outside_allowlist(tmp_path, config_near_models):

async def test_model_command_rejects_models_outside_allowlist(tmp_path, config_near_models):
 main
 main
 main
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)

    resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model anthropic/claude-3-5-sonnet")
    )

 codex/implement-dynamic-model-switching-in-bot-8zkqjx

 codex/implement-dynamic-model-switching-in-bot-ki1ptz

 codex/implement-dynamic-model-switching-in-bot-c42t1p
 main
 main
    assert "Temporary model set" in resp.content

    show_resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model")
    )
    assert "anthropic/claude-3-5-sonnet" in show_resp.content
    assert "temporary override" in show_resp.content

 codex/implement-dynamic-model-switching-in-bot-8zkqjx

 codex/implement-dynamic-model-switching-in-bot-ki1ptz

    assert "not in allowlist" in resp.content
 main

 main
 main

@pytest.mark.asyncio
async def test_model_command_rejects_invalid_format_without_provider_prefix(tmp_path, config_near_models):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)

    resp = await loop._process_message(
        InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/model gemini-2.5-flash-preview")
    )

    assert "Invalid model name" in resp.content


@pytest.mark.asyncio
async def test_new_command_clears_model_override(tmp_path, config_near_models):
    loop = AgentLoop(bus=MessageBus(), provider=_DummyProvider(), workspace=tmp_path)
    session = loop.sessions.get_or_create("cli:c")
    session.metadata["model"] = "openai/gpt-4o-mini"
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
    session.metadata["temp_model"] = "openai/gpt-5.1"


 codex/implement-dynamic-model-switching-in-bot-ki1ptz
    session.metadata["temp_model"] = "openai/gpt-5.1"


 codex/implement-dynamic-model-switching-in-bot-c42t1p
    session.metadata["temp_model"] = "openai/gpt-5.1"

 main

 main
 main
    await loop._process_message(InboundMessage(channel="cli", sender_id="u", chat_id="c", content="/new"))

    refreshed = loop.sessions.get_or_create("cli:c")
    assert "model" not in refreshed.metadata
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
    assert "temp_model" not in refreshed.metadata



 codex/implement-dynamic-model-switching-in-bot-ki1ptz
    assert "temp_model" not in refreshed.metadata


 codex/implement-dynamic-model-switching-in-bot-c42t1p
    assert "temp_model" not in refreshed.metadata

 main

 main

 main
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
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
    session.metadata["temp_model"] = "openai/gpt-5.1"


 codex/implement-dynamic-model-switching-in-bot-ki1ptz
    session.metadata["temp_model"] = "openai/gpt-5.1"


 codex/implement-dynamic-model-switching-in-bot-c42t1p
    session.metadata["temp_model"] = "openai/gpt-5.1"

 main

 main
 main
    loop._run_agent_loop = AsyncMock(return_value=("ok", [], []))

    await loop._process_message(InboundMessage(channel="cli", sender_id="u", chat_id="c", content="hello"))

    assert loop._run_agent_loop.await_count == 1
 codex/implement-dynamic-model-switching-in-bot-8zkqjx
    assert loop._run_agent_loop.await_args.kwargs["model"] == "openai/gpt-5.1"

 codex/implement-dynamic-model-switching-in-bot-ki1ptz
    assert loop._run_agent_loop.await_args.kwargs["model"] == "openai/gpt-5.1"

 codex/implement-dynamic-model-switching-in-bot-c42t1p
    assert loop._run_agent_loop.await_args.kwargs["model"] == "openai/gpt-5.1"

    assert loop._run_agent_loop.await_args.kwargs["model"] == "openai/gpt-4o-mini"
 main
 main
 main
