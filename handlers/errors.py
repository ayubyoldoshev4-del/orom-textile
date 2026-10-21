import logging
from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramAPIError
)

logger = logging.getLogger(__name__)
router = Router(name="error_router")


@router.errors()
async def global_error_handler(event: ErrorEvent):
    """Barcha kutilmagan va Telegram xatolarini ushlab qoluvchi global handler."""
    exc = event.exception

    # 1. Foydalanuvchi botni bloklaganda bot to'xtamasligi kerak
    if isinstance(exc, TelegramForbiddenError):
        logger.warning(f"Foydalanuvchi botni bloklagan: {exc}")
        return True

    # 2. Noto'g'ri so'rovlar (masalan eskirgan inline tugma)
    if isinstance(exc, TelegramBadRequest):
        logger.warning(f"Telegram BadRequest xatoligi: {exc}")
        return True

    # 3. Tarmoq xatolari
    if isinstance(exc, TelegramNetworkError):
        logger.warning(f"Telegram tarmoq xatosi: {exc}")
        return True

    # 4. Boshqa barcha xatoliklar
    logger.error(f"Kutilmagan bot xatosi: {exc}", exc_info=True)

    try:
        update = event.update
        if update.message:
            await update.message.answer(
                "⚠️ Kechirasiz, vaqtinchalik texnik uzilish yuz berdi. "
                "Iltimos, qaytadan /start buyrug‘ini bosing."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "⚠️ Texnik uzilish yuz berdi. Qaytadan urinib ko‘ring.",
                show_alert=True
            )
    except Exception:
        pass

    return True
