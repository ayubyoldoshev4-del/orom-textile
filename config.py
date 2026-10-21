import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Asosiy Telegram sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ID ro'yxati (vergul bilan ajratilgan)
_admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS: list[int] = []
if _admin_ids_raw:
    for item in _admin_ids_raw.split(","):
        clean_item = item.strip()
        if clean_item.isdigit() or (clean_item.startswith("-") and clean_item[1:].isdigit()):
            ADMIN_IDS.append(int(clean_item))

# Ma'lumotlar bazasi
DB_NAME = os.getenv("DB_NAME", "orom_textile.db").strip()
DB_PATH = BASE_DIR / DB_NAME

# Kompaniya va administrator aloqa ma'lumotlari
COMPANY_NAME = "OROM TEXTILE"
COMPANY_PHONE = "+998 99 996 61 44"
ADMIN_USERNAME = "Sherzod_6144"
COMPANY_LOCATION = "Toshkent shahri, Chilonzor tumani, Bunyodkor ko'chasi 42-uy"
COMPANY_LOCATION_LAT = 41.2858
COMPANY_LOCATION_LON = 69.2036

# Yetkazib berish sozlamalari
FREE_DELIVERY_THRESHOLD = 500000  # 500 000 so'mdan oshsa bepul
STANDARD_DELIVERY_PRICE = 25000   # Toshkent ichida

# Salomlashuv matni
WELCOME_TEXT = (
    "Assalomu alaykum! 🌿\n\n"
    "<b>OROM TEXTILE</b> botiga xush kelibsiz!\n\n"
    "Uyingiz uchun sifatli va nafis tekstil mahsulotlarini biz bilan tanlang. "
    "Mahsulotlarni ko‘ring, narxlarni bilib oling va qulay tarzda buyurtma bering."
)

# Yetkazib berish ma'lumoti
DELIVERY_INFO_TEXT = (
    "🚚 <b>YETKAZIB BERISH XIZMATI</b>\n\n"
    "Biz buyurtmalaringizni butun O‘zbekiston bo‘ylab tez va xavfsiz yetkazib beramiz!\n\n"
    "📍 <b>Toshkent shahri bo‘ylab:</b>\n"
    "• Yetkazib berish muddati: <b>24 soat ichida</b>\n"
    "• Buyurtma summasi 500 000 so‘mdan oshsa — <b>Yetkazib berish BEPUL!</b>\n"
    "• Standart yetkazish narxi: 25 000 so‘m\n\n"
    "🇺🇿 <b>Viloyatlar bo‘ylab:</b>\n"
    "• BTS / Fargo pochta xizmati orqali: <b>1-3 ish kuni</b>\n"
    "• Pochta tarifiga asosan yetkaziladi\n\n"
    "💳 <b>To‘lov usullari:</b>\n"
    "• Naqd pul (mahsulotni qabul qilib olganda)\n"
    "• Payme / Click orqali onlayn to‘lov"
)

# Aloqa va Murojaat matni
CONTACTS_TEXT = (
    "☎️ <b>MUROJAAT UCHUN</b>\n\n"
    "Savollaringiz, takliflaringiz yoki maxsus buyurtmalaringiz bo‘lsa, biz bilan bog‘laning:\n\n"
    f"📞 <b>Telefon raqam:</b> <code>{COMPANY_PHONE}</code>\n"
    f"👨‍💼 <b>Administrator:</b> @{ADMIN_USERNAME}\n"
    "⏰ <b>Ish vaqti:</b> Har kuni 09:00 dan 21:00 gacha (dam olish kunlarisiz)\n\n"
    "<i>Quyidagi tugmalar orqali qo‘ng‘iroq qilishingiz yoki administrator bilan bevosita yozishishingiz mumkin:</i>"
)

# Administrator sahifasi matni
ADMIN_INFO_TEXT = (
    "👨‍💼 <b>OROM TEXTILE ADMINISTRATORI</b>\n\n"
    "Kompaniya rahbariyati va savdo boshqaruvi:\n"
    f"👤 <b>Menejer:</b> Sherzod\n"
    f"✈️ <b>Telegram:</b> @{ADMIN_USERNAME}\n"
    f"📞 <b>Telefon:</b> <code>{COMPANY_PHONE}</code>\n\n"
    "Mahsulotlar haqida qo‘shimcha ma’lumot, ulgurji xaridlar va hamkorlik uchun murojaat qilishingiz mumkin."
)
