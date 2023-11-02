import json
import os
import time

from bilireq.live import get_rooms_info_by_uids
from khl import Bot, Message
from khl.card import Card, CardMessage, Element, Module, Struct, Types
from dotenv import load_dotenv

from .utils import SingletonLogger, calc_time_total

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
bot = Bot(token=TOKEN)

from .db_handler import DBHandler

db = DBHandler("bilibili_live_user_ids.db")
logger = SingletonLogger().get_logger()
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


@bot.task.add_interval(minutes=2)
async def live_sched() -> None:
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
                Module.Section(Element.Image(src=cover)),
                Module.Section(url),
            )
        else:  # 下播
            logger.info(f"检测到下播：{name}（{uid}）")
            live_time_msg = (
                f"\n本次直播时长 {calc_time_total(time.time() - live_time[uid])}。"
                if live_time.get(uid)
                else "。"
            )
            live_msg = Card(Module.Header(f"{name} 下播了{live_time_msg}"))
        logger.info(json.dumps(live_msg))
        ret = await ch.send(CardMessage(live_msg))
        logger.info(f"Sent message: {ret['msg_id']}")


def klb():
    """
    Runs the bot.
    """
    bot.run()
