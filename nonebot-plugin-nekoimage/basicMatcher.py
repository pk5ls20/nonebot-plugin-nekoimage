from typing import Union
from nonebot.params import ShellCommandArgs
from nonebot.rule import Namespace, ArgumentParser
from nonebot import get_driver, on_shell_command
from nonebot.adapters.qq import MessageEvent as QQMessageEvent
from nonebot.adapters.onebot.v11.event import MessageEvent as V11MessageEvent
from .extraLogic import checkMsg, exHandler, handle_basicSearch_msg, handle_txtSearch_msg
from .apiModels.request import BasicSearchModel, TextSearchModel, ImageSearchModel, SimilarSearchModel, \
    AdvancedSearchModel, BasisSearchEnum, SearchModelEnum

logger = get_driver().logger
config = get_driver().config

basicParser, advanceParser = ArgumentParser(), ArgumentParser()
basicParser.add_argument("prompt", help="fetch pic index", type=str, nargs='*')
basicParser.add_argument("-d", "--detail", help="show detail result", action="store_true")
basicParser.add_argument("-i", "--index", help="fetch pic index", type=int, default=0)
basicParser.add_argument("-n", "--num", help="fetch pic num", type=int, default=1)
advanceParser.add_argument("-p", "--positive", help="Positive criteria", type=str)
advanceParser.add_argument("-n", "--negative", help="Negative criteria", type=str)
advanceParser.add_argument("-b", "--basis", help="basis of search", type=str)
cmd_visionSearch = on_shell_command("t2i", rule=checkMsg, parser=basicParser)
cmd_ocrSearch = on_shell_command("o2i", rule=checkMsg, parser=basicParser)
cmd_picSearch = on_shell_command("i2i", rule=checkMsg, parser=basicParser)
cmd_advanceSearch = on_shell_command("ac", rule=checkMsg, parser=advanceParser)


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
