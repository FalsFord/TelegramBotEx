from aiogram.utils.keyboard import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardBuilder,
)

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Оформить заказ", callback_data="to_order")],
        [InlineKeyboardButton(text="📌 Проверить статус заказа", callback_data="status")],
        [InlineKeyboardButton(text="🔒 Админ-панель", callback_data="admin")],
    ]
)


go_back = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🏠 Главное меню", callback_data="back")]]
)

go_admin = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🔒 Админ-панель", callback_data="admin_panel")]]
)

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Список заказов", callback_data="admin_check_orders_page_"),
     InlineKeyboardButton(text="🏠 Главное меню", callback_data="back")],
])


async def orders_page(page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_check_orders_page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"admin_check_orders_page_{page + 1}"))

    keyboard.row(*nav_buttons)
    keyboard.row(InlineKeyboardButton(text="🔄 Обновить статус заказа", callback_data="change_status"))
    keyboard.row(InlineKeyboardButton(text="🔒 Админ панель", callback_data="admin_panel"))

    return keyboard.as_markup()




async def order_status() -> InlineKeyboardMarkup:
    types_orders = ["Заказ собирается", "Находится в пути", "Пришел в пункт выдачи", "Готов к выдаче", ]
    keyboard = InlineKeyboardBuilder()
    for type_order in types_orders:
        keyboard.add(InlineKeyboardButton(text=type_order, callback_data=type_order))
    keyboard.adjust(2)
    return keyboard.as_markup()