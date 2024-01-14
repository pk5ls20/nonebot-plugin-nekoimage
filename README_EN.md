## nonebot-plugin-nekoimage
A nonebot plugin for integrating with [NekoImageGallery](https://github.com/hv0905/NekoImageGallery) (An online AI image search engine based on the Clip model and Qdrant vector database. Supports keyword search and similar image search).

### Installation
1. **Manually build the latest version of **[nonebot-plugin-send-anything-anywhere](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere) (hereafter referred to as saa) and install it    

> As of 2024.1.15, the latest version number of saa is still [0.4.0](https://pypi.org/project/nonebot-plugin-send-anything-anywhere/0.4.0/) as of November 18, 2023, which does not have a better adaptation of the qq adapter. So you need to manually build the latest version of saa manually and install it with the following command:

```bash
git clone https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere
cd nonebot-plugin-send-anything-anywhere
poetry install
```

2. Install this plugin
- Use nb-cli to install  
  ``nb plugin install nonebot-plugin-nekoimage``
- Install using poetry  
  ``poetry add nonebot-plugin-nekoimage``
- Install using pip  
  `pip install nonebot-plugin-nekoimage`

### ENV
```env
NEKOIMAGE_API=http://127.0.0.1:8000 # See [NekoImageGallery](https://github.com/hv0905/NekoImageGallery)
NEKOIMAGE_SECRET=your-super-secret-access-token # See [NekoImageGallery](https://github.com/hv0905/NekoImageGallery)
NEKOIMAGE_AT_MSG=true # Whether to process **only messages from at bots**
NEKOIMAGE_BETTER_URL=true # Send the information in url format after processing, especially for adapter-qq
NEKOIMAGE_HTTPX_TIMEOUT=30 # Waiting timeout for plugins to send requests to the NekoImageGallery backend
```

### Supported Adapter
Use [nonebot-saa](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere) to enhance the compatibility, The adapters listed below have been adapted
- [adapter-onebot [v11,Tested on OpenShamrock] ](https://whitechi73.github.io/OpenShamrock/api)
- [adapter-qq](https://github.com/nonebot/adapter-qq)

### Special thanks
- [KirbyScarlet/vanilla-bot](https://github.com/KirbyScarlet/vanilla-bot)