from hoshino import Service


sv = Service("方舟帮助")


ark_txt = '''
方舟抽卡模拟

根据原神抽卡插件改写
作者 黒下やみ（757994086）

指令

@bot 方舟十连
@bot 方舟百连
@bot 方舟井
方舟卡池切换

目前提供无up常驻池，W限定池，年限定池，温蒂限定池
井是300抽，模拟抽卡考虑前10发的保底5星/6星
'''


@sv.on_fullmatch("方舟帮助")
async def help(bot, ev):
    await bot.send(ev, ark_txt)


