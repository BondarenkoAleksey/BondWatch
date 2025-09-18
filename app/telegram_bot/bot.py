import asyncio
import logging
import os

from aiogram import F
from aiogram.filters import CommandObject
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from app.celery_tasks.tasks import sync_all_bonds_task, sync_bond_task
from app.t_investicii.portfolio import get_portfolio_info

logging.basicConfig(level=logging.INFO)

# Берём токен из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Не найден TELEGRAM_TOKEN в переменных окружения")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class BondSync(StatesGroup):
    waiting_for_isin = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я BondWatch Bot.\n"
        "Доступные команды:\n"
        "/sync_all — синхронизировать все облигации\n"
        "/bond — синхронизировать конкретный бонд\n"
        "/portfolio —  получить информацию о портфеле в Т-инвестициях"
    )


@dp.message(Command("sync_all"))
async def cmd_sync_all(message: types.Message):
    sync_all_bonds_task.delay()
    await message.answer("🔄 Запущено обновление всех облигаций!")


@dp.message(Command("bond"))
async def cmd_sync_bond(message: types.Message, state: FSMContext):
    await message.answer("✍ Введите ISIN облигации:")
    await state.set_state(BondSync.waiting_for_isin)


@dp.message(BondSync.waiting_for_isin)
async def process_isin(message: types.Message, state: FSMContext):
    isin = message.text.strip()
    sync_bond_task.delay(isin)
    await message.answer(f"🔄 Запущена синхронизация для {isin}")
    await state.clear()


@dp.message(Command("portfolio"))
async def cmd_portfolio(message: types.Message):
    try:
        portfolio = get_portfolio_info()
        if not portfolio:
            await message.answer("📭 У вас нет доступных счетов.")
            return

        text = "💼 Ваш портфель:\n\n"
        for acc in portfolio:
            text += f"📌 Счет: {acc['account_name']} ({acc['account_id']})\n"
            for pos in acc['positions']:
                text += f"— {pos['figi']}: {pos['quantity']} шт.\n"
            text += "\n"

        await message.answer(text)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())