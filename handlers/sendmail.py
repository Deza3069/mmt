import asyncio
import smtplib
from email.mime.text import MIMEText
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from database.mongo import is_sudo, get_smtps, get_smtp_by_username
from config import LOG_CHANNEL

SENDMAIL_STATE = {}

@Client.on_message(filters.command("sendmail") & filters.private)
async def sendmail_entry(client: Client, message: Message):
    user_id = message.from_user.id
    if not is_sudo(user_id):
        return await message.reply("Only sudo users can use this command.")
    smtps = get_smtps(user_id)
    if not smtps:
        return await message.reply("You have no SMTPs. Use /addsmtp to add.")

    buttons = [
        [InlineKeyboardButton(smtp["username"], callback_data=f"sendmail_smtp:{smtp['username']}")]
        for smtp in smtps
    ]
    await message.reply("Choose an SMTP to send mail from:", reply_markup=InlineKeyboardMarkup(buttons))
    SENDMAIL_STATE[user_id] = {"step": "awaiting_smtp"}

@Client.on_callback_query(filters.regex(r"sendmail_smtp:(.+)"))
async def sendmail_choose_smtp(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    smtp_username = callback_query.data.split(":")[1]
    SENDMAIL_STATE[user_id] = {"smtp_username": smtp_username, "step": "awaiting_target"}
    await callback_query.message.edit("Send the recipient's email address:")

@Client.on_message(filters.private & filters.text)
async def sendmail_steps(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in SENDMAIL_STATE:
        return

    state = SENDMAIL_STATE[user_id]
    step = state.get("step")

    if step == "awaiting_target":
        state["to_email"] = message.text
        state["step"] = "awaiting_subject"
        return await message.reply("Send the subject of the email:")

    elif step == "awaiting_subject":
        state["subject"] = message.text
        state["step"] = "awaiting_body"
        return await message.reply("Send the body of the email:")

    elif step == "awaiting_body":
        state["body"] = message.text
        state["step"] = "awaiting_count"
        return await message.reply("How many times to send the email? (2–50)")

    elif step == "awaiting_count":
        try:
            count = int(message.text)
            if not (2 <= count <= 50):
                raise ValueError
            state["count"] = count
            state["step"] = "awaiting_delay"
            return await message.reply("Enter delay between emails (15–1500 seconds):")
        except:
            return await message.reply("Invalid input. Enter a number between 2 and 50.")

    elif step == "awaiting_delay":
        try:
            delay = int(message.text)
            if not (15 <= delay <= 1500):
                raise ValueError
            state["delay"] = delay
        except:
            return await message.reply("Invalid delay. Enter a number between 15 and 1500.")
        
        await message.reply("Mass Mailing has been started...\nSending progress will be shown here.")

        smtp_data = get_smtp_by_username(user_id, state["smtp_username"])
        smtp_host = smtp_data["host"]
        smtp_port = smtp_data["port"]
        smtp_user = smtp_data["username"]
        smtp_pass = smtp_data["password"]
        to_email = state["to_email"]
        subject = state["subject"]
        body = state["body"]
        count = state["count"]
        delay = state["delay"]

        log_text = (
            f"#MassMail\nUser: {message.from_user.mention} (`{user_id}`)\n"
            f"SMTPs in DB: {len(get_smtps(user_id))}\n"
            f"Process: Single SMTP\nFrom: `{smtp_user}`\nTo: `{to_email}`\n"
            f"Subject: `{subject}`\nBody:\n{body}\nTotal Mails: {count}"
        )
        await client.send_message(LOG_CHANNEL, log_text)

        sent = 0
        msg = await message.reply(f"Sending: {sent}/{count} via `{smtp_user}`")
        for _ in range(count):
            try:
                mime = MIMEText(body, "plain")
                mime["From"] = smtp_user
                mime["To"] = to_email
                mime["Subject"] = subject

                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, to_email, mime.as_string())

                sent += 1
                await msg.edit(f"Sending: {sent}/{count} via `{smtp_user}`")
                await asyncio.sleep(delay)
            except Exception as e:
                await msg.edit(f"Failed: {e}")
                break

        await msg.edit(f"✅ Completed sending {count} mails from `{smtp_user}`.")
        SENDMAIL_STATE.pop(user_id, None)
