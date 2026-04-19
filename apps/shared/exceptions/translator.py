import logging
from typing import TypedDict, Any, Dict

from apps.shared.messages import MESSAGES, MessageTemplate

logger = logging.getLogger(__name__)


class MessageDetail(TypedDict):
    """Structure for formatted message details"""
    id: str
    message: str
    status_code: int


def get_message_detail(
        message_key: str,
        lang: str = "en",
        context: Dict[str, Any] | None = None
) -> MessageDetail:
    # Get message template with fallback
    message = MESSAGES.get(message_key)

    if not message:
        logger.warning(f"Message key not found: {message_key}")
        message = MESSAGES.get('UNKNOWN_ERROR')

        if not message:
            logger.error("UNKNOWN_ERROR message not found in MESSAGES dictionary")
            return {
                "id": "SYSTEM_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500
            }

    context = context or {}
    messages_dict = message["messages"]

    # Language fallback chain
    base_lang = lang.split('-')[0].split('_')[0]
    template = (
            messages_dict.get(lang)
            or messages_dict.get(base_lang)
            or messages_dict.get("en", "Error occurred")
    )

    # Format message
    try:
        formatted_message: str = template.format(**context)
    except (KeyError, ValueError) as e:
        logger.warning(
            f"Message formatting failed - "
            f"key: {message_key}, lang: {lang}, "
            f"error: {e}, context: {context}"
        )
        formatted_message = template

    return {
        "id": message["id"],
        "message": formatted_message,
        "status_code": message["status_code"]
    }


def get_raw_message(message_key: str) -> MessageTemplate | None:
    """
    Get raw message template (internal use only).

    Args:
        message_key: Key to look up in MESSAGES dictionary

    Returns:
        MessageTemplate or None if not found
    """
    return MESSAGES.get(message_key)