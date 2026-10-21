from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """OROM TEXTILE asosiy menyu klaviaturasi (yangi dizayn)."""
    buttons = [
        [KeyboardButton(text="🛍 Mahsulotlar katalogi")],
        [KeyboardButton(text="🛏 Pastellar"), KeyboardButton(text="🧸 Yostiqlar")],
        [KeyboardButton(text="🛌 Matrasniklar"), KeyboardButton(text="🧵 Namat mahsulotlari")],
        [KeyboardButton(text="📦 Buyurtmalarim"), KeyboardButton(text="🚚 Yetkazib berish")],
        [KeyboardButton(text="📍 Manzilimiz"), KeyboardButton(text="☎️ Murojaat uchun")],
        [KeyboardButton(text="👨‍💼 Administrator")]
    ]

    # Agar foydalanuvchi admin bo'lsa, alohida admin tugmasi
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Quyidagi bo‘limlardan birini tanlang..."
    )


def phone_share_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni kontakt orqali yuborish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Raqamingizni yuboring..."
    )


def location_share_keyboard() -> ReplyKeyboardMarkup:
    """Manzilni lokatsiya orqali yuborish tugmasi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Joylashuvimni yuborish", request_location=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Lokatsiya yuboring yoki manzilni yozing..."
    )


def cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish uchun oddiy reply tugma."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
