#!/usr/bin/env bash
# =============================================================================
#  install_nanobot.sh — автоматическая установка nanobot на Ubuntu
#  Репо: https://github.com/modeco46/nanobot
#
#  Использование:
#    wget -O install_nanobot.sh <URL_скрипта>
#    chmod +x install_nanobot.sh
#    ./install_nanobot.sh
# =============================================================================
set -euo pipefail

# ─── цвета ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

info()    { echo -e "${CYAN}[•]${NC} $*"; }
success() { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }
header()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════${NC}"; \
            echo -e "${BOLD}${CYAN}  $*${NC}"; \
            echo -e "${BOLD}${CYAN}══════════════════════════════════════${NC}\n"; }

# ─── вспомогательная функция запроса значения ────────────────────────────────
prompt() {
    local var_name="$1"
    local prompt_text="$2"
    local default="$3"
    local secret="${4:-no}"

    while true; do
        if [[ -n "$default" ]]; then
            echo -ne "${BOLD}${prompt_text}${NC} ${YELLOW}[${default}]${NC}: "
        else
            echo -ne "${BOLD}${prompt_text}${NC}: "
        fi

        if [[ "$secret" == "yes" ]]; then
            read -rs value; echo
        else
            read -r value
        fi

        value="${value:-$default}"

        if [[ -z "$value" ]]; then
            warn "Значение не может быть пустым. Попробуйте снова."
        else
            printf -v "$var_name" '%s' "$value"
            break
        fi
    done
}

# ─── константы ───────────────────────────────────────────────────────────────
REPO_URL="https://github.com/modeco46/nanobot.git"
SERVICE_FILE="/etc/systemd/system/nanobot.service"
SERVICE_NAME="nanobot"

# ─── root check ──────────────────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && error "Запустите скрипт от root (sudo или под root)"

header "Установка nanobot"

# =============================================================================
#  0. ПОИСК И ОЧИСТКА СУЩЕСТВУЮЩИХ УСТАНОВОК
# =============================================================================
header "Поиск существующих установок nanobot"

FOUND_SERVICES=()
FOUND_VENVS=()
FOUND_DATADIRS=()

# ── systemd сервисы ──────────────────────────────────────────────────────────
while IFS= read -r -d '' svc; do
    FOUND_SERVICES+=("$svc")
done < <(find /etc/systemd/system -maxdepth 1 -name "nanobot*.service" -print0 2>/dev/null || true)

# ── виртуальные окружения (по наличию bin/nanobot внутри) ────────────────────
while IFS= read -r -d '' nb_bin; do
    venv_dir="$(dirname "$(dirname "$nb_bin")")"
    FOUND_VENVS+=("$venv_dir")
done < <(find /root /home /opt -maxdepth 4 \
              -name "nanobot" -path "*/bin/nanobot" \
              -print0 2>/dev/null || true)

# ── директории данных .nanobot ───────────────────────────────────────────────
while IFS= read -r -d '' datadir; do
    FOUND_DATADIRS+=("$datadir")
done < <(find /root /home -maxdepth 2 \
              -name ".nanobot" -type d \
              -print0 2>/dev/null || true)

FOUND_TOTAL=$(( ${#FOUND_SERVICES[@]} + ${#FOUND_VENVS[@]} + ${#FOUND_DATADIRS[@]} ))

# ── вывод результатов ────────────────────────────────────────────────────────
if [[ $FOUND_TOTAL -eq 0 ]]; then
    success "Существующих установок не найдено — продолжаем"
else
    warn "Найдено ${FOUND_TOTAL} объект(ов) от предыдущих установок:"
    echo

    if [[ ${#FOUND_SERVICES[@]} -gt 0 ]]; then
        echo -e "  ${BOLD}Systemd сервисы (${#FOUND_SERVICES[@]}):${NC}"
        for svc in "${FOUND_SERVICES[@]}"; do
            svc_name="$(basename "$svc" .service)"
            status_str=""
            if systemctl is-active --quiet "$svc_name" 2>/dev/null; then
                status_str="${GREEN} [запущен]${NC}"
            elif systemctl is-enabled --quiet "$svc_name" 2>/dev/null; then
                status_str="${YELLOW} [включён, не запущен]${NC}"
            else
                status_str="${DIM} [остановлен]${NC}"
            fi
            echo -e "    ${RED}▸${NC} $svc${status_str}"
        done
        echo
    fi

    if [[ ${#FOUND_VENVS[@]} -gt 0 ]]; then
        echo -e "  ${BOLD}Виртуальные окружения (${#FOUND_VENVS[@]}):${NC}"
        for venv in "${FOUND_VENVS[@]}"; do
            size_str=""
            size_str=$(du -sh "$venv" 2>/dev/null | cut -f1 || echo "?")
            echo -e "    ${RED}▸${NC} $venv  ${DIM}(${size_str})${NC}"
        done
        echo
    fi

    if [[ ${#FOUND_DATADIRS[@]} -gt 0 ]]; then
        echo -e "  ${BOLD}Директории данных .nanobot (${#FOUND_DATADIRS[@]}):${NC}"
        for datadir in "${FOUND_DATADIRS[@]}"; do
            size_str=$(du -sh "$datadir" 2>/dev/null | cut -f1 || echo "?")
            echo -e "    ${RED}▸${NC} $datadir  ${DIM}(${size_str})${NC}"
        done
        echo
    fi

    # ── предложение удалить ──────────────────────────────────────────────────
    echo -e "${YELLOW}Что удалить перед установкой?${NC}"
    echo -e "  ${BOLD}1${NC}) Всё перечисленное выше (полная очистка)"
    echo -e "  ${BOLD}2${NC}) Только сервисы и виртуальные окружения (данные .nanobot оставить)"
    echo -e "  ${BOLD}3${NC}) Ничего не удалять (продолжить без очистки)"
    echo
    while true; do
        read -rp "$(echo -e "${BOLD}Ваш выбор [1/2/3]${NC}: ")" CLEANUP_CHOICE
        case "${CLEANUP_CHOICE:-}" in
            1|2|3) break ;;
            *) warn "Введите 1, 2 или 3" ;;
        esac
    done

    if [[ "$CLEANUP_CHOICE" == "1" || "$CLEANUP_CHOICE" == "2" ]]; then
        echo
        info "Начинаем очистку..."

        # Останавливаем и удаляем сервисы
        for svc in "${FOUND_SERVICES[@]}"; do
            svc_name="$(basename "$svc" .service)"
            if systemctl is-active --quiet "$svc_name" 2>/dev/null; then
                info "Остановка сервиса: $svc_name"
                systemctl stop "$svc_name" || true
            fi
            if systemctl is-enabled --quiet "$svc_name" 2>/dev/null; then
                info "Отключение из автозагрузки: $svc_name"
                systemctl disable "$svc_name" || true
            fi
            info "Удаление файла сервиса: $svc"
            rm -f "$svc"
        done
        if [[ ${#FOUND_SERVICES[@]} -gt 0 ]]; then
            systemctl daemon-reload
            success "Сервисы удалены"
        fi

        # Добиваем возможные процессы nanobot запущенные вручную (не через systemd)
        if pgrep -f "bin/nanobot" &>/dev/null; then
            warn "Найдены процессы nanobot вне systemd — останавливаем..."
            pkill -TERM -f "bin/nanobot" || true
            sleep 2
            # SIGKILL если не вышли сами
            pkill -KILL -f "bin/nanobot" 2>/dev/null || true
            success "Процессы nanobot остановлены"
        fi

        # Удаляем виртуальные окружения
        for venv in "${FOUND_VENVS[@]}"; do
            info "Удаление virtualenv: $venv"
            rm -rf "$venv"
        done
        [[ ${#FOUND_VENVS[@]} -gt 0 ]] && success "Виртуальные окружения удалены"

        # Удаляем директории данных (только при выборе 1)
        if [[ "$CLEANUP_CHOICE" == "1" ]]; then
            for datadir in "${FOUND_DATADIRS[@]}"; do
                info "Удаление директории данных: $datadir"
                rm -rf "$datadir"
            done
            [[ ${#FOUND_DATADIRS[@]} -gt 0 ]] && success "Директории данных удалены"
        else
            [[ ${#FOUND_DATADIRS[@]} -gt 0 ]] && \
                warn "Директории данных .nanobot оставлены без изменений"
        fi

        success "Очистка завершена"
    else
        warn "Очистка пропущена — продолжаем установку поверх"
    fi
fi

# =============================================================================
#  1. СИСТЕМНЫЕ ЗАВИСИМОСТИ
# =============================================================================
header "Шаг 1/6 — Системные зависимости"

info "Обновление apt..."
apt-get update -qq

PACKAGES=(python3 python3-pip python3-venv python3-dev \
          git curl build-essential libssl-dev libffi-dev \
          ca-certificates)

info "Установка пакетов: ${PACKAGES[*]}"
apt-get install -y -qq "${PACKAGES[@]}"
success "Зависимости установлены"

# =============================================================================
#  2. ПОЛЬЗОВАТЕЛЬ
# =============================================================================
header "Шаг 2/6 — Пользователь"

echo -e "${YELLOW}Под каким пользователем будет работать nanobot?${NC}"
echo -e "${YELLOW}Если пользователь не существует — будет создан.${NC}\n"

prompt BOT_USER "Имя пользователя" "root" no

# Определяем домашнюю директорию
if [[ "$BOT_USER" == "root" ]]; then
    BOT_HOME="/root"
else
    BOT_HOME="/home/$BOT_USER"
fi

# Создаём пользователя если нужно
if id "$BOT_USER" &>/dev/null; then
    success "Пользователь '${BOT_USER}' уже существует"
    BOT_HOME=$(getent passwd "$BOT_USER" | cut -d: -f6)
    info "Домашняя директория: $BOT_HOME"
else
    info "Создание пользователя '${BOT_USER}'..."
    [[ "$BOT_USER" =~ ^[a-z_][a-z0-9_-]*$ ]] \
        || error "Некорректное имя пользователя: '$BOT_USER' (только строчные буквы, цифры, _ -)"
    useradd --create-home --shell /bin/bash --comment "Nanobot service user" "$BOT_USER"
    success "Пользователь '${BOT_USER}' создан, home: $BOT_HOME"
fi

# Динамические пути — зависят от выбранного пользователя
VENV_DIR="$BOT_HOME/nanobot-env"
NANOBOT_DIR="$BOT_HOME/.nanobot"
CONFIG_FILE="$NANOBOT_DIR/config.json"

info "Пути установки:"
echo -e "  Virtualenv:  ${GREEN}${VENV_DIR}${NC}"
echo -e "  Данные бота: ${GREEN}${NANOBOT_DIR}${NC}"

# =============================================================================
#  3. ПАРАМЕТРЫ БОТА
# =============================================================================
header "Шаг 3/6 — Настройка бота"

echo -e "${YELLOW}Введите параметры конфигурации.${NC}"
echo -e "${YELLOW}Нажмите Enter чтобы принять значение по умолчанию.${NC}\n"

prompt TELEGRAM_TOKEN    "Telegram Bot Token"                   ""                              yes
prompt ALLOW_FROM        "Telegram username (allowFrom)"        "talismansim"                   no
prompt TAVILY_KEY        "Tavily API Key"                       ""                              yes
prompt PROVIDER_BASE_URL "Провайдер моделей — Base URL"        "https://api.polza.ai/api/v1"  no
prompt PROVIDER_API_KEY  "Провайдер моделей — API Key"         ""                              yes
prompt MODEL_NAME        "Модель"                               "google/gemini-3-flash-preview" no
prompt PORT              "HTTP порт"                            "18790"                         no

[[ "$PORT" =~ ^[0-9]+$ ]] && [[ "$PORT" -ge 1 ]] && [[ "$PORT" -le 65535 ]] \
    || error "Некорректный номер порта: $PORT"

echo
info "Итоговые параметры:"
echo -e "  Пользователь:    ${GREEN}${BOT_USER}${NC}"
echo -e "  Telegram Token:  ${GREEN}***${TELEGRAM_TOKEN: -6}${NC}"
echo -e "  allowFrom:       ${GREEN}${ALLOW_FROM}${NC}"
echo -e "  Tavily Key:      ${GREEN}***${TAVILY_KEY: -4}${NC}"
echo -e "  Provider URL:    ${GREEN}${PROVIDER_BASE_URL}${NC}"
echo -e "  Provider Key:    ${GREEN}***${PROVIDER_API_KEY: -4}${NC}"
echo -e "  Модель:          ${GREEN}${MODEL_NAME}${NC}"
echo -e "  Порт:            ${GREEN}${PORT}${NC}"
echo
read -rp "$(echo -e "${BOLD}Продолжить установку? [Y/n]: ${NC}")" CONFIRM
CONFIRM="${CONFIRM:-Y}"
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo "Установка отменена."; exit 0; }

# =============================================================================
#  4. ВИРТУАЛЬНОЕ ОКРУЖЕНИЕ И NANOBOT
# =============================================================================
header "Шаг 4/6 — Виртуальное окружение и nanobot"

# Функция: выполнить команду от имени BOT_USER
run_as() {
    if [[ "$BOT_USER" == "root" ]]; then
        bash -c "$*"
    else
        su - "$BOT_USER" -s /bin/bash -c "$*"
    fi
}

if [[ -d "$VENV_DIR" ]]; then
    warn "Виртуальное окружение уже существует: $VENV_DIR"
    read -rp "$(echo -e "${YELLOW}Пересоздать? [y/N]: ${NC}")" RECREATE
    if [[ "${RECREATE:-N}" =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
        info "Старое окружение удалено"
    fi
fi

if [[ ! -d "$VENV_DIR" ]]; then
    info "Создание virtualenv: $VENV_DIR (от пользователя ${BOT_USER})..."
    run_as "python3 -m venv '$VENV_DIR'"
    success "Virtualenv создан"
fi

PIP="$VENV_DIR/bin/pip"
NANOBOT_BIN="$VENV_DIR/bin/nanobot"

info "Обновление pip..."
run_as "'$PIP' install --quiet --upgrade pip"

info "Установка nanobot из репо..."
run_as "'$PIP' install --quiet --no-cache-dir 'git+${REPO_URL}'"
success "nanobot установлен"

[[ -f "$NANOBOT_BIN" ]] || error "Бинарник nanobot не найден: $NANOBOT_BIN"

# =============================================================================
#  5. КОНФИГУРАЦИЯ
# =============================================================================
header "Шаг 5/6 — Конфигурация"

# ── 5а. onboard: генерирует валидный конфиг и рабочее пространство ───────────
info "Инициализация workspace (nanobot onboard)..."
# Передаём 'y' чтобы всегда перезаписать дефолтный конфиг — патчим его сразу после
echo "y" | run_as "'$NANOBOT_BIN' onboard"
success "Workspace инициализирован, дефолтный config.json создан"

[[ -f "$CONFIG_FILE" ]] || error "onboard не создал config.json: $CONFIG_FILE"

# ── 5б. Бэкап дефолтного конфига ────────────────────────────────────────────
BACKUP="$CONFIG_FILE.bak.$(date +%Y%m%d%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP"
info "Дефолтный конфиг сохранён: $BACKUP"

# ── 5в. Патч конфига: вставляем все ключи через python3 ─────────────────────
info "Запись параметров в $CONFIG_FILE ..."
"$VENV_DIR/bin/python3" - <<PYEOF
import json, sys

cfg_path = "$CONFIG_FILE"
with open(cfg_path) as f:
    cfg = json.load(f)

# Telegram
cfg.setdefault("channels", {}).setdefault("telegram", {})
cfg["channels"]["telegram"]["token"]     = "$TELEGRAM_TOKEN"
cfg["channels"]["telegram"]["allowFrom"] = ["$ALLOW_FROM"]
cfg["channels"]["telegram"]["enabled"]   = True

# Провайдер моделей
cfg.setdefault("providers", {}).setdefault("custom", {})
cfg["providers"]["custom"]["apiKey"]  = "$PROVIDER_API_KEY"
cfg["providers"]["custom"]["apiBase"] = "$PROVIDER_BASE_URL"

# Модель
cfg.setdefault("agents", {}).setdefault("defaults", {})
cfg["agents"]["defaults"]["model"]    = "$MODEL_NAME"
cfg["agents"]["defaults"]["provider"] = "custom"

# Порт
cfg.setdefault("gateway", {})
cfg["gateway"]["port"] = int("$PORT")

# Поиск Tavily
cfg.setdefault("tools", {}).setdefault("web", {}).setdefault("search", {})
cfg["tools"]["web"]["search"]["engine"] = "tavily"
cfg["tools"]["web"]["search"]["apiKey"] = "$TAVILY_KEY"

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("OK")
PYEOF

chmod 600 "$CONFIG_FILE"
chown -R "${BOT_USER}:${BOT_USER}" "$NANOBOT_DIR"
success "config.json обновлён (права 600, владелец: ${BOT_USER})"

# =============================================================================
#  6. SYSTEMD СЕРВИС
# =============================================================================
header "Шаг 6/6 — Systemd сервис"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Nanobot Telegram AI Bot
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=${BOT_USER}
WorkingDirectory=${NANOBOT_DIR}
ExecStart=${NANOBOT_BIN} gateway
Restart=always
RestartSec=5

# Корректная кодировка
Environment=LANG=en_US.UTF-8
Environment=LC_ALL=en_US.UTF-8
Environment=PYTHONIOENCODING=utf-8

# Tavily search (nanobot читает из env, не из config.json)
Environment=TAVILY_API_KEY=${TAVILY_KEY}
Environment=WEB_SEARCH_ENGINE=tavily

# Логирование через journald
StandardOutput=journal
StandardError=journal
SyslogIdentifier=nanobot

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
success "Сервис ${SERVICE_NAME} зарегистрирован и включён в автозагрузку"

# =============================================================================
#  ЗАПУСК
# =============================================================================
echo
read -rp "$(echo -e "${BOLD}Запустить nanobot прямо сейчас? [Y/n]: ${NC}")" START_NOW
START_NOW="${START_NOW:-Y}"

if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    info "Запуск сервиса..."
    systemctl start "$SERVICE_NAME"
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "nanobot запущен и работает!"
    else
        warn "Сервис не запустился. Проверьте логи:"
        echo -e "  ${YELLOW}journalctl -u nanobot -n 30 --no-pager${NC}"
    fi
fi

# =============================================================================
#  ИТОГ
# =============================================================================
header "Установка завершена"

echo -e "  ${BOLD}Пользователь:${NC}  $BOT_USER"
echo -e "  ${BOLD}Конфиг:${NC}        $CONFIG_FILE"
echo -e "  ${BOLD}Virtualenv:${NC}    $VENV_DIR"
echo -e "  ${BOLD}Сервис:${NC}        $SERVICE_NAME (systemd)"
echo
echo -e "${BOLD}Полезные команды:${NC}"
echo -e "  ${CYAN}systemctl status nanobot${NC}                 — статус"
echo -e "  ${CYAN}systemctl restart nanobot${NC}                — перезапуск"
echo -e "  ${CYAN}journalctl -u nanobot -f${NC}                 — логи в реальном времени"
echo -e "  ${CYAN}journalctl -u nanobot -n 100 --no-pager${NC}  — последние 100 строк"
echo
echo -e "${BOLD}Обновление nanobot:${NC}"
echo -e "  ${CYAN}${PIP} install --no-cache-dir --force-reinstall git+${REPO_URL}${NC}"
echo -e "  ${CYAN}systemctl restart nanobot${NC}"
echo
success "Готово!"
