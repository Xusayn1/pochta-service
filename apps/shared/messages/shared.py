from typing import Dict

from .types import MessageTemplate

SHARED_MESSAGES: Dict[str, MessageTemplate] = {
    "SUCCESS": {
        "id": "SUCCESS",
        "messages": {
            "en": "Operation completed successfully",
            "uz": "Operatsiya muvaffaqiyatli yakunlandi",
            "ru": "Операция успешно завершена",
        },
        "status_code": 200
    },
    "CREATED": {
        "id": "CREATED",
        "messages": {
            "en": "Resource created successfully",
            "uz": "Resurs muvaffaqiyatli yaratildi",
            "ru": "Ресурс успешно создан",
        },
        "status_code": 201
    },
    "NOT_CREATED": {
        "id": "NOT_CREATED",
        "messages": {
            "en": "Resource not created successfully",
            "uz": "Resurs muvaffaqiyatli yaratilmadi",
            "ru": "Ресурс не создан успешно",
        },
        "status_code": 500
    },
    "UPDATED": {
        "id": "UPDATED",
        "messages": {
            "en": "Resource updated successfully",
            "uz": "Resurs muvaffaqiyatli yangilandi",
            "ru": "Ресурс успешно обновлен",
        },
        "status_code": 200
    },
    "NOT_UPDATED": {
        "id": "NOT_UPDATED",
        "messages": {
            "en": "Resource does not updated successfully",
            "uz": "Resurs muvaffaqiyatli yangilanmadi",
            "ru": "Ресурс не обновлен успешно",
        },
        "status_code": 500
    },
    "DELETED": {
        "id": "DELETED",
        "messages": {
            "en": "Resource deleted successfully",
            "uz": "Resurs muvaffaqiyatli o'chirildi",
            "ru": "Ресурс успешно удален",
        },
        "status_code": 200
    },
    "NOT_DELETED": {
        "id": "NOT_DELETED",
        "messages": {
            "en": "Resource not deleted",
            "uz": "Resurs o'chirildimadi",
            "ru": "Ресурс не удален",
        },
        "status_code": 200
    },
    "VALIDATION_ERROR": {
        "id": "VALIDATION_ERROR",
        "messages": {
            "en": "Invalid input data",
            "uz": "Noto'g'ri ma'lumot kiritildi",
            "ru": "Неверные входные данные",
        },
        "status_code": 400
    },
    "NOT_FOUND": {
        "id": "NOT_FOUND",
        "messages": {
            "en": "Resource not found",
            "uz": "Resurs topilmadi",
            "ru": "Ресурс не найден",
        },
        "status_code": 404
    },
    "PERMISSION_DENIED": {
        "id": "PERMISSION_DENIED",
        "messages": {
            "en": "You don't have permission to perform this action",
            "uz": "Sizda bu amalni bajarish uchun ruxsat yo'q",
            "ru": "У вас нет прав для выполнения этого действия",
        },
        "status_code": 403
    },
    "UNAUTHORIZED": {
        "id": "UNAUTHORIZED",
        "messages": {
            "en": "Authentication required",
            "uz": "Autentifikatsiya talab qilinadi",
            "ru": "Требуется аутентификация",
        },
        "status_code": 401
    },
    "INTERNAL_SERVER_ERROR": {
        "id": "INTERNAL_SERVER_ERROR",
        "messages": {
            "en": "Internal server error occurred",
            "uz": "Ichki server xatosi yuz berdi",
            "ru": "Произошла внутренняя ошибка сервера",
        },
        "status_code": 500
    },
    "UNKNOWN_ERROR": {
        "id": "UNKNOWN_ERROR",
        "messages": {
            "en": "An unexpected error occurred",
            "uz": "Kutilmagan xatolik yuz berdi",
            "ru": "Произошла непредвиденная ошибка",
        },
        "status_code": 500
    },
    "SYSTEM_ERROR": {
        "id": "SYSTEM_ERROR",
        "messages": {
            "en": "System error occurred",
            "uz": "Tizim xatosi yuz berdi",
            "ru": "Произошла системная ошибка",
        },
        "status_code": 500
    },
    "FIELD_REQUIRED": {
        "id": "FIELD_REQUIRED",
        "messages": {
            "en": "This filed is required {filed_name}",
            "uz": "Ushbu ma'lumot majburiry {field_name}",
            "ru": "Это поле обязательно для заполнения {filed_name}",
        },
        "status_code": 400
    },
}