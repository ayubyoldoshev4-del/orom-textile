# 🌿 OROM TEXTILE — 24/7 Professional Telegram Bot

OROM TEXTILE brendi uchun yuqori darajada nafis, mustahkam va kechayu-kunduz (24/7) uzluksiz ishlaydigan professional Telegram bot tizimi.

---

## 💎 Brend va Aloqa Ma’lumotlari

- **Brend:** OROM TEXTILE
- **Yo‘nalish:** Uy tekstili mahsulotlari savdosi
- **Uslub:** Premium, nafis va ishonchli
- **Asosiy telefon raqam:** `+998 99 996 61 44`
- **Asosiy administrator:** [@Sherzod_6144](https://t.me/Sherzod_6144)

---

## 🗂 Asosiy Toifalar (4 ta)

Pardalar bo‘limi butunlay olib tashlangan va quyidagi 4 ta asosiy toifa shakllantirilgan:
1. **🛏 Pastellar** — 100% tabiiy paxta, sateen va jakard to‘plamlari.
2. **🧸 Yostiqlar** — Bambuk va anatomik ortopedik xotirali yostiqlar.
3. **🛌 Matrasniklar** — Aquastop suv o‘tkazmaydigan va paxtali himoya qoplamalari.
4. **🧵 Namat mahsulotlari** — Tabiiy toza qo‘y junidan tayyorlangan milliy namatlar.

---

## 📱 Asosiy Menyu va Imkoniyatlar

- `🛍 Mahsulotlar katalogi` — Barcha toifalarni ko‘rish.
- `🛏 Pastellar`, `🧸 Yostiqlar`, `🛌 Matrasniklar`, `🧵 Namat mahsulotlari` — To‘g‘ridan-to‘g‘ri toifaga o‘tish.
- `📦 Buyurtmalarim` — Mijoz faqat o‘zining buyurtmalari va ularning holatini kuzatib boradi.
- `🚚 Yetkazib berish` — Toshkentda 500 000 so‘mdan oshsa **BEPUL**, viloyatlarga pochta orqali.
- `📍 Manzilimiz` — Shourum manzili va xaritadagi aniq geolokatsiya.
- `☎️ Murojaat uchun` — `+998 99 996 61 44` raqami va @Sherzod_6144 ga to‘g‘ridan-to‘g‘ri murojaat.
- `👨‍💼 Administrator` — Menejer Sherzod bilan aloqa.

---

## 🛡 24/7 Uzluksiz Ishlash Mexanizmlari

Ushbu bot quyidagi chidamlilik mexanizmlari bilan jihozlangan:
1. **Avtomatik qayta ulanish (Supervisor Loop):** Tarmoq yoki Telegram serverida uzilish bo‘lsa, bot to‘xtamaydi, balki har 3–5 soniyada avtomatik qayta ulanadi.
2. **Global xatoliklar filtri:** Agar biror foydalanuvchi botni bloklasa yoki noto‘g‘ri ma’lumot yuborsa, bot boshqa mijozlarga xizmat ko‘rsatishda davom etadi.
3. **Rotating File Logger:** Barcha hodisalar `logs/bot.log` faylida xavfsiz saqlanadi.
4. **Xavfsiz sozlamalar:** Bot tokeni va maxfiy ma’lumotlar `.env` faylida saqlanadi.

---

## 💻 1-QISM: Windows Kompyuteringizda Ishga Tushirish

Kompyuteringizda botni 2 ta usulda yoqishingiz mumkin:

### A) Avtomatik qayta ishga tushiruvchi skript orqali (Tavsiya etiladi):
Loyiha papkasidagi `run_bot.bat` faylini ikki marta bosing.  
Ushbu skript botni yurgizadi va agar bot qandaydir sabab bilan to‘xtab qolsa, uni 5 soniyadan keyin avtomatik qayta ishga tushirib turadi.

### B) Terminal orqali:
```powershell
py -3.12 main.py
```

---

## 🌐 2-QISM: Nega 24/7 Ishlash Uchun Server (Hosting) Kerak?

> [!IMPORTANT]
> **Kompyuterda 24/7 ishlatishning cheklovlari:**
> 1. Agar kompyuteringiz o‘chsa, qayta yuklansa yoki "Uyqu" (Sleep) rejimiga o‘tsa, bot mijozlarga javob bermay to‘xtaydi.
> 2. Kompyuteringizdagi Wi-Fi yoki internet uzilsa, mijozlar botga kira olmay qoladi.
> 3. Shaxsiy kompyuterni kunu-tun yoqiq qoldirish elektr sarfi va texnikaga og‘irlik qiladi.

Shuning uchun Telegram botlar **Linux VPS (Virtual Private Server)** da yurgiziladi.  
VPS serverlar (masalan: Hetzner, DigitalOcean, Vultr, Beget yoki Uzinfocom) oyiga 2–4 dollar turadi va interneti uzilmay 365 kun 24 soat tinimsiz ishlaydi.

---

## 🚀 3-QISM: Serverda (Ubuntu / Debian Linux) O‘rnatish Yo‘riqnomasi

### 1-qadam: Serverga kirish va Python o‘rnatish
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

### 2-qadam: Loyihani serverga joylash
Loyihangizni serverdagi `/var/www/orom_textile_bot` papkasiga joylashtiring:
```bash
sudo mkdir -p /var/www/orom_textile_bot
cd /var/www/orom_textile_bot
```

### 3-qadam: Virtual muhit va kutubxonalar
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4-qadam: .env faylini sozlash
`.env` faylini ochib, bot tokeningizni joylashtiring:
```bash
nano .env
```

### 5-qadam: 24/7 Doimiy xizmat (systemd) sifatida yoqish
Loyihadagi `orom_textile_bot.service` faylidan foydalaning:
```bash
sudo cp orom_textile_bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable orom_textile_bot
sudo systemctl start orom_textile_bot
```

Holatini tekshirish:
```bash
sudo systemctl status orom_textile_bot
```
Endi kompyuteringizni xohlagancha o‘chirib qo‘ysangiz ham, bot serverda 24/7 ishlab turadi!

---

## 🐳 4-QISM: Docker Orqali Ishga Tushirish (Muqobil variant)

Serverda Docker o‘rnatilgan bo‘lsa, botni bitta buyruq bilan 24/7 avtomatik qayta yuklanadigan qilib yoqish mumkin:
```bash
docker compose up -d --build
```
Loglarni ko‘rish:
```bash
docker compose logs -f
```
