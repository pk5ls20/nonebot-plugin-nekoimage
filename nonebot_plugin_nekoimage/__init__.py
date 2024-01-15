from nonebot import get_driver, require
from nonebot.plugin import PluginMetadata
from .Models.config import ConfigModel

require("nonebot_plugin_saa")

__plugin_meta = PluginMetadata(
    name="nonebot-plugin-nekoimage",
    description="A nonebot plugin for integrating with [NekoImageGallery](https://github.com/hv0905/NekoImageGallery).",
    usage="",
    config=ConfigModel,
    type="application",
    homepage="https://github.com/pk5ls20/nonebot-plugin-nekoimage",
    supported_adapters={"~onebot.v11", "~qq"},
)

from . import Matchers
config = get_driver().config
assert config.nekoimage_api
assert config.nekoimage_secret
