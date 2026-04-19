"""
Exception message templates for DRF exception handler.
Maps exception types to translated error messages with appropriate status codes.
"""

from typing import Dict

from .types import MessageTemplate

EXCEPTION_MESSAGES: Dict[str, MessageTemplate] = {
    "AUTHENTICATION_FAILED": {
        "id": "AUTHENTICATION_FAILED",
        "messages": {
            "en": "Authentication credentials were not provided or are invalid",
            "uz": "Autentifikatsiya ma'lumotlari taqdim etilmagan yoki noto'g'ri",
            "ru": "Учетные данные аутентификации не предоставлены или недействительны",
        },
        "status_code": 401
    },
    "METHOD_NOT_ALLOWED": {
        "id": "METHOD_NOT_ALLOWED",
        "messages": {
            "en": "Method not allowed for this endpoint",
            "uz": "Bu endpoint uchun metod ruxsat etilmagan",
            "ru": "Метод не разрешен для этой конечной точки",
        },
        "status_code": 405
    },
    "NOT_ACCEPTABLE": {
        "id": "NOT_ACCEPTABLE",
        "messages": {
            "en": "Could not satisfy the request Accept header",
            "uz": "So'rovning Accept sarlavhasini qondirish imkonsiz",
            "ru": "Не удалось удовлетворить заголовок Accept запроса",
        },
        "status_code": 406
    },
    "UNSUPPORTED_MEDIA_TYPE": {
        "id": "UNSUPPORTED_MEDIA_TYPE",
        "messages": {
            "en": "Unsupported media type in request",
            "uz": "So'rovda qo'llab-quvvatlanmaydigan media turi",
            "ru": "Неподдерживаемый тип медиа в запросе",
        },
        "status_code": 415
    },
    "THROTTLED": {
        "id": "THROTTLED",
        "messages": {
            "en": "Request was throttled. Please try again later",
            "uz": "So'rov cheklandi. Keyinroq qayta urinib ko'ring",
            "ru": "Запрос был ограничен. Пожалуйста, попробуйте позже",
        },
        "status_code": 429
    },
    "UNKNOWN_FIELDS_ERROR": {
        "id": "UNKNOWN_FIELDS_ERROR",
        "messages": {
            "en": "Invalid field names: {fields}",
            "uz": "Noto'g'ri kalitlar: {fields}",
            "ru": "Недопустимые имена полей: {fields}",
        },
        "status_code": 400
    },
}