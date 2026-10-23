import asyncio
import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError
from aiohttp import web

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers import register_all_handlers

# Windows terminallarida UTF-8 emoji kodlash xatoliklarini oldini olish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def setup_logging():
    """Konsol va aylanuvchi faylga yozuvchi professional logging tizimi."""
    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "bot.log"

    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    )

    # Konsol chiqishi
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Faylga yozish (har bir fayl maks 5MB, 3 ta zaxira fayl)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


async def setup_bot_commands(bot: Bot):
    """Telegram menyusidagi standart buyruqlarni o'rnatish."""
    commands = [
        BotCommand(command="start", description="Botni qayta ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo‘llanma"),
        BotCommand(command="admin", description="Administrator paneli")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logging.warning(f"Buyruqlarni o'rnatishda xatolik: {e}")


async def notify_admins_on_startup(bot: Bot):
    """Bot ishga tushganda barcha adminlarga bildirishnoma yuborish."""
    startup_msg = (
        "🚀 <b>OROM TEXTILE boti muvaffaqiyatli ishga tushirildi! (24/7 Rejim)</b>\n\n"
        "📦 Ma’lumotlar bazasi va toifalar to‘liq tayyor.\n"
        "Mijozlardan yangi buyurtmalar qabul qilinmoqda."
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=startup_msg, parse_mode="HTML")
        except Exception:
            pass


async def handle_ping(request):
    """Render.com uchun HTTP health-check javobi."""
    return web.Response(
        text="OROM TEXTILE Telegram Bot is running 24/7!",
        content_type="text/plain",
        status=200
    )


async def start_dummy_web_server():
    """Render.com Web Service rejimida portni tinglash uchun yengil HTTP server."""
    port_str = os.getenv("PORT")
    if not port_str:
        return None
    try:
        port = int(port_str)
        app = web.Application()
        app.router.add_get("/", handle_ping)
        app.router.add_get("/health", handle_ping)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logging.getLogger("OROM_TEXTILE").info(
            f"Render Web Service uchun HTTP server {port}-portda muvaffaqiyatli ishga tushdi."
        )
        return runner
    except Exception as e:
        logging.getLogger("OROM_TEXTILE").warning(
            f"HTTP serverni ishga tushirishda ogohlantirish: {e}"
        )
        return None


async def run_bot():
    """Botning asosiy ishchi asinxron sikli."""
    setup_logging()
    logger = logging.getLogger("OROM_TEXTILE")
    logger.info("Bot initsializatsiya qilinmoqda...")

    # Token tekshiruvi (.env faylidan olingan)
    if not BOT_TOKEN or "1234567890" in BOT_TOKEN:
        logger.error(
            "XATOLIK: .env faylida haqiqiy BOT_TOKEN topilmadi! "
            "Iltimos, .env faylini to'ldiring."
        )
        return

    # Ma'lumotlar bazasini sozlash
    try:
        await init_db()
        logger.info("Ma'lumotlar bazasi tayyor holatda.")
    except Exception as e:
        logger.critical(f"Ma'lumotlar bazasini ishga tushirishda xatolik: {e}", exc_info=True)
        return

    # Bot va Dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Barcha handlerlarni va xatoliklar menejerini ulash
    register_all_handlers(dp)

    # Telegram menyusidagi buyruqlarni o'rnatish
    await setup_bot_commands(bot)

    # Adminlarga xabar berish
    await notify_admins_on_startup(bot)

    # Render.com yoki bulutli serverlar uchun Web Port tinglovchisi
    web_runner = await start_dummy_web_server()

    # 24/7 Uzluksiz ishlash va avtomatik qayta ulanish mexanizmi (Supervisor)
    reconnect_delay = 3
    logger.info("OROM TEXTILE boti 24/7 rejimida ish boshladi...")

    while True:
        try:
            # Eski kutilib qolgan xabarlarni tozalab, pollingni boshlash
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
            break
        except (TelegramNetworkError, asyncio.TimeoutError, ConnectionError) as net_err:
            logger.warning(
                f"Tarmoq uzilishi yuz berdi: {net_err}. "
                f"{reconnect_delay} soniyadan keyin qayta ulanadi..."
            )
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 1.5, 30)  # Maksimal 30 soniyagacha oshirish
        except TelegramAPIError as api_err:
            logger.error(f"Telegram API xatosi: {api_err}. 5 soniyadan keyin qayta ulanish...")
            await asyncio.sleep(5)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot operator tomonidan to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Kutilmagan xatolik yuz berdi: {e}. 5 soniyadan keyin qayta ishga tushiriladi...", exc_info=True)
            await asyncio.sleep(5)
        finally:
            reconnect_delay = 3

    # Yopilish jarayoni
    if web_runner:
        try:
            await web_runner.cleanup()
        except Exception:
            pass
    try:
        await bot.session.close()
    except Exception:
        pass
    logger.info("Bot sessiyasi yakunlandi.")


def main():
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Dastur yakunlandi.")


if __name__ == "__main__":
    main()
