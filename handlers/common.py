import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_IDS,
    WELCOME_TEXT,
    DELIVERY_INFO_TEXT,
    CONTACTS_TEXT,
    ADMIN_INFO_TEXT,
    COMPANY_LOCATION,
    COMPANY_LOCATION_LAT,
    COMPANY_LOCATION_LON
)
from database import (
    add_or_update_user,
    get_category_by_slug,
    get_products_by_category,
    get_categories,
    get_user_orders
)
from keyboards import (
    main_menu_keyboard,
    products_inline_keyboard,
    categories_inline_keyboard,
    contact_actions_keyboard,
    admin_link_keyboard,
    format_price
)

logger = logging.getLogger(__name__)
router = Router(name="common_router")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Botga start berilganda salomlashuv va asosiy menyuni chiqarish."""
    await state.clear()

    user = message.from_user
    full_name = user.full_name or "Hurmatli mijoz"
    username = user.username

    try:
        await add_or_update_user(
            user_id=user.id,
            full_name=full_name,
            username=username
        )
    except Exception as e:
        logger.error(f"Foydalanuvchini saqlashda xatolik: {e}")

    is_admin = user.id in ADMIN_IDS
    await message.answer(
        text=WELCOME_TEXT,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam bo'limi."""
    help_text = (
        "ℹ️ <b>OROM TEXTILE Bot qo‘llanmasi:</b>\n\n"
        "🛍 <b>Mahsulotlar katalogi</b> — Barcha toifalarni ko‘rish va tanlash.\n"
        "🛏 <b>Pastellar</b> — Nafis va shinam pastel to‘plamlari.\n"
        "🧸 <b>Yostiqlar</b> — Ortopedik va qulay yostiqlar.\n"
        "🛌 <b>Matrasniklar</b> — Suv o‘tkazmaydigan va paxtali matras himoyalari.\n"
        "🧵 <b>Namat mahsulotlari</b> — Tabiiy jundan tayyorlangan milliy namatlar.\n"
        "📦 <b>Buyurtmalarim</b> — Faqat o‘zingizning buyurtmalaringiz va ularning holati.\n"
        "🚚 <b>Yetkazib berish</b> — Shartlar va muddatlar.\n"
        "📍 <b>Manzilimiz</b> — Shourum manzili va xaritasi.\n"
        "☎️ <b>Murojaat uchun</b> — Telefon va aloqa kanallari.\n"
        "👨‍💼 <b>Administrator</b> — Menejer bilan to‘g‘ridan-to‘g‘ri bog‘lanish."
    )
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        help_text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )


@router.message(F.text == "🚚 Yetkazib berish")
async def show_delivery(message: Message):
    """Yetkazib berish shartlari."""
    await message.answer(DELIVERY_INFO_TEXT, parse_mode="HTML")


@router.message(F.text == "📍 Manzilimiz")
async def show_location(message: Message):
    """Kompaniya manzili va geolokatsiyasi."""
    loc_text = (
        "📍 <b>OROM TEXTILE Shourumi</b>\n\n"
        f"🏢 <b>Manzil:</b> {COMPANY_LOCATION}\n"
        "🎯 <b>Mo‘ljal:</b> «Bunyodkor» metro bekati yaqinida\n"
        "⏰ <b>Ish vaqti:</b> Har kuni 09:00 — 21:00\n\n"
        "Quyida xaritadagi aniq joylashuvimiz:"
    )
    await message.answer(loc_text, parse_mode="HTML")
    try:
        await message.answer_location(
            latitude=COMPANY_LOCATION_LAT,
            longitude=COMPANY_LOCATION_LON
        )
    except Exception as e:
        logger.error(f"Lokatsiya yuborishda xatolik: {e}")


@router.message(F.text == "☎️ Murojaat uchun")
async def show_contacts(message: Message):
    """Aloqa va telefon raqami bo'limi."""
    await message.answer(
        text=CONTACTS_TEXT,
        parse_mode="HTML",
        reply_markup=contact_actions_keyboard()
    )


@router.callback_query(F.data == "copy_phone")
async def cb_copy_phone(callback: CallbackQuery):
    """Telefon raqamini ko'rsatish."""
    from config import COMPANY_PHONE
    await callback.answer(f"📞 Qo‘ng‘iroq uchun: {COMPANY_PHONE}", show_alert=True)


@router.message(F.text == "👨‍💼 Administrator")
async def show_admin_profile(message: Message):
    """Administrator profili bo'limi."""
    await message.answer(
        text=ADMIN_INFO_TEXT,
        parse_mode="HTML",
        reply_markup=admin_link_keyboard()
    )


# ==================== BUYURTMALARIM BO'LIMI ====================

@router.message(F.text == "📦 Buyurtmalarim")
async def show_my_orders(message: Message):
    """Mijozning faqat o'z buyurtmalarini ko'rsatish."""
    orders = await get_user_orders(user_id=message.from_user.id)

    if not orders:
        await message.answer(
            "📦 <b>Sizda hali birorta buyurtma mavjud emas.</b>\n\n"
            "Mahsulotlar katalogidan o‘zingizga yoqqan tovarlarni tanlang va qulay buyurtma bering! ✨",
            parse_mode="HTML"
        )
        return

    status_badges = {
        "yangi": "🟡 Yangi",
        "tasdiqlandi": "🔵 Tasdiqlandi",
        "tayyorlanmoqda": "🟠 Tayyorlanmoqda",
        "yetkazilmoqda": "🚚 Yetkazilmoqda",
        "yakunlandi": "🟢 Yakunlandi",
        "bekor_qilindi": "🔴 Bekor qilindi"
    }

    header_text = f"📦 <b>SIZNING BUYURTMALARINGIZ (Jami: {len(orders)} ta):</b>\n"
    await message.answer(header_text, parse_mode="HTML")

    for ord_item in orders:
        st_text = status_badges.get(ord_item["status"], ord_item["status"])
        total_str = format_price(ord_item["total_price"])
        unit_str = format_price(ord_item["unit_price"])

        card = (
            f"🧾 <b>Buyurtma kodi:</b> <code>#{ord_item['order_number']}</code>\n"
            f"📊 <b>Holati:</b> <b>{st_text}</b>\n"
            f"🕒 <b>Sana:</b> {ord_item['created_at'][:16]}\n"
            "────────────────────────\n"
            f"🛍 <b>Mahsulot:</b> {ord_item['product_name']}\n"
            f"📏 <b>O‘lcham:</b> {ord_item['product_size']} | 🎨 <b>Rang:</b> {ord_item['product_color']}\n"
            f"🔢 <b>Miqdori:</b> {ord_item['quantity']} dona x {unit_str} so‘m\n"
            f"💰 <b>Jami to‘lov:</b> <u>{total_str} so‘m</u>\n"
            f"📍 <b>Yetkazish manzili:</b> {ord_item['delivery_address']}\n"
        )
        await message.answer(card, parse_mode="HTML")


# ==================== TEZKOR TOIFALAR ====================

@router.message(F.text == "🛏 Pastellar")
async def shortcut_pastellar(message: Message):
    """Pastellar toifasiga to'g'ridan-to'g'ri o'tish."""
    category = await get_category_by_slug("pastellar")
    if not category:
        await message.answer("Ushbu bo‘limda hozircha mahsulotlar mavjud emas.")
        return

    products = await get_products_by_category(category["id"])
    if not products:
        await message.answer("🛏 Pastellar to‘plamlari tez kunda yangilanadi!")
        return

    text = (
        "🛏 <b>Pastellar to‘plamlari</b>\n\n"
        "100% tabiiy paxta va nafis jakard to‘qimali shinam pastellar. "
        "Batafsil ma’lumot olish uchun mahsulotni tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=products_inline_keyboard(products, category["id"]))


@router.message(F.text == "🧸 Yostiqlar")
async def shortcut_yostiqlar(message: Message):
    """Yostiqlar toifasiga to'g'ridan-to'g'ri o'tish."""
    category = await get_category_by_slug("yostiqlar")
    if not category:
        await message.answer("Ushbu bo‘limda hozircha mahsulotlar mavjud emas.")
        return

    products = await get_products_by_category(category["id"])
    if not products:
        await message.answer("🧸 Yostiqlar bo‘limida yangi kolleksiya kutilmoqda!")
        return

    text = (
        "🧸 <b>Yostiqlar to‘plami</b>\n\n"
        "Ortopedik, bambuk va yumshoq xotirali yostiqlar bilan xotirjam uyqudan bahramand bo‘ling. "
        "Mahsulotni tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=products_inline_keyboard(products, category["id"]))


@router.message(F.text == "🛌 Matrasniklar")
async def shortcut_matrasniklar(message: Message):
    """Matrasniklar toifasiga to'g'ridan-to'g'ri o'tish."""
    category = await get_category_by_slug("matrasniklar")
    if not category:
        await message.answer("Ushbu bo‘limda hozircha mahsulotlar mavjud emas.")
        return

    products = await get_products_by_category(category["id"])
    if not products:
        await message.answer("🛌 Matrasniklar tez kunda sotuvga chiqariladi!")
        return

    text = (
        "🛌 <b>Matrasniklar</b>\n\n"
        "Suv o‘tkazmaydigan, gigiyenik va nafas oluvchi yuqori sifatli matras himoyalari. "
        "Variantni tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=products_inline_keyboard(products, category["id"]))


@router.message(F.text == "🧵 Namat mahsulotlari")
async def shortcut_namat(message: Message):
    """Namat mahsulotlari toifasiga to'g'ridan-to'g'ri o'tish."""
    category = await get_category_by_slug("namat")
    if not category:
        await message.answer("Ushbu bo‘limda hozircha mahsulotlar mavjud emas.")
        return

    products = await get_products_by_category(category["id"])
    if not products:
        await message.answer("🧵 Namat mahsulotlari bo‘limida mahsulotlar tayyorlanmoqda!")
        return

    text = (
        "🧵 <b>Namat mahsulotlari</b>\n\n"
        "100% tabiiy jundan to‘qilgan issiq, sog‘lom va milliy naqshli namatlar. "
        "Ko‘rish uchun mahsulotni tanlang:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=products_inline_keyboard(products, category["id"]))


@router.message(F.text == "❌ Bekor qilish")
async def cancel_any_action(message: Message, state: FSMContext):
    """Har qanday FSM jarayonini bekor qilish."""
    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        "❌ Amal bekor qilindi. Siz asosiy menyudasiz.",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )


# ==================== CALLBACK NAVIGATSIYA ====================

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish."""
    await state.clear()
    is_admin = callback.from_user.id in ADMIN_IDS
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        "🏠 Asosiy menyudasiz. O‘zingizga kerakli bo‘limni tanlang:",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_cats")
async def cb_back_to_cats(callback: CallbackQuery):
    """Toifalar ro'yxatiga qaytish."""
    categories = await get_categories()
    text = (
        "🛍 <b>OROM TEXTILE Mahsulotlar Katalogi</b>\n\n"
        "Quyidagi toifalardan birini tanlang:"
    )
    try:
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(
                text=text,
                parse_mode="HTML",
                reply_markup=categories_inline_keyboard(categories)
            )
        else:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=categories_inline_keyboard(categories)
            )
    except Exception:
        await callback.message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=categories_inline_keyboard(categories)
        )
    await callback.answer()
