from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from database.mongo import add_sudo, remove_sudo, get_sudoers

@app.on_message(filters.command("addsudo") & filters.private)
async def add_sudo(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("Only the bot owner can add sudo users.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("Usage: /addsudo <user_id>")
    
    user_id = int(message.command[1])
    added = add_sudo_user(user_id)
    if added:
        await message.reply(f"User {user_id} added as sudo.")
    else:
        await message.reply("User is already a sudo user.")

@app.on_message(filters.command("delsudo") & filters.private)
async def del_sudo(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("Only the bot owner can remove sudo users.")
    
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("Usage: /delsudo <user_id>")
    
    user_id = int(message.command[1])
    removed = remove_sudo_user(user_id)
    if removed:
        await message.reply(f"User {user_id} removed from sudo.")
    else:
        await message.reply("User was not a sudo user.")
