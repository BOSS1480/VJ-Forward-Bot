import asyncio 
from database import Db, db
from script import Script
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT, parse_buttons
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .db import connect_user_db

CLIENT = CLIENT()


@Client.on_message(filters.command('settings'))
async def settings(client, message):
   await message.reply_text(
     "<b>כאן לוח ההגדרות ⚙️\n\nשנה את ההגדרות שלך כרצונך 👇</b>",
     reply_markup=main_buttons()
     )


@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
  user_id = query.from_user.id
  i, type = query.data.split("#")
  buttons = [[InlineKeyboardButton('חזרה', callback_data="settings#main")]]
  if type=="main":
     await query.message.edit_text(
       "<b>כאן לוח ההגדרות ⚙️\n\nשנה את ההגדרות שלך כרצונך 👇</b>",
       reply_markup=main_buttons())
  elif type=="extra":
       await query.message.edit_text(
         "<b>הנה פאנל הגדרות נוסף ⚙\n\nשנה את ההגדרות שלך כרצונך 👇</b>",
         reply_markup=extra_buttons())
  elif type=="bots":
     buttons = [] 
     _bot = await db.get_bot(user_id)
     usr_bot = await db.get_userbot(user_id)
     if _bot is not None:
        buttons.append([InlineKeyboardButton(_bot['name'],
                         callback_data=f"settings#editbot")])
     else:
        buttons.append([InlineKeyboardButton('✚ הוסף בוט ✚', 
                         callback_data="settings#addbot")])
     if usr_bot is not None:
        buttons.append([InlineKeyboardButton(usr_bot['name'],
                         callback_data=f"settings#edituserbot")])
     else:
        buttons.append([InlineKeyboardButton('✚ הוסף יוזרבוט ✚', 
                         callback_data="settings#adduserbot")])
     buttons.append([InlineKeyboardButton('חזרה', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>הבוטים שלי:</b></u>\n\n<b>אתה יכול לנהל את הבוטים שלך כאן</b>",
       reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addbot":
     await query.message.delete()
     bot = await CLIENT.add_bot(bot, query)
     if bot != True: return
     await query.message.reply_text(
        "<b>אסימון הבוט נוסף בהצלחה ל-db</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="adduserbot":
     await query.message.delete()
     user = await CLIENT.add_session(bot, query)
     if user != True: return
     await query.message.reply_text(
        "<b>ההפעלה נוספה בהצלחה ל-db</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="channels":
     buttons = []
     channels = await db.get_user_channels(user_id)
     for channel in channels:
        buttons.append([InlineKeyboardButton(f"{channel['title']}",
                         callback_data=f"settings#editchannels_{channel['chat_id']}")])
     buttons.append([InlineKeyboardButton('✚ הוסף ערוץ ✚', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('חזרה', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>הערוצים שלי:</b></u>\n\n<b>אתה יכול לנהל את הצ'אטים היעד שלך כאן</b>",
       reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addchannel":  
     await query.message.delete()
     chat_ids = await bot.ask(chat_id=query.from_user.id, text="<b>❪ הגדר צ'אט יעד ❫\n\nהעבר הודעה מצ'אט היעד שלך\n/cancel - לבטל את התהליך הזה</b>")
     if chat_ids.text=="/cancel":
        return await chat_ids.reply_text(
                  "<b>התהליך בוטל</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
     elif not chat_ids.forward_date:
        return await chat_ids.reply("**זו לא הודעה עם תג הועבר**")
     else:
        chat_id = chat_ids.forward_from_chat.id
        title = chat_ids.forward_from_chat.title
        username = chat_ids.forward_from_chat.username
        username = "@" + username if username else "private"
     chat = await db.add_channel(user_id, chat_id, title, username)
     await query.message.reply_text(
        "<b>Successfully updated</b>" if chat else "<b>הערוץ הזה כבר נוסף!</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="editbot": 
     bot = await db.get_bot(user_id)
     TEXT = Script.BOT_DETAILS if bot['is_bot'] else Script.USER_DETAILS
     buttons = [[InlineKeyboardButton('❌ מחק ❌', callback_data=f"settings#removebot")
               ],
               [InlineKeyboardButton('חזרה', callback_data="settings#bots")]]
     await query.message.edit_text(
        TEXT.format(bot['name'], bot['id'], bot['username']),
        reply_markup=InlineKeyboardMarkup(buttons))
     
  elif type=="edituserbot": 
     bot = await db.get_userbot(user_id)
     TEXT = Script.USER_DETAILS
     buttons = [[InlineKeyboardButton('❌ מחק ❌', callback_data=f"settings#removeuserbot")
               ],
               [InlineKeyboardButton('חזרה', callback_data="settings#bots")]]
     await query.message.edit_text(
        TEXT.format(bot['name'], bot['id'], bot['username']),
        reply_markup=InlineKeyboardMarkup(buttons))
     
  elif type=="removebot":
     await db.remove_bot(user_id)
     await query.message.edit_text(
        "<b>עודכן בהצלחה!</b>",
        reply_markup=InlineKeyboardMarkup(buttons))
     
  elif type=="removeuserbot":
     await db.remove_userbot(user_id)
     await query.message.edit_text(
        "<b>עודכן בהצלחה!</b>",
        reply_markup=InlineKeyboardMarkup(buttons))
     
  elif type.startswith("editchannels"): 
     chat_id = type.split('_')[1]
     chat = await db.get_channel_details(user_id, chat_id)
     buttons = [[InlineKeyboardButton('❌ מחק ❌', callback_data=f"settings#removechannel_{chat_id}")
               ],
               [InlineKeyboardButton('חזרה', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 פרטי הערוץ</b></u>\n\n<b>- כותרת:</b> <code>{chat['title']}</code>\n<b>- מזהה ערוץ: </b> <code>{chat['chat_id']}</code>\n<b>- יוזר:</b> {chat['username']}",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type.startswith("removechannel"):
     chat_id = type.split('_')[1]
     await db.remove_channel(user_id, chat_id)
     await query.message.edit_text(
        "<b>עודכן בהצלחה!</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="caption":
     buttons = []
     data = await get_configs(user_id)
     caption = data['caption']
     if caption is None:
        buttons.append([InlineKeyboardButton('✚ הוסף כיתוב ✚', 
                      callback_data="settings#addcaption")])
     else:
        buttons.append([InlineKeyboardButton('See Caption', 
                      callback_data="settings#seecaption")])
        buttons[-1].append(InlineKeyboardButton('🗑️ מחק כיתוב', 
                      callback_data="settings#deletecaption"))
     buttons.append([InlineKeyboardButton('חזרה', 
                      callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>כתובית מותאמת אישית</b></u>\n\n<b>אתה יכול להגדיר כיתוב מותאם אישית לסרטונים ומסמכים.  בדרך כלל השתמש בכיתוב ברירת המחדל שלו</b>\n\n<b><u>מילויים זמינים:</b></u>\n- <code>{filename}</code> : שם קובץ\n- <code>{size}</code> : גודל קובץ\n- <code>{caption}</code> : כיתוב ברירת מחדל",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="seecaption":   
     data = await get_configs(user_id)
     buttons = [[InlineKeyboardButton('🖋️ ערוך כיתוב', 
                  callback_data="settings#addcaption")
               ],[
               InlineKeyboardButton('חזרה', 
                 callback_data="settings#caption")]]
     await query.message.edit_text(
        f"<b><u>הכיתוב המותאם אישית שלך:</b></u>\n\n<code>{data['caption']}</code>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="deletecaption":
     await update_configs(user_id, 'caption', None)
     await query.message.edit_text(
        "<b>עודכן בהצלחה</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addcaption":
     await query.message.delete()
     caption = await bot.ask(query.message.chat.id, "שלח את הכיתוב המותאם אישית שלך\n/cancel - <code>לבטל את התהליך הזה</code>")
     if caption.text=="/cancel":
        return await caption.reply_text(
                  "<b>התהליך בוטל!</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
     try:
         caption.text.format(filename='', size='', caption='')
     except KeyError as e:
         return await caption.reply_text(
            f"<b>מילוי שגוי {e} בשימוש בכיתוב שלך.  לשנות את זה</b>",
            reply_markup=InlineKeyboardMarkup(buttons))
     await update_configs(user_id, 'caption', caption.text)
     await caption.reply_text(
        "<b>עודכן בהצלחה</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="button":
     buttons = []
     button = (await get_configs(user_id))['button']
     if button is None:
        buttons.append([InlineKeyboardButton('✚ הוסף כפתור ✚', 
                      callback_data="settings#addbutton")])
     else:
        buttons.append([InlineKeyboardButton('👀 צפה בכפתור', 
                      callback_data="settings#seebutton")])
        buttons[-1].append(InlineKeyboardButton('🗑️ מחק כפתור', 
                      callback_data="settings#deletebutton"))
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>כפתור מותאם אישית</b></u>\n\n<b>אתה יכול להגדיר כפתור מוטבע להודעות.</b>\n\n<b><u>פורמט:</b></u>\n`[Forward bot][buttonurl:https://t.me/bot_sratim_sdarot]`\n",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addbutton":
     await query.message.delete()
     ask = await bot.ask(user_id, text="**שלח את הכפתור המותאם אישית שלך.\n\nפורמט:**\n`[forward bot][buttonurl:https://t.me/bot_sratim_sdarot]`\n")
     button = parse_buttons(ask.text.html)
     if not button:
        return await ask.reply("**כפתור לא חוקי!**")
     await update_configs(user_id, 'button', ask.text.html)
     await ask.reply("**הכפתור נוסף בהצלחה!**",
             reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="seebutton":
      button = (await get_configs(user_id))['button']
      button = parse_buttons(button, markup=False)
      button.append([InlineKeyboardButton("חזרה", "settings#button")])
      await query.message.edit_text(
         "**הכפתורים שלך**",
         reply_markup=InlineKeyboardMarkup(button))

  elif type=="deletebutton":
     await update_configs(user_id, 'button', None)
     await query.message.edit_text(
        "**Successfully button deleted**",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="database":
     buttons = []
     db_uri = (await get_configs(user_id))['db_uri']
     if db_uri is None:
        buttons.append([InlineKeyboardButton('✚ הוסף קישור mongo', 
                      callback_data="settings#addurl")])
     else:
        buttons.append([InlineKeyboardButton('👀 צפה בקישור', 
                      callback_data="settings#seeurl")])
        buttons[-1].append(InlineKeyboardButton('❌ מחק קישור', 
                      callback_data="settings#deleteurl"))
     buttons.append([InlineKeyboardButton('חזרה', 
                      callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>מסד נתונים</u>\n\nמסד נתונים נדרש לאחסון ההודעות הכפולות שלך לצמיתות. מדיה כפולה אחרת המאוחסנת בצורה חכמה עשויה להיעלם לאחר הפעלה מחדש של הבוט.</b>",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="addurl":
     await query.message.delete()
     uri = await bot.ask(user_id, "<b>אנא שלח את כתובת האתר שלך ל-mongodb.</b>\n\n<i>קבל את כתובת האתר שלך מ- [MangoDb](https://mongodb.com)</i>", disable_web_page_preview=True)
     if uri.text=="/cancel":
        return await uri.reply_text(
                  "<b>התהליך בוטל !</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
     if not uri.text.startswith("mongodb+srv://") and not uri.text.endswith("majority"):
        return await uri.reply("<b>כתובת אתר לא חוקית של Mongodb</b>",
                   reply_markup=InlineKeyboardMarkup(buttons))
     connect, udb = await connect_user_db(user_id, uri.text, "test")
     if connect:
        await udb.drop_all()
        await udb.close()
     else:
        return await uri.reply("<b>כתובת אתר לא חוקית של Mongodb לא יכולה להתחבר לכתובת האתר הזו</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
     await update_configs(user_id, 'db_uri', uri.text)
     await uri.reply("**כתובת האתר של מסד הנתונים נוספה בהצלחה**",
             reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="seeurl":
     db_uri = (await get_configs(user_id))['db_uri']
     await query.answer(f"DATABASE URL: {db_uri}", show_alert=True)

  elif type=="deleteurl":
     await update_configs(user_id, 'db_uri', None)
     await query.message.edit_text(
        "**כתובת האתר של מסד הנתונים שלך נמחקה בהצלחה**",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type=="filters":
     await query.message.edit_text(
        "<b><u>💠 מסננים מותאמים אישית 💠</b></u>\n\n**הגדר את סוג ההודעות שברצונך להעביר**",
        reply_markup=await filters_buttons(user_id))

  elif type=="nextfilters":
     await query.edit_message_reply_markup( 
        reply_markup=await next_filters_buttons(user_id))

  elif type.startswith("updatefilter"):
     i, key, value = type.split('-')
     if value=="True":
        await update_configs(user_id, key, False)
     else:
        await update_configs(user_id, key, True)
     if key in ['poll', 'protect', 'voice', 'animation', 'sticker', 'duplicate']:
        return await query.edit_message_reply_markup(
           reply_markup=await next_filters_buttons(user_id)) 
     await query.edit_message_reply_markup(
        reply_markup=await filters_buttons(user_id))

  elif type.startswith("file_size"):
    settings = await get_configs(user_id)
    size = settings.get('min_size', 0)
    await query.message.edit_text(
       f'<b><u>מגבלת גודל</b></u><b>\n\nאתה יכול להגדיר את מגבלת הגודל המינימלית לקובץ קדימה\n\nקבצים עם יותר מ- `{size} MB` יעביר</b>',
       reply_markup=size_button(size))
     
  elif type.startswith("maxfile_size"):
    settings = await get_configs(user_id)
    size = settings.get('max_size', 0)
    await query.message.edit_text(
       f'<b><u>מגבלת גודל מקסימלית</b></u><b>\n\nאתה יכול להגדיר את מגבלת הגודל המקסימלית לקובץ קדימה\n\nקבצים עם פחות מ `{size} MB` יעביר</b>',
       reply_markup=maxsize_button(size))

  elif type.startswith("update_size"):
    size = int(query.data.split('-')[1])
    if 0 < size > 4000:
      return await query.answer("size limit exceeded", show_alert=True)
    await update_configs(user_id, 'min_size', size)
    i, limit = size_limit((await get_configs(user_id))['size_limit'])
    await query.message.edit_text(
       f'<b><u>מגבלת גודל</b></u><b>\n\nאתה יכול להגדיר את מגבלת הגודל המינימלית לקובץ קדימה\n\nקבצים עם יותר מ- `{size} MB` יעביר</b>',
       reply_markup=size_button(size))
     
  elif type.startswith("maxupdate_size"):
    size = int(query.data.split('-')[1])
    if 0 < size > 4000:
      return await query.answer("size limit exceeded", show_alert=True)
    await update_configs(user_id, 'max_size', size)
    i, limit = size_limit((await get_configs(user_id))['size_limit'])
    await query.message.edit_text(
       f'<b><u>מגבלת גודל מקסימלית</b></u><b>\n\nאתה יכול להגדיר את מגבלת הגודל המקסימלית לקובץ קדימה\n\nקבצים עם פחות מ `{size} MB` יעביר</b>',
       reply_markup=maxsize_button(size))

  elif type.startswith('update_limit'):
    i, limit, size = type.split('-')
    limit, sts = size_limit(limit)
    await update_configs(user_id, 'size_limit', limit) 
    await query.message.edit_text(
       f'<b><u>מגבלת גודל</b></u><b>\n\nאתה יכול להגדיר את מגבלת גודל הקובץ להעברה\n\nסטטוס: קבצים עם {sts} `{size} MB` יעביר</b>',
       reply_markup=size_button(int(size)))

  elif type == "add_extension":
    await query.message.delete() 
    ext = await bot.ask(user_id, text="**אנא שלח את ההרחבות שלך (מופרדים ברווח)**")
    if ext.text == '/cancel':
       return await ext.reply_text(
                  "<b>התהליך בוטל!</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
    extensions = ext.text.split(" ")
    extension = (await get_configs(user_id))['extension']
    if extension:
        for extn in extensions:
            extension.append(extn)
    else:
        extension = extensions
    await update_configs(user_id, 'extension', extension)
    buttons = []
    buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#get_extension")])
    await ext.reply_text(
        f"**successfully updated**",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type == "get_extension":
    extensions = (await get_configs(user_id))['extension']
    btn = []
    text = ""
    if extensions:
       text += "**🕹 הרחבות**"
       for ext in extensions:
          text += f"\n<code>-{ext}</code>"
    else:
       text += "** No Extensions Here**"
    btn.append([InlineKeyboardButton('✚ הוסף', 'settings#add_extension')])
    btn.append([InlineKeyboardButton('מחק הכל', 'settings#rmve_all_extension')])
    btn.append([InlineKeyboardButton('back', 'settings#extra')])
    await query.message.edit_text(
        text=f"<b><u>הרחבות</u></b>\n\n**קבצים עם כינויים אלה לא יועברו**\n\n{text}",
        reply_markup=InlineKeyboardMarkup(btn))

  elif type == "rmve_all_extension":
    await update_configs(user_id, 'extension', None)
    buttons = []
    buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#get_extension")])
    await query.message.edit_text(text="**נמחק בהצלחה!**",
                                   reply_markup=InlineKeyboardMarkup(buttons))
  elif type == "add_keyword":
    await query.message.delete()
    ask = await bot.ask(user_id, text="**נא לשלוח את מילות המפתח (מופרדות ברווח כמו:- 1080p Hdrip)**")
    if ask.text == '/cancel':
       return await ask.reply_text(
                  "<b>התהליך בוטל!</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
    keywords = ask.text.split(" ")
    keyword = (await get_configs(user_id))['keywords']
    if keyword:
        for word in keywords:
            keyword.append(word)
    else:
        keyword = keywords
    await update_configs(user_id, 'keywords', keyword)
    buttons = []
    buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#get_keyword")])
    await ask.reply_text(
        f"**עודכן בהצלחה!**",
        reply_markup=InlineKeyboardMarkup(buttons))

  elif type == "get_keyword":
    keywords = (await get_configs(user_id))['keywords']
    btn = []
    text = ""
    if keywords:
       text += "**🔖 מילות מפתח:**"
       for key in keywords:
          text += f"\n<code>-{key}</code>"
    else:
       text += "**לא הוספת מילות מפתח**"
    btn.append([InlineKeyboardButton('✚ הוסף', 'settings#add_keyword')])
    btn.append([InlineKeyboardButton('מחק הכל', 'settings#rmve_all_keyword')])
    btn.append([InlineKeyboardButton('Back', 'settings#extra')])
    await query.message.edit_text(
        text=f"<b><u>מילות מפתח</u></b>\n\n**קבצים עם מילות מפתח אלו בשם הקובץ יעברו רק**\n\n{text}",
        reply_markup=InlineKeyboardMarkup(btn))

  elif type == "rmve_all_keyword":
    await update_configs(user_id, 'keywords', None)
    buttons = []
    buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#get_keyword")])
    await query.message.edit_text(text="**נמחק בהצלחה את כל מילות המפתח**",
                                   reply_markup=InlineKeyboardMarkup(buttons))
  elif type.startswith("alert"):
    alert = type.split('_')[1]
    await query.answer(alert, show_alert=True)


def extra_buttons():
   buttons = [[
       InlineKeyboardButton('💾 מגבלת גודל מינימלית',
                    callback_data=f'settings#file_size')
       ],[
       InlineKeyboardButton('💾 מגבלת גודל מקסימלית',
                    callback_data=f'settings#maxfile_size ')
       ],[
       InlineKeyboardButton('🚥 מילות מפתח',
                    callback_data=f'settings#get_keyword'),
       InlineKeyboardButton('🕹 הרחבות',
                    callback_data=f'settings#get_extension')
       ],[
       InlineKeyboardButton('⫷ Bᴀᴄᴋ',
                    callback_data=f'settings#main')
       ]]
   return InlineKeyboardMarkup(buttons)


def main_buttons():
  buttons = [[
       InlineKeyboardButton('🤖 בוטים',
                    callback_data=f'settings#bots'),
       InlineKeyboardButton('🏷 ערוצים',
                    callback_data=f'settings#channels')
       ],[
       InlineKeyboardButton('🖋️ כותרת',
                    callback_data=f'settings#caption'),
       InlineKeyboardButton('⏹ כפתורים',
                    callback_data=f'settings#button')
       ],[
       InlineKeyboardButton('🕵‍♀ מסננים 🕵‍♀',
                    callback_data=f'settings#filters'),
       InlineKeyboardButton('מסד נתונים 🗃️',
                    callback_data=f'settings#database')
       ],[
       InlineKeyboardButton('הגדרות נוספות 🧪',
                    callback_data=f'settings#extra')
       ],[
       InlineKeyboardButton('⫷ Bᴀᴄᴋ',
                    callback_data=f'help')
       ]]
  return InlineKeyboardMarkup(buttons)


def size_limit(limit):
   if str(limit) == "None":
      return None, ""
   elif str(limit) == "True":
      return True, "more than"
   else:
      return False, "less than"


def extract_btn(datas):
    i = 0
    btn = []
    if datas:
       for data in datas:
         if i >= 3:
            i = 0
         if i == 0:
            btn.append([InlineKeyboardButton(data, f'settings#alert_{data}')])
            i += 1
            continue
         elif i > 0:
            btn[-1].append(InlineKeyboardButton(data, f'settings#alert_{data}'))
            i += 1
    return btn 


def maxsize_button(size):
  buttons = [[
       InlineKeyboardButton('💾 מגבלת גודל מקסימלית',
                    callback_data=f'noth')
       ],[
       InlineKeyboardButton('+1',
                    callback_data=f'settings#maxupdate_size-{size + 1}'),
       InlineKeyboardButton('-1',
                    callback_data=f'settings#maxupdate_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#maxupdate_size-{size + 5}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#maxupdate_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10',
                    callback_data=f'settings#maxupdate_size-{size + 10}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#maxupdate_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50',
                    callback_data=f'settings#maxupdate_size-{size + 50}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#maxupdate_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100',
                    callback_data=f'settings#maxupdate_size-{size + 100}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#maxupdate_size_-{size - 100}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#extra")
     ]]
  return InlineKeyboardMarkup(buttons)


def size_button(size):
  buttons = [[
       InlineKeyboardButton('💾 מגבלת גודל מינימלית',
                    callback_data=f'noth')
       ],[
       InlineKeyboardButton('+1',
                    callback_data=f'settings#update_size-{size + 1}'),
       InlineKeyboardButton('-1',
                    callback_data=f'settings#update_size_-{size - 1}')
       ],[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#update_size-{size + 5}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#update_size_-{size - 5}')
       ],[
       InlineKeyboardButton('+10',
                    callback_data=f'settings#update_size-{size + 10}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#update_size_-{size - 10}')
       ],[
       InlineKeyboardButton('+50',
                    callback_data=f'settings#update_size-{size + 50}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#update_size_-{size - 50}')
       ],[
       InlineKeyboardButton('+100',
                    callback_data=f'settings#update_size-{size + 100}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#update_size_-{size - 100}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#extra")
     ]]
  return InlineKeyboardMarkup(buttons)


async def filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       InlineKeyboardButton('🏷️ תג הועבר',
                    callback_data=f'settings_#updatefilter-forward_tag-{filter["forward_tag"]}'),
       InlineKeyboardButton('✅' if filter['forward_tag'] else '❌',
                    callback_data=f'settings#updatefilter-forward_tag-{filter["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ טקסט',
                    callback_data=f'settings_#updatefilter-text-{filters["text"]}'),
       InlineKeyboardButton('✅' if filters['text'] else '❌',
                    callback_data=f'settings#updatefilter-text-{filters["text"]}')
       ],[
       InlineKeyboardButton('📁 קבצים',
                    callback_data=f'settings_#updatefilter-document-{filters["document"]}'),
       InlineKeyboardButton('✅' if filters['document'] else '❌',
                    callback_data=f'settings#updatefilter-document-{filters["document"]}')
       ],[
       InlineKeyboardButton('🎞️ וידאו',
                    callback_data=f'settings_#updatefilter-video-{filters["video"]}'),
       InlineKeyboardButton('✅' if filters['video'] else '❌',
                    callback_data=f'settings#updatefilter-video-{filters["video"]}')
       ],[
       InlineKeyboardButton('📷 תמונות',
                    callback_data=f'settings_#updatefilter-photo-{filters["photo"]}'),
       InlineKeyboardButton('✅' if filters['photo'] else '❌',
                    callback_data=f'settings#updatefilter-photo-{filters["photo"]}')
       ],[
       InlineKeyboardButton('🎧 אודיו',
                    callback_data=f'settings_#updatefilter-audio-{filters["audio"]}'),
       InlineKeyboardButton('✅' if filters['audio'] else '❌',
                    callback_data=f'settings#updatefilter-audio-{filters["audio"]}')
       ],[
       InlineKeyboardButton('⫷ back',
                    callback_data="settings#main"),
       InlineKeyboardButton('next ⫸',
                    callback_data="settings#nextfilters")
       ]]
  return InlineKeyboardMarkup(buttons) 


async def next_filters_buttons(user_id):
  filter = await get_configs(user_id)
  filters = filter['filters']
  buttons = [[
       ],[
       InlineKeyboardButton('🎤 קוליות',
                    callback_data=f'settings_#updatefilter-voice-{filters["voice"]}'),
       InlineKeyboardButton('✅' if filters['voice'] else '❌',
                    callback_data=f'settings#updatefilter-voice-{filters["voice"]}')
       ],[
       InlineKeyboardButton('🎭 אנימציות',
                    callback_data=f'settings_#updatefilter-animation-{filters["animation"]}'),
       InlineKeyboardButton('✅' if filters['animation'] else '❌',
                    callback_data=f'settings#updatefilter-animation-{filters["animation"]}')
       ],[
       InlineKeyboardButton('🃏 סטיקרים',
                    callback_data=f'settings_#updatefilter-sticker-{filters["sticker"]}'),
       InlineKeyboardButton('✅' if filters['sticker'] else '❌',
                    callback_data=f'settings#updatefilter-sticker-{filters["sticker"]}')
       ],[
       InlineKeyboardButton('▶️ דלג על כפילות',
                    callback_data=f'settings_#updatefilter-duplicate-{filter["duplicate"]}'),
       InlineKeyboardButton('✅' if filter['duplicate'] else '❌',
                    callback_data=f'settings#updatefilter-duplicate-{filter["duplicate"]}')
       ],[
       InlineKeyboardButton('📊 סקרים',
                    callback_data=f'settings_#updatefilter-poll-{filters["poll"]}'),
       InlineKeyboardButton('✅' if filters['poll'] else '❌',
                    callback_data=f'settings#updatefilter-poll-{filters["poll"]}')
       ],[
       InlineKeyboardButton('🔒 הודעות נעולות',
                    callback_data=f'settings_#updatefilter-protect-{filter["protect"]}'),
       InlineKeyboardButton('✅' if filter['protect'] else '❌',
                    callback_data=f'settings#updatefilter-protect-{filter["protect"]}')
       ],[
       InlineKeyboardButton('⫷ back', 
                    callback_data="settings#filters"),
       InlineKeyboardButton('End ⫸',
                    callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 
