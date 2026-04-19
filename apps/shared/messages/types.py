from typing import TypedDict, Dict


class MessageTemplate(TypedDict):
    """Structure for message templates"""
    id: str
    messages: Dict[str, str]  # lang code -> message template
    status_code: int