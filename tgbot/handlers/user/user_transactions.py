# - *- coding: utf- 8 - *-
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.data.config import *
from tgbot.data.loader import dp
from tgbot.keyboards.inline_user import refill_bill_finl, refill_select_finl
from tgbot.services.api_qiwi import QiwiAPI
from tgbot.services.api_sqlite import update_userx, get_refillx, add_refillx, get_userx
from tgbot.utils.const_functions import get_date, get_unix
from tgbot.utils.crystalpay_sdk import CrystalPAY
from tgbot.utils.misc_functions import send_admins

# Минимальная сумма пополнения в рублях
min_input_qiwi = 5
min_input_crystal = 5


# Выбор способа пополнения
@dp.callback_query_handler(text="user_refill", state="*")
async def refill_way(call: CallbackQuery, state: FSMContext):
    get_kb = refill_select_finl()

    if get_kb is not None:
        await call.message.edit_text("<b>💰 Выберите способ пополнения</b>", reply_markup=get_kb)
    else:
        await call.answer("⛔ Пополнение временно недоступно", True)


# Выбор способа пополнения
@dp.callback_query_handler(text_startswith="refill_select", state="*")
async def refill_way_select(call: CallbackQuery, state: FSMContext):
    get_way = call.data.split(":")[1]
    await state.update_data(here_pay_way=get_way)
    if get_way == 'Crystal':
        print('crystal')
        await state.set_state("here_refill_amount_crystal")
        await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")
    else:
        await state.set_state("here_refill_amount")
        await call.message.edit_text("<b>💰 Введите сумму пополнения</b>")


###################################################################################
#################################### ВВОД СУММЫ ###################################
# Принятие суммы для пополнения средств через QIWI
@dp.message_handler(state="here_refill_amount")
async def refill_get(message: Message, state: FSMContext):
    if message.text.isdigit():
        cache_message = await message.answer("<b>♻ Подождите, платёж генерируется...</b>")
        pay_amount = int(message.text)

        if min_input_qiwi <= pay_amount <= 300000:
            get_way = (await state.get_data())['here_pay_way']
            await state.finish()

            get_message, get_link, receipt = await (
                QiwiAPI(cache_message, pass_user=True)
            ).bill(pay_amount, get_way)

            if get_message:
                await cache_message.edit_text(get_message, reply_markup=refill_bill_finl(get_link, receipt, get_way))
        else:
            await cache_message.edit_text(
                f"<b>❌ Неверная сумма пополнения</b>\n"
                f"▶ Cумма не должна быть меньше <code>{min_input_qiwi}₽</code> и больше <code>300 000₽</code>\n"
                f"💰 Введите сумму для пополнения средств",
            )
    else:
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💰 Введите сумму для пополнения средств")


# Принятие суммы для пополнения средств через CrystalPAY
@dp.message_handler(state="here_refill_amount_crystal")
async def create_crystal_pay(message: Message, state: FSMContext, del_msg=None):
    if message.text.isdigit() and int(message.text) >= 0:
        get_way = (await state.get_data())['here_pay_way']
        crystal = CrystalPAY(crystal_name, crystal_secret)
        link = crystal.Invoice.create(amount=int(message.text), currency="RUB", description="Пополнение баланса",
                                      type_="purchase", lifetime=120, redirect_url=redirect_url.format())
        await message.answer("🎈 Ссылка на оплату сгенерирована:\n"
                             f"✔ ID платежа: {link['id']}\n"
                             f"📎 Ссылка: <a href='{link['url']}'>нажмите для пополнения счёта</a>",
                             reply_markup=refill_bill_finl(link['url'], link['id'], get_way))
        await state.finish()
    else:
        await message.answer(f"❌ <b>Неверная сумма пополнения</b>\n"
                             f"▶ Мин. сумма пополнения: <code>{min_input_crystal}руб</code>\n"
                             f"💵 Введите сумму для пополнения средств 💎")


###################################################################################
################################ ПРОВЕРКА ПЛАТЕЖЕЙ ################################
# Проверка оплаты через форму
@dp.callback_query_handler(text_startswith="Pay:Form")
async def refill_check_form(call: CallbackQuery):
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        QiwiAPI(call, pass_user=True)
    ).check_form(receipt)

    if pay_status == "PAID":
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, "Form")
        else:
            await call.answer("❗ Ваше пополнение уже было зачислено.", True)
    elif pay_status == "EXPIRED":
        await call.message.edit_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>")
    elif pay_status == "WAITING":
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == "REJECTED":
        await call.message.edit_text("<b>❌ Счёт был отклонён.</b>")


# Проверка оплаты по переводу (по нику или номеру)
@dp.callback_query_handler(text_startswith=['Pay:Number', 'Pay:Nickname'])
async def refill_check_send(call: CallbackQuery):
    way_pay = call.data.split(":")[1]
    receipt = call.data.split(":")[2]

    pay_status, pay_amount = await (
        QiwiAPI(call, pass_user=True)
    ).check_send(receipt)

    if pay_status == 1:
        await call.answer("❗ Оплата была произведена не в рублях.", True, cache_time=5)
    elif pay_status == 2:
        await call.answer("❗ Платёж не был найден.\n"
                          "⌛ Попробуйте чуть позже.", True, cache_time=5)
    elif pay_status == 4:
        pass
    else:
        get_refill = get_refillx(refill_receipt=receipt)
        if get_refill is None:
            await refill_success(call, receipt, pay_amount, way_pay)
        else:
            await call.answer("❗ Ваше пополнение уже зачислено.", True, cache_time=60)


# Проверка платежа через Crystal Pay
@dp.callback_query_handler(text_startswith="Pay:Crystal")
async def refill_check_crystal(call: CallbackQuery):
    print("Check")
    call_data = call.data.split(":")
    receipt = call_data[2]
    way_pay = call_data[1]
    crystal = CrystalPAY(crystal_name, crystal_secret)
    status = crystal.Invoice.getinfo(receipt)
    pay_amount = status['pay_amount']
    pay_status = status['state']
    get_user_info = get_userx(user_id=call.from_user.id)
    print("Pay amount")
    if pay_status == "payed":
        await refill_success(call, receipt, pay_amount, way_pay)
        await call.message.edit_text(
            f"<b>💰 Вы пополнили баланс на сумму <code>{pay_amount}₽</code>. Удачи ❤\n"
            f"🧾 Номер платежа: <code>{receipt}</code>\n"
            f"📱 Профиль: <a href='tg://user?id={call.from_user.id}'>{get_user_info['user_name']}</a></b>",
            reply_markup=None,
        )
    else:
        await call.message.edit_text(
            f"<b>❌ Платёж не был проведён</b>\n"
            f"🧾 Номер платежа: <code>{receipt}</code>\n"
            f"💰 Введите сумму для пополнения средств",
            reply_markup=None,
        )


##########################################################################################
######################################### ПРОЧЕЕ #########################################
##########################################################################################
# Зачисление средств
async def refill_success(call: CallbackQuery, receipt, amount, get_way):
    get_user = get_userx(user_id=call.from_user.id)

    add_refillx(get_user['user_id'], get_user['user_login'], get_user['user_name'], receipt,
                amount, receipt, get_way, get_date(), get_unix())

    update_userx(
        call.from_user.id,
        user_balance=get_user['user_balance'] + amount,
        user_refill=get_user['user_refill'] + amount,
    )

    await call.message.edit_text(
        f"<b>💰 Вы пополнили баланс на сумму <code>{amount}₽</code>. Удачи ❤\n"
        f"🧾 Чек: <code>#{receipt}</code></b>",
    )

    await send_admins(
        f"👤 Пользователь: <b>@{get_user['user_login']}</b> | <a href='tg://user?id={get_user['user_id']}'>{get_user['user_name']}</a> | <code>{get_user['user_id']}</code>\n"
        f"💰 Сумма пополнения: <code>{amount}₽</code>\n"
        f"🧾 Чек: <code>#{receipt}</code>\n"
        f"💳 Способ: <code>{get_way}"
    )
