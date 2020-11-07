from hoshino import Service
from .gacha import gacha_info , FILE_PATH , Gacha , POOL
import os
import json
from hoshino.util import DailyNumberLimiter
from ..config import Gacha10Limit,Gacha90Limit,Gacha180Limit


daily_limiter_10 = DailyNumberLimiter(Gacha10Limit)
daily_limiter_90 = DailyNumberLimiter(Gacha90Limit)
daily_limiter_180 = DailyNumberLimiter(Gacha180Limit)

sv = Service('方舟抽卡')

group_pool = {
    # 这个字典保存每个群对应的卡池是哪个，群号字符串为key,卡池名为value，群号不包含在字典key里卡池按默认DEFAULT_POOL
}

def save_group_pool():
    with open(os.path.join(FILE_PATH,'gid_pool.json'),'w',encoding='UTF-8') as f:
        json.dump(group_pool,f,ensure_ascii=False)



# 检查gid_pool.json是否存在，没有创建空的
if not os.path.exists(os.path.join(FILE_PATH,'gid_pool.json')):
    save_group_pool()



# 读取gid_pool.json的信息
with open(os.path.join(FILE_PATH,'gid_pool.json'),'r',encoding='UTF-8') as f:
    if f.startswith(u'\ufeff'):
        f = f.encode('utf8')[3:].decode('utf8')
    group_pool = json.load(f)




@sv.on_prefix(["方舟十连"], only_to_me=True)
async def gacha_(bot, ev):
    gid = str(ev.group_id)
    userid = ev['user_id']
    if not daily_limiter_10.check(userid):
        await bot.send(ev, '今天已经抽了很多次啦，明天再来吧~')
        return
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    daily_limiter_10.increase(userid)
    await bot.send(ev, G.gacha_10() , at_sender=True)

@sv.on_prefix(["方舟百连"], only_to_me=True)
async def gacha_(bot, ev):
    gid = str(ev.group_id)
    userid = ev['user_id']
    if not daily_limiter_90.check(userid):
        await bot.send(ev, '今天已经抽了很多次啦，明天再来吧~')
        return
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    daily_limiter_90.increase(userid)
    await bot.send(ev, G.gacha_90(100) , at_sender=True)



@sv.on_prefix(["方舟井"], only_to_me=True)
async def gacha_(bot, ev):
    gid = str(ev.group_id)
    userid = ev['user_id']
    if not daily_limiter_180.check(userid):
        await bot.send(ev, '今天已经抽了很多次啦，明天再来吧~')
        return
    daily_limiter_180.increase(userid)
    if gid in group_pool:
        G = Gacha(group_pool[gid])
    else:
        G = Gacha()
    await bot.send(ev, G.gacha_90(300) , at_sender=True)



@sv.on_prefix(["方舟卡池","方舟up","方舟UP"])
async def gacha_(bot, ev):
    gid = str(ev.group_id)

    if gid in group_pool:
        info = gacha_info(group_pool[gid])
    else:
        info = gacha_info()

    await bot.send(ev, info , at_sender=True)

@sv.on_prefix(('方舟卡池切换','方舟切换卡池'))
async def set_pool(bot, ev):

    pool_name = ev.message.extract_plain_text().strip()
    gid = str(ev.group_id)

    if pool_name in POOL.keys():
        if gid in group_pool:
            group_pool[gid] = pool_name
        else:
            group_pool.setdefault(gid,pool_name)
        save_group_pool()
        await bot.send(ev, f"卡池已切换为 {pool_name} ")
        return

    txt = "请使用以下命令来切换卡池\n"
    for i in POOL.keys():
        txt += f"方舟卡池切换 {i} \n"

    await bot.send(ev, txt)
