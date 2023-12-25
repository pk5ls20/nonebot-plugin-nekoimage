import re
from typing import Union, Annotated
from nonebot.exception import ParserExit
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace, ArgumentParser
from nonebot import get_driver, on_shell_command
from nonebot.adapters.qq import MessageEvent as QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from .extraLogic import checkMsg, exHandler, handle_search_msg, handle_txtSearch_msg
from .apiModels.request import ImageSearchModel, AdvancedSearchModel, BasisSearchEnum, CombinedSearchModel

logger = get_driver().logger
config = get_driver().config
basicParser, advanceParser = ArgumentParser(), ArgumentParser()

basicParser.add_argument("prompt", help="fetch pic index", type=str, nargs='*')
basicParser.add_argument("-d", "--detail", help="show detail result", action="store_true")
basicParser.add_argument("-i", "--index", help="fetch pic index", type=int, default=0)
basicParser.add_argument("-n", "--num", help="fetch pic num", type=int, default=1)
basicParser.add_argument("-e", "--extra", help="extra prompt in combinedSearch", type=str, nargs='*')

advanceParser.add_argument("-d", "--detail", help="show detail result", action="store_true")
advanceParser.add_argument("-i", "--index", help="fetch pic index", type=int, default=0)
advanceParser.add_argument("-n", "--num", help="fetch pic num", type=int, default=1)
advanceParser.add_argument("-pc", "--positive", help="Positive criteria", type=str, nargs='*')
advanceParser.add_argument("-nc", "--negative", help="Negative criteria", type=str, nargs='*')
advanceParser.add_argument("-b", "--basis", help="basis of advanceSearch", type=str, default="vision")
advanceParser.add_argument("-m", "--mode", help="mode of advanceSearch", type=str, default="average")
advanceParser.add_argument("-e", "--extra", help="extra prompt in combinedSearch", type=str, nargs='*')

cmd_visionSearch = on_shell_command("t2i", rule=checkMsg, parser=basicParser)
cmd_ocrSearch = on_shell_command("o2i", rule=checkMsg, parser=basicParser)
cmd_picSearch = on_shell_command("i2i", rule=checkMsg, parser=basicParser)
cmd_advanceSearch = on_shell_command("ac", rule=checkMsg, parser=advanceParser)


@cmd_visionSearch.handle()
@cmd_ocrSearch.handle()
@cmd_picSearch.handle()
@cmd_advanceSearch.handle()
async def _(foo: Annotated[ParserExit, ShellCommandArgs()]):
    if foo.status != 0:
        await cmd_visionSearch.finish(f"Invalid input! {foo.message}")


@cmd_visionSearch.handle()
@exHandler(cmd_visionSearch)
async def handle_cmd_visionSearch(event: Union[QQMessageEvent, V11MessageEvent],
                                  bot,
                                  args: Namespace = ShellCommandArgs()):
    await handle_txtSearch_msg(event, bot, args, matcher=cmd_visionSearch, basisValue=BasisSearchEnum.vision.value)


@cmd_ocrSearch.handle()
@exHandler(cmd_ocrSearch)
async def handle_cmd_ocrSearch(event: Union[QQMessageEvent, V11MessageEvent],
                               bot,
                               args: Namespace = ShellCommandArgs()):
    await handle_txtSearch_msg(event, bot, args, matcher=cmd_ocrSearch, basisValue=BasisSearchEnum.ocr.value)


@cmd_picSearch.handle()
@exHandler(cmd_picSearch)
async def handle_cmd_picSearch(event: Union[QQMessageEvent, V11MessageEvent],
                               bot,
                               args: Namespace = ShellCommandArgs()):
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
    payload, url, picDataDict = await ImageSearchModel(image=picUrl,
                                                       count=requestDict['num'],
                                                       index=requestDict['index'])()
    await handle_search_msg(event, bot, args, matcher=cmd_picSearch, requestPayload=payload, requestUrl=url,
                            requestFiles=picDataDict, extraMsg=warnInfo)


@cmd_advanceSearch.handle()
@exHandler(cmd_advanceSearch)
async def handle_cmd_advanceSearch(event: Union[QQMessageEvent, V11MessageEvent],
                                   bot,
                                   args: Namespace = ShellCommandArgs()):
    requestDict = vars(args)
    if requestDict['basis'] not in ["vision", "ocr"]:
        raise ValueError("Invalid basis input!\nbasis must be 'vision' or 'ocr'")
    if requestDict['mode'] not in ["average", "best"]:
        raise ValueError("Invalid mode input!\nbasis must be 'average' or 'best'")
    if not requestDict['positive'] and not requestDict['negative']:
        raise ValueError("Invalid prompt input!\none of positive and negative must be provided")
    if requestDict['extra']:
        _extra = " ".join(requestDict['extra']) if isinstance(requestDict['extra'], list) else requestDict['extra']
        payload, url, requestBody = CombinedSearchModel(basis=requestDict['basis'],
                                                        extra_prompt=_extra,
                                                        criteria=requestDict['positive'],
                                                        negative_criteria=requestDict['negative'],
                                                        count=requestDict['num'],
                                                        index=requestDict['index'])()
    else:
        payload, url, requestBody = AdvancedSearchModel(basis=requestDict['basis'],
                                                        mode=requestDict['mode'],
                                                        criteria=requestDict['positive'],
                                                        negative_criteria=requestDict['negative'],
                                                        count=requestDict['num'],
                                                        index=requestDict['index'])()
    await handle_search_msg(event, bot, args, matcher=cmd_picSearch,
                            requestPayload=payload, requestUrl=url, requestContent=requestBody)
