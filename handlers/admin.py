from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_IDS
from database.db import SessionLocal
from database.models import User
from database.likes import Like
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
import io
from aiogram.types import FSInputFile

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS 

# 👑 Admin panel menyusi
@router.message(Command("test"))
async def test_handler(message: types.Message):
    await message.answer("✅ Test handler ishladi!")
import csv
import tempfile
from aiogram.types import FSInputFile

@router.message(Command("export"))
async def export_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")

    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    if not users:
        return await message.answer("👥 Foydalanuvchilar topilmadi.")

    # 📝 CSV faylni vaqtincha diskka yozamiz
    with tempfile.NamedTemporaryFile("w+", newline="", delete=False, suffix=".csv") as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["ID", "Ism", "Yosh", "Jins", "Shahar", "Qiziqishlar", "VIP"])
        for user in users:
            writer.writerow([
                user.id,
                user.name,
                user.age,
                user.gender,
                user.city,
                user.interests,
                "✅" if user.is_premium else "❌"
            ])
        tmp_path = tmp.name  # Fayl yo‘li

    # 📎 Telegramga yuborish
    await message.answer_document(document=FSInputFile(tmp_path, filename="users_export.csv"))

    await message.answer(
        "👑 *Admin panelga xush kelibsiz!*\n\n"
        "📋 Buyruqlar:\n"
        "/users — Foydalanuvchilar ro‘yxati\n"
        "/vip <id> — Foydalanuvchini VIP qilish\n"
        "/ban <id> — Foydalanuvchini bloklash\n"
        "/stats — Umumiy statistika\n"
        "/find <username> — Username orqali qidirish\n"
        "/growth — VIP o‘sish statistikasi\n"
        "/logs <id> — Foydalanuvchi faoliyati",
        parse_mode="Markdown"
    )

# 👥 Foydalanuvchilar ro‘yxati
@router.message(Command("users"))
async def list_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    db = SessionLocal()
    users = db.query(User).all()
    if not users:
        await message.answer("👥 Hozircha foydalanuvchilar yo‘q.")
    else:
        for user in users:
            await message.answer(
                f"🆔 ID: {user.id}\n"
                f"👤 {user.name}, {user.age} yosh\n"
                f"📍 {user.city}\n"
                f"🎯 {user.interests}\n"
                f"⭐ VIP: {'✅' if user.is_premium else '❌'}"
            )
    db.close()

# 💎 VIP qilish
@router.message(Command("vip"))
async def make_vip(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("❗ Foydalanuvchi ID’sini to‘g‘ri kiriting: /vip <id>")
    user_id = int(args[1])
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_premium = True
        db.commit()
        await message.answer(f"✅ {user.name} endi VIP foydalanuvchi!")
    else:
        await message.answer("❌ Bunday foydalanuvchi topilmadi.")
    db.close()

# 🚫 Ban qilish
@router.message(Command("ban"))
async def ban_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("❗ Foydalanuvchi ID’sini to‘g‘ri kiriting: /ban <id>")
    user_id = int(args[1])
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        await message.answer(f"🚫 {user.name} bloklandi va bazadan o‘chirildi.")
    else:
        await message.answer("❌ Bunday foydalanuvchi topilmadi.")
    db.close()

# 📊 Umumiy statistika
@router.message(Command("stats"))
async def show_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    db = SessionLocal()

    total_users = db.query(func.count(User.id)).scalar()
    vip_users = db.query(func.count(User.id)).filter(User.is_premium == True).scalar()
    total_likes = db.query(func.count(Like.id)).filter(Like.is_like == True).scalar()
    total_dislikes = db.query(func.count(Like.id)).filter(Like.is_like == False).scalar()

    mutual_likes = db.query(Like).filter(Like.is_like == True).all()
    mutual_count = 0
    for like in mutual_likes:
        reverse = db.query(Like).filter(
            Like.from_user_id == like.to_user_id,
            Like.to_user_id == like.from_user_id,
            Like.is_like == True
        ).first()
        if reverse:
            mutual_count += 1
    mutual_count = mutual_count // 2

    db.close()

    await message.answer(
        f"📊 *Statistik ma’lumotlar:*\n\n"
        f"👥 Umumiy foydalanuvchilar: {total_users}\n"
        f"💎 VIP foydalanuvchilar: {vip_users}\n"
        f"❤️ Like bosilganlar: {total_likes}\n"
        f"💔 Dislike bosilganlar: {total_dislikes}\n"
        f"🔁 O‘zaro mosliklar: {mutual_count}",
        parse_mode="Markdown"
    )

# 🔍 Username orqali qidirish
@router.message(Command("find"))
async def find_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split()
    if len(args) != 2:
        return await message.answer("❗ Foydalanuvchi username’sini kiriting: /find <username>")
    username = args[1].lstrip("@")
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_username == username).first()
    if user:
        await message.answer(
            f"🔎 Topildi:\n"
            f"🆔 ID: {user.id}\n"
            f"👤 {user.name}, {user.age} yosh\n"
            f"📍 {user.city}\n"
            f"🎯 {user.interests}\n"
            f"⭐ VIP: {'✅' if user.is_premium else '❌'}"
        )
    else:
        await message.answer("❌ Bunday username topilmadi.")
    db.close()

# 📈 VIP o‘sish statistikasi
@router.message(Command("growth"))
async def user_growth(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    db = SessionLocal()
    today = datetime.utcnow().date()
    stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = db.query(User).filter(
            func.date(User.vip_until) == day
        ).count()
        stats.append(f"{day.strftime('%Y-%m-%d')}: {count} ta VIP")
    db.close()
    await message.answer("📈 Oxirgi 7 kun VIP o‘sishi:\n\n" + "\n".join(reversed(stats)))

# 🧾 Foydalanuvchi faoliyati (like va matchlar)
@router.message(Command("logs"))
async def user_logs(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("❗ Foydalanuvchi ID’sini to‘g‘ri kiriting: /logs <id>")
    user_id = int(args[1])
    db = SessionLocal()
    likes = db.query(Like).filter(Like.from_user_id == user_id).all()
    if not likes:
        await message.answer("📝 Bu foydalanuvchi hech kimga like/dislike bosmagan.")
    else:
        await message.answer(f"🧾 Foydalanuvchi #{user_id} faoliyati:")
        for like in likes[:10]:
            status = "❤️ Like" if like.is_like else "💔 Dislike"
            await message.answer(f"{status} → foydalanuvchi ID: {like.to_user_id}")
    db.close()
@router.message(Command("edit"))
async def edit_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("❗ Foydalanuvchi ID’sini kiriting: /edit <id>")
    
    user_id = int(args[1])
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await message.answer("❌ Foydalanuvchi topilmadi.")
        db.close()
        return

    await message.answer(
        f"✏️ Tahrirlash uchun quyidagi formatda yozing:\n"
        f"`/update {user_id} Ism Yosh Shahar Qiziqishlar VIP(0/1)`\n\n"
        f"Masalan:\n`/update {user_id} Dilnoza 23 Tashkent Kitoblar 1`",
        parse_mode="Markdown"
    )
    db.close()

@router.message(Command("update"))
async def update_user(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    args = message.text.split(maxsplit=6)
    if len(args) != 7:
        return await message.answer("❗ Format noto‘g‘ri. /edit <id> orqali ko‘rsatmani o‘qing.")
    
    user_id = int(args[1])
    name, age, city, interests, vip = args[2], int(args[3]), args[4], args[5], bool(int(args[6]))

    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.age = age
        user.city = city
        user.interests = interests
        user.is_premium = vip
        db.commit()
        await message.answer(f"✅ {user.name} ma’lumotlari yangilandi.")
    else:
        await message.answer("❌ Foydalanuvchi topilmadi.")
    db.close()
@router.message(Command("chart"))
async def chart_growth(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")
    
    db = SessionLocal()
    today = datetime.utcnow().date()
    chart = []

    for i in range(7):
        day = today - timedelta(days=i)
        count = db.query(User).filter(func.date(User.vip_until) == day).count()
        bar = "█" * count if count > 0 else "░"
        chart.append(f"{day.strftime('%d-%b')}: {bar} ({count})")

    db.close()
    await message.answer("📊 VIP o‘sish grafigi (oxirgi 7 kun):\n\n" + "\n".join(reversed(chart)))

@router.message(Command("export"))
async def export_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")

    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    if not users:
        return await message.answer("👥 Foydalanuvchilar topilmadi.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Telegram ID", "Name", "Age", "Gender", "City", "Interests", "VIP", "Username"])

    for user in users:
        writer.writerow([
            user.id,
            user.telegram_id,
            user.name,
            user.age,
            user.gender,
            user.city,
            user.interests,
            "Yes" if user.is_premium else "No",
            user.telegram_username or ""
        ])

    output.seek(0)
    file = io.BytesIO(output.read().encode("utf-8"))
    file.name = "users_export.csv"

    await message.answer_document(document=FSInputFile(file, filename="users_export.csv"))
    @router.message(Command("live"))
    async def live_activity(message: types.Message):
     if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")

    db = SessionLocal()
    recent_users = db.query(User).order_by(User.id.desc()).limit(10).all()
    recent_likes = db.query(Like).order_by(Like.id.desc()).limit(10).all()
    db.close()

    msg = "🖥 *Oxirgi 10 foydalanuvchi:*\n"
    for user in recent_users:
        msg += f"👤 {user.name} ({user.age}) — {user.city} | VIP: {'✅' if user.is_premium else '❌'}\n"

    msg += "\n❤️ *Oxirgi 10 like/dislike:*\n"
    for like in recent_likes:
        status = "❤️" if like.is_like else "💔"
        msg += f"{status} {like.from_user_id} → {like.to_user_id}\n"

    await message.answer(msg, parse_mode="Markdown")
@router.message(Command("segment"))
async def segment_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return await message.answer("⛔ Sizga ruxsat yo‘q.")

    db = SessionLocal()
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)

    active_users = db.query(User).filter(User.vip_until != None, User.vip_until > seven_days_ago).count()
    vip_users = db.query(User).filter(User.is_premium == True).count()
    hidden_users = db.query(User).filter(User.is_hidden == True).count()
    db.close()

    await message.answer(
        f"📂 *Foydalanuvchi segmentlari:*\n\n"
        f"🟢 Faol (oxirgi 7 kun): {active_users}\n"
        f"💎 VIP foydalanuvchilar: {vip_users}\n"
        f"🕵️ Yashirin rejimdagilar: {hidden_users}",
        parse_mode="Markdown"
    )


