from typing import Dict

from .types import MessageTemplate

USER_MESSAGES: Dict[str, MessageTemplate] = {
    "USER_NOT_FOUND": {
        "id": "USER_NOT_FOUND",
        "messages": {
            "en": "Invalid credentials. Please check your login details.",
            "uz": "Ushbu ma'lumotlar bo'yicha foydalanuvchi topilmadi.",
            "ru": "Неверные учетные данные. Пожалуйста, проверьте свои данные для входа.",
        },
        "status_code": 400
    },
    "USER_IS_NOT_ACTIVE": {
        "id": "USER_IS_NOT_ACTIVE",
        "messages": {
            "en": "User is not active.",
            "uz": "Faol foydalanuvchi emas.",
            "ru": "Пользователь неактивен.",
        },
        "status_code": 400
    },
    "TOKEN_GENERATING_ERROR": {
        "id": "TOKEN_GENERATING_ERROR",
        "messages": {
            "en": "Error happens while generating tokens.",
            "uz": "Token yaratishda xatolik yuz berdi.",
            "ru": "Ошибка возникает при генерации токенов.",
        },
        "status_code": 500
    },
    "INVALID_TOKEN": {
        "id": "INVALID_TOKEN",
        "messages": {
            "en": "Invalid token",
            "uz": "Token yaroqli emas.",
            "ru": "Недействительный токен",
        },
        "status_code": 500
    },
    "PHONE_NUMBER_EXIST_ERROR": {
        "id": "PHONE_NUMBER_EXIST_ERROR",
        "messages": {
            "en": "These phone numbers are already exists ({phone_numbers})",
            "uz": "Ushbu telefon raqamlar allaqachon qo'shilgan ({phone_numbers})",
            "ru": "Эти номера телефонов уже существуют ({phone_numbers})",
        },
        "status_code": 400
    },
    "INVALID_PHONE_NUMBER_ERROR": {
        "id": "INVALID_PHONE_NUMBER_ERROR",
        "messages": {
            "en": "These phone numbers are not valid ({phone_numbers})",
            "uz": "Ushbu telefon raqamlar noto'g'ri ({phone_numbers})",
            "ru": "Эти номера телефонов недействительны ({phone_numbers})",
        },
        "status_code": 400
    },
    "USER_REGISTERED_SUCCESSFULLY": {
        "id": "USER_REGISTERED_SUCCESSFULLY",
        "messages": {
            "en": "User registered successfully",
            "uz": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
            "ru": "Пользователь успешно зарегистрирован",
        },
        "status_code": 201
    },
    "INVALID_LANGUAGE_TYPE": {
        "id": "INVALID_LANGUAGE_TYPE",
        "messages": {
            "en": "Invalid language type",
            "uz": "Noto'g'ri til tipi",
            "ru": "Неверный тип языка"
        },
        "status_code": 400
    },

}
