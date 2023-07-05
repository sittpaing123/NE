import math
import re
import random
import asyncio
from bot import Bot
from pyrogram import enums, errors, filters, types

from ..config import Config
from ..database import a_filter
from ..database import configDB as config_db
from ..utils.botTools import check_fsub, format_buttons, get_size, parse_link
from ..utils.cache import Cache
from ..utils.imdbHelpers import get_poster, get_photo
from ..utils.logger import LOGGER

log = LOGGER(__name__)


@Bot.on_message(filters.group & filters.text & filters.incoming, group=-1)
async def auto_filter(bot: Bot, message: types.Message, text=True):
    #if not await check_fsub(bot, message):
        #return 
    #a = await ch1_give_filter(bot, message)
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_G1']:
        ka = await ch1_give_filter(bot, message)
        #return 
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_POST']:
        kt = await ch9_imdb(bot, message)
        return 
    settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
    if settings['CH_G2']:
        kb = await ch2_give_filter(bot, message)



async def ch1_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    
    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
    #if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F\u1000-\u109F()\d]).*)", message.text, re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER']
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search
    
    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
    else:
        imdb = {}
    cap = f"⚜️ 𝗤𝘂𝗲𝗿𝘆   : {search}\n🔰 𝗧𝗼𝘁𝗮𝗹    : {total_results}\n🙋🏻‍♂️ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n"

    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings
    if not settings.get("DOWNLOAD_BUTTON"):  # type: ignore
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
        if offset != "":
            req = message.from_user.id if message.from_user else 0
            btn.append(
                [
                    types.InlineKeyboardButton(
                        text=f"🗓 1/{math.ceil(int(total_results) / 5)}",
                        callback_data="pages",
                    ),
                    types.InlineKeyboardButton(
                        text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
                    ),
                ]
            )
        else:
            btn.append(
                [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    f"📥  {search}  📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    if imdb:
        cap += Config.TEMPLATE.format(  # type: ignore
            query=search,
            **imdb,
            **locals(),
        )
    
    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"

    cap2 = f"""────── • ADS • ──────
အပျင်းပြေ အရင်းကြေ ပလေးဖိုအတွက် RBY99 မှ 
မန်ဘာဝင်သူတွေအတွက် (3)ရက်တစ်ကြိမ် 
Free-10000 ပေးနေတဲ့အပြင် 
နေ့စဥ် 30%  အပိုဘောနပ်လည်းပေးနေသေးတယ်နော်💓

RBY99 မှာဆိုရင် 
-စလော့၊ငါးပစ်၊ဘင်းဂိုး ဂိမ်းများစွာနဲ့
-ရှမ်းကိုးမီး
-Sexy Girl လေးတွေရဲ့တိုက်ရိုက်လွှင့်အွန်လိုင်းကာစီနိုတွေအပြင်
-ဘောလုံးပါလောင်းနိုင်လို ဂိမ်းအကောင့်တစ်ခုဖွင့်ရုံနဲ့တစ်နေရာတည်းမှာစုံစုံလင်လင်ကစားလိုရနေပြီနော်
☎️ 09 756 395 343 
Viber Link 👉 https://jdb.link/rby99viber
Telegram Link 👉 https://jdb.link/RBY99
Website Link 👉 https://www.rby999.com/?pid=KP
────── • ◆ • ──────
"""
    cap3 = f"⚜️ 𝗤𝘂𝗲𝗿𝘆   : {search}\n🔰 𝗧𝗼𝘁𝗮𝗹    : {total_results}\n🙋🏻‍♂️𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+AGntow9MZbs2MjRh'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>"
    cap += f"</b><a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+AGntow9MZbs2MjRh'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>"

    ADS = [
        {"photo": "https://graph.org/file/0be0e71bc13476647bd19.jpg", "caption": f"""{cap2}

{cap3}"""},		
        {"photo": "https://graph.org/file/2b4db709aca0c0917d87b.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/331d22fcd77cec24bac2f.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/01d63b8c3a60f9187c22d.jpg", "caption": f"""{cap2}

{cap3}"""},	
        {"photo": "https://graph.org/file/05a6fa48bcb06f9cfd765.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/feef0f68141265de8b398.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/1492654d9fc001e13059f.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/57508fcf475eed5c4c53c.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/f3845e6030a4822864fd2.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/ae4b672952e107979fd7f.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/5bbaf63bdc2828d3d9d8a.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/332f2cd26287b2e4aeb08.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/4fae4f94aabaf7ab2fe0f.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/dbf5a27121cd32506267b.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/88c212c9ae989dffcb3b9.jpg", "caption": f"""{cap2}

{cap3}"""},
        {"photo": "https://graph.org/file/5293b1e858b610fa9e9f2.jpg", "caption": f"""{cap2}

{cap3}"""},
    ]


    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        if not settings["TEXT_LINK"]:
            try:
                await message.reply_photo(
                    photo=imdb.get("poster"),  # type: ignore
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                await message.reply_photo(
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
        else:
            try:
                file_send = await bot.send_photo(
                    chat_id=Config.FILE_GROUP,
                    photo=imdb.get("poster"),
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(ADS)
                photo_url = ad1["photo"]
                caption = ad1["caption"]
                await message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                            [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send.link)]
                        ]
                    ),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                file_send2 = await bot.send_photo(
                    chat_id=Config.FILE_GROUP,
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(ADS)
                photo_url = ad1["photo"]
                caption = ad1["caption"]
                await message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                            [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send2.link)]
                        ]
                    ),
                    quote=True,
                )
    else:
        if not settings["TEXT_LINK"]:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
        else:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            file_send3 = await bot.send_photo(
                chat_id=Config.FILE_GROUP,
                photo=random.choice(Config.PICS),
                caption=cap,
                reply_markup=types.InlineKeyboardMarkup(btn),
            )
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send3.link)]
                    ]
                ),
                quote=True
            )

async def ch2_give_filter(bot: Bot, message: types.Message):

    if message.text.startswith("/"):
        return  # ignore commands

    
    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
    #if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F\u1000-\u109F()\d]).*)", message.text, re.UNICODE):
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True, photo=settings['PHOTO_FILTER']
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search
    
    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
    else:
        imdb = {}
    cap = f"⚜️ 𝗤𝘂𝗲𝗿𝘆   : {search}\n🔰 𝗧𝗼𝘁𝗮𝗹    : {total_results}\n🙋🏻‍♂️ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n"

    Cache.SEARCH_DATA[key] = files, offset, total_results, imdb, settings
    if not settings.get("DOWNLOAD_BUTTON"):  # type: ignore
        btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore
        if offset != "":
            req = message.from_user.id if message.from_user else 0
            btn.append(
                [
                    types.InlineKeyboardButton(
                        text=f"🗓 1/{math.ceil(int(total_results) / 5)}",
                        callback_data="pages",
                    ),
                    types.InlineKeyboardButton(
                        text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}"
                    ),
                ]
            )
        else:
            btn.append(
                [types.InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
            )
    else:
        btn = [
            [
                types.InlineKeyboardButton(
                    f"📥  {search}  📥", url=f"https://t.me/{bot.me.username}?start=filter{key}"
                )
            ]
        ]

    if imdb:
        cap += Config.TEMPLATE.format(  # type: ignore
            query=search,
            **imdb,
            **locals(),
        )
    
    else:
        cap += f"𝗤𝘂𝗲𝗿𝘆   : {search}\n𝗧𝗼𝘁𝗮𝗹    : {total_results}\n𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>"

    cap2 = f"""────── • ADS • ──────
အပျင်းပြေ အရင်းကြေ ပလေးဖိုအတွက် RBY99 မှ 
မန်ဘာဝင်သူတွေအတွက် (3)ရက်တစ်ကြိမ် 
Free-10000 ပေးနေတဲ့အပြင် 
နေ့စဥ် 30%  အပိုဘောနပ်လည်းပေးနေသေးတယ်နော်💓

RBY99 မှာဆိုရင် 
-စလော့၊ငါးပစ်၊ဘင်းဂိုး ဂိမ်းများစွာနဲ့
-ရှမ်းကိုးမီး
-Sexy Girl လေးတွေရဲ့တိုက်ရိုက်လွှင့်အွန်လိုင်းကာစီနိုတွေအပြင်
-ဘောလုံးပါလောင်းနိုင်လို ဂိမ်းအကောင့်တစ်ခုဖွင့်ရုံနဲ့တစ်နေရာတည်းမှာစုံစုံလင်လင်ကစားလိုရနေပြီနော်
☎️ 09 756 395 343 
Viber Link 👉 https://jdb.link/rby99viber
Telegram Link 👉 https://jdb.link/RBY99
Website Link 👉 https://www.rby999.com/?pid=KP
────── • ◆ • ──────
"""
    cap3 = f"⚜️ 𝗤𝘂𝗲𝗿𝘆   : {search}\n🔰 𝗧𝗼𝘁𝗮𝗹    : {total_results}\n🙋🏻‍♂️𝗥𝗲𝗾𝘂𝗲𝘀𝘁 : {message.from_user.mention} \n\n</b><a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+AGntow9MZbs2MjRh'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>"
    cap += f"</b><a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>\n<a href='https://t.me/+6lHs-byrjxczY2U1'>©️ 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+AGntow9MZbs2MjRh'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>"

    ADS = [
        {"photo": "https://graph.org/file/b25eb7857fa579db610c1.jpg", "caption": f"""
{cap3}"""},	
        {"photo": "https://graph.org/file/ab82371f728850bb27193.jpg", "caption": f"""
{cap3}"""},
        {"photo": "https://graph.org/file/22dfe609e517c6ab960b0.jpg", "caption": f"""
{cap3}"""},
        {"photo": "https://graph.org/file/2fe6b8b98ad6be46c120b.jpg", "caption": f"""
{cap3}"""},	
        
    ]


    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        if not settings["TEXT_LINK"]:
            try:
                await message.reply_photo(
                    photo=imdb.get("poster"),  # type: ignore
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                await message.reply_photo(
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                    quote=True,
                )
        else:
            try:
                file_send = await bot.send_photo(
                    chat_id=Config.FILE_GROUP,
                    photo=imdb.get("poster"),
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(ADS)
                photo_url = ad1["photo"]
                caption = ad1["caption"]
                await message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                            [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send.link)]
                        ]
                    ),
                    quote=True,
                )
            except (errors.MediaEmpty, errors.PhotoInvalidDimensions, errors.WebpageMediaEmpty):
                pic = imdb.get("poster")
                poster = pic.replace(".jpg", "._V1_UX360.jpg")
                file_send2 = await bot.send_photo(
                    chat_id=Config.FILE_GROUP,
                    photo=poster,
                    caption=cap[:1024],
                    reply_markup=types.InlineKeyboardMarkup(btn),
                )
                ad1 = random.choice(ADS)
                photo_url = ad1["photo"]
                caption = ad1["caption"]
                await message.reply_photo(
                    photo=photo_url,
                    caption=caption,
                    reply_markup=types.InlineKeyboardMarkup(
                        [
                            [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                            [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send2.link)]
                        ]
                    ),
                    quote=True,
                )
    else:
        if not settings["TEXT_LINK"]:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(btn),
                quote=True
            )
        else:
            ad = random.choice(ADS)
            photo_url = ad["photo"]
            caption = ad["caption"]
            file_send3 = await bot.send_photo(
                chat_id=Config.FILE_GROUP,
                photo=random.choice(Config.PICS),
                caption=cap,
                reply_markup=types.InlineKeyboardMarkup(btn),
            )
            await message.reply_photo(
                photo=photo_url,
                caption=caption,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('ဝင်မရရင်ဒီကိုအရင်နှိပ် Join ပေးပါ', url="https://t.me/+AGntow9MZbs2MjRh")],
                        [types.InlineKeyboardButton(f'📥 {search} 📥', url=file_send3.link)]
                    ]
                ),
                quote=True
            )

@Bot.on_callback_query(filters.regex(r"^next"))  # type: ignore
async def next_page(bot: Bot, query: types.CallbackQuery):
    _, req, key, offset = query.data.split("_")  # type: ignore
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This is not for you", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = Cache.BUTTONS.get(key)
    if not search:
        await query.answer(
            "You are using one of my old messages, please send the request again.",
            show_alert=True,
        )
        return

    files, n_offset, total = await a_filter.get_search_results(
        search, offset=offset, filter=True
    )
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")

    btn = await format_buttons(files, settings["CHANNEL"])  # type: ignore

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"📃 Pages {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
            ]
        )
    elif off_set is None:
        btn.append(
            [
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ]
        )
    else:
        btn.append(
            [
                types.InlineKeyboardButton(
                    "⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"
                ),
                types.InlineKeyboardButton(
                    f"🗓 {math.ceil(int(offset) / 5) + 1} / {math.ceil(total / 5)}",
                    callback_data="pages",
                ),
                types.InlineKeyboardButton(
                    "NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}"
                ),
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=types.InlineKeyboardMarkup(btn)
        )
    except errors.MessageNotModified:
        pass
    await query.answer()


@Bot.on_callback_query(filters.regex("^file"))  # type: ignore
async def handle_file(bot: Bot, query: types.CallbackQuery):
    _, file_id = query.data.split()
    file_info = await a_filter.get_file_details(file_id)  # type: ignore
    if not file_info:
        return await query.answer("FileNotFoundError", True)
    if file_info["file_type"] == "photo":
        file_id = file_info["file_ref"]
    query.message.from_user = query.from_user
    isMsg = query.message.chat.type == enums.ChatType.PRIVATE
    if not await check_fsub(bot, query.message, sendMsg=isMsg):
        if not isMsg:
            return await query.answer(url=f"https://t.me/{bot.me.username}?start=fsub")
        return await query.answer("Please Join My Update Channel and click again")
    try:         
        file_send = await bot.send_cached_media(
                chat_id=Config.FILE_CHANNEL2,
                file_id=file_id,
                caption=Config.CUSTOM_FILE_CAPTION2.format(
                file_name=file_info["file_name"],
                file_size=get_size(file_info["file_size"]),
                caption=file_info["caption"],
            ),
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton("Join Channel", url="https://t.me/+6lHs-byrjxczY2U1")],
                        [types.InlineKeyboardButton("Group Link ", url="https://t.me/+X7DNvf9iCy5jOGJl")]
                    ]
            ),
                reply_to_message_id=query.message.id,
        )
        caption1 = f"Hi {query.from_user.mention} \n\nအချောလေး ရှာတဲ့ <a href='{file_send.link}'>{file_info['file_name']}</a> ဇာတ်ကား အဆင့်သင့်ပါ ⬇️\n\nဝင်မရရင် <a href='https://t.me/+H7ERsk_04EoxOTU1'>🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿</a> ကို Join ပါ \n\n"
        settings = await config_db.get_settings(f"SETTINGS_{query.message.chat.id}")
        if settings["DOWNLOAD_BUTTON"]:
            await query.message.reply_text(                
                caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton('🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿', url="https://t.me/+H7ERsk_04EoxOTU1")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]}📥', url=file_send.link)]
                    ]
                ),
                quote=True,
                disable_web_page_preview=True,
            )
        else:
            await bot.send_message(
                chat_id=query.from_user.id,                
                text=caption1,
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [types.InlineKeyboardButton( '🍿 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🍿', url="https://t.me/+H7ERsk_04EoxOTU1")],
                        [types.InlineKeyboardButton(f'📥 {file_info["file_name"]} {file_info["caption"]} 📥', url=file_send.link)]
                    ]
                )
            )
    except errors.PeerIdInvalid:
        return await query.answer(f"https://t.me/{bot.me.username}?start=okok")
    await query.answer(f'Sending : သင်နှိပ်လိုက်တဲ့ ဇာတ်ကားအား Channel သို့ပေးပို့လိုက်ပါပြီ \n\nCheck Channel Message \n\n {file_info["file_name"]}')	



async def ch9_imdb(bot: Bot, message: types.Message, text=True):
    if message.text.startswith("/"):
        return  # ignore commands
    
    if re.findall(r"((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()]).*)", str(message.text), re.UNICODE):
    #if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F()\d]).*)", message.text): 
        return

    if 2 < len(message.text) < 150:
        settings = await config_db.get_settings(f"SETTINGS_{message.chat.id}")
        search = message.text
        files, offset, total_results = await a_filter.get_search_results(
            search.lower(), offset=0, filter=True
        )
        if not files:
            return
    else:
        return
    key = f"{message.chat.id}-{message.id}"

    Cache.BUTTONS[key] = search
    
    if settings["IMDB"]:
        imdb = await get_poster(search, file=(files[0])["file_name"])
	
    else:
        imdb = {}

    cap = f"{search}\n\n"
    
    if imdb:
        
        cap += Config.TEMPLATE2.format(
            query=search,
            **imdb,
            **locals(),
        )

    cap1_options = [
        f"""<a href='https://t.me/+X7DNvf9iCy5jOGJl'>ဇာတ်ကား ကြည့်ရန်
အောက်က Link ကို Join ပါ ⬇️</a>
https://t.me/+X7DNvf9iCy5jOGJl

ဂရုထဲရောက်ရင်
👉<code>  {search}  </code> 👈 ဟုရိုက်ပြီး

ဇာတ်ကားကို ကြည့်ရှုနိုင်ပါသည်။

<a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗦𝗧𝗢𝗥𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a><a href='https://t.me/+X7DNvf9iCy5jOGJl'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a>""",
        f"""<a href='https://t.me/+KzKnH0ApsmVjNjM9'>ဇာတ်ကား ကြည့်ရန်
အောက်က Link ကို Join ပါ ⬇️</a>
https://t.me/+KzKnH0ApsmVjNjM9

ဂရုထဲရောက်ရင်
👉<code>  {search}  </code> 👈 ဟုရိုက်ပြီး

ဇာတ်ကားကို ကြည့်ရှုနိုင်ပါသည်။
<a href='https://t.me/+KzKnH0ApsmVjNjM9'>©️ 𝗝𝗢𝗜𝗡 𝗚𝗥𝗢𝗨𝗣</a><a href='https://t.me/+TIwZJBnFDP1kM2Q1'>©️ 𝗙𝗜𝗟𝗘 𝗦𝗧𝗢𝗥𝗘 𝗖𝗛𝗔𝗡𝗡𝗘𝗟</a>""",
    ]
    cap += random.choice(cap1_options)

    if imdb and imdb.get("poster") and settings["IMDB_POSTER"]:
        try:
            await bot.send_photo(
                Config.FILE_CHANNEL3,
		photo=imdb.get("poster"),
                caption=cap,
	    )

        except (
            errors.MediaEmpty,
            errors.PhotoInvalidDimensions,
            errors.WebpageMediaEmpty,
        ):
            pic = imdb.get("poster")
            poster = pic.replace(".jpg", "._V1_UX360.jpg")
            await bot.send_photo(
                Config.FILE_CHANNEL3,
                photo=poster,
                caption=cap[:1024], 
	    )
        except Exception as e:
            log.exception(e)
            await message.reply_text(
                cap, quote=True
            )
    else:
        await message.reply_text(
            cap,            
            quote=True,
            disable_web_page_preview=True,
        )

 
	
