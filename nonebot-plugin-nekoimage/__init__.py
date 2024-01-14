from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from .Models.config import ConfigModel
from . import Matchers

__plugin_meta = PluginMetadata(
    name="nonebot-plugin-nekoimage",
    description="A nonebot plugin for integrating with [NekoImageGallery](https://github.com/hv0905/NekoImageGallery).",
    usage="",
    config=ConfigModel,
    type="application",
    homepage="https://github.com/pk5ls20/nonebot-plugin-nekoimage",
    supported_adapters={"~onebot.v11", "~qq"},
)

config = get_driver().config
assert config.nekoimage_api
assert config.nekoimage_secret
