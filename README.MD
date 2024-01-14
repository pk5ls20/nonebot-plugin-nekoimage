## nonebot-plugin-nekoimage
对接[NekoImageGallery](https://github.com/hv0905/NekoImageGallery)（一个AI驱动的自然语言和反向图像搜索引擎，由CLIP和qdrant提供支持）的nonebot插件

### 安装
1. **手动构建最新版本的**[nonebot-plugin-send-anything-anywhere](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere)（以下简称saa）并安装    

> 截止2024.1.15，saa的最新版本号仍为2023年11月18日的[0.4.0](https://pypi.org/project/nonebot-plugin-send-anything-anywhere/0.4.0/)，这个版本并未对qq适配器进行较好的适配，因此需要手动构建最新版本的saa并安装，安装命令如下：

```bash
git clone https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere
cd nonebot-plugin-send-anything-anywhere
poetry install
```

2. 安装本插件
- 使用 nb-cli 安装  
  `nb plugin install nonebot-plugin-nekoimage`
- 使用 poetry 安装  
  `poetry add nonebot-plugin-nekoimage`
- 使用 pip 安装  
  `pip install nonebot-plugin-nekoimage`

### 配置文件
```env
NEKOIMAGE_API=http://127.0.0.1:8000 # 参见 [NekoImageGallery](https://github.com/hv0905/NekoImageGallery)
NEKOIMAGE_SECRET=your-super-secret-access-token # 参见 [NekoImageGallery](https://github.com/hv0905/NekoImageGallery)
NEKOIMAGE_AT_MSG=true # 是否**仅处理at机器人**的消息
NEKOIMAGE_BETTER_URL=true # 将url格式的信息处理后发送，特别适用于adapter-qq
NEKOIMAGE_HTTPX_TIMEOUT=30 # 插件向NekoImageGallery后端发送请求的等待超时时间
```

### 支持的适配器
本插件使用 [nonebot-saa](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere) 同时适配以下适配器使用：
- [adapter-onebot [v11,测试于OpenShamrock的实现] ](https://whitechi73.github.io/OpenShamrock/api)
- [adapter-qq](https://github.com/nonebot/adapter-qq)

### 特别感谢
- [KirbyScarlet/vanilla-bot](https://github.com/KirbyScarlet/vanilla-bot)