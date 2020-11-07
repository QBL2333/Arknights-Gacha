from PIL import Image
from io import BytesIO


import os
import json
import random
import math
import base64

FILE_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(FILE_PATH,'icon')



DEFAULT_POOL = "常驻池" # 默认卡池

POOL_PROBABILITY  = {
    # 所有卡池的4星和5星概率,这里直接填写官方给出的概率，程序会自动对4星概率进行累计
    "迷迭香限定池":{"6" : 0.02 , "5" : 0.08 , "4" : 0.50 , "3" : 0.40 },
    "年限定池":{"6" : 0.02 , "5" : 0.08 , "4" : 0.50 , "3" : 0.40 },
    "W限定池":{"6" : 0.02 , "5" : 0.08 , "4" : 0.50 , "3" : 0.40 },
    "常驻池" : {"6" : 0.02 , "5" : 0.08 , "4" : 0.50 , "3" : 0.40 }
}


ROLE_ARMS_LIST = {
    # 所有卡池数据

    "W限定6星up": [],
    "年限定6星up": [],
    "迷迭香限定6星up": [],
    "W限定5星up": [],
    "年限定5星up": [],
    "迷迭香限定5星up": [],
    "迷迭香限定4星up": [],
    "常驻6星up": [],
    "常驻6星": [],
    "常驻5星up": [],
    "常驻5星": [],
    "常驻4星up": [],
    "常驻4星": [],
    "常驻3星": [],

    "空":[], #这个列表是留空占位的，不会有任何数据

    '6星全角色':[],

    '6星常驻池':[],
    '5星常驻池':[],
    '4星常驻池':[],
    '3星常驻池':[],

    '6星迷迭香限定池':[],
    '6星W限定池':[],
    '6星年限定池':[],
}


CORRESPONDENCE = {
    # 这里记录的是ROLE_ARMS_LIST最后7个列表与其他列表的包含关系
    '6星全角色':["W限定6星up","年限定6星up","迷迭香限定6星up","常驻6星"],

    '6星常驻池':["常驻6星"],
    '5星常驻池':["常驻5星"],
    '4星常驻池':["常驻4星"],
    '3星常驻池':["常驻3星"],

    '6星迷迭香限定池':["迷迭香限定6星up","常驻6星"],
    '6星W限定池':["W限定6星up","常驻6星"],
    '6星年限定池':["年限定6星up","常驻6星"],
}


POOL = {
    # 这个字典记录的是3个不同的卡池，每个卡池的抽取列表的value是ROLE_ARMS_LIST的哪个列表的key
    # 比如角色UP池的5星UP列表value是"5星up角色"，就表示角色UP池的5星UP列表是保存在ROLE_ARMS_LIST["5星up角色"]这个列表里的
    '常驻池':{
        '6星up':"常驻6星up",
        '随机全6星':'6星常驻池',
        '5星up':"常驻5星up",
        '随机全5星':'5星常驻池',
        '4星up':"常驻4星up",
        '随机全4星':'4星常驻池'
    },

    '迷迭香限定池':{
        '6星up':"迷迭香限定6星up",
        '随机全6星':'6星常驻池',
        '5星up':"迷迭香限定5星up",
        '随机全5星':'5星常驻池',
        '4星up':"迷迭香限定4星up",
        '随机全4星':'4星常驻池'
    },

    '年限定池':{
        '6星up':"年限定6星up",
        '随机全6星':'6星常驻池',
        '5星up':"年限定5星up",
        '随机全5星':'5星常驻池',
        '4星up':"常驻4星up",
        '随机全4星':'4星常驻池'
    },
    
    'W限定池':{
        '6星up':"W限定6星up",
        '随机全6星':'6星常驻池',
        '5星up':"W限定5星up",
        '随机全5星':'5星常驻池',
        '4星up':"常驻4星up",
        '随机全4星':'4星常驻池'
    },
}







def init_role_arms_list():
    # 初始化卡池数据
    with open(os.path.join(FILE_PATH,'config.json'),'r', encoding='UTF-8') as f:
        data = json.load(f)
        for key in data.keys():
            ROLE_ARMS_LIST[key] = data[key]

    for key in CORRESPONDENCE.keys():
        for i in CORRESPONDENCE[key]:
            ROLE_ARMS_LIST[key].extend(ROLE_ARMS_LIST[i]) # 对后7个列表填充数据
        ROLE_ARMS_LIST[key] = list(set(ROLE_ARMS_LIST[key])) # 去除重复数据

init_role_arms_list()








class Gacha(object):

    def __init__(self,_pool = DEFAULT_POOL):
        # 实例化的时候就要传进来字符串表明要抽哪个卡池
        self.pool = _pool

        self.last_time_5 = "" # 记录上一次抽卡的5星是什么
        self.last_time_4 = "" # 记录上一次抽卡的4星是什么

        # 保底计数,注意这个计数是从0开始的，每一次抽卡（包括第一次）之前都得+1
        self.distance_5_star = 0
        self.distance_6_star = 0

        # 需要生成图片的抽卡结果列表
        self.gacha_list = []

        # 记录多少抽第一次出现UP
        self.last_6_up = 0
        self.last_4_up = 0
        self.last_5_up = 0

        # 记录多少抽第一次出现4星或5星
        self.last_4 = 0
        self.last_5 = 0
        self.last_6 = 0

        self.gacha_rarity_statistics = {
            # 这个列表记录的是本轮抽卡，每种稀有度各抽到了多少
            '3星': 0,
            '4星': 0,
            '5星': 0,
            '6星': 0
        }

        # 当前是多少抽
        self.current_times = 0

        # 记录抽卡每个角色或装备各抽到多少
        self.gacha_all_statistics = {}


    #complete
    @staticmethod
    def get_png_path(name):
        # 获取png文件路径，传入的参数是角色或武器名字，会自动在角色和武器文件夹搜索，找不到抛出异常

        role_name_path = os.path.join(ICON_PATH, "角色", str(name) + ".png")
        arms_name_path = os.path.join(ICON_PATH, "武器", str(name) + ".png")
        if os.path.exists(role_name_path):
            return role_name_path

        if os.path.exists(arms_name_path):
            return arms_name_path

        raise FileNotFoundError(f"找不到 {name} 的图标，请检查图标是否存在")

    #complete
    def is_up(self,name):
        # 检查角色是否在UP里

        _6_star_up_list = POOL[self.pool]["6星up"]
        _5_star_up_list = POOL[self.pool]["5星up"]
        _4_star_up_list = POOL[self.pool]["4星up"]

        if (name in ROLE_ARMS_LIST[_4_star_up_list]) or (name in ROLE_ARMS_LIST[_5_star_up_list]) or (name in ROLE_ARMS_LIST[_6_star_up_list]):
            return True

        return False


    #complete
    @staticmethod
    def is_star(name):
        # 检查角色或物品是几星的
        # 返回对应的星星数
        if name in ROLE_ARMS_LIST['6星全角色']:
            return "★★★★★★"
        if name in ROLE_ARMS_LIST['5星常驻池']:
            return "★★★★★"
        if name in ROLE_ARMS_LIST['4星常驻池']: # 4星常驻池就包含所有4星角色装备了
            return "★★★★"
        return "★★★"

    #complete
    @staticmethod
    def pic2b64(im):
        # im是Image对象，把Image图片转成base64
        bio = BytesIO()
        im.save(bio, format='PNG')
        base64_str = base64.b64encode(bio.getvalue()).decode()
        return 'base64://' + base64_str

    #complete
    @staticmethod
    def ba64_to_cq(base64_str):
        return f"[CQ:image,file={base64_str}]"

    #complete
    def concat_pic(self, border=5):
        # self.gacha_list是一个列表，这个函数找到列表中名字对应的图片，然后拼接成一张大图返回
        num = len(self.gacha_list)
        # w, h = pics[0].size
        w, h = [180, 180]
        des = Image.new('RGBA', (w * min(num, border), h * math.ceil(num / border)), (255, 255, 255, 0))

        for i in range(num):
            im = Image.open(self.get_png_path(self.gacha_list[i]))

            pixel_w_offset = (125 - im.size[0]) / 2
            pixel_h_offset = (130 - im.size[1]) / 2  # 因为角色和武器大小不一样，小的图像设置居中显示

            w_row = (i % border) + 1
            h_row = math.ceil((i + 1) / border)

            pixel_w = (w_row - 1) * w + pixel_w_offset
            pixel_h = (h_row - 1) * h + pixel_h_offset

            des.paste(im, (int(pixel_w), int(pixel_h)))

        return des

    #complete
    def add_gacha_all_statistics(self,name):
        # 把每一次抽卡结果添加到gacha_all_statistics
        if name in self.gacha_all_statistics.keys():
            self.gacha_all_statistics[name] += 1
        else:
            self.gacha_all_statistics[name] = 1

    def update_last(self,name):
        # 这个方法用来更新第一次抽到4星或5星或6星或UP的计数
        if not self.last_4_up:
            up_4_star = POOL[self.pool]['4星up']
            if name in ROLE_ARMS_LIST[up_4_star]:
                self.last_4_up = self.current_times + 1

        if not self.last_5_up:
            up_5_star = POOL[self.pool]['5星up']
            if name in ROLE_ARMS_LIST[up_5_star]:
                self.last_5_up = self.current_times + 1

        if not self.last_6_up:
            up_6_star = POOL[self.pool]['6星up']
            if name in ROLE_ARMS_LIST[up_6_star]:
                self.last_6_up = self.current_times + 1

        if not self.last_4:
            if name in ROLE_ARMS_LIST["4星常驻池"]:
                self.last_4 = self.current_times + 1

        if not self.last_5:
            if name in ROLE_ARMS_LIST["常驻5星"]:
                self.last_5 = self.current_times + 1

        if not self.last_6:
            if name in ROLE_ARMS_LIST["6星全角色"]:
                self.last_6 = self.current_times + 1

    #complete
    def get_most_arms(self):
        # 返回抽出的角色抽出最多的是哪个，抽出了多少次
        if not self.gacha_all_statistics:
            raise KeyError(f"字典 self.gacha_all_statistics 是空的")
        most_value = max(self.gacha_all_statistics.values())
        for key,value in self.gacha_all_statistics.items():
            if most_value == value :
                return {"name":key,"most":value}

    #complete
    def get_6_star(self):
        # 检查是否有UP，如果有UP此次抽取70%概率为UP内
        
        all_6_star = POOL[self.pool]['随机全6星']
        if not POOL[self.pool]['6星up']:
            return random.choice(ROLE_ARMS_LIST[all_6_star])

        up_6_star = POOL[self.pool]['6星up']

        rsix = random.random()

        if rsix < 0.7:
            return random.choice(ROLE_ARMS_LIST[up_6_star])
        return random.choice(ROLE_ARMS_LIST[all_6_star])
        
    #complete
    def get_5_star(self):
        # 检查是否有UP，如果有UP此次抽取50%概率为UP内

        all_5_star = POOL[self.pool]['随机全5星']
        if not POOL[self.pool]['5星up']:
            return random.choice(ROLE_ARMS_LIST[all_5_star])

        up_5_star = POOL[self.pool]['5星up']

        rfive = random.random()

        if rfive < 0.5:
            return random.choice(ROLE_ARMS_LIST[up_5_star])
        return random.choice(ROLE_ARMS_LIST[all_5_star])

    #complete
    def get_4_star(self):
        # 检查是否有UP，如果有UP此次抽取20%概率为UP内

        all_4_star = POOL[self.pool]['随机全4星']
        if not POOL[self.pool]['4星up']:
            return random.choice(ROLE_ARMS_LIST[all_4_star])

        up_4_star = POOL[self.pool]['4星up']

        rfour = random.random()

        if rfour < 0.2:
            return random.choice(ROLE_ARMS_LIST[up_4_star])
        return random.choice(ROLE_ARMS_LIST[all_4_star])


    #complete
    def gacha_one(self):
        # self.last_time_4表示上一个4星角色
        # self.last_time_5表示上一个5星角色
        # self.distance_4_star是4星保底计数
        # self.distance_5_star是5星保底计数
        self.distance_5_star += 1
        self.distance_6_star += 1
        prosix = POOL_PROBABILITY[self.pool]["6"]
        profive = POOL_PROBABILITY[self.pool]["5"]
        profour = POOL_PROBABILITY[self.pool]["4"]
        prothree = POOL_PROBABILITY[self.pool]["3"]
        #定义本次抽卡的概率，50次未出提升6x几率
        if self.distance_6_star >=50:
            prosix += 0.02*(self.distance_6_star-49)
            profive = (1-prosix)/(1-POOL_PROBABILITY[self.pool]["6"])*POOL_PROBABILITY[self.pool]["5"]
            profour = (1-prosix)/(1-POOL_PROBABILITY[self.pool]["6"])*POOL_PROBABILITY[self.pool]["4"]
            prothree = (1-prosix)/(1-POOL_PROBABILITY[self.pool]["6"])*POOL_PROBABILITY[self.pool]["3"]

        r = random.random()

        # 检查是不是概率6星
        if r < prosix:
            self.gacha_rarity_statistics["6星"] += 1
            self.distance_6_star = 0
            self.last_time_6 = self.get_6_star()  # 抽一次卡，把结果赋值留给下一次抽卡判断
            return self.last_time_6  # 返回刚抽出的卡

        # 检查是不是保底5星
        if self.current_times == 10:
            if self.distance_6_star ==10:
                if self.distance_5_star ==10:
                    self.gacha_rarity_statistics["5星"] += 1
                    self.distance_5_star = 0 # 重置保底计数
                    self.last_time_5 = self.get_5_star() # 抽一次卡，把结果赋值留给下一次抽卡判断
                    return self.last_time_5 # 返回刚抽出的卡

        # 检查是不是概率5星
        if r < (prosix + profive):
            self.gacha_rarity_statistics["5星"] += 1
            self.distance_5_star = 0
            self.last_time_5 = self.get_5_star()  # 抽一次卡，把结果赋值留给下一次抽卡判断
            return self.last_time_5  # 返回刚抽出的卡


        # 检查是不是概率4星
        if r < (prosix + profive + profour):
            self.gacha_rarity_statistics["4星"] += 1
            self.last_time_4 = self.get_4_star()
            return self.last_time_4

        # 以上都不是返回3星
        self.gacha_rarity_statistics["3星"] += 1
        return random.choice(ROLE_ARMS_LIST["常驻3星"])



    #complete
    def gacha_10(self):
        # 抽10连

        gacha_txt = ""

        for self.current_times in range(10):

            new_gacha = self.gacha_one()
            self.gacha_list.append(new_gacha)
            gacha_txt += new_gacha
            gacha_txt += self.is_star(new_gacha)

            if (self.current_times + 1) % 5 == 0:
                gacha_txt += '\n'

            self.add_gacha_all_statistics(new_gacha)  # 把所有抽卡结果添加到gacha_all_statistics用于最后统计

            self.update_last(new_gacha) # 更新第一次抽到的计数

        mes = '本次抽卡得到以下角色：\n'
        res = self.concat_pic()
        res = self.pic2b64(res)
        mes += self.ba64_to_cq(res)
        mes += '\n'
        mes += gacha_txt

        if self.last_4: # 如果self.last_4为0表示没有抽到，这句话就不写了，下边3个判断标准一样
            mes += f'第 {self.last_4} 抽首次出现4★!\n'
        if self.last_4_up:
            mes += f'第 {self.last_4_up} 抽首次出现4★UP!\n'
        if self.last_5:
            mes += f'第 {self.last_5} 抽首次出现5★!\n'
        if self.last_5_up:
            mes += f'第 {self.last_5_up} 抽首次出现5★UP!\n'
        if self.last_6:
            mes += f'第 {self.last_6} 抽首次出现6★!\n'
        if self.last_6_up:
            mes += f'第 {self.last_6_up} 抽首次出现6★UP!\n'

        mes += f"\n* 本次抽取卡池为 {self.pool} \n* 发送 方舟卡池切换 可切换卡池"

        return mes


    #complete
    def gacha_90(self,frequency=100):
        # 抽一井
        gacha_txt = ""

        for self.current_times in range(frequency):

            new_gacha = self.gacha_one()

            if new_gacha in ROLE_ARMS_LIST["6星全角色"]: # 抽一井时图片上不保留3星4星
                self.gacha_list.append(new_gacha)
            if new_gacha in ROLE_ARMS_LIST["5星常驻池"]: # 抽一井时图片上不保留3星4星
                self.gacha_list.append(new_gacha)

            self.add_gacha_all_statistics(new_gacha) # 把所有抽卡结果添加到gacha_all_statistics用于最后统计

            self.update_last(new_gacha)  # 更新第一次抽到的计数

        gacha_txt += f"★★★★★★×{self.gacha_rarity_statistics['6星']}    ★★★★★×{self.gacha_rarity_statistics['5星']}    ★★★★×{self.gacha_rarity_statistics['4星']}    ★★★×{self.gacha_rarity_statistics['3星']}\n"

        mes = '本次抽卡得到以下角色：\n'
        res = self.concat_pic()
        res = self.pic2b64(res)
        mes += self.ba64_to_cq(res)
        mes += '\n'
        mes += gacha_txt

        if self.last_4: # 如果self.last_4为0表示没有抽到，这句话就不写了
            mes += f'第 {self.last_4} 抽首次出现4★!\n'
        if self.last_4_up:
            mes += f'第 {self.last_4_up} 抽首次出现4★UP!\n'
        if self.last_5:
            mes += f'第 {self.last_5} 抽首次出现5★!\n'
        if self.last_5_up:
            mes += f'第 {self.last_5_up} 抽首次出现5★UP!\n'
        if self.last_6:
            mes += f'第 {self.last_6} 抽首次出现6★!\n'
        if self.last_6_up:
            mes += f'第 {self.last_6_up} 抽首次出现6★UP!\n'

        most_arms = self.get_most_arms()
        mes += f"本次抽取最多的角色是 {most_arms['name']} {self.is_star(most_arms['name'])} ,共抽取到 {most_arms['most']} 次\n"

        mes += f"\n* 本次抽取卡池为 {self.pool} \n* 发送 方舟卡池切换 可切换卡池"
        return mes



def gacha_info(pool = DEFAULT_POOL):
    # 重载卡池数据，然后返回UP角色信息
    init_role_arms_list() # 重新载入config.json的卡池数据
    info_txt = f'当前卡池为 {pool} ，UP信息如下：\n'

    _6_star_up_info = POOL[pool]["6星up"]
    _5_star_up_info = POOL[pool]["5星up"]
    _4_star_up_info = POOL[pool]["4星up"]
    up_info = ""

    for _6_star in ROLE_ARMS_LIST[_6_star_up_info]:
        im = Image.open(Gacha.get_png_path(_6_star))
        im = Gacha.pic2b64(im)
        up_info += Gacha.ba64_to_cq(im)
        up_info += "\n"
        up_info += f"{_6_star} ★★★★★★"

    for _5_star in ROLE_ARMS_LIST[_5_star_up_info]:
        im = Image.open(Gacha.get_png_path(_5_star))
        im = Gacha.pic2b64(im)
        up_info += Gacha.ba64_to_cq(im)
        up_info += "\n"
        up_info += f"{_5_star} ★★★★★"

    for _4_star in ROLE_ARMS_LIST[_4_star_up_info]:
        im = Image.open(Gacha.get_png_path(_4_star))
        im = Gacha.pic2b64(im)
        up_info += Gacha.ba64_to_cq(im)
        up_info += "\n"
        up_info += f"{_4_star} ★★★★"

    if up_info == "":
        # 如果up_info是空的，表示当前是常驻池没有UP
        up_info += "没有UP"

    info_txt += up_info
    return info_txt


