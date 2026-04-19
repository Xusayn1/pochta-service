from typing import Dict

from .types import MessageTemplate

VERSION_MESSAGES: Dict[str, MessageTemplate] = {
    "ACTIVE_APP_VERSION_EXISTS": {
        "id": "ACTIVE_APP_VERSION_EXISTS",
        "messages": {
            "en": "Active version already exists",
            "uz": "Faol versiya mavjud",
            "ru": "Активная версия уже существует",
        },
        "status_code": 400
    },
    "FORCE_UPDATE_REQUIRES_ACTIVE": {
        "id": "FORCE_UPDATE_REQUIRES_ACTIVE",
        "messages": {
            "en": "Force update requires active True",
            "uz": "Majburiy o'zgarish faollikni talab qiladi",
            "ru": "Принудительное обновление требует активного True",
        },
        "status_code": 400
    },
    "APP_VERSION_NOT_FOUND": {
        "id": "APP_VERSION_NOT_FOUND",
        "messages": {
            "en": "App version is not found",
            "uz": "Ushbu versiya topilmadi",
            "ru": "Версия приложения не найдена",
        },
        "status_code": 400
    },
    "VERSION_ALREADY_EXISTS": {
        "id": "VERSION_ALREADY_EXISTS",
        "messages": {
            "en": "Version with this number and device type already exists",
            "uz": "Ushbu verisya raqami ushbu qurilma turida allaqachon mavjud",
            "ru": "Версия с таким номером и типом устройства уже существует",
        },
        "status_code": 400
    }
}