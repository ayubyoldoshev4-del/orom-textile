import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_IDS, FREE_DELIVERY_THRESHOLD, STANDARD_DELIVERY_PRICE
from database import (
    get_product_by_id,
    create_order,
    get_categories,
    update_user_phone
)
from keyboards import (
    categories_inline_keyboard,
    sizes_inline_keyboard,
    colors_inline_keyboard,
    quantity_inline_keyboard,
    order_confirmation_keyboard,
    phone_share_keyboard,
    location_share_keyboard,
    cancel_reply_keyboard,
    main_menu_keyboard,
    admin_order_actions_keyboard,
    format_price
)

logger = logging.getLogger(__name__)
router = Router(name="order_router")


class OrderStates(StatesGroup):
    product_id = State()
    select_size = State()
    select_color = State()
    enter_quantity = State()
    enter_name = State()
    enter_phone = State()
    enter_address = State()
    confirm_order = State()


# ==================== BUYURTMA BERISHNING BOSHLANISHI ====================

@router.callback_query(F.data.startswith("order_start:"))
async def start_order_process(callback: CallbackQuery, state: FSMContext):
    """Mahsulot kartasidan buyurtma jarayonini boshlash."""
    await state.clear()
    product_id = int(callback.data.split(":")[1])
    product = await get_product_by_id(product_id)

    if not product:
        await callback.answer("Kechirasiz, mahsulot topilmadi!", show_alert=True)
        return

    # Holatga mahsulot ma'lumotlarini saqlash
    await state.update_data(
        product_id=product["id"],
        product_code=product.get("product_code", ""),
        product_name=product["name"],
        unit_price=product["price"],
        selected_size="Standart",
        selected_color="Standart",
        quantity=1
    )

    # 1. O'lcham tanlash tekshiruvi
    raw_sizes = product.get("sizes")
    if raw_sizes and raw_sizes.strip():
        sizes_list = [s.strip() for s in raw_sizes.split(",") if s.strip()]
        if len(sizes_list) > 1:
            await state.update_data(available_sizes=sizes_list)
            await state.set_state(OrderStates.select_size)
            await callback.message.answer(
                f"📏 <b>«{product['name']}»</b> uchun o‘lchamni tanlang:",
                parse_mode="HTML",
                reply_markup=sizes_inline_keyboard(sizes_list, product_id)
            )
            await callback.answer()
            return
        elif len(sizes_list) == 1:
            await state.update_data(selected_size=sizes_list[0])

    # 2. Rang tanlash tekshiruvi
    raw_colors = product.get("colors")
    if raw_colors and raw_colors.strip():
        colors_list = [c.strip() for c in raw_colors.split(",") if c.strip()]
        if len(colors_list) > 1:
            await state.update_data(available_colors=colors_list)
            await state.set_state(OrderStates.select_color)
            await callback.message.answer(
                f"🎨 <b>«{product['name']}»</b> uchun rangni tanlang:",
                parse_mode="HTML",
                reply_markup=colors_inline_keyboard(colors_list, product_id)
            )
            await callback.answer()
            return
        elif len(colors_list) == 1:
            await state.update_data(selected_color=colors_list[0])

    # 3. Miqdorni tanlash
    await state.set_state(OrderStates.enter_quantity)
    await callback.message.answer(
        f"🔢 <b>«{product['name']}»</b> dan necha dona buyurtma qilmoqchisiz?",
        parse_mode="HTML",
        reply_markup=quantity_inline_keyboard()
    )
    await callback.answer()


# ==================== O'LCHAM TANLASH ====================

@router.callback_query(OrderStates.select_size, F.data.startswith("size_pick:"))
async def process_size_selection(callback: CallbackQuery, state: FSMContext):
    """O'lcham tanlanganda."""
    size_idx = int(callback.data.split(":")[1])
    data = await state.get_data()
    sizes_list = data.get("available_sizes", [])

    chosen_size = sizes_list[size_idx] if 0 <= size_idx < len(sizes_list) else "Standart"
    await state.update_data(selected_size=chosen_size)

    # Rang tanlashga o'tish
    product_id = data["product_id"]
    product = await get_product_by_id(product_id)
    raw_colors = product.get("colors") if product else None

    if raw_colors and raw_colors.strip():
        colors_list = [c.strip() for c in raw_colors.split(",") if c.strip()]
        if len(colors_list) > 1:
            await state.update_data(available_colors=colors_list)
            await state.set_state(OrderStates.select_color)
            await callback.message.edit_text(
                f"✅ Tanlangan o‘lcham: <b>{chosen_size}</b>\n\n"
                f"🎨 Endi rangni tanlang:",
                parse_mode="HTML",
                reply_markup=colors_inline_keyboard(colors_list, product_id)
            )
            await callback.answer()
            return
        elif len(colors_list) == 1:
            await state.update_data(selected_color=colors_list[0])

    # Ranglar bitta bo'lsa to'g'ridan-to'g'ri miqdorga
    await state.set_state(OrderStates.enter_quantity)
    await callback.message.edit_text(
        f"✅ Tanlangan o‘lcham: <b>{chosen_size}</b>\n\n"
        f"🔢 Necha dona buyurtma qilmoqchisiz?",
        parse_mode="HTML",
        reply_markup=quantity_inline_keyboard()
    )
    await callback.answer()


# ==================== RANG TANLASH ====================

@router.callback_query(OrderStates.select_color, F.data.startswith("color_pick:"))
async def process_color_selection(callback: CallbackQuery, state: FSMContext):
    """Rang tanlanganda."""
    color_idx = int(callback.data.split(":")[1])
    data = await state.get_data()
    colors_list = data.get("available_colors", [])

    chosen_color = colors_list[color_idx] if 0 <= color_idx < len(colors_list) else "Standart"
    await state.update_data(selected_color=chosen_color)

    await state.set_state(OrderStates.enter_quantity)
    await callback.message.edit_text(
        f"✅ Tanlangan rang: <b>{chosen_color}</b>\n\n"
        f"🔢 Necha dona buyurtma qilmoqchisiz?",
        parse_mode="HTML",
        reply_markup=quantity_inline_keyboard()
    )
    await callback.answer()


# ==================== MIQDOR TANLASH ====================

@router.callback_query(OrderStates.enter_quantity, F.data.startswith("qty_pick:"))
async def process_quantity_pick(callback: CallbackQuery, state: FSMContext):
    """Miqdor inline tugmasi bosilganda."""
    action = callback.data.split(":")[1]

    if action == "custom":
        await callback.message.edit_text(
            "🔢 Kerakli miqdorni son ko‘rinishida kiriting (masalan: <b>6</b>):",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    qty = int(action)
    await _proceed_to_name(callback.message, state, qty, is_callback=True)
    await callback.answer()


@router.message(OrderStates.enter_quantity)
async def process_quantity_custom(message: Message, state: FSMContext):
    """Foydalanuvchi miqdorni qo'lda yozganda."""
    text = message.text.strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("⚠️ Iltimos, faqat musbat son kiriting (masalan: 1, 2, 5):")
        return

    qty = int(text)
    if qty > 100:
        await message.answer("⚠️ Bir martalik buyurtma uchun miqdor 100 donadan oshmasligi kerak. Qayta kiriting:")
        return

    await _proceed_to_name(message, state, qty, is_callback=False)


async def _proceed_to_name(message: Message, state: FSMContext, qty: int, is_callback: bool = False):
    """Miqdor olingach ism kiritishga o'tish."""
    data = await state.get_data()
    unit_price = data.get("unit_price", 0)
    subtotal = unit_price * qty

    # Yetkazib berish narxini hisoblash
    delivery_price = 0 if subtotal >= FREE_DELIVERY_THRESHOLD else STANDARD_DELIVERY_PRICE
    total_price = subtotal + delivery_price

    await state.update_data(
        quantity=qty,
        subtotal=subtotal,
        delivery_price=delivery_price,
        total_price=total_price
    )
    await state.set_state(OrderStates.enter_name)

    prompt = (
        f"🔢 Miqdor: <b>{qty} dona</b>\n"
        f"💰 Mahsulot narxi: <b>{format_price(subtotal)} so‘m</b>\n\n"
        "👤 Buyurtmani rasmiylashtirish uchun <b>Ism va Familiyangizni</b> kiriting:"
    )

    if is_callback:
        await message.edit_text(prompt, parse_mode="HTML")
        await message.answer("Masalan: <code>Sherzod Karimov</code>", parse_mode="HTML", reply_markup=cancel_reply_keyboard())
    else:
        await message.answer(prompt, parse_mode="HTML", reply_markup=cancel_reply_keyboard())


# ==================== ISM KIRITISH ====================

@router.message(OrderStates.enter_name)
async def process_name(message: Message, state: FSMContext):
    """Mijoz ismini qabul qilish."""
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("⚠️ Iltimos, ismingizni to‘liqroq yozing:")
        return

    await state.update_data(customer_name=name)
    await state.set_state(OrderStates.enter_phone)

    prompt = (
        f"Rahmat, <b>{name}</b>!\n\n"
        "📱 Endi bog‘lanish uchun telefon raqamingizni yuboring.\n"
        "Pastdagi <b>«📱 Telefon raqamimni yuborish»</b> tugmasini bosishingiz yoki "
        "qo‘lda yozishingiz mumkin (<code>+998999966144</code>):"
    )
    await message.answer(prompt, parse_mode="HTML", reply_markup=phone_share_keyboard())


# ==================== TELEFON RAQAM ====================

@router.message(OrderStates.enter_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Kontakt orqali telefon raqam."""
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    await state.update_data(customer_phone=phone)
    await update_user_phone(message.from_user.id, phone)
    await _proceed_to_address(message, state)


@router.message(OrderStates.enter_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    """Matn orqali telefon raqam."""
    phone = message.text.strip()
    clean_digits = "".join(filter(str.isdigit, phone))

    if len(clean_digits) < 9:
        await message.answer("⚠️ Telefon raqam noto‘g‘ri kiritildi. Iltimos, qayta yozing yoki tugmani bosing:")
        return

    if not phone.startswith("+"):
        phone = "+" + phone

    await state.update_data(customer_phone=phone)
    await update_user_phone(message.from_user.id, phone)
    await _proceed_to_address(message, state)


async def _proceed_to_address(message: Message, state: FSMContext):
    """Manzil kiritish bosqichi."""
    await state.set_state(OrderStates.enter_address)
    prompt = (
        "📍 <b>Yetkazib berish manzilini yuboring:</b>\n\n"
        "Manzilni matn ko‘rinishida yozishingiz (<i>Shahar, tuman, ko‘cha, xonadon</i>) "
        "yoki <b>«📍 Joylashuvimni yuborish»</b> tugmasi orqali geolokatsiya jo‘natishingiz mumkin:"
    )
    await message.answer(prompt, parse_mode="HTML", reply_markup=location_share_keyboard())


# ==================== MANZIL VA TASDIQLASH ====================

@router.message(OrderStates.enter_address, F.location)
async def process_address_location(message: Message, state: FSMContext):
    """Manzil lokatsiya orqali yuborilganda."""
    lat = message.location.latitude
    lon = message.location.longitude
    maps_link = f"https://maps.google.com/?q={lat},{lon}"
    address_str = f"Geolokatsiya: {maps_link}"

    await state.update_data(delivery_address=address_str)
    await _show_order_confirmation(message, state)


@router.message(OrderStates.enter_address, F.text)
async def process_address_text(message: Message, state: FSMContext):
    """Manzil matn sifatida kiritilganda."""
    address = message.text.strip()
    if len(address) < 4:
        await message.answer("⚠️ Iltimos, yetkazib berish manzilini to‘liqroq yozing:")
        return

    await state.update_data(delivery_address=address)
    await _show_order_confirmation(message, state)


async def _show_order_confirmation(message: Message, state: FSMContext):
    """Barcha ma'lumotlar bilan rasmiy chek shakllantirish."""
    await state.set_state(OrderStates.confirm_order)
    data = await state.get_data()

    product_name = data.get("product_name")
    code_tag = f" (#{data.get('product_code')})" if data.get("product_code") else ""
    size = data.get("selected_size", "Standart")
    color = data.get("selected_color", "Standart")
    qty = data.get("quantity", 1)
    unit_price = data.get("unit_price", 0)
    subtotal = data.get("subtotal", unit_price * qty)
    delivery_price = data.get("delivery_price", 0)
    total_price = data.get("total_price", subtotal + delivery_price)
    name = data.get("customer_name")
    phone = data.get("customer_phone")
    address = data.get("delivery_address")

    delivery_text = "Bepul (Aksiya)" if delivery_price == 0 else f"{format_price(delivery_price)} so‘m"

    check_text = (
        "🧾 <b>BUYURTMANI TEKSHIRISH VA TASDIQLASH</b>\n"
        "────────────────────────\n"
        f"📦 <b>Mahsulot:</b> {product_name}{code_tag}\n"
        f"📏 <b>O‘lcham:</b> {size}\n"
        f"🎨 <b>Rang:</b> {color}\n"
        f"🔢 <b>Miqdori:</b> {qty} dona\n"
        f"💵 <b>Dona narxi:</b> {format_price(unit_price)} so‘m\n"
        f"💰 <b>Mahsulot summasi:</b> {format_price(subtotal)} so‘m\n"
        f"🚚 <b>Yetkazib berish:</b> {delivery_text}\n"
        "────────────────────────\n"
        f"💳 <b>JAMI TO‘LOV:</b> <u>{format_price(total_price)} so‘m</u>\n"
        "────────────────────────\n"
        f"👤 <b>Qabul qiluvchi:</b> {name}\n"
        f"📱 <b>Telefon:</b> {phone}\n"
        f"📍 <b>Manzil:</b> {address}\n"
        "────────────────────────\n"
        "Barcha ma’lumotlar to‘g‘rimi? Buyurtmani tasdiqlaysizmi?"
    )

    await message.answer(
        check_text,
        parse_mode="HTML",
        reply_markup=order_confirmation_keyboard()
    )


# ==================== TASDIQLASH VA ADMIN BILDIRISHNOMASI ====================

@router.callback_query(OrderStates.confirm_order, F.data == "confirm_order_yes")
async def confirm_order_execution(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Buyurtmani bazada saqlash va adminlarga xabar yuborish."""
    data = await state.get_data()
    user = callback.from_user

    try:
        new_order = await create_order(
            user_id=user.id,
            customer_name=data["customer_name"],
            customer_phone=data["customer_phone"],
            delivery_address=data["delivery_address"],
            delivery_price=data.get("delivery_price", 0),
            product_id=data["product_id"],
            product_name=data["product_name"],
            product_size=data.get("selected_size", "Standart"),
            product_color=data.get("selected_color", "Standart"),
            quantity=data.get("quantity", 1),
            unit_price=data.get("unit_price", 0),
            total_price=data.get("total_price", 0),
            notes=""
        )
    except Exception as e:
        logger.error(f"Buyurtma yaratishda xatolik: {e}")
        await callback.answer("Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)
        return

    await state.clear()

    order_num = new_order["order_number"]
    total_str = format_price(new_order["total_price"])
    del_str = "Bepul" if new_order["delivery_price"] == 0 else f"{format_price(new_order['delivery_price'])} so‘m"

    success_text = (
        "🎉 <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"🔢 <b>Buyurtma kodi:</b> <code>#{order_num}</code>\n"
        f"📦 <b>Mahsulot:</b> {new_order['product_name']}\n"
        f"🔢 <b>Miqdori:</b> {new_order['quantity']} dona\n"
        f"🚚 <b>Yetkazib berish:</b> {del_str}\n"
        f"💰 <b>Umumiy summa:</b> <code>{total_str} so‘m</code>\n"
        f"📊 <b>Holati:</b> 🟡 Yangi\n\n"
        "Tez orada menejerimiz siz bilan bog‘lanib, buyurtmani tasdiqlaydi.\n"
        "Holatni <b>«📦 Buyurtmalarim»</b> bo‘limida kuzatib borishingiz mumkin. ✨"
    )

    is_admin = user.id in ADMIN_IDS
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        success_text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )
    await callback.answer("Buyurtma qabul qilindi!")

    # ==================== ADMINLARGA BILDIRISHNOMA ====================
    admin_alert = (
        "🔔 <b>YANGI BUYURTMA QABUL QILINDI!</b>\n"
        "────────────────────────\n"
        f"🔢 <b>Buyurtma:</b> #{order_num}\n"
        f"📦 <b>Mahsulot:</b> {new_order['product_name']}\n"
        f"📏 <b>O‘lcham:</b> {new_order['product_size']} | 🎨 <b>Rang:</b> {new_order['product_color']}\n"
        f"🔢 <b>Miqdori:</b> {new_order['quantity']} dona\n"
        f"🚚 <b>Yetkazish:</b> {del_str}\n"
        f"💰 <b>Jami summa:</b> {total_str} so‘m\n"
        "────────────────────────\n"
        f"👤 <b>Mijoz:</b> {new_order['customer_name']}\n"
        f"📱 <b>Telefon:</b> {new_order['customer_phone']}\n"
        f"📍 <b>Manzil:</b> {new_order['delivery_address']}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user.id}</code> (@{user.username or 'yo‘q'})\n"
        "────────────────────────\n"
        "Buyurtma holatini tanlang:"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_alert,
                parse_mode="HTML",
                reply_markup=admin_order_actions_keyboard(new_order["id"], new_order["status"])
            )
        except Exception as e:
            logger.warning(f"Adminga ({admin_id}) xabar yetmadi: {e}")


@router.callback_query(F.data == "cancel_order")
async def cancel_order_flow(callback: CallbackQuery, state: FSMContext):
    """Buyurtma jarayonini bekor qilish."""
    await state.clear()
    is_admin = callback.from_user.id in ADMIN_IDS
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        "❌ Buyurtma berish bekor qilindi. Siz asosiy menyudasiz:",
        reply_markup=main_menu_keyboard(is_admin=is_admin)
    )
    await callback.answer()
