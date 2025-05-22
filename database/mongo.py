from pymongo import MongoClient
from datetime import datetime

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["mailer_db"]

users = db["users"]
smtps = db["smtps"]
mail_logs = db["mail_logs"]
sudoers = db["sudoers"]

OWNER_ID = 7580991572  # Replace with actual owner ID

def get_owner_id():
    return OWNER_ID

# ─── User / Sudo Management ─────────────────────────────

def get_user(user_id: int):
    return users.find_one({"user_id": user_id})

def add_sudo(user_id: int):
    if not is_sudo(user_id):
        sudoers.insert_one({"user_id": user_id})

def remove_sudo(user_id: int):
    sudoers.delete_one({"user_id": user_id})

def get_sudoers():
    return [u["user_id"] for u in sudoers.find()]

def is_sudo(user_id: int):
    return user_id == OWNER_ID or sudoers.find_one({"user_id": user_id}) is not None

# ─── SMTP Management ────────────────────────────────────

def get_user_smtps(user_id: int):
    return list(smtps.find({"user_id": user_id}))

def add_smtp(user_id: int, smtp_data: dict):
    count = count_smtps(user_id)
    if count >= 5:
        return False
    smtp_data["user_id"] = user_id
    smtps.insert_one(smtp_data)
    return True

def delete_smtp(user_id: int, smtp_id: str):
    result = smtps.delete_one({"user_id": user_id, "smtp_id": smtp_id})
    return result.deleted_count > 0

def count_smtps(user_id: int):
    return smtps.count_documents({"user_id": user_id})

async def get_smtp_by_username(user_id: int, smtp_username: str):
    user_data = await smtp_collection.find_one({"user_id": user_id})
    if not user_data:
        return None

    for smtp in user_data.get("smtps", []):
        if smtp.get("username") == smtp_username:
            return smtp
    return None


# ─── Mail Log / Record ──────────────────────────────────

def save_mail_record(user_id: int, smtp_id: str, recipients: list, subject: str, content: str):
    mail_logs.insert_one({
        "user_id": user_id,
        "smtp_id": smtp_id,
        "recipients": recipients,
        "subject": subject,
        "content": content,
        "timestamp": datetime.utcnow()
    })

def get_mail_records(user_id: int, limit: int = 20):
    return list(mail_logs.find({"user_id": user_id}).sort("timestamp", -1).limit(limit))
