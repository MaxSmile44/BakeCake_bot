# Еще сырой вариант
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)

TG_TOKEN = 'TG_TOKEN'

# тестовые данные
orders = [{'id': 25, 'count': 3}, {'id': 14, 'count': 1}]

data = {'address': "", 'date': "", 'time': "", "comments": ""}

ADDRESS = 1
DATE = 2
TIME = 3
COMMENTS = 4

updater = Updater('TG_TOKEN')
dispatcher = updater.dispatcher


def start(update, _):
    for i, order in enumerate(orders):
        keyboard = [
            [
                InlineKeyboardButton("+", callback_data=f'sign+ {i}'),
                InlineKeyboardButton("-", callback_data=f'sign- {i}'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f'id: {order['id']}, Количество: {order['count']}', reply_markup=reply_markup)

    keyboard = [
        [
            InlineKeyboardButton("Оформление заказа", callback_data=f'orders {orders}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'{orders}', reply_markup=reply_markup)


def button(update, _):
    query = update.callback_query
    query.answer()

    variant = query.data[4]
    order_num = int(query.data[6:])

    if variant == '+':
        orders[order_num]['count'] += 1
    elif variant == '-' and orders[order_num]['count'] > 0:
        orders[order_num]['count'] -= 1
    keyboard = [
        [
            InlineKeyboardButton("+", callback_data=f'sign+ {order_num}'),
            InlineKeyboardButton("-", callback_data=f'sign- {order_num}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        f'id: {orders[order_num]['id']}, Количество: {orders[order_num]['count']}', reply_markup=reply_markup
    )


def place_order(update, _):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{orders}')


def add(update, _):
    global data
    data = {'address': "", 'date': "", 'time': "", "comments": ""}
    update.message.reply_text("Укажите данные о себе\n\nАдрес доставки:")
    return ADDRESS


def get_address(update, _):
    data['address'] = update.message.text
    update.message.reply_text(f"Адрес доставки: {update.message.text}\n\nДата доставки (обязательное поле, если доставка в ближайшие 24 часа +20%)")
    return DATE


def get_date(update, _):
    data['date'] = update.message.text
    update.message.reply_text(f"Дата доставки: {update.message.text}\n\nВремя доставки (обязательное поле)")
    return TIME


def get_time(update, _):
    data['time'] = update.message.text
    update.message.reply_text(f"Время доставки: {update.message.text}\n\nКомментарий к заказу")
    return COMMENTS


def get_comments(update, _):
    data['comments'] = update.message.text
    update.message.reply_text(f"Комментарий: {update.message.text}")
    msg = """Ваши данные

Адрес: {}
Дата: {}
Время: {}
Комментарий: {}""".format(data['address'], data['date'], data['time'], data['comments'])
    update.message.reply_text(msg)
    return ConversationHandler.END


def cancel(update, _):
    update.message.reply_text('canceled')
    return ConversationHandler.END


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button, pattern='^sign'))
dispatcher.add_handler(CallbackQueryHandler(place_order, pattern='^orders'))

my_conversation_handler = ConversationHandler(
   entry_points=[CommandHandler('add', add)],
   states={
       ADDRESS: [
           CommandHandler('cancel', cancel),
           MessageHandler(Filters.text, get_address)
       ],
       DATE: [
           CommandHandler('cancel', cancel),
           MessageHandler(Filters.text, get_date)
       ],
       TIME: [
           CommandHandler('cancel', cancel),
           MessageHandler(Filters.text, get_time)
       ],
       COMMENTS: [
           CommandHandler('cancel', cancel),
           MessageHandler(Filters.text, get_comments)
       ],
   },
   fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(my_conversation_handler)

updater.start_polling()
updater.idle()