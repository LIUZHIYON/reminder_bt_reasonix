import edge_tts, asyncio
async def run():
    c = edge_tts.Communicate('小明该吃饭啦', 'zh-CN-XiaoyiNeural')
    await c.save('E:/LuBanCat/BT_ros2/reminder_bt/_pc_tts.mp3')
    print('done')
asyncio.run(run())
