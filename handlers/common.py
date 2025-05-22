from pyrogram.types import InlineKeyboardButton

def make_pagination_buttons(items, callback_prefix, per_row=2):
    buttons = []
    row = []
    for index, item in enumerate(items):
        row.append(InlineKeyboardButton(item, callback_data=f"{callback_prefix}:{item}"))
        if len(row) == per_row:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return buttons
