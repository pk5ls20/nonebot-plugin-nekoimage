import pytz
import json
import httpx
import asyncio
import datetime
from functools import wraps
from typing import Optional, Dict, Any, Union, Type
from nonebot import logger, get_driver
from nonebot.internal.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace, ArgumentParser
from nonebot.adapters.qq import QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot_plugin_saa import Image, Text, MessageFactory
from .apiModels.request import BasicSearchModel, TextSearchModel, BasisSearchEnum
from .apiModels.response import SearchResult, SearchApiResponse

config = get_driver().config


def exHandler(cmd):
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            try:
                return await func(event, *args, **kwargs)
            except Exception as e:
                await handleError(cmd, event, e)

        return wrapper

    return decorator


async def handleError(matcher, _, ex):
    tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.datetime.now(tz)
    raiseTime = current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    logger.opt(exception=True).error(type(ex).__name__)
    await matcher.finish(f"qwq出错了呢\n{type(ex).__name__} - {ex}\ntime={raiseTime}")


async def checkMsg(event, bot):
    return (event.get_user_id() == bot.self_id and config.is_self_msg) or (event.to_me and config.is_at_msg)


async def handle_txtSearch_msg(event: Union[QQMessageEvent, V11MessageEvent],
                               bot,
                               args: Namespace = ShellCommandArgs(),
                               matcher: Type[Matcher] = None,
                               basisValue: str = None):
    requestDict = vars(args)
    prompt = " ".join(requestDict['prompt']) if isinstance(requestDict['prompt'], list) else requestDict['prompt']
    Payload, Url = TextSearchModel(basis=basisValue,
                                   prompt=prompt,
                                   count=requestDict['num'],
                                   index=requestDict['index'])()
    await handle_basicSearch_msg(event, bot, args, matcher=matcher, requestPayload=Payload, requestUrl=Url)


async def handle_basicSearch_msg(event: Union[QQMessageEvent, V11MessageEvent],
                                 bot,
                                 args: Namespace = ShellCommandArgs(),
                                 matcher: Type[Matcher] = None,
                                 requestPayload: dict = None,
                                 requestUrl: str = None):
    res = await request(url=requestUrl, payload=requestPayload, token={"x-access-token": config.nekoimagesecret})
    res = SearchApiResponse.parse_obj(res)
    picList = await fetchAllPic([f"{config.nekoimageapi}{res.img.url}" for res in res.result])
    if len(picList) == 0:
        await matcher.finish("未找到图片")
    else:
        for idx, raw_res in enumerate(picList):
            await selfMessageFactory(oriInfo=res.result[idx], picByte=raw_res.content, isDetailed=args.detail).send()
            await asyncio.sleep(1)


async def request(url: str, payload: Dict, files: Optional[Dict] = None, token: Optional[Dict] = None):
    async with httpx.AsyncClient() as client:
        if files:
            response = await client.post(url, params=payload, files=files, headers=token)
        else:
            response = await client.get(url, params=payload, headers=token)
        response.raise_for_status()
        return response.json()


async def fetchAllPic(picList: list) -> tuple[Any]:
    try:
        async with httpx.AsyncClient() as client:
            tasks = [client.get(picurl) for picurl in picList]
            return await asyncio.gather(*tasks)
    except Exception as e:
        logger.warning(e)
        return tuple()


def selfMessageFactory(picByte: bytes,
                       oriInfo: Optional[SearchResult] = None,
                       isDetailed: bool = False) -> MessageFactory:
    return MessageFactory([
        Text(str(json.loads(oriInfo.json()))) if isDetailed else None,
        Image(picByte)
    ])
