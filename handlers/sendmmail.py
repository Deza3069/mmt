import asyncio
import smtplib
from email.mime.text import MIMEText
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.mongo import is_sudo, get_user_smtps, get_smtp_by_username
from aizen import app
from config import LOG_CHANNEL

SENDMMAIL_STATE = {}

@app.on_callback_query(filters.regex(r"mmail_select:(.+)"))
async def mmail_select_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in SENDMMAIL_STATE:
        return
    selected = callback_query.data.split(":")[1]
    state = SENDMMAIL_STATE[user_id]
    if selected in state["smtps"]:
        state["smtps"].remove(selected)
    else:
        state["smtps"].append(selected)

    buttons = [
        [InlineKeyboardButton(f"{smtp['username']} {'✅' if smtp['username'] in state['smtps'] else ''}", callback_data=f"mmail_select:{smtp['username']}")]
        for smtp in get_smtps(user_id)
    ]
    buttons.append([
        InlineKeyboardButton("✅ Confirm", callback_data="mmail_confirm"),
        InlineKeyboardButton("❌ Abort", callback_data="mmail_abort"),
    ])
    await callback_query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("mmail_confirm"))
async def mmail_confirm_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = SENDMMAIL_STATE[user_id]
    if not state["smtps"]:
        return await callback_query.answer("Select at least one SMTP.")
    state["step"] = "awaiting_target"
    await callback_query.message.edit("Send the recipient's email address:")

@app.on_callback_query(filters.regex("mmail_abort"))
async def mmail_abort_handler(client: Client, callback_query: CallbackQuery):
    SENDMMAIL_STATE.pop(callback_query.from_user.id, None)
    await callback_query.message.edit("Aborted mass mail process.")

@app.on_message(filters.command("sendmmail") & filters.private)
async def sendmmail_entry(client: Client, message: Message):
    user_id = message.from_user.id
    if not is_sudo(user_id):
        return await message.reply("Only sudo users can use this command.")
    smtps = get_smtps(user_id)
    if not smtps:
        return await message.reply("No SMTPs found.")
    buttons = [
        [InlineKeyboardButton(smtp["username"], callback_data=f"mmail_select:{smtp['username']}")]
        for smtp in smtps
    ]
    buttons.append([
        InlineKeyboardButton("✅ Confirm", callback_data="mmail_confirm"),
        InlineKeyboardButton("❌ Abort", callback_data="mmail_abort"),
    ])
    SENDMMAIL_STATE[user_id] = {"step": "selecting_smtps", "smtps": []}
    await message.reply("Select SMTPs for sending:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_message(filters.private & filters.text)
async def mmail_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in SENDMMAIL_STATE:
        return
    state = SENDMMAIL_STATE[user_id]
    step = state.get("step")

    if step == "awaiting_target":
        state["to_email"] = message.text
        state["step"] = "awaiting_subject"
        return await message.reply("Send the subject:")

    elif step == "awaiting_subject":
        state["subject"] = message.text
        state["step"] = "awaiting_body"
        return await message.reply("Send the body of email:")

    elif step == "awaiting_body":
        state["body"] = message.text
        state["step"] = "awaiting_count"
        return await message.reply("How many mails to send per SMTP? (2–30)")

    elif step == "awaiting_count":
        try:
            count = int(message.text)
            if not (2 <= count <= 30):
                raise ValueError
            state["count"] = count
            state["step"] = "awaiting_delay"
            return await message.reply("Enter delay in seconds between mails (30–600):")
        except:
            return await message.reply("Invalid number. Try again (2–30).")

    elif step == "awaiting_delay":
        try:
            delay = int(message.text)
            if not (30 <= delay <= 600):
                raise ValueError
            state["delay"] = delay
        except:
            return await message.reply("Invalid delay. Try again (30–600).")

        subject = state["subject"]
        body = state["body"]
        count = state["count"]
        delay = state["delay"]
        to_email = state["to_email"]

        smtp_list = state["smtps"]
        total = len(smtp_list)
        progress = [0] * total
        msg = await message.reply("Mass mail from multiple SMTPs started...\n")

        for i, smtp_username in enumerate(smtp_list):
            smtp_data = get_smtp_by_username(user_id, smtp_username)
            smtp_host = smtp_data["host"]
            smtp_port = smtp_data["port"]
            smtp_user = smtp_data["username"]
            smtp_pass = smtp_data["password"]

            for j in range(count):
                try:
                    mime = MIMEText(body, "plain")
                    mime["From"] = smtp_user
                    mime["To"] = to_email
                    mime["Subject"] = subject

                    with smtplib.SMTP(smtp_host, smtp_port) as server:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                        server.sendmail(smtp_user, to_email, mime.as_string())

                    progress[i] += 1
                    display = "\n".join(
                        [f"{smtp}: {progress[x]}/{count}" for x, smtp in enumerate(smtp_list)]
                    )
                    await msg.edit(f"📤 Mass Mailing Progress:\n{display}")
                    await asyncio.sleep(delay)
                except Exception as e:
                    await msg.edit(f"Error sending from {smtp_user}: {e}")
                    break

        await msg.edit("✅ All mails sent successfully.")
        log_text = (
            f"#MultiMailLog\nUser: {message.from_user.mention} (`{user_id}`)\n"
            f"SMTPs used: {total}\nTo: `{to_email}`\nSubject: `{subject}`\n\nBody:\n{body}"
        )
        await client.send_message(LOG_CHANNEL, log_text)
        SENDMMAIL_STATE.pop(user_id, None)
