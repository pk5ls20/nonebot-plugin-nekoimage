from typing import Union, Annotated
from nonebot.exception import ParserExit
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace, ArgumentParser
from nonebot import get_driver, on_shell_command
from nonebot.adapters.qq import MessageEvent as QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from ..Services.searchService import SearchService
from ..Models.request import BasisSearchEnum
from ..Utils.extraLogic import checkMsg, sendMsg, exHandler, replace_urls

logger = get_driver().logger
config = get_driver().config
basicParser, advanceParser = ArgumentParser(), ArgumentParser()

basicParser.add_argument("prompt", help="fetch pic index", type=str, nargs='*')
basicParser.add_argument("-d", "--detail", help="show detail result", action="store_true")
basicParser.add_argument("-i", "--index", help="fetch pic index", type=int, default=0)
basicParser.add_argument("-n", "--num", help="fetch pic num", type=int, default=1)
basicParser.add_argument("-e", "--extra", help="extra prompt in combinedSearch", type=str, nargs='*')
basicParser.add_argument("-ex", "--exact", help="Returns the portion of the lookup result that contains "
                                                "only the prompt.", action="store_true")
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
cmd_imageSearch = on_shell_command("i2i", rule=checkMsg, parser=basicParser)
cmd_advanceSearch = on_shell_command("ac", rule=checkMsg, parser=advanceParser)


@cmd_visionSearch.handle()
@cmd_ocrSearch.handle()
@cmd_imageSearch.handle()
@cmd_advanceSearch.handle()
async def _(foo: Annotated[ParserExit, ShellCommandArgs()], matcher):
    if foo.status != 0:
        send = f"Invalid input! {foo.message}"
        send = send if not config.nekoimage_better_url else replace_urls(send)
        await matcher.finish(send)


@cmd_visionSearch.handle()
@exHandler(cmd_visionSearch)
async def handle_cmd_visionSearch(event: Union[QQMessageEvent, V11MessageEvent],
                                  args: Namespace = ShellCommandArgs()):
    msgList = await SearchService.textSearch(args, basisValue=BasisSearchEnum.vision.value)
    await sendMsg(msgList)


@cmd_ocrSearch.handle()
@exHandler(cmd_ocrSearch)
async def handle_cmd_ocrSearch(event: Union[QQMessageEvent, V11MessageEvent],
                               args: Namespace = ShellCommandArgs()):
    msgList = await SearchService.textSearch(args, basisValue=BasisSearchEnum.ocr.value)
    await sendMsg(msgList)


@cmd_imageSearch.handle()
@exHandler(cmd_imageSearch)
async def handle_cmd_imageSearch(event: Union[QQMessageEvent, V11MessageEvent],
                                 args: Namespace = ShellCommandArgs()):
    msgList = await SearchService.imageSearch(event, args)
    await sendMsg(msgList)


@cmd_advanceSearch.handle()
@exHandler(cmd_advanceSearch)
async def handle_cmd_advanceSearch(event: Union[QQMessageEvent, V11MessageEvent],
                                   args: Namespace = ShellCommandArgs()):
    msgList = await SearchService.advancedSearch(args)
    await sendMsg(msgList)
