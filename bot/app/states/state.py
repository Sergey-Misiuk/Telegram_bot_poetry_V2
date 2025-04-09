from aiogram.fsm.state import StatesGroup, State


class Reg_poem(StatesGroup):
    title = State()
    text = State()
    author = State()
    
    
class Del_poem(StatesGroup):
    title = State()
    text = State()
