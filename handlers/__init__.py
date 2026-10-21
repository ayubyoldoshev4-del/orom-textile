from aiogram import Dispatcher
from .common import router as common_router
from .catalog import router as catalog_router
from .order import router as order_router
from .admin import router as admin_router
from .errors import router as error_router


def register_all_handlers(dp: Dispatcher):
    """Barcha routerlarni ro'yxatdan o'tkazish tartibi."""
    # Xatoliklarni ushlovchi router
    dp.include_router(error_router)

    # Asosiy biznes-mantiq routerlari
    dp.include_router(admin_router)
    dp.include_router(order_router)
    dp.include_router(catalog_router)
    dp.include_router(common_router)
