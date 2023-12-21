## nonebot-plugin-nekoimage
A nonebot plugin for integrating with [NekoImageGallery](https://github.com/hv0905/NekoImageGallery) (An online AI image search engine based on the Clip model and Qdrant vector database. Supports keyword search and similar image search).

## ENV
```env
nekoImageAPI=http://127.0.0.1:8000
nekoImageSecret=your-super-secret-access-token
is_self_msg=false # Whether to process messages sent by the bot itself
is_at_msg=true # Whether to process messages that <at> the bot
```
### Supported Adapter
Use [nonebot-saa](https://github.com/MountainDash/nonebot-plugin-send-anything-anywhere) to enhance the compatibility, The adapters listed below have been adapted
- [adapter-onebot [v11,Tested on OpenShamrock] ](https://whitechi73.github.io/OpenShamrock/api)
- [adapter-qq](https://github.com/nonebot/adapter-qq)

### Special thanks
- [KirbyScarlet/vanilla-bot](https://github.com/KirbyScarlet/vanilla-bot)