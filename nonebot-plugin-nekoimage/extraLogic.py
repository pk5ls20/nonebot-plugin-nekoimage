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
from nonebot.rule import Namespace
from nonebot.adapters.qq import QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot_plugin_saa import Image, Text, MessageFactory
from .apiModels.request import TextSearchModel, CombinedSearchModel
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
                await cmd.finish()

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
    prompt = prompt.join("  ") if len(prompt) <= 2 else prompt
    if requestDict['extra']:
        _extra = " ".join(requestDict['extra']) if isinstance(requestDict['extra'], list) else requestDict['extra']
        payload, url, body = CombinedSearchModel(basis=basisValue,
                                                 criteria=[prompt],
                                                 extra_prompt=_extra,
                                                 count=requestDict['num'],
                                                 index=requestDict['index'])()
    else:
        payload, url, body = TextSearchModel(basis=basisValue,
                                             prompt=prompt,
                                             count=requestDict['num'],
                                             index=requestDict['index'],
                                             exact=requestDict['exact'])()
    await handle_search_msg(event, bot, args, matcher=matcher,
                            requestPayload=payload, requestUrl=url, requestContent=body)


async def handle_search_msg(event: Union[QQMessageEvent, V11MessageEvent],
                            bot,
                            args: Namespace = ShellCommandArgs(),
                            matcher: Type[Matcher] = None,
                            requestPayload: dict = None,
                            requestUrl: str = None,
                            requestContent: Optional[str] = None,
                            requestFiles: Optional[Dict] = None,
                            extraMsg: Optional[str] = None):
    res = await request(url=requestUrl,
                        payload=requestPayload,
                        files=requestFiles,
                        content=requestContent,
                        token={"x-access-token": config.nekoimagesecret})
    res = SearchApiResponse.parse_obj(res)
    picList = await fetchAllPic([f"{config.nekoimageapi}{res.img.url}" for res in res.result])
    if extraMsg:
        await MessageFactory([Text(extraMsg)]).send()
    if len(picList) == 0:
        await matcher.finish("未找到图片哦~")
    else:
        for idx, raw_res in enumerate(picList):
            await selfMessageFactory(oriInfo=res.result[idx], picByte=raw_res.content, isDetailed=args.detail).send()
            await asyncio.sleep(1)


async def request(url: str,
                  payload: Dict,
                  content: Optional[str] = None,
                  files: Optional[Dict] = None,
                  token: Optional[Dict] = None) -> dict:
    timeout = httpx.Timeout(timeout=config.httpx_timeout,
                            read=config.httpx_timeout) if config.httpx_timeout is not None else httpx.Timeout()
    async with httpx.AsyncClient(timeout=timeout) as client:
        if files:
            response = await client.post(url, params=payload, files=files, headers=token)
        elif content:
            response = await client.post(url, params=payload, content=content, headers=token)
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
    info = json.loads(oriInfo.json())
    if config.remove_detail_url:
        del info['img']["url"]
        del info['img']["thumbnail_url"]
    return MessageFactory([
        Text(str(info)) if isDetailed else None,
        Image(picByte)
    ])
