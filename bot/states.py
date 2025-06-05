from aiogram.fsm.state import State,StatesGroup

class OrderState(StatesGroup):
    order_name = State()
    last_message_id = State()

class AdminState(StatesGroup):
    last_message_id = State()
    name = State()
    password = State()

class ChangeStatus(StatesGroup):
    last_message_id = State()
    status = State()
    order_id = State()