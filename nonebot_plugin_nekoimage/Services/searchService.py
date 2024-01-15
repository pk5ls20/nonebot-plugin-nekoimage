import re
import json
import httpx
import asyncio
from typing import Optional, Dict, Any, Union
from nonebot import get_driver, logger
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace
from nonebot.adapters.qq import QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from nonebot_plugin_saa import Image, Text, MessageFactory
from ..Models.request import TextSearchModel, CombinedSearchModel, ImageSearchModel, AdvancedSearchModel
from ..Models.response import SearchResult, SearchApiResponse
from ..Utils.extraLogic import replace_urls

config = get_driver().config


class SearchService:
    @classmethod
    async def textSearch(cls,
                         args: Namespace = ShellCommandArgs(),
                         basisValue: str = None) -> list[MessageFactory]:
        requestDict = vars(args)
        prompt = " ".join(requestDict['prompt']) if isinstance(requestDict['prompt'], list) else requestDict['prompt']
        prompt = prompt.join("  ") if len(prompt) <= 2 else prompt
        if requestDict['extra']:
            _extra = " ".join(requestDict['extra']) if isinstance(requestDict['extra'], list) else requestDict['extra']
            payload, url, method, body = CombinedSearchModel(basis=basisValue,
                                                             criteria=[prompt],
                                                             extra_prompt=_extra,
                                                             count=requestDict['num'],
                                                             index=requestDict['index'])()
        else:
            payload, url, method, body = TextSearchModel(basis=basisValue,
                                                         prompt=prompt,
                                                         count=requestDict['num'],
                                                         index=requestDict['index'],
                                                         exact=requestDict['exact'])()
        msgList = await cls._search(args, requestMethod=method, requestPayload=payload,
                                    requestUrl=url, requestContent=body)
        return msgList

    @classmethod
    async def imageSearch(cls,
                          event: Union[QQMessageEvent, V11MessageEvent],
                          args: Namespace = ShellCommandArgs()) -> list[MessageFactory]:
        requestDict = vars(args)
        warnInfo, picUrl = None, None
        if event.reply and "image" in [i.type for i in event.reply.message]:
            warnInfo = f"[Reply content overload the possible uploaded image!]"
            picUrl = event.reply.message[0].data['url']
        else:
            picUrl = re.findall(r"https?://.*?(?=[]>])", requestDict['prompt'][0])[0]
        if not requestDict['prompt'] and not picUrl:
            raise ValueError("No image upload!")
        if len(requestDict['prompt']) > 1:
            warnInfo = f"⚠️You uploaded{len(requestDict['prompt'])}, but only the first image will be used!]"
        payload, url, method, body = await ImageSearchModel(image=picUrl,
                                                            count=requestDict['num'],
                                                            index=requestDict['index'])()
        msgList = [MessageFactory([Text(warnInfo)])] if warnInfo else []
        msgList.extend(await cls._search(args, requestMethod=method, requestPayload=payload,
                                         requestUrl=url, requestFiles=body))
        return msgList

    @classmethod
    async def advancedSearch(cls,
                             args: Namespace = ShellCommandArgs()) -> list[MessageFactory]:
        requestDict = vars(args)
        if requestDict['basis'] not in ["vision", "ocr"]:
            raise ValueError("Invalid basis input!\nbasis must be 'vision' or 'ocr'")
        if requestDict['mode'] not in ["average", "best"]:
            raise ValueError("Invalid mode input!\nbasis must be 'average' or 'best'")
        if not requestDict['positive'] and not requestDict['negative']:
            raise ValueError("Invalid prompt input!\none of positive and negative must be provided")
        if requestDict['extra']:
            _extra = " ".join(requestDict['extra']) if isinstance(requestDict['extra'], list) else requestDict['extra']
            payload, url, method, body = CombinedSearchModel(basis=requestDict['basis'],
                                                             extra_prompt=_extra,
                                                             criteria=requestDict['positive'],
                                                             negative_criteria=requestDict['negative'],
                                                             count=requestDict['num'],
                                                             index=requestDict['index'])()
        else:
            payload, url, method, body = AdvancedSearchModel(basis=requestDict['basis'],
                                                             mode=requestDict['mode'],
                                                             criteria=requestDict['positive'],
                                                             negative_criteria=requestDict['negative'],
                                                             count=requestDict['num'],
                                                             index=requestDict['index'])()
        msgList = await cls._search(args, requestMethod=method, requestPayload=payload,
                                    requestUrl=url, requestContent=body)
        return msgList

    @classmethod
    async def _search(cls,
                      args: Namespace = ShellCommandArgs(),
                      requestMethod: str = None,
                      requestPayload: dict = None,
                      requestUrl: str = None,
                      requestContent: Optional[str] = None,
                      requestFiles: Optional[Dict] = None) -> list[MessageFactory]:
        res = await cls._request(url=requestUrl, method=requestMethod, payload=requestPayload, content=requestContent,
                                 files=requestFiles, token={"x-access-token": config.nekoimage_secret})
        res = SearchApiResponse.parse_obj(res)
        picList = await cls._fetchAllPic([f"{config.nekoimage_api}{res.img.url}" for res in res.result])
        result = []
        if len(picList) == 0:
            result.extend(MessageFactory([Text("No result found!")]))
        else:
            result.extend(
                [
                    cls._picMessageFactory(picByte=raw_res.content, oriInfo=res.result[idx], isDetailed=args.detail)
                    for idx, raw_res in enumerate(picList)
                ]
            )
        return result

    @classmethod
    async def _request(cls,
                       url: str,
                       method: str,
                       payload: Dict,
                       content: Optional[str] = None,
                       files: Optional[Dict] = None,
                       token: Optional[Dict] = None) -> dict:
        timeout = httpx.Timeout(timeout=config.nekoimage_httpx_timeout, read=config.nekoimage_httpx_timeout) \
            if config.nekoimage_httpx_timeout is not None else httpx.Timeout()
        async with httpx.AsyncClient(timeout=timeout) as client:
            request = getattr(client, method)
            response = await request(
                url,
                params=payload,
                headers=token,
                **({"files": files} if files is not None else {}),
                **({"content": content} if content is not None else {}),
            )
            response.raise_for_status()
            return response.json()

    @classmethod
    async def _fetchAllPic(cls, picList: list) -> tuple[Any]:
        try:
            async with httpx.AsyncClient() as client:
                tasks = [client.get(picurl) for picurl in picList]
                return await asyncio.gather(*tasks)
        except Exception as e:
            logger.warning(e)
            return tuple()

    @classmethod
    def _picMessageFactory(cls,
                           picByte: bytes,
                           oriInfo: Optional[SearchResult] = None,
                           isDetailed: bool = False) -> MessageFactory:
        info = json.loads(oriInfo.json())
        if config.nekoimage_better_url:
            info = replace_urls(str(info))
        return MessageFactory([
            Text(str(info)) if isDetailed else None,
            Image(picByte)
        ])
