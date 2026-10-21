from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_USERNAME, COMPANY_PHONE


def format_price(amount: int) -> str:
    """Narxni chiroyli ko'rinishda formatlash (masalan, 850 000)."""
    return f"{amount:,}".replace(",", " ")


# ==================== MIJOZ KLAVIATURALARI ====================

def categories_inline_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    """Kategoriyalar ro'yxatini chiqaruvchi inline klaviatura."""
    keyboard = []
    for cat in categories:
        btn_text = f"{cat.get('icon', '📦')} {cat['name']}"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"cat:{cat['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def products_inline_keyboard(products: list[dict], category_id: int) -> InlineKeyboardMarkup:
    """Kategoriyadagi mahsulotlar ro'yxati."""
    keyboard = []
    for prod in products:
        price_str = format_price(prod["price"])
        code_tag = f" [{prod['product_code']}]" if prod.get("product_code") else ""
        btn_text = f"{prod['name']}{code_tag} — {price_str} so‘m"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"prod:{prod['id']}")])

    # Navigatsiya tugmalari
    nav_buttons = [
        InlineKeyboardButton(text="⬅️ Barcha toifalar", callback_data="back_to_cats"),
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")
    ]
    keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def product_detail_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    """Alohida mahsulot ko'rilganda buyurtma, savol va orqaga tugmalari."""
    keyboard = [
        [InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data=f"order_start:{product_id}")],
        [
            InlineKeyboardButton(text="☎️ Savol berish", url=f"https://t.me/{ADMIN_USERNAME}"),
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"cat:{category_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def sizes_inline_keyboard(sizes_list: list[str], product_id: int) -> InlineKeyboardMarkup:
    """Mahsulot o'lchamlarini tanlash inline klaviaturasi."""
    keyboard = []
    for idx, size in enumerate(sizes_list):
        keyboard.append([InlineKeyboardButton(text=f"📐 {size.strip()}", callback_data=f"size_pick:{idx}")])
    keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def colors_inline_keyboard(colors_list: list[str], product_id: int) -> InlineKeyboardMarkup:
    """Mahsulot ranglarini tanlash inline klaviaturasi."""
    keyboard = []
    row = []
    for idx, color in enumerate(colors_list):
        row.append(InlineKeyboardButton(text=f"🎨 {color.strip()}", callback_data=f"color_pick:{idx}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def quantity_inline_keyboard() -> InlineKeyboardMarkup:
    """Mahsulot miqdorini tanlash."""
    keyboard = [
        [
            InlineKeyboardButton(text="1 dona", callback_data="qty_pick:1"),
            InlineKeyboardButton(text="2 dona", callback_data="qty_pick:2"),
            InlineKeyboardButton(text="3 dona", callback_data="qty_pick:3")
        ],
        [
            InlineKeyboardButton(text="4 dona", callback_data="qty_pick:4"),
            InlineKeyboardButton(text="5 dona", callback_data="qty_pick:5"),
            InlineKeyboardButton(text="🔢 Boshqa miqdor", callback_data="qty_pick:custom")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def order_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash yoki bekor qilish."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Buyurtmani tasdiqlash", callback_data="confirm_order_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def contact_actions_keyboard() -> InlineKeyboardMarkup:
    """Murojaat uchun bo'limida aloqa tugmalari."""
    keyboard = [
        [InlineKeyboardButton(text="💬 Administratorga yozish (@Sherzod_6144)", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton(text="📞 Telefon raqamni ko‘rsatish", callback_data="copy_phone")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_link_keyboard() -> InlineKeyboardMarkup:
    """Administrator profiliga o'tish tugmasi."""
    keyboard = [
        [InlineKeyboardButton(text="💬 Administratorga yozish (@Sherzod_6144)", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ==================== ADMIN KLAVIATURALARI ====================

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv panelining bosh menyusi."""
    keyboard = [
        [
            InlineKeyboardButton(text="📦 Mahsulotlar boshqaruvi", callback_data="admin:products"),
            InlineKeyboardButton(text="➕ Mahsulot qo‘shish", callback_data="admin:add_product")
        ],
        [
            InlineKeyboardButton(text="📋 Buyurtmalar ro‘yxati", callback_data="admin:orders_menu"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")
        ],
        [
            InlineKeyboardButton(text="📢 Xabarnoma yuborish (Broadcast)", callback_data="admin:broadcast")
        ],
        [
            InlineKeyboardButton(text="🏠 Foydalanuvchi menyusiga qaytish", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_orders_filter_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmalarni holat bo'yicha filtrlash klaviaturasi."""
    keyboard = [
        [
            InlineKeyboardButton(text="🟡 Yangi", callback_data="admin:orders:yangi"),
            InlineKeyboardButton(text="🔵 Tasdiqlandi", callback_data="admin:orders:tasdiqlandi")
        ],
        [
            InlineKeyboardButton(text="🟠 Tayyorlanmoqda", callback_data="admin:orders:tayyorlanmoqda"),
            InlineKeyboardButton(text="🚚 Yetkazilmoqda", callback_data="admin:orders:yetkazilmoqda")
        ],
        [
            InlineKeyboardButton(text="🟢 Yakunlandi", callback_data="admin:orders:yakunlandi"),
            InlineKeyboardButton(text="📋 Barcha buyurtmalar", callback_data="admin:orders:all")
        ],
        [
            InlineKeyboardButton(text="⬅️ Admin panelga qaytish", callback_data="admin:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_order_actions_keyboard(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Alohida buyurtma holatini o'zgartirish tugmalari."""
    keyboard = []

    # 1-qator: Tasdiqlash / Tayyorlash
    row1 = []
    if current_status != "tasdiqlandi":
        row1.append(InlineKeyboardButton(text="🔵 Tasdiqlash", callback_data=f"adm_st:{order_id}:tasdiqlandi"))
    if current_status != "tayyorlanmoqda":
        row1.append(InlineKeyboardButton(text="🟠 Tayyorlash", callback_data=f"adm_st:{order_id}:tayyorlanmoqda"))
    if row1:
        keyboard.append(row1)

    # 2-qator: Yetkazish / Yakunlash
    row2 = []
    if current_status != "yetkazilmoqda":
        row2.append(InlineKeyboardButton(text="🚚 Yetkazish", callback_data=f"adm_st:{order_id}:yetkazilmoqda"))
    if current_status != "yakunlandi":
        row2.append(InlineKeyboardButton(text="🟢 Yakunlash", callback_data=f"adm_st:{order_id}:yakunlandi"))
    if row2:
        keyboard.append(row2)

    # 3-qator: Bekor qilish
    if current_status != "bekor_qilindi":
        keyboard.append([
            InlineKeyboardButton(text="🔴 Bekor qilish", callback_data=f"adm_st:{order_id}:bekor_qilindi")
        ])

    keyboard.append([
        InlineKeyboardButton(text="📋 Buyurtmalar ro‘yxatiga", callback_data="admin:orders_menu"),
        InlineKeyboardButton(text="👑 Admin panel", callback_data="admin:back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_products_list_keyboard(products: list[dict]) -> InlineKeyboardMarkup:
    """Barcha mahsulotlar ro'yxati (tahrirlash yoki o'chirish uchun)."""
    keyboard = []
    for prod in products:
        status_icon = "🟢" if prod["is_available"] else "🔴"
        code_tag = f"[{prod['product_code']}] " if prod.get("product_code") else ""
        btn_text = f"{status_icon} {code_tag}{prod['name']} ({format_price(prod['price'])} so‘m)"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"adm_pview:{prod['id']}")])

    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi mahsulot qo‘shish", callback_data="admin:add_product"),
        InlineKeyboardButton(text="⬅️ Admin panel", callback_data="admin:back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_product_actions_keyboard(product_id: int, is_available: int) -> InlineKeyboardMarkup:
    """Alohida mahsulot ustida admin amallari."""
    toggle_text = "🔴 Sotuvdan olish" if is_available else "🟢 Sotuvga chiqarish"
    keyboard = [
        [InlineKeyboardButton(text=toggle_text, callback_data=f"adm_ptoggle:{product_id}")],
        [InlineKeyboardButton(text="🗑 Butunlay o‘chirish", callback_data=f"adm_pdel:{product_id}")],
        [
            InlineKeyboardButton(text="⬅️ Mahsulotlar ro‘yxati", callback_data="admin:products"),
            InlineKeyboardButton(text="👑 Admin panel", callback_data="admin:back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_category_select_keyboard(categories: list[dict]) -> InlineKeyboardMarkup:
    """Yangi mahsulot qo'shishda kategoriya tanlash."""
    keyboard = []
    for cat in categories:
        keyboard.append([
            InlineKeyboardButton(text=f"{cat.get('icon', '📦')} {cat['name']}", callback_data=f"adm_add_cat:{cat['id']}")
        ])
    keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
