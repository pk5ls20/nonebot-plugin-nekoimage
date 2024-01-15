import re
import pytz
import asyncio
import datetime
from functools import wraps
from nonebot import logger, get_driver
from nonebot_plugin_saa import MessageFactory

config = get_driver().config


def exHandler(matcher):
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            try:
                return await func(event, *args, **kwargs)
            except Exception as ex:
                await handleError(matcher, ex)
                await matcher.finish()

        return wrapper

    return decorator


async def handleError(matcher, ex):
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.datetime.now(tz)
    raiseTime = current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    logger.opt(exception=True).error(type(ex).__name__)
    _ex = f"qwq出错了呢\n{type(ex).__name__} - {ex}\ntime={raiseTime}"
    _ex = _ex if not config.nekoimage_better_url else replace_urls(_ex)
    await matcher.finish(f"qwq出错了呢\n{type(ex).__name__} - {ex}\ntime={raiseTime}")


async def checkMsg(event):
    return (event.to_me and config.nekoimage_at_msg) or (not config.nekoimage_at_msg)


async def sendMsg(msg_list: list[MessageFactory]):
    for message_factory in msg_list:
        await message_factory.send()
        await asyncio.sleep(1) if len(msg_list) > 1 else None


def replace_urls(input_str: str) -> str:
    return re.sub(r'(?:https?://)?([\w-]+(\.[\w-]+)+)',
                  lambda m: "(" + m.group(1).replace('.', '+') + ")", input_str)
