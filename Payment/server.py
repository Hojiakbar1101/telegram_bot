from fastapi import FastAPI, Request
from database.db import SessionLocal
from database.models import User
from datetime import datetime, timedelta

app = FastAPI()

@app.post("/payment/callback")
async def payment_callback(request: Request):
    data = await request.json()
    user_id = int(data["user_id"])
    days = int(data["days"])

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if user:
        user.is_premium = True
        user.vip_until = datetime.now() + timedelta(days=days)
        db.commit()
    db.close()
    return {"status": "ok"}
