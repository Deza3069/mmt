# handlers/smtp.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongo import is_sudo, add_smtp, remove_smtp, get_smtps

@Client.on_message(filters.command("addsmtp") & filters.private)
async def add_smtp_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if not is_sudo(user_id):
        return await message.reply("Only sudo users can add SMTP accounts.")

    try:
        parts = message.text.split()
        if len(parts) < 5:
            return await message.reply("Usage:\n/addsmtp <host> <port> <username> <password>")
        
        host, port, username, password = parts[1], int(parts[2]), parts[3], parts[4]
        result = add_smtp(user_id, host, port, username, password)
        if result:
            await message.reply("SMTP added successfully.")
        else:
            await message.reply("You can only add up to 5 SMTP accounts.")
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.command("delsmtp") & filters.private)
async def remove_smtp_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if not is_sudo(user_id):
        return await message.reply("Only sudo users can remove SMTP accounts.")
    
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("Usage: /delsmtp <username>")
    
    username = parts[1]
    removed = remove_smtp(user_id, username)
    if removed:
        await message.reply(f"SMTP with username '{username}' removed.")
    else:
        await message.reply("SMTP not found.")
