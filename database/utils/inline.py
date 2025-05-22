from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def smtp_selection_markup(smtps):
    buttons = []
    for smtp in smtps:
        buttons.append([InlineKeyboardButton(text=smtp["smtp_id"], callback_data=f"selectsmtp:{smtp['smtp_id']}")])
    buttons.append([InlineKeyboardButton("Abort ❌", callback_data="abort_process")])
    return InlineKeyboardMarkup(buttons)

def multi_smtp_selector(smtps, selected_ids):
    buttons = []
    for smtp in smtps:
        tick = "✅" if smtp["smtp_id"] in selected_ids else ""
        text = f"{smtp['smtp_id']} {tick}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"togglemulti:{smtp['smtp_id']}")])
    if selected_ids:
        buttons.append([
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_multi"),
            InlineKeyboardButton("❌ Abort", callback_data="abort_process")
        ])
    else:
        buttons.append([InlineKeyboardButton("❌ Abort", callback_data="abort_process")])
    return InlineKeyboardMarkup(buttons)

def progress_message(selected_smtp, sent_count, total):
    return (
        f"📤 Sending Emails...\n\n"
        f"📧 From: `{selected_smtp}`\n"
        f"✅ Progress: `{sent_count}/{total}`"
    )

def final_log_message(user, smtp_used, target_email, subject, content, count):
    return (
        f"📨 **Mass Mailing Log**\n"
        f"👤 User: `{user}`\n"
        f"📧 SMTP: `{smtp_used}`\n"
        f"🎯 Target: `{target_email}`\n"
        f"📝 Subject: `{subject}`\n"
        f"✉️ Body:\n{content}\n"
        f"🔁 Times Sent: {count}"
    )
