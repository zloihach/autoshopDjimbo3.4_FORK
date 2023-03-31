# - *- coding: utf- 8 - *-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.data.config import payments_enabled


# Выбор способов пополнения
def refill_select_finl():
    pay_type = InlineKeyboardMarkup()
    if "qiwi" in payments_enabled:
        pay_type.add(InlineKeyboardButton("📋 QIWI форма", callback_data="refill_select:Form"))
        pay_type.add(InlineKeyboardButton("📞 QIWI номер", callback_data="refill_select:Number"))
        pay_type.add(InlineKeyboardButton("Ⓜ QIWI никнейм", callback_data="refill_select:Nickname"))
    if "crystal" in payments_enabled:
        pay_type.add(InlineKeyboardButton("💎 CrystalPay", callback_data="refill_select:Crystal"))
    return pay_type


# Проверка киви платежа
def refill_bill_finl(send_requests, get_receipt, get_way):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("🌀 Перейти к оплате", url=send_requests)
    ).add(
        InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"Pay:{get_way}:{get_receipt}")
    )

    return keyboard


# Кнопки при открытии самого товара
def products_open_finl(position_id, category_id, remover):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("💰 Купить товар", callback_data=f"buy_item_open:{position_id}:{remover}")
    ).add(
        InlineKeyboardButton("🔙 Вернуться", callback_data=f"buy_category_open:{category_id}:{remover}")
    )

    return keyboard


# Подтверждение покупки товара
def products_confirm_finl(position_id, get_count):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"buy_item_confirm:yes:{position_id}:{get_count}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"buy_item_confirm:not:{position_id}:{get_count}")
    )

    return keyboard


# Ссылка на поддержку
def user_support_finl(user_name):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton("💌 Написать в поддержку", url=f"https://t.me/{user_name}"),
    )

    return keyboard