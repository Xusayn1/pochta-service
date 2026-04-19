from typing import Dict

from .types import MessageTemplate

MEDIA_MESSAGES: Dict[str, MessageTemplate] = {
    "MEDIA_UPLOADED": {
        "id": "MEDIA_UPLOADED",
        "messages": {
            "en": "File uploaded successfully",
            "uz": "Fayl muvaffaqiyatli yuklandi",
            "ru": "Файл успешно загружен",
        },
        "status_code": 201
    },
    "MEDIA_DELETED": {
        "id": "MEDIA_DELETED",
        "messages": {
            "en": "File deleted successfully",
            "uz": "Fayl muvaffaqiyatli o'chirildi",
            "ru": "Файл успешно удален",
        },
        "status_code": 200
    },
    "MEDIA_NOT_FOUND": {
        "id": "MEDIA_NOT_FOUND",
        "messages": {
            "en": "Media file not found",
            "uz": "Media fayl topilmadi",
            "ru": "Медиа-файл не найден",
        },
        "status_code": 404
    },
    "MEDIA_UPLOAD_ERROR": {
        "id": "MEDIA_UPLOAD_ERROR",
        "messages": {
            "en": "Failed to upload file",
            "uz": "Faylni yuklashda xatolik yuz berdi",
            "ru": "Не удалось загрузить файл",
        },
        "status_code": 500
    },
    "MEDIA_FILE_REQUIRED": {
        "id": "MEDIA_FILE_REQUIRED",
        "messages": {
            "en": "File is required",
            "uz": "Fayl majburiy",
            "ru": "Файл обязателен",
        },
        "status_code": 400
    },
}