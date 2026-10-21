import aiosqlite
import logging
from contextlib import asynccontextmanager
from datetime import datetime
import random
from config import DB_PATH

logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_connection():
    """Ma'lumotlar bazasiga asinxron ulanish kontekst menejeri."""
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        yield conn


async def init_db():
    """Barcha jadvallarni yaratish, yangilash va boshlang'ich ma'lumotlarni kiritish."""
    async with get_connection() as conn:
        # 1. Foydalanuvchilar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                username TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Kategoriyalar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                icon TEXT DEFAULT '📦',
                order_num INTEGER DEFAULT 0
            );
        """)

        # 3. Mahsulotlar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                product_code TEXT,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                image_url TEXT,
                sizes TEXT,
                colors TEXT,
                stock_status TEXT DEFAULT 'Omborda mavjud',
                is_available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
            );
        """)

        # 4. Buyurtmalar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                delivery_price INTEGER DEFAULT 0,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                product_size TEXT,
                product_color TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price INTEGER NOT NULL,
                total_price INTEGER NOT NULL,
                status TEXT DEFAULT 'yangi',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Mavjud bazalar uchun ustunlarni tekshirish va qo'shish (Migratsiya)
        await _apply_migrations(conn)

        # PARDALAR BO'LIMINI VA MAHSULOTLARINI BUTUNLAY TOZALASH
        await _purge_curtains(conn)

        # Yangi 4 ta asosiy toifani sozlash
        await _setup_target_categories(conn)

        await conn.commit()
        logger.info("Ma'lumotlar bazasi jadvallari va toifalari muvaffaqiyatli tekshirildi.")


async def _apply_migrations(conn: aiosqlite.Connection):
    """Eski bazada yetishmayotgan ustunlarni xavfsiz qo'shish."""
    # products jadvalidagi ustunlarni tekshirish
    cursor = await conn.execute("PRAGMA table_info(products);")
    columns = [row["name"] for row in await cursor.fetchall()]

    if "product_code" not in columns:
        await conn.execute("ALTER TABLE products ADD COLUMN product_code TEXT;")
    if "stock_status" not in columns:
        await conn.execute("ALTER TABLE products ADD COLUMN stock_status TEXT DEFAULT 'Omborda mavjud';")

    # orders jadvalidagi ustunlarni tekshirish
    cursor = await conn.execute("PRAGMA table_info(orders);")
    order_cols = [row["name"] for row in await cursor.fetchall()]
    if "delivery_price" not in order_cols:
        await conn.execute("ALTER TABLE orders ADD COLUMN delivery_price INTEGER DEFAULT 0;")


async def _purge_curtains(conn: aiosqlite.Connection):
    """Pardalar va eski ortiqcha bo'limlarni butunlay tozalash."""
    cursor = await conn.execute("SELECT id FROM categories WHERE slug IN ('pardalar', 'uy-tekstili') OR LOWER(name) LIKE '%parda%';")
    rows = await cursor.fetchall()
    for r in rows:
        cat_id = r["id"]
        await conn.execute("DELETE FROM products WHERE category_id = ?;", (cat_id,))
        await conn.execute("DELETE FROM categories WHERE id = ?;", (cat_id,))

    await conn.execute("DELETE FROM products WHERE LOWER(name) LIKE '%parda%';")


async def _setup_target_categories(conn: aiosqlite.Connection):
    """Yangi to'rtta asosiy kategoriyani kiritish yoki yangilash."""
    # Maqsadli to'rtta kategoriya:
    # 🛏 Pastellar
    # 🧸 Yostiqlar
    # 🛌 Matrasniklar
    # 🧵 Namat mahsulotlari

    target_cats = [
        {"name": "Pastellar", "slug": "pastellar", "icon": "🛏", "order_num": 1},
        {"name": "Yostiqlar", "slug": "yostiqlar", "icon": "🧸", "order_num": 2},
        {"name": "Matrasniklar", "slug": "matrasniklar", "icon": "🛌", "order_num": 3},
        {"name": "Namat mahsulotlari", "slug": "namat", "icon": "🧵", "order_num": 4},
    ]

    for cat in target_cats:
        # Slug bo'yicha mavjudligini tekshirish
        cursor = await conn.execute("SELECT id FROM categories WHERE slug = ?;", (cat["slug"],))
        row = await cursor.fetchone()
        if row:
            await conn.execute(
                "UPDATE categories SET name = ?, icon = ?, order_num = ? WHERE slug = ?;",
                (cat["name"], cat["icon"], cat["order_num"], cat["slug"])
            )
        else:
            # Agar eski choyshablar bo'lsa uni Pastellar ga o'zgartirish
            if cat["slug"] == "pastellar":
                c_old = await conn.execute("SELECT id FROM categories WHERE slug = 'choyshablar';")
                r_old = await c_old.fetchone()
                if r_old:
                    await conn.execute(
                        "UPDATE categories SET name = 'Pastellar', slug = 'pastellar', icon = '🛏', order_num = 1 WHERE id = ?;",
                        (r_old["id"],)
                    )
                    continue

            # Agar eski yostiq-korpalar bo'lsa uni Yostiqlar ga o'zgartirish
            if cat["slug"] == "yostiqlar":
                c_old = await conn.execute("SELECT id FROM categories WHERE slug = 'yostiq-korpalar';")
                r_old = await c_old.fetchone()
                if r_old:
                    await conn.execute(
                        "UPDATE categories SET name = 'Yostiqlar', slug = 'yostiqlar', icon = '🧸', order_num = 2 WHERE id = ?;",
                        (r_old["id"],)
                    )
                    continue

            # Yangi kiritish
            await conn.execute(
                "INSERT INTO categories (name, slug, icon, order_num) VALUES (?, ?, ?, ?);",
                (cat["name"], cat["slug"], cat["icon"], cat["order_num"])
            )

    # Toifalarga oid namunaviy mahsulotlar borligini tekshirish
    await _seed_target_products(conn)


async def _seed_target_products(conn: aiosqlite.Connection):
    """4 ta kategoriya uchun dastlabki sifatli mahsulotlarni kiritish."""
    # Kategoriya ID larini olish
    cat_map = {}
    async with conn.execute("SELECT id, slug FROM categories;") as cursor:
        async for r in cursor:
            cat_map[r["slug"]] = r["id"]

    # Har bir toifada mahsulot bormi?
    for slug in ["pastellar", "yostiqlar", "matrasniklar", "namat"]:
        if slug not in cat_map:
            continue
        c_prod = await conn.execute("SELECT COUNT(*) as cnt FROM products WHERE category_id = ?;", (cat_map[slug],))
        cnt = (await c_prod.fetchone())["cnt"]
        if cnt == 0:
            if slug == "pastellar":
                await conn.execute("""
                    INSERT INTO products (
                        category_id, product_code, name, description, price,
                        image_url, sizes, colors, stock_status, is_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
                """, (
                    cat_map["pastellar"],
                    "OT-PAS-101",
                    "Satin Jakard Royal Pastel to‘plami",
                    "100% tabiiy ipakdek yumshoq turk paxtasi. Jakard naqshli, yuvilganda tiftiklanmaydi va rangi o‘chmaydi.",
                    850000,
                    "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=800&q=80",
                    "1.5 kishilik (160x220 sm), Yevro (200x220 sm), Oilaviy (2 x 150x215 sm)",
                    "Krem / Marvarid, Tillarang, Qahva",
                    "Omborda mavjud"
                ))
            elif slug == "yostiqlar":
                await conn.execute("""
                    INSERT INTO products (
                        category_id, product_code, name, description, price,
                        image_url, sizes, colors, stock_status, is_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
                """, (
                    cat_map["yostiqlar"],
                    "OT-YOS-201",
                    "Bambuk Anatomik Ortopedik Yostiq",
                    "Bambuk tolali tabiiy qoplama va bo‘yin umurtqasini qulay ushlab turuvchi xotirali to‘ldiruvchi (Memory foam).",
                    195000,
                    "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?auto=format&fit=crop&w=800&q=80",
                    "50x70 sm, 70x70 sm",
                    "Oq, Och yashil hoshiyali",
                    "Omborda mavjud"
                ))
            elif slug == "matrasniklar":
                await conn.execute("""
                    INSERT INTO products (
                        category_id, product_code, name, description, price,
                        image_url, sizes, colors, stock_status, is_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
                """, (
                    cat_map["matrasniklar"],
                    "OT-MAT-301",
                    "Aquastop Suv o‘tkazmaydigan Matrasnik",
                    "Nafas oluvchi mikrofibra va suv o‘tkazmaydigan elastik membranali matras qoplamasi. Matrasni chang va namlikdan asraydi.",
                    280000,
                    "https://images.unsplash.com/photo-1631679706909-1844bbd07221?auto=format&fit=crop&w=800&q=80",
                    "90x200 sm, 160x200 sm, 180x200 sm, 200x200 sm",
                    "Oq, Och kulrang",
                    "Omborda mavjud"
                ))
            elif slug == "namat":
                await conn.execute("""
                    INSERT INTO products (
                        category_id, product_code, name, description, price,
                        image_url, sizes, colors, stock_status, is_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
                """, (
                    cat_map["namat"],
                    "OT-NAM-401",
                    "Tabiiy Qo‘y Juni Namati (Milliy naqshli)",
                    "100% tabiiy toza jundan tayyorlangan issiq va shinam milliy namat. Xonadon shinamligi va salomatlik uchun ideal.",
                    350000,
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
                    "100x200 sm, 150x200 sm, 200x250 sm",
                    "Tabiiy jun rangi, Qizil hoshiyali",
                    "Omborda mavjud"
                ))


# ==================== FOYDALANUVCHILAR ====================

async def add_or_update_user(user_id: int, full_name: str, username: str = None, phone: str = None):
    """Foydalanuvchini bazaga qo'shish yoki yangilash."""
    async with get_connection() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, full_name, username, phone)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                username = COALESCE(excluded.username, users.username),
                phone = COALESCE(excluded.phone, users.phone);
        """, (user_id, full_name, username, phone))
        await conn.commit()


async def update_user_phone(user_id: int, phone: str):
    """Foydalanuvchi telefon raqamini yangilash."""
    async with get_connection() as conn:
        await conn.execute("UPDATE users SET phone = ? WHERE user_id = ?;", (phone, user_id))
        await conn.commit()


async def get_user(user_id: int) -> dict | None:
    """Foydalanuvchi ma'lumotlarini olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?;", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_users() -> list[dict]:
    """Barcha foydalanuvchilar ro'yxati (xabarnoma yuborish uchun)."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM users ORDER BY created_at DESC;")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


# ==================== KATEGORIYALAR ====================

async def get_categories() -> list[dict]:
    """Barcha faol kategoriyalarni tartibi bo'yicha olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM categories ORDER BY order_num ASC, id ASC;")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_category_by_id(cat_id: int) -> dict | None:
    """Kategoriyani ID bo'yicha olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM categories WHERE id = ?;", (cat_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_category_by_slug(slug: str) -> dict | None:
    """Kategoriyani slug bo'yicha olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM categories WHERE slug = ?;", (slug,))
        row = await cursor.fetchone()
        return dict(row) if row else None


# ==================== MAHSULOTLAR ====================

async def get_products_by_category(category_id: int) -> list[dict]:
    """Kategoriya bo'yicha sotuvda mavjud mahsulotlarni olish."""
    async with get_connection() as conn:
        cursor = await conn.execute(
            "SELECT * FROM products WHERE category_id = ? AND is_available = 1 ORDER BY id DESC;",
            (category_id,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_all_products(include_unavailable: bool = False) -> list[dict]:
    """Barcha mahsulotlar ro'yxatini olish (Admin uchun)."""
    async with get_connection() as conn:
        if include_unavailable:
            query = """
                SELECT p.*, c.name as category_name, c.icon as category_icon
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.id DESC;
            """
        else:
            query = """
                SELECT p.*, c.name as category_name, c.icon as category_icon
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_available = 1
                ORDER BY p.id DESC;
            """
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_product_by_id(product_id: int) -> dict | None:
    """Mahsulotni ID orqali olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("""
            SELECT p.*, c.name as category_name, c.icon as category_icon
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?;
        """, (product_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_product(
    category_id: int,
    name: str,
    description: str,
    price: int,
    product_code: str = None,
    image_url: str = None,
    sizes: str = None,
    colors: str = None,
    stock_status: str = "Omborda mavjud"
) -> int:
    """Yangi mahsulot qo'shish."""
    if not product_code:
        product_code = f"OT-{random.randint(100, 999)}"

    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO products (
                category_id, product_code, name, description, price,
                image_url, sizes, colors, stock_status, is_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
        """, (category_id, product_code, name, description, price, image_url, sizes, colors, stock_status))
        await conn.commit()
        return cursor.lastrowid


async def delete_product(product_id: int):
    """Mahsulotni bazadan butunlay o'chirish."""
    async with get_connection() as conn:
        await conn.execute("DELETE FROM products WHERE id = ?;", (product_id,))
        await conn.commit()


async def toggle_product_availability(product_id: int) -> int:
    """Mahsulot mavjudligini o'zgartirish (0 yoki 1)."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT is_available FROM products WHERE id = ?;", (product_id,))
        row = await cursor.fetchone()
        if not row:
            return 0
        new_status = 0 if row["is_available"] == 1 else 1
        await conn.execute("UPDATE products SET is_available = ? WHERE id = ?;", (new_status, product_id))
        await conn.commit()
        return new_status


# ==================== BUYURTMALAR ====================

def generate_order_number() -> str:
    """Noyob buyurtma raqamini generatsiya qilish (masalan, #OT-261017-4821)."""
    now = datetime.now()
    rand_suffix = random.randint(1000, 9999)
    return f"OT-{now.strftime('%y%m%d')}-{rand_suffix}"


async def create_order(
    user_id: int,
    customer_name: str,
    customer_phone: str,
    delivery_address: str,
    product_id: int,
    product_name: str,
    product_size: str,
    product_color: str,
    quantity: int,
    unit_price: int,
    total_price: int,
    delivery_price: int = 0,
    notes: str = ""
) -> dict:
    """Yangi buyurtma yaratish."""
    order_number = generate_order_number()
    async with get_connection() as conn:
        cursor = await conn.execute("""
            INSERT INTO orders (
                order_number, user_id, customer_name, customer_phone, delivery_address,
                delivery_price, product_id, product_name, product_size, product_color,
                quantity, unit_price, total_price, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'yangi', ?);
        """, (
            order_number, user_id, customer_name, customer_phone, delivery_address,
            delivery_price, product_id, product_name, product_size, product_color,
            quantity, unit_price, total_price, notes
        ))
        await conn.commit()
        order_id = cursor.lastrowid

    return await get_order_by_id(order_id)


async def get_order_by_id(order_id: int) -> dict | None:
    """Buyurtmani ID bo'yicha olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM orders WHERE id = ?;", (order_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_order_by_number(order_number: str) -> dict | None:
    """Buyurtmani unikal raqami bo'yicha olish."""
    async with get_connection() as conn:
        cursor = await conn.execute("SELECT * FROM orders WHERE order_number = ?;", (order_number,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_orders(user_id: int, limit: int = 15) -> list[dict]:
    """Faqat shu mijozning o'z buyurtmalarini olish (boshqa mijozlarga ko'rinmaydi)."""
    async with get_connection() as conn:
        cursor = await conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?;",
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_all_orders(status: str = None, limit: int = 30) -> list[dict]:
    """Barcha buyurtmalarni olish (Admin panel uchun)."""
    async with get_connection() as conn:
        if status:
            cursor = await conn.execute(
                "SELECT * FROM orders WHERE status = ? ORDER BY id DESC LIMIT ?;",
                (status, limit)
            )
        else:
            cursor = await conn.execute(
                "SELECT * FROM orders ORDER BY id DESC LIMIT ?;",
                (limit,)
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def update_order_status(order_id: int, new_status: str) -> bool:
    """Buyurtma holatini yangilash."""
    async with get_connection() as conn:
        await conn.execute("UPDATE orders SET status = ? WHERE id = ?;", (new_status, order_id))
        await conn.commit()
        return True


# ==================== STATISTIKA ====================

async def get_statistics() -> dict:
    """Admin panel uchun to'liq statistika."""
    async with get_connection() as conn:
        # Jami mijozlar
        c_users = await conn.execute("SELECT COUNT(*) as count FROM users;")
        users_count = (await c_users.fetchone())["count"]

        # Jami buyurtmalar
        c_orders = await conn.execute("SELECT COUNT(*) as count FROM orders;")
        orders_count = (await c_orders.fetchone())["count"]

        # Bugungi buyurtmalar
        today_date = datetime.now().strftime("%Y-%m-%d")
        c_today = await conn.execute(
            "SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = DATE(?);",
            (today_date,)
        )
        today_orders_count = (await c_today.fetchone())["count"]

        # Yangi (kutilayotgan) buyurtmalar
        c_pending = await conn.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'yangi';")
        pending_count = (await c_pending.fetchone())["count"]

        # Jami savdo summasi
        c_rev = await conn.execute(
            "SELECT SUM(total_price) as sum FROM orders WHERE status IN ('tasdiqlandi', 'tayyorlanmoqda', 'yetkazilmoqda', 'yakunlandi');"
        )
        rev_row = await c_rev.fetchone()
        total_revenue = rev_row["sum"] if rev_row and rev_row["sum"] else 0

        # Jami faol mahsulotlar soni
        c_prod = await conn.execute("SELECT COUNT(*) as count FROM products WHERE is_available = 1;")
        products_count = (await c_prod.fetchone())["count"]

        return {
            "users_count": users_count,
            "orders_count": orders_count,
            "today_orders_count": today_orders_count,
            "pending_count": pending_count,
            "total_revenue": total_revenue,
            "products_count": products_count
        }
