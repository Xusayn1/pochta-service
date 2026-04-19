import html
import logging
import threading

from apps.shared.utils.custom_current_host import get_client_ip
from core import config

logger = logging.getLogger(__name__)

try:
    import telebot
except ImportError:  # pragma: no cover - optional dependency
    telebot = None


def _get_bot():
    if not telebot or not config.TELEGRAM_BOT_TOKEN:
        return None
    return telebot.TeleBot(config.TELEGRAM_BOT_TOKEN)


def _send_telegram_message(text: str):
    bot = _get_bot()
    if bot is None or not config.TELEGRAM_CHANNEL_ID:
        logger.debug("Telegram alerts are disabled")
        return

    try:
        bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except Exception as exc:  # pragma: no cover - network dependent
        logger.error("Failed to send alert to Telegram: %s", exc)


def send_alert(text: str):
    threading.Thread(target=_send_telegram_message, args=(text,), daemon=True).start()


def alert_to_telegram(traceback_text: str, message: str = "No message provided",
                      request=None, ip: str = None, port: str = None):
    if not isinstance(message, str):
        message = str(message)

    if request and not ip:
        ip = get_client_ip(request)
        port = request.META.get("REMOTE_PORT")

    safe_message = html.escape(message)
    safe_traceback = html.escape(traceback_text)
    safe_ip = html.escape(ip) if ip else "unknown"
    safe_port = html.escape(str(port)) if port else "unknown"

    text = (
        "Exception Alert\n\n"
        f"Message: {safe_message}\n\n"
        f"Traceback: {safe_traceback}\n\n"
        f"IP Address/Port: {safe_ip}:{safe_port}\n"
    )
    send_alert(text)
