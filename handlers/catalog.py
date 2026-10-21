import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import (
    get_categories,
    get_category_by_id,
    get_products_by_category,
    get_product_by_id
)
from keyboards import (
    categories_inline_keyboard,
    products_inline_keyboard,
    product_detail_keyboard,
    format_price
)

logger = logging.getLogger(__name__)
router = Router(name="catalog_router")


@router.message(F.text == "🛍 Mahsulotlar katalogi")
async def show_catalog(message: Message, state: FSMContext):
    """Katalogni ochish — 4 ta asosiy kategoriya ro'yxatini ko'rsatish."""
    await state.clear()
    categories = await get_categories()

    if not categories:
        await message.answer("⚠️ Hozirda mahsulot toifalari mavjud emas.")
        return

    text = (
        "🛍 <b>OROM TEXTILE Mahsulotlar Katalogi</b>\n\n"
        "Xonadoningiz uchun qulaylik va shinamlik ulashuvchi sifatli to‘qimachilik mahsulotlari.\n"
        "Kerakli toifani tanlang:"
    )
    await message.answer(
        text=text,
        parse_mode="HTML",
        reply_markup=categories_inline_keyboard(categories)
    )


@router.callback_query(F.data.startswith("cat:"))
async def cb_category_selected(callback: CallbackQuery):
    """Foydalanuvchi biror kategoriyani tanlaganda mahsulotlar ro'yxatini chiqarish."""
    cat_id = int(callback.data.split(":")[1])
    category = await get_category_by_id(cat_id)

    if not category:
        await callback.answer("Kategoriya topilmadi!", show_alert=True)
        return

    products = await get_products_by_category(cat_id)

    if not products:
        await callback.answer("Ushbu toifada hozircha mahsulot yo‘q.", show_alert=True)
        return

    text = (
        f"{category.get('icon', '📦')} <b>{category['name']}</b>\n\n"
        "Mahsulot haqida to‘liq ma’lumot olish va narxini ko‘rish uchun kerakli variantni tanlang:"
    )

    try:
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(
                text=text,
                parse_mode="HTML",
                reply_markup=products_inline_keyboard(products, cat_id)
            )
        else:
            await callback.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=products_inline_keyboard(products, cat_id)
            )
    except Exception:
        await callback.message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=products_inline_keyboard(products, cat_id)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("prod:"))
async def cb_product_detail(callback: CallbackQuery):
    """Alohida mahsulotning standart kartasi."""
    prod_id = int(callback.data.split(":")[1])
    product = await get_product_by_id(prod_id)

    if not product:
        await callback.answer("Kechirasiz, ushbu mahsulot topilmadi!", show_alert=True)
        return

    price_str = format_price(product["price"])
    code_str = f" (#{product['product_code']})" if product.get("product_code") else ""
    stock_str = product.get("stock_status") or "Omborda mavjud"
    sizes_str = product.get("sizes") or "Standart"
    colors_str = product.get("colors") or "Standart"

    # Talab qilingan standart karta formati:
    card_text = (
        f"📦 <b>{product['name']}</b>{code_str}\n\n"
        f"📝 <b>Tavsif:</b> {product['description']}\n\n"
        f"📏 <b>O‘lcham:</b> {sizes_str}\n"
        f"🎨 <b>Rang:</b> {colors_str}\n"
        f"💰 <b>Narx:</b> <code>{price_str} so‘m</code>\n"
        f"📦 <b>Mavjudligi:</b> {stock_str}"
    )

    reply_kb = product_detail_keyboard(prod_id, product["category_id"])
    image_url = product.get("image_url")

    try:
        await callback.message.delete()
    except Exception:
        pass

    if image_url:
        try:
            await callback.message.answer_photo(
                photo=image_url,
                caption=card_text,
                parse_mode="HTML",
                reply_markup=reply_kb
            )
            await callback.answer()
            return
        except Exception as e:
            logger.warning(f"Rasm yuklashda xatolik ({image_url}): {e}")

    await callback.message.answer(
        text=card_text,
        parse_mode="HTML",
        reply_markup=reply_kb
    )
    await callback.answer()
