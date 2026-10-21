import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_IDS
from database import (
    get_statistics,
    get_all_orders,
    get_order_by_id,
    update_order_status,
    get_all_products,
    get_product_by_id,
    add_product,
    delete_product,
    toggle_product_availability,
    get_categories,
    get_all_users
)
from keyboards import (
    admin_panel_keyboard,
    admin_orders_filter_keyboard,
    admin_order_actions_keyboard,
    admin_products_list_keyboard,
    admin_product_actions_keyboard,
    admin_category_select_keyboard,
    cancel_reply_keyboard,
    main_menu_keyboard,
    format_price
)

logger = logging.getLogger(__name__)
router = Router(name="admin_router")


class AddProductStates(StatesGroup):
    category = State()
    code = State()
    name = State()
    description = State()
    price = State()
    sizes = State()
    colors = State()
    stock_status = State()
    photo = State()


class BroadcastStates(StatesGroup):
    message = State()


def is_admin_filter(user_id: int) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    return user_id in ADMIN_IDS


# ==================== ADMIN PANELGA KIRISH ====================

@router.message(Command("admin"))
@router.message(F.text == "👑 Admin Panel")
async def show_admin_panel(message: Message, state: FSMContext):
    """Admin panel bosh sahifasi."""
    if not is_admin_filter(message.from_user.id):
        await message.answer("⛔️ Kechirasiz, sizda admin huquqi yo‘q.")
        return

    await state.clear()
    welcome_admin = (
        "👑 <b>OROM TEXTILE — Administrator Paneli</b>\n\n"
        "Quyidagi boshqaruv bo‘limlaridan birini tanlang:"
    )
    await message.answer(
        text=welcome_admin,
        parse_mode="HTML",
        reply_markup=admin_panel_keyboard()
    )


@router.callback_query(F.data == "admin:back")
async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    """Admin panel bosh menyusiga qaytish."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    await state.clear()
    text = "👑 <b>OROM TEXTILE — Administrator Paneli</b>\n\nBo‘limni tanlang:"
    try:
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_panel_keyboard())
    await callback.answer()


# ==================== STATISTIKA ====================

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Statistika ma'lumotlari."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    stats = await get_statistics()
    rev_str = format_price(stats["total_revenue"])

    stats_text = (
        "📊 <b>OROM TEXTILE — BIZNES STATISTIKASI</b>\n"
        "────────────────────────\n"
        f"👥 <b>Jami mijozlar:</b> {stats['users_count']} nafar\n"
        f"📦 <b>Faol mahsulotlar:</b> {stats['products_count']} ta\n"
        f"📋 <b>Jami buyurtmalar:</b> {stats['orders_count']} ta\n"
        f"🟡 <b>Kutilayotgan (yangi):</b> {stats['pending_count']} ta\n"
        f"📅 <b>Bugungi buyurtmalar:</b> {stats['today_orders_count']} ta\n"
        f"💰 <b>Jami savdo tushumi:</b> <u>{rev_str} so‘m</u>\n"
        "────────────────────────\n"
        "<i>Ma’lumotlar bazadan avtomatik hisoblandi.</i>"
    )

    try:
        await callback.message.edit_text(
            stats_text,
            parse_mode="HTML",
            reply_markup=admin_panel_keyboard()
        )
    except Exception:
        await callback.message.answer(
            stats_text,
            parse_mode="HTML",
            reply_markup=admin_panel_keyboard()
        )
    await callback.answer()


# ==================== BUYURTMALAR RO'YXATI ====================

@router.callback_query(F.data == "admin:orders_menu")
async def cb_admin_orders_menu(callback: CallbackQuery):
    """Buyurtmalar filtri menyusi."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    text = "📋 <b>Qaysi toifadagi buyurtmalarni ko‘rmoqchisiz?</b>"
    try:
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=admin_orders_filter_keyboard())
    except Exception:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_orders_filter_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:orders:"))
async def cb_admin_orders_list(callback: CallbackQuery):
    """Filtrlangan buyurtmalar ro'yxati."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    filter_type = callback.data.split(":")[2]
    status_filter = None if filter_type == "all" else filter_type

    orders = await get_all_orders(status=status_filter, limit=10)

    if not orders:
        await callback.answer("Ushbu bo‘limda buyurtmalar mavjud emas.", show_alert=True)
        return

    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass

    status_badges = {
        "yangi": "🟡 Yangi",
        "tasdiqlandi": "🔵 Tasdiqlandi",
        "tayyorlanmoqda": "🟠 Tayyorlanmoqda",
        "yetkazilmoqda": "🚚 Yetkazilmoqda",
        "yakunlandi": "🟢 Yakunlandi",
        "bekor_qilindi": "🔴 Bekor qilindi"
    }

    for ord_item in orders:
        st_text = status_badges.get(ord_item["status"], ord_item["status"])
        total_str = format_price(ord_item["total_price"])
        del_str = "Bepul" if ord_item.get("delivery_price", 0) == 0 else f"{format_price(ord_item['delivery_price'])} so‘m"

        order_card = (
            f"🧾 <b>Buyurtma kodi:</b> #{ord_item['order_number']}\n"
            f"🕒 <b>Vaqti:</b> {ord_item['created_at'][:16]}\n"
            f"📊 <b>Holati:</b> <b>{st_text}</b>\n"
            "────────────────────────\n"
            f"📦 <b>Mahsulot:</b> {ord_item['product_name']}\n"
            f"📏 <b>O‘lcham:</b> {ord_item['product_size']} | 🎨 <b>Rang:</b> {ord_item['product_color']}\n"
            f"🔢 <b>Miqdori:</b> {ord_item['quantity']} dona\n"
            f"🚚 <b>Yetkazish:</b> {del_str}\n"
            f"💰 <b>Jami summa:</b> <u>{total_str} so‘m</u>\n"
            "────────────────────────\n"
            f"👤 <b>Mijoz:</b> {ord_item['customer_name']}\n"
            f"📱 <b>Telefon:</b> {ord_item['customer_phone']}\n"
            f"📍 <b>Manzil:</b> {ord_item['delivery_address']}\n"
        )

        await callback.message.answer(
            order_card,
            parse_mode="HTML",
            reply_markup=admin_order_actions_keyboard(ord_item["id"], ord_item["status"])
        )


@router.callback_query(F.data.startswith("adm_st:"))
async def cb_admin_change_order_status(callback: CallbackQuery, bot: Bot):
    """Buyurtma holatini yangilash va mijozga bildirishnoma jo'natish."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    parts = callback.data.split(":")
    order_id = int(parts[1])
    new_status = parts[2]

    order = await get_order_by_id(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi!", show_alert=True)
        return

    await update_order_status(order_id, new_status)

    status_labels = {
        "tasdiqlandi": "🔵 Tasdiqlandi",
        "tayyorlanmoqda": "🟠 Tayyorlanmoqda",
        "yetkazilmoqda": "🚚 Yetkazilmoqda",
        "yakunlandi": "🟢 Yakunlandi",
        "bekor_qilindi": "🔴 Bekor qilindi"
    }
    status_label = status_labels.get(new_status, new_status)
    await callback.answer(f"Holat o‘zgartirildi: {status_label}")

    # Mijozga avtomatik xabar
    customer_id = order.get("user_id")
    order_num = order["order_number"]

    notification_messages = {
        "tasdiqlandi": (
            f"🔵 <b>Hurmatli {order['customer_name']}!</b>\n\n"
            f"Sizning <b>#{order_num}</b> raqamli buyurtmangiz tasdiqlandi! ✨"
        ),
        "tayyorlanmoqda": (
            f"🟠 <b>Hurmatli {order['customer_name']}!</b>\n\n"
            f"Sizning <b>#{order_num}</b> raqamli buyurtmangiz omborda tayyorlanmoqda va qadoqlanmoqda."
        ),
        "yetkazilmoqda": (
            f"🚚 <b>Hurmatli {order['customer_name']}!</b>\n\n"
            f"Sizning <b>#{order_num}</b> raqamli buyurtmangiz kuryerga topshirildi va yetkazilmoqda!"
        ),
        "yakunlandi": (
            f"🟢 <b>Hurmatli {order['customer_name']}!</b>\n\n"
            f"Sizning <b>#{order_num}</b> raqamli buyurtmangiz muvaffaqiyatli topshirildi va yakunlandi.\n"
            "OROM TEXTILE ni tanlaganingiz uchun tashakkur! 🌿"
        ),
        "bekor_qilindi": (
            f"🔴 <b>Hurmatli {order['customer_name']}!</b>\n\n"
            f"Sizning <b>#{order_num}</b> raqamli buyurtmangiz bekor qilindi.\n"
            "Savollaringiz bo‘lsa, administrator bilan bog‘lanishingiz mumkin."
        )
    }

    if customer_id and new_status in notification_messages:
        try:
            await bot.send_message(
                chat_id=customer_id,
                text=notification_messages[new_status],
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Mijozga ({customer_id}) status bildirishnomasi yetmadi: {e}")

    try:
        await callback.message.edit_reply_markup(
            reply_markup=admin_order_actions_keyboard(order_id, new_status)
        )
    except Exception:
        pass


# ==================== MAHSULOTLAR BOSHQARUVI ====================

@router.callback_query(F.data == "admin:products")
async def cb_admin_products(callback: CallbackQuery):
    """Mahsulotlar ro'yxati."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    products = await get_all_products(include_unavailable=True)
    if not products:
        await callback.answer("Hozirda bazada mahsulotlar yo‘q.", show_alert=True)
        return

    text = (
        "📦 <b>Barcha mahsulotlar ro‘yxati:</b>\n"
        "🟢 — Sotuvda mavjud | 🔴 — Sotuvdan olingan\n\n"
        "Batafsil ko‘rish yoki o‘chirish uchun mahsulotni tanlang:"
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=admin_products_list_keyboard(products)
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=admin_products_list_keyboard(products)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_pview:"))
async def cb_admin_view_product(callback: CallbackQuery):
    """Alohida mahsulot tafsiloti."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    prod_id = int(callback.data.split(":")[1])
    product = await get_product_by_id(prod_id)
    if not product:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    status_str = "🟢 Sotuvda mavjud" if product["is_available"] else "🔴 Sotuvdan olingan"
    price_str = format_price(product["price"])
    code_str = product.get("product_code") or "Belgilanmagan"
    stock_str = product.get("stock_status") or "Omborda mavjud"

    card_text = (
        f"🏷 <b>{product['name']}</b> ({status_str})\n"
        f"🔢 <b>Kodi:</b> <code>#{code_str}</code>\n"
        f"📁 <b>Toifa:</b> {product.get('category_name', 'Mavjud emas')}\n"
        f"💰 <b>Narxi:</b> {price_str} so‘m\n"
        f"📦 <b>Mavjudligi:</b> {stock_str}\n"
        f"📏 <b>O‘lchamlar:</b> {product.get('sizes') or 'Standart'}\n"
        f"🎨 <b>Ranglar:</b> {product.get('colors') or 'Standart'}\n\n"
        f"📝 <b>Tavsif:</b>\n{product.get('description') or 'Yo‘q'}\n"
    )

    try:
        await callback.message.edit_text(
            card_text,
            parse_mode="HTML",
            reply_markup=admin_product_actions_keyboard(prod_id, product["is_available"])
        )
    except Exception:
        await callback.message.answer(
            card_text,
            parse_mode="HTML",
            reply_markup=admin_product_actions_keyboard(prod_id, product["is_available"])
        )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_ptoggle:"))
async def cb_admin_toggle_product(callback: CallbackQuery):
    """Mahsulot mavjudligini o'zgartirish."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    prod_id = int(callback.data.split(":")[1])
    new_status = await toggle_product_availability(prod_id)
    txt = "🟢 Mahsulot sotuvga chiqarildi!" if new_status == 1 else "🔴 Mahsulot sotuvdan olindi!"
    await callback.answer(txt, show_alert=True)
    await cb_admin_view_product(callback)


@router.callback_query(F.data.startswith("adm_pdel:"))
async def cb_admin_delete_product(callback: CallbackQuery):
    """Mahsulotni o'chirish."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    prod_id = int(callback.data.split(":")[1])
    await delete_product(prod_id)
    await callback.answer("🗑 Mahsulot o‘chirildi!", show_alert=True)
    await cb_admin_products(callback)


# ==================== YANGI MAHSULOT QO'SHISH ====================

@router.callback_query(F.data == "admin:add_product")
async def cb_admin_add_product_start(callback: CallbackQuery, state: FSMContext):
    """Mahsulot qo'shish boshlanishi."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    await state.clear()
    categories = await get_categories()

    await state.set_state(AddProductStates.category)
    await callback.message.edit_text(
        "➕ <b>Yangi mahsulot qo‘shish:</b>\n\nQaysi toifaga mahsulot qo‘shmoqchisiz?",
        parse_mode="HTML",
        reply_markup=admin_category_select_keyboard(categories)
    )
    await callback.answer()


@router.callback_query(AddProductStates.category, F.data.startswith("adm_add_cat:"))
async def cb_add_product_cat(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlandi -> Mahsulot kodi so'raladi."""
    cat_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=cat_id)

    await state.set_state(AddProductStates.code)
    await callback.message.answer(
        "🔢 Mahsulot <b>kodini</b> kiriting (Masalan: <code>OT-PAS-105</code>) "
        "yoki avtomatik berilishi uchun <b>«Avto»</b> deb yozing:",
        parse_mode="HTML",
        reply_markup=cancel_reply_keyboard()
    )
    await callback.answer()


@router.message(AddProductStates.code)
async def process_add_code(message: Message, state: FSMContext):
    """Mahsulot kodi olindi -> Nom so'raladi."""
    text = message.text.strip()
    code = None if text.lower() == "avto" else text
    await state.update_data(product_code=code)

    await state.set_state(AddProductStates.name)
    await message.answer("✏️ Mahsulot <b>nomini</b> kiriting:", parse_mode="HTML")


@router.message(AddProductStates.name)
async def process_add_name(message: Message, state: FSMContext):
    """Nom olindi -> Tavsif so'raladi."""
    name = message.text.strip()
    await state.update_data(name=name)

    await state.set_state(AddProductStates.description)
    await message.answer(f"📝 <b>«{name}»</b> uchun to‘liq <b>tavsif matnini</b> kiriting:", parse_mode="HTML")


@router.message(AddProductStates.description)
async def process_add_desc(message: Message, state: FSMContext):
    """Tavsif olindi -> Narx so'raladi."""
    desc = message.text.strip()
    await state.update_data(description=desc)

    await state.set_state(AddProductStates.price)
    await message.answer("💰 Mahsulot <b>narxini</b> so‘mda kiriting (Masalan: <b>450000</b>):", parse_mode="HTML")


@router.message(AddProductStates.price)
async def process_add_price(message: Message, state: FSMContext):
    """Narx olindi -> O'lchamlar so'raladi."""
    price_text = message.text.strip().replace(" ", "")
    if not price_text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting (masalan: 350000):")
        return

    price = int(price_text)
    await state.update_data(price=price)

    await state.set_state(AddProductStates.sizes)
    await message.answer(
        "📏 Mavjud <b>o‘lchamlarni</b> vergul bilan kiriting\n"
        "(Masalan: <i>160x220 sm, 200x220 sm</i> yoki <i>Standart</i>):",
        parse_mode="HTML"
    )


@router.message(AddProductStates.sizes)
async def process_add_sizes(message: Message, state: FSMContext):
    """O'lchamlar olindi -> Ranglar so'raladi."""
    sizes = message.text.strip()
    await state.update_data(sizes=sizes)

    await state.set_state(AddProductStates.colors)
    await message.answer(
        "🎨 Mavjud <b>ranglarni</b> vergul bilan kiriting\n"
        "(Masalan: <i>Oq, Qahva, Zaytun</i> yoki <i>Standart</i>):",
        parse_mode="HTML"
    )


@router.message(AddProductStates.colors)
async def process_add_colors(message: Message, state: FSMContext):
    """Ranglar olindi -> Ombordagi mavjudlik holati so'raladi."""
    colors = message.text.strip()
    await state.update_data(colors=colors)

    await state.set_state(AddProductStates.stock_status)
    await message.answer(
        "📦 <b>Ombordagi mavjudligi</b> holatini kiriting:\n"
        "(Masalan: <i>Omborda mavjud</i> yoki <i>Buyurtma asosida</i>):",
        parse_mode="HTML"
    )


@router.message(AddProductStates.stock_status)
async def process_add_stock(message: Message, state: FSMContext):
    """Mavjudlik holati olindi -> Rasm so'raladi."""
    stock = message.text.strip()
    await state.update_data(stock_status=stock)

    await state.set_state(AddProductStates.photo)
    await message.answer(
        "🖼 Mahsulot <b>rasmini</b> yuboring (yoki rasmsiz qoldirish uchun <b>«O‘tkazib yuborish»</b> deb yozing):",
        parse_mode="HTML"
    )


@router.message(AddProductStates.photo, F.photo)
async def process_add_photo(message: Message, state: FSMContext):
    """Rasm jo'natilganda."""
    file_id = message.photo[-1].file_id
    await _finalize_add_product(message, state, image_url=file_id)


@router.message(AddProductStates.photo, F.text)
async def process_add_photo_text(message: Message, state: FSMContext):
    """Havola yoki o'tkazib yuborish matni."""
    text = message.text.strip()
    image_url = text if text.startswith("http://") or text.startswith("https://") else None
    await _finalize_add_product(message, state, image_url=image_url)


async def _finalize_add_product(message: Message, state: FSMContext, image_url: str = None):
    """Yangi mahsulotni bazada saqlash."""
    data = await state.get_data()
    try:
        await add_product(
            category_id=data["category_id"],
            name=data["name"],
            description=data["description"],
            price=data["price"],
            product_code=data.get("product_code"),
            image_url=image_url,
            sizes=data.get("sizes"),
            colors=data.get("colors"),
            stock_status=data.get("stock_status", "Omborda mavjud")
        )
    except Exception as e:
        logger.error(f"Mahsulot saqlashda xato: {e}")
        await message.answer("⚠️ Mahsulotni saqlashda xatolik yuz berdi.")
        await state.clear()
        return

    await state.clear()
    is_admin = is_admin_filter(message.from_user.id)
    await message.answer(
        f"🎉 <b>«{data['name']}»</b> mahsuloti muvaffaqiyatli saqlandi va katalogga qo‘shildi!",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )


# ==================== OMMUVIY XABARNOMA (BROADCAST) ====================

@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Broadcast xabarnoma jo'natish."""
    if not is_admin_filter(callback.from_user.id):
        await callback.answer("Ruxsat yo‘q!", show_alert=True)
        return

    await state.clear()
    await state.set_state(BroadcastStates.message)
    await callback.message.answer(
        "📢 <b>Barcha mijozlarga xabarnoma yuborish:</b>\n\n"
        "Xabar matnini yoki rasmini yuboring:",
        parse_mode="HTML",
        reply_markup=cancel_reply_keyboard()
    )
    await callback.answer()


@router.message(BroadcastStates.message)
async def process_broadcast_message(message: Message, state: FSMContext, bot: Bot):
    """Xabarnomani tarqatish."""
    await state.clear()
    users = await get_all_users()
    total_users = len(users)

    if total_users == 0:
        await message.answer("⚠️ Bazada foydalanuvchilar mavjud emas.")
        return

    sent_count = 0
    blocked_count = 0
    progress_msg = await message.answer(f"⏳ Xabarnoma jo‘natilmoqda: 0/{total_users}...")

    for user in users:
        uid = user["user_id"]
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked_count += 1

    is_admin = is_admin_filter(message.from_user.id)
    result_text = (
        "✅ <b>Xabarnoma yakunlandi!</b>\n\n"
        f"👥 Jami mijozlar: {total_users}\n"
        f"📬 Yetkazildi: {sent_count}\n"
        f"🚫 Bloklagan/Xato: {blocked_count}"
    )
    try:
        await progress_msg.edit_text(result_text, parse_mode="HTML")
    except Exception:
        await message.answer(result_text, parse_mode="HTML", reply_markup=main_menu_keyboard(is_admin=is_admin))
