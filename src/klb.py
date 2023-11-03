import json
import os
import time

from bilireq.live import get_rooms_info_by_uids
from dotenv import load_dotenv
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Struct, Types

from .utils import SingletonLogger, calc_time_total

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
bot = Bot(token=TOKEN)

from .db_handler import DBHandler

db = DBHandler("bilibili_live_user_ids.db")


def reset_data() -> None:
    """
    Resets the status and live_time dictionaries.

    Returns:
        None
    """
    global status, live_time
    status = {}
    live_time = {}


@bot.command(name="ping")
async def world(msg: Message):
    """
    Responds with 'pong!' when the user sends the command '!ping'.
    """
    await msg.reply("pong!")


@bot.command(name="subscribe")
async def subscribe(msg: Message, user_id: str):
    """
    Subscribes to a Bilibili live user ID and stores it in a SQLite database.
    """
    try:
        if db.check_user_id_exists(user_id):
            await msg.reply(f"Bilibili live user ID {user_id} is already subscribed!")
        else:
            db.insert_user_id(user_id)
            await msg.reply(f"Subscribed to Bilibili live user ID {user_id}!")
    except Exception as e:
        await msg.reply(
            f"An error occurred while subscribing to Bilibili live user ID {user_id}: {e}"
        )


@bot.command(name="unsubscribe")
async def unsubscribe(msg: Message, user_id: str):
    """
    Unsubscribes from a Bilibili live user ID and removes it from the SQLite database.
    """
    try:
        if db.check_user_id_exists(user_id):
            db.delete_user_id(user_id)
            await msg.reply(f"Unsubscribed from Bilibili live user ID {user_id}!")
        else:
            await msg.reply(f"Bilibili live user ID {user_id} is not subscribed!")
    except Exception as e:
        await msg.reply(
            f"An error occurred while unsubscribing from Bilibili live user ID {user_id}: {e}"
        )


@bot.command(name="all")
async def all_ids(msg: Message):
    """
    Fetches all Bilibili live user IDs from the SQLite database and shows them in the conversation.
    """
    try:
        user_ids = db.get_all_user_ids()
        res = await get_rooms_info_by_uids(
            user_ids,
            reqtype="web",
        )
        id_string = ""
        name_string = ""
        image_list = []
        for uid, info in res.items():
            id_string += f"\n{uid} "
            name_string += f"\n{info['uname']}"
            image_list.append(Element.Image(src=info["face"], circle=True, size='lg'))
        all_msg = CardMessage(
            Card(
                Module.Section(
                    Struct.Paragraph(
                        2,
                        Element.Text(f"**ID**{id_string}", type=Types.Text.KMD),
                        Element.Text(f"**昵称**{name_string}", type=Types.Text.KMD),
                    )
                ),
                Module.Context(*image_list),
            )
        )
        await msg.reply(all_msg)
    except Exception as e:
        await msg.reply(f"An error occurred while fetching Bilibili live user IDs: {e}")


@bot.command(name="help")
async def help(msg: Message):
    """
    Shows all the useful commands.
    """
    commands = """
    subscribe <user_id>: Subscribes to a Bilibili live user ID.
    unsubscribe <user_id>: Unsubscribes from a Bilibili live user ID.
    all: Fetches all Bilibili live user IDs.
    """
    await msg.reply(commands)


@bot.task.add_interval(seconds=10)
async def live_sched():
    """
    Task that checks if certain Bilibili users are live streaming, and sends notifications when their streaming status changes.

    Args:
        msg: The message object to reply to.

    Returns:
        None
    """
    uids = db.get_all_user_ids()
    ch = await bot.client.fetch_public_channel(CHANNEL_ID)
    if not uids:
        return
    logger.debug(f"爬取直播列表，目前开播{sum(status.values())}人，总共{len(uids)}人")
    res = await get_rooms_info_by_uids(
        uids,
        reqtype="web",
    )
    if not res:
        return
    for uid, info in res.items():
        new_status = 0 if info["live_status"] == 2 else info["live_status"]
        if uid not in status:
            status[uid] = new_status
            continue
        old_status = status[uid]
        if new_status == old_status:
            continue
        status[uid] = new_status

        name = info["uname"]
        if new_status:
            live_time[uid] = info["live_time"]
            room_id = info["short_id"] or info["room_id"]
            url = f"https://live.bilibili.com/{room_id}"
            title = info["title"]
            cover = info["cover_from_user"] or info["keyframe"]
            area = info["area_v2_name"]
            area_parent = info["area_v2_parent_name"]
            room_area = f"{area_parent} / {area}"
            logger.info(f"检测到开播：{name}（{uid}）")
            live_msg = Card(
                Module.Header(f"{name} 开播啦！"),
                Module.Context(f"分区：{room_area}"),
                Module.Section(f"标题：{title}"),
                Module.Container(Element.Image(src=cover)),
                Module.Section(f"[{url}]({url})"),
            )
        else:  # 下播
            logger.info(f"检测到下播：{name}（{uid}）")
            live_time_msg = (
                f"\n本次直播时长 {calc_time_total(time.time() - live_time[uid])}。"
                if live_time.get(uid)
                else "。"
            )
            live_msg = Card(Module.Header(f"{name} 下播了{live_time_msg}"))
        ret = await ch.send(CardMessage(live_msg))
        logger.info(f"Sent message: {ret['msg_id']}")


def klb(debug: bool):
    """
    Runs the bot.
    """
    global logger
    reset_data()
    logger = SingletonLogger(debug).get_logger()
    bot.run()
