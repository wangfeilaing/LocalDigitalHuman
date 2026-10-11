from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1] / "data" / "broll"
INDEX_PATH = ROOT / "broll-index.json"


def words(value: str) -> list[str]:
    return [part for part in value.split() if part]


def review(
    category: str,
    summary: str,
    scenes: str,
    emotions: str,
    subjects: str,
    actions: str,
    themes: str,
    flags: str = "",
    mode: str = "ready",
    similar_to: str = "",
) -> dict:
    return {
        "primaryCategory": category,
        "visualSummary": summary,
        "sceneTags": words(scenes),
        "emotionTags": words(emotions),
        "subjectTags": words(subjects),
        "actionTags": words(actions),
        "themeTags": words(themes),
        "qualityFlags": words(flags),
        "useMode": mode,
        "similarTo": similar_to or None,
    }


REVIEWS = {
    "A001": review("情绪氛围", "暴雨积水的院落中有人躺在水里戏水", "暴雨 积水 院落 户外", "释放 乐观 荒诞", "人物", "戏水", "逆境乐观 情绪释放"),
    "A002": review("情绪氛围", "雨夜城市街道与撑伞行人", "城市 雨夜 街道", "孤独 惆怅", "行人", "行走 撑伞", "低落 回忆 城市孤独"),
    "A003": review("亲密关系", "夜晚车窗外手持红色发光爱心", "夜晚 车内 霓虹", "浪漫 思念", "手部 爱心", "手持", "爱情 表白 思念"),
    "A004": review("情绪氛围", "乌云下巨浪拍打海岸堤坝", "海洋 风暴 乌云", "压迫 震撼", "海浪", "翻涌", "困境 情绪风暴 压力"),
    "A005": review("个人成长", "镜面海面上的小船与巨大云墙", "天空 海面 梦境", "梦幻 希望 辽阔", "小船 人物", "航行", "梦想 人生旅程 希望"),
    "A006": review("个人成长", "燃烧的植物化为发光碎片", "暗场 火焰 抽象", "强烈 释放", "植物 火焰", "燃烧 消散", "告别 重生 转变 情绪爆发"),
    "A007": review("亲密关系", "夜晚餐馆外独自打电话的女子", "城市 夜晚 餐馆", "孤独 等待 焦虑", "女性 手机", "打电话 等待", "情感关系 思念 独处"),
    "A008": review("情绪氛围", "暴雨城市、田野背影与雨夜长椅组成的伤感合集", "暴雨 城市 田野 夜晚", "孤独 压抑 悲伤", "人物 背影", "独处", "情绪低谷 城市孤独", "多镜头合集 水印", "review"),
    "A009": review("情绪氛围", "昏暗房间里透过百叶窗看到城市夜景", "室内 窗边 夜晚", "安静 孤独 压抑", "窗户", "静止", "深夜 独处 沉思"),
    "A010": review("情绪氛围", "暴雨城市、田野背影与雨夜长椅组成的伤感合集", "暴雨 城市 田野 夜晚", "孤独 压抑 悲伤", "人物 背影", "独处", "情绪低谷 城市孤独", "近似重复 多镜头合集 水印", "disabled", "A008"),
    "A011": review("情绪氛围", "雨滴、草地小狗与风中人物组成的混剪", "雨天 草地 山野", "治愈 孤独", "小狗 人物", "眺望", "日常 治愈 独处", "多镜头合集", "review"),
    "A012": review("个人成长", "云层裂开光束照向雪山与城市", "天空 雪山 云层", "希望 神圣 震撼", "光束 山脉", "照耀", "希望 信念 启示 转机"),
    "A013": review("亲密关系", "黑夜中沾着水珠的红玫瑰特写", "夜晚 花卉 特写", "浪漫 深情", "玫瑰", "绽放", "爱情 浪漫 纪念"),
    "A014": review("亲密关系", "红玫瑰爆裂成花瓣和碎片", "暗场 花卉 抽象", "激烈 心碎", "玫瑰 花瓣", "破碎 飘散", "分手 爱情受伤 告别"),
    "A015": review("个人成长", "第一视角躺在海边山坡眺望阴天大海", "海边 山坡 阴天", "平静 孤独 松弛", "人物双腿 大海", "躺卧 眺望", "独处 休息 人生思考"),
    "A016": review("情绪氛围", "雨天室内透过纱帘看阳台与远景", "室内 窗边 雨天", "安静 孤独", "窗帘 阳台", "静止", "雨天 独处 沉思"),
    "A017": review("心理健康", "阴沉海面中一只手伸出水面", "海洋 阴天 水中", "无助 渴望 压抑", "手部 海水", "伸手", "求助 救赎 情绪低谷", "溺水联想", "review"),
    "A018": review("心理健康", "昏暗绿色画面中人物蜷缩躺卧", "室内 暗场", "压抑 疲惫 孤独", "人物", "躺卧 蜷缩", "情绪低谷 失眠 抑郁", "画面模糊 内嵌文字", "review"),
    "A019": review("情绪氛围", "雨天室内透过纱帘看阳台与远景", "室内 窗边 雨天", "安静 孤独", "窗帘 阳台", "静止", "雨天 独处 沉思", "内容重复", "disabled", "A016"),
    "A020": review("心理健康", "昏暗绿色画面中人物蜷缩躺卧", "室内 暗场", "压抑 疲惫 孤独", "人物", "躺卧 蜷缩", "情绪低谷 失眠 抑郁", "内容重复 内嵌文字", "disabled", "A018"),
    "A021": review("情绪氛围", "夜晚车内独坐的女子与流动霓虹", "车内 城市 夜晚", "迷茫 孤独", "女性", "独坐", "逃离 夜生活 情绪低谷"),
    "A022": review("情绪氛围", "暴雨城市、田野背影与雨夜长椅组成的伤感合集", "暴雨 城市 田野 夜晚", "孤独 压抑 悲伤", "人物 背影", "独处", "情绪低谷 城市孤独", "近似重复 多镜头合集 水印", "disabled", "A008"),
    "A023": review("情绪氛围", "空旷雨夜街道上独自张开双臂的人", "雨夜 街道 路灯", "孤独 释放", "人物", "站立 张开双臂", "情绪释放 接纳 风雨"),
    "A024": review("情绪氛围", "雨中的手臂与灰暗海面", "雨天 海边 特写", "孤独 冰冷", "手臂 海水", "触碰", "低落 疏离 回忆"),
    "A025": review("个人成长", "坐在行驶列车门边看沿途风景的人", "列车 旅途 山野", "离别 平静 孤独", "人物", "乘车 眺望", "出发 告别 人生旅程"),
    "A026": review("情绪氛围", "乌云下巨浪拍打海岸堤坝", "海洋 风暴 乌云", "压迫 震撼", "海浪", "翻涌", "困境 情绪风暴 压力", "内容重复", "disabled", "A004"),
    "A027": review("心理健康", "昏黄灯光下人物的压抑剪影", "夜晚 暗场 剪影", "焦虑 压抑", "人物剪影", "抱头", "压力 痛苦 情绪崩溃"),
    "A028": review("个人成长", "落日海边一个人缓慢走过", "海边 日落", "释然 温暖", "人物剪影", "行走", "告别 向前走 希望", "片头内嵌文字", "review"),
    "A029": review("情绪氛围", "暴雨城市、田野背影与雨夜长椅组成的伤感合集", "暴雨 城市 田野 夜晚", "孤独 压抑 悲伤", "人物 背影", "独处", "情绪低谷 城市孤独", "内容重复 多镜头合集 水印", "disabled", "A008"),
    "A030": review("亲子家庭", "婴儿委屈哭泣的面部特写", "车内 近景", "委屈 难过", "婴儿", "哭泣", "婴幼儿情绪 亲子安抚"),
    "A031": review("情绪氛围", "穿连帽衣的人独坐海边木阶", "海边 黄昏 木阶", "孤独 沉思", "人物背影", "坐下 眺望", "独处 等待 人生思考"),
    "A032": review("心理健康", "女子在旧建筑和窗边独自沉思", "室内 窗边 日落", "孤独 迷茫", "女性", "站立 眺望", "等待 情绪低谷 自我对话"),
    "A033": review("情绪氛围", "暴雨城市、田野背影与雨夜长椅组成的伤感合集", "暴雨 城市 田野 夜晚", "孤独 压抑 悲伤", "人物 背影", "独处", "情绪低谷 城市孤独", "内容重复 多镜头合集 水印", "disabled", "A008"),
    "A034": review("情绪氛围", "车内夜景转为户外烟花庆祝", "车内 户外 黄昏", "兴奋 欢庆", "人物 烟花", "燃放 奔跑", "庆祝 青春 快乐", "多镜头合集", "review"),
    "A035": review("心理健康", "黑白剪影中人物被阴影和情绪困住", "室内 黑白 剪影", "压抑 恐惧", "人物剪影", "蜷缩 挣扎", "心理困境 情绪崩溃 自我束缚", "内嵌文字", "review"),
    "A036": review("城市生活", "夜晚城市天桥上独自行走的女子", "城市 天桥 夜晚", "孤独 克制", "女性", "行走", "城市独处 职场归途 独立"),
    "A037": review("情绪氛围", "秋夜雨后铺满落叶的街道", "城市 雨夜 秋天", "怀旧 安静", "落叶 街道", "静止", "回忆 秋天 深夜"),
    "A038": review("情绪氛围", "海边黄昏围坐篝火的人群", "海边 黄昏 篝火", "温暖 治愈", "人物 火焰", "围坐", "陪伴 聚会 松弛 治愈"),
    "A039": review("城市生活", "城市夜景虚化背景下手持手机", "城市 夜晚 街头", "日常 疏离", "手机 手部", "浏览手机", "社交媒体 数字生活 沟通"),
    "A040": review("情绪氛围", "夜晚路灯下大片雪花飘落", "城市 夜晚 冬季", "安静 浪漫", "路灯 雪花", "飘雪", "冬天 思念 治愈"),
    "A041": review("心理健康", "蓝色水下女子缓慢下沉", "水下 暗场", "压抑 窒息", "女性", "下沉", "压力 情绪低谷 救赎", "溺水联想", "review"),
    "A042": review("个人成长", "女子和狗并肩看向草原与马群", "草原 山野 乡村", "平静 治愈", "女性 狗 马", "坐下 眺望", "陪伴 自然疗愈 慢生活"),
    "A043": review("城市生活", "金色夜景街头独自停留的女子", "城市 夜晚 街道", "独立 孤独", "女性", "站立 等待", "城市女性 独处 独立"),
    "A044": review("亲密关系", "手持粉色玫瑰花束", "户外 花卉 特写", "浪漫 喜悦", "花束", "手持", "爱情 礼物 约会"),
    "A045": review("亲密关系", "手捧红粉玫瑰花束向前走", "户外 花卉 日常", "浪漫 期待", "花束 手部", "行走 手持", "爱情 礼物 纪念日"),
    "V001": review("心理健康", "女子坐在床上捂脸哭泣", "卧室 床边", "悲伤 焦虑", "女性", "哭泣 捂脸", "压力 情绪崩溃 抑郁"),
    "V002": review("睡眠健康", "女子深夜卧床看手机后疲惫入睡", "卧室 夜晚 清晨", "疲惫 无精打采", "女性 手机", "看手机 睡觉", "熬夜 蓝光 睡眠健康 手机依赖"),
    "V003": review("亲密关系", "昏暗房间里两人通过影子交流争执", "室内 暗场 剪影", "克制 矛盾", "男性", "交谈 争执", "沟通 理解 包容 关系", "内嵌字幕", "review"),
    "V004": review("职场社会", "包含家庭、饭局和职场人物的十分钟剧情成片", "室内 饭局 职场", "复杂", "多人", "对话 用餐", "人际关系 职场 家庭", "超长视频 多镜头成片 内嵌字幕 需切片", "review"),
    "V005": review("亲子家庭", "夜晚男子受挫与母女互动组成的剧情混剪", "夜晚 街头 家庭", "难过 温情", "男性 母亲 女孩", "哭泣 牵手", "家庭 和解 亲情", "多镜头成片 内嵌字幕 需切片", "review"),
    "V006": review("睡眠健康", "失眠女子起床服用助眠药后入睡", "卧室 夜晚", "焦虑 疲惫 安心", "女性 药物", "起床 服药 睡觉", "失眠 焦虑 睡眠健康", "内嵌字幕", "review"),
    "V007": review("亲密关系", "大面积粉色和橙色玫瑰花田", "花田 户外 自然", "浪漫 美好", "玫瑰", "盛开", "爱情 美好 自然"),
    "V008": review("社会人文", "老人独自坐在城市路边", "城市 路边 白天", "孤独 心酸", "老人", "坐下", "老年生活 困境 关怀"),
    "V009": review("亲密关系", "庭院墙边盛开的爬藤玫瑰", "庭院 花园", "浪漫 治愈", "玫瑰 植物", "盛开", "爱情 生活美学 自然"),
    "V010": review("个人成长", "女子在高山花海中自由奔跑", "高山 草地 花海", "自由 喜悦", "女性", "奔跑", "自由 成长 远方 梦想"),
    "V011": review("个人成长", "日出照亮绿色山谷和风力发电机", "山谷 日出 草地", "希望 活力", "太阳 风机", "推进", "新生 希望 未来 能量"),
    "V012": review("成长教育", "背书包的孩子独自走在乡村上学路上", "乡村 道路 白天", "朴实 坚定", "儿童 书包", "步行 上学", "教育 坚持 成长 求学"),
    "V013": review("亲密关系", "情侣在古典长廊中奔跑拥抱", "长廊 旅行 日光", "浪漫 喜悦", "情侣", "奔跑 拥抱", "爱情 约会 幸福"),
    "V014": review("亲子家庭", "父母孩子和宠物在明亮厨房互动", "家庭 厨房 室内", "温暖 幸福", "父母 儿童 宠物", "做饭 陪伴", "家庭生活 亲子 陪伴"),
    "V015": review("亲子家庭", "父母陪幼儿在夜晚公园散步", "公园 夜晚", "温暖 快乐", "父母 幼儿", "散步 陪伴", "亲子 成长 家庭陪伴"),
    "V016": review("亲子家庭", "夕阳把成人和孩子的影子投在墙上", "街边 夕阳 墙面", "温暖 诗意", "成人 儿童 影子", "互动", "亲子陪伴 成长 时光"),
    "V017": review("亲密关系", "昏暗房间里两人通过影子交流争执", "室内 暗场 剪影", "克制 矛盾", "男性", "交谈 争执", "沟通 理解 包容 关系", "内容重复 内嵌字幕", "disabled", "V003"),
    "V018": review("亲子家庭", "父母陪幼儿在夜晚公园散步", "公园 夜晚", "温暖 快乐", "父母 幼儿", "散步 陪伴", "亲子 成长 家庭陪伴", "内容重复", "disabled", "V015"),
    "V019": review("职场社会", "包含会议、同事与情感对话的职场剧情成片", "办公室 户外 家庭", "压力 难过", "职场男女", "开会 交谈", "职场关系 女性压力 人际沟通", "长视频 多镜头成片 内嵌字幕 需切片", "review"),
    "V020": review("亲子家庭", "父母孩子和宠物在明亮厨房互动", "家庭 厨房 室内", "温暖 幸福", "父母 儿童 宠物", "做饭 陪伴", "家庭生活 亲子 陪伴", "内容重复", "disabled", "V014"),
    "V021": review("亲子家庭", "夕阳把成人和孩子的影子投在墙上", "街边 夕阳 墙面", "温暖 诗意", "成人 儿童 影子", "互动", "亲子陪伴 成长 时光", "内容重复", "disabled", "V016"),
    "V022": review("亲密关系", "情侣在古典长廊中奔跑拥抱", "长廊 旅行 日光", "浪漫 喜悦", "情侣", "奔跑 拥抱", "爱情 约会 幸福", "内容重复", "disabled", "V013"),
    "V023": review("成长教育", "青蛙效应动画与课堂孩子组成的寓言视频", "动画 课堂", "警醒 励志", "青蛙 学生", "加热 学习", "积累 习惯 成长 教育", "多镜头成片 内嵌字幕 需切片", "review"),
    "V024": review("亲子家庭", "乡村与游乐场儿童成长主题的长剧情", "乡村 游乐场 户外", "温暖 励志", "儿童 家长", "玩耍 行走", "儿童成长 挫折 独立", "超长视频 多镜头成片 内嵌字幕 需切片", "review"),
    "V025": review("亲子家庭", "一家人在金黄秋林中散步", "公园 秋天 林间", "温暖 幸福", "父母 儿童", "散步 抱孩子", "家庭陪伴 亲子 秋日"),
    "V026": review("心理健康", "女子蜷缩倒在室内地面", "室内 地面", "疲惫 痛苦", "女性", "倒地 蜷缩", "身体不适 情绪崩溃 疲惫", "不适画面", "review"),
    "V027": review("亲密关系", "客厅中女子与坐在沙发上的男子争执", "家庭 客厅", "生气 冲突", "男女", "争吵 对峙", "伴侣冲突 家庭矛盾 沟通", "疑似剧情原声", "review"),
    "V028": review("个人成长", "雕塑木偶与文字组成的哲理讲解长视频", "抽象 雕塑 暗场", "压迫 警醒", "木偶 雕塑", "操控 对视", "人性 经济规律 关系博弈", "超长视频 多镜头成片 内嵌字幕 需切片", "review"),
    "V029": review("亲子家庭", "父亲在客厅训斥孩子", "家庭 客厅", "生气 紧张", "父亲 儿童", "训斥", "家庭教育 亲子冲突 沟通", "内嵌字幕", "review"),
    "V030": review("成长教育", "孩子在夜市摊位独自掌勺做饭", "夜市 摊位 夜晚", "认真 坚强", "儿童", "做饭 劳作", "独立 成长 生活教育"),
    "V031": review("社会人文", "电影片段组成的老年人与家庭长剧情", "家庭 餐桌 夜晚", "心酸 温情", "老人 家人", "用餐 交谈", "老年生活 家庭 亲情", "超长视频 横屏嵌套 黑边 内嵌字幕 需切片", "review"),
    "V032": review("亲子家庭", "动画与纪实画面讲述童年伤害", "动画 街头 横屏", "压抑 警醒", "儿童 成人", "争执 回忆", "童年创伤 家庭教育 心理", "多镜头成片 横屏嵌套 黑边 内嵌字幕", "review"),
    "V033": review("亲子家庭", "阳光下成人的手伸向床上的婴儿", "卧室 清晨", "温暖 安心", "婴儿 手部", "伸手 互动", "依恋 安抚 亲子连接"),
    "V034": review("亲子家庭", "母亲陪两个幼儿在家里玩耍", "家庭 客厅 冬季", "快乐 温暖", "母亲 儿童", "玩耍 互动", "亲子陪伴 手足 家庭生活"),
    "V035": review("亲子家庭", "母亲为床上的婴儿做细致护理", "卧室 床边", "温柔 安心", "母亲 婴儿", "护理 安抚", "育儿 母爱 婴儿护理"),
    "V036": review("亲子家庭", "穿防护服的家长一路抱着孩子回家", "停车场 楼道", "疲惫 保护", "家长 儿童", "抱孩子 行走 上楼", "父母守护 生病 家庭责任", "内嵌字幕", "review"),
    "V037": review("亲子家庭", "监控视角下母亲应对哭闹孩子", "家庭 客厅 监控", "崩溃 烦躁", "母亲 儿童", "安抚 哭闹", "育儿压力 亲子沟通 情绪管理", "监控时间戳 内嵌字幕", "review"),
    "V038": review("睡眠健康", "女子卧床玩手机并演示颈部不适", "卧室 夜晚", "疲惫 不适", "女性 手机", "躺卧 看手机 按揉颈部", "睡姿 颈椎 手机依赖 睡眠", "内嵌字幕", "review"),
    "V039": review("心理健康", "女子在茶室盘腿静坐冥想", "茶室 室内 日光", "平静 专注", "女性", "冥想 静坐", "正念 情绪调节 自我疗愈"),
    "V040": review("心理健康", "职场女性、独处与被安慰组成的心理主题长片", "办公室 家庭 室内", "焦虑 难过 安慰", "女性 同事", "工作 独坐 拥抱", "心理咨询 职场压力 情绪支持", "超长视频 多镜头成片 内嵌字幕 需切片", "review"),
    "V041": review("亲密关系", "雨夜中一对男女靠近并相拥", "城市 雨夜", "浪漫 克制", "情侣", "交谈 拥抱", "爱情 和解 陪伴"),
    "V042": review("亲子家庭", "动画展示父母争吵对孩子的长期影响", "家庭 课堂 动画", "紧张 警醒", "父母 儿童", "争吵 学习", "家庭冲突 童年创伤 亲子教育", "多镜头成片 内嵌字幕", "review"),
    "V043": review("心理健康", "人物讲述父母冲突与成年后的依恋问题", "室内 暗场", "焦虑 防御", "男性", "讲述 哭泣", "童年创伤 亲密关系 回避型依恋 信任", "口播成片 大量内嵌文字", "review"),
    "V044": review("亲密关系", "白发老夫妻互相搀扶散步", "公园 秋天", "温暖 感动", "老人 夫妻", "散步 搀扶", "长久陪伴 爱情 老年生活"),
    "V045": review("个人成长", "年轻女子的妆容与面部肖像展示", "室内 人像 特写", "自信 柔和", "女性", "化妆 展示", "女性成长 自我形象 美丽"),
    "V046": review("职场社会", "职业女性在电梯和走廊打电话看文件", "写字楼 电梯 走廊", "专业 忙碌", "职业女性 手机 文件", "打电话 行走", "职场 女性成长 工作"),
    "V047": review("城市生活", "穿黑色套装的女子走进高档餐厅", "餐厅 夜晚 室内", "自信 高级", "女性", "行走 入场", "独立女性 社交 品质生活"),
    "V048": review("心理健康", "女子被困在巨大鸟笼中的象征画面", "暗场 舞台 鸟笼", "压抑 渴望", "女性 羽毛", "伸手", "束缚 自由 心理困境"),
    "V049": review("情绪氛围", "夜晚车窗后视镜与伸出的手", "车内 城市 夜晚", "离别 怀旧", "手部 后视镜", "伸手 行车", "告别 旅程 回忆"),
    "V050": review("城市生活", "行驶车辆视角中的夜晚城市道路", "城市 道路 夜晚", "孤独 平静", "路灯 建筑", "行车", "归途 城市夜景 旅程"),
    "V051": review("情绪氛围", "推门进入灯光昏暗的空客厅", "家庭 客厅 夜晚", "孤独 悬念", "门锁 空房间", "开门 进入", "回家 独处 等待"),
    "V052": review("亲子家庭", "明亮家中女子围绕摆满饭菜的餐桌忙碌", "家庭 客厅 餐厅", "温馨 忙碌", "女性 饭菜", "走动 准备饭菜", "家庭生活 团聚 烟火气"),
    "V053": review("认知科学", "发光的大脑神经网络三维动画", "抽象 科技 暗场", "理性 震撼", "大脑 神经", "发光 运转", "心理学 认知 脑科学 神经系统"),
    "V054": review("成长教育", "夕阳下背书包的孩子走在乡间道路", "乡村 道路 夕阳", "怀旧 温暖", "儿童 书包", "步行 上学", "童年 教育 成长 故乡"),
}


def status_label(mode: str) -> str:
    return {"ready": "可直接推荐", "review": "需先切片/审核", "disabled": "暂不自动调用"}[mode]


def status_color(mode: str) -> str:
    return {"ready": "#22c55e", "review": "#f59e0b", "disabled": "#ef4444"}[mode]


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf")]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def build_overview_image(data: dict) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in data["assets"]:
        grouped[item["primaryCategory"]].append(item)
    mode_counts = Counter(item["useMode"] for item in data["assets"])
    categories = sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0]))

    canvas = Image.new("RGB", (1080, 1920), "#0b1220")
    draw = ImageDraw.Draw(canvas)
    draw.text((48, 42), "B-Roll 素材初步分类", fill="#ffffff", font=font(52))
    draw.text((48, 112), "99 条素材 · 原文件未移动", fill="#94a3b8", font=font(25))
    summaries = [
        ("可直接推荐", mode_counts["ready"], "#22c55e"),
        ("需切片审核", mode_counts["review"], "#f59e0b"),
        ("暂不自动调用", mode_counts["disabled"], "#ef4444"),
    ]
    for index, (label, count, color) in enumerate(summaries):
        left = 48 + index * 328
        draw.rounded_rectangle((left, 168, left + 304, 274), radius=18, fill="#141f31", outline="#25344b", width=2)
        draw.text((left + 18, 182), str(count), fill=color, font=font(42))
        draw.text((left + 91, 198), label, fill="#e5e7eb", font=font(21))

    card_w, card_h = 312, 358
    start_x, start_y, gap_x, gap_y = 48, 320, 24, 24
    for index, (category, items) in enumerate(categories):
        row, column = divmod(index, 3)
        left = start_x + column * (card_w + gap_x)
        top = start_y + row * (card_h + gap_y)
        draw.rounded_rectangle((left, top, left + card_w, top + card_h), radius=16, fill="#141f31", outline="#25344b", width=2)
        representative = next((item for item in items if item["useMode"] == "ready"), items[0])
        with Image.open(ROOT / representative["previewFrames"][1]) as source:
            source = source.convert("RGB")
            source.thumbnail((card_w - 20, 242))
            frame = Image.new("RGB", (card_w - 20, 242), "#000000")
            frame.paste(source, ((frame.width - source.width) // 2, (frame.height - source.height) // 2))
            canvas.paste(frame, (left + 10, top + 10))
        draw.text((left + 15, top + 266), category, fill="#ffffff", font=font(25))
        draw.text((left + 15, top + 309), f"{len(items)} 条 · 示例 {representative['id']}", fill="#93c5fd", font=font(18))

    canvas.save(ROOT / "初步分类总览.jpg", quality=92)


def build_html(data: dict) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in data["assets"]:
        grouped[item["primaryCategory"]].append(item)
    mode_counts = Counter(item["useMode"] for item in data["assets"])

    sections = []
    for category in sorted(grouped):
        cards = []
        for item in grouped[category]:
            thumb = item["previewFrames"][1]
            tags = item["themeTags"] + item["sceneTags"] + item["emotionTags"]
            flags = "".join(f'<span class="flag">{html.escape(flag)}</span>' for flag in item["qualityFlags"])
            similar = f'<div class="similar">关联素材：{html.escape(item["similarTo"])}</div>' if item.get("similarTo") else ""
            cards.append(
                f"""
                <article class="card">
                  <img src="{html.escape(thumb)}" alt="{item['id']}">
                  <div class="body">
                    <div class="line"><b>{item['id']}</b><span class="status" style="--c:{status_color(item['useMode'])}">{status_label(item['useMode'])}</span></div>
                    <p>{html.escape(item['visualSummary'])}</p>
                    <div class="meta">{item['durationSeconds']:.1f}s · {item['width']}×{item['height']} · {item['fps']:.1f}fps</div>
                    <div class="tags">{''.join(f'<span>{html.escape(tag)}</span>' for tag in tags[:8])}</div>
                    <div class="flags">{flags}</div>{similar}
                  </div>
                </article>
                """
            )
        sections.append(f'<section><h2>{html.escape(category)} <small>{len(cards)} 条</small></h2><div class="grid">{"".join(cards)}</div></section>')

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>B-Roll 素材初步分类报告</title>
  <style>
    *{{box-sizing:border-box}} body{{margin:0;background:#0b1220;color:#e5e7eb;font-family:'Microsoft YaHei',sans-serif}}
    main{{max-width:1480px;margin:auto;padding:28px}} h1{{margin:0 0 10px;font-size:34px}} .lead{{color:#94a3b8;margin:0 0 22px}}
    .summary{{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0 32px}} .summary div{{background:#141f31;border:1px solid #25344b;border-radius:12px;padding:14px 18px}}
    .summary b{{display:block;font-size:25px;color:white}} h2{{margin:38px 0 14px;font-size:25px}} h2 small{{font-size:15px;color:#94a3b8;font-weight:normal}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}} .card{{display:flex;background:#141f31;border:1px solid #25344b;border-radius:14px;overflow:hidden;min-height:238px}}
    .card img{{width:132px;object-fit:cover;background:#000}} .body{{padding:13px;min-width:0;flex:1}} .line{{display:flex;align-items:center;justify-content:space-between;gap:8px}} .line b{{color:#fde047;font-size:20px}}
    .status{{font-size:12px;color:var(--c);border:1px solid var(--c);padding:3px 7px;border-radius:99px;white-space:nowrap}} p{{font-size:15px;line-height:1.55;margin:10px 0;color:#f8fafc}}
    .meta{{font-size:12px;color:#94a3b8;margin-bottom:9px}} .tags,.flags{{display:flex;flex-wrap:wrap;gap:5px}} .tags span{{font-size:12px;background:#20314a;color:#bfdbfe;padding:3px 6px;border-radius:5px}}
    .flag{{font-size:12px;background:#47212a;color:#fecaca;padding:3px 6px;border-radius:5px;margin-top:6px}} .similar{{font-size:12px;color:#fda4af;margin-top:7px}}
    .rules{{background:#141f31;border:1px solid #25344b;border-radius:14px;padding:18px 22px;line-height:1.8}} .rules li{{margin:5px 0}}
  </style>
</head>
<body><main>
  <h1>B-Roll 素材初步分类报告</h1>
  <p class="lead">原文件未移动、未改名。A 为氛围感素材，V 为画面感素材；本报告用于确认分类和后续自动匹配思路。</p>
  <div class="summary">
    <div><b>{data['assetCount']}</b>素材总数</div><div><b>{data['uniqueAssetCount']}</b>指纹去重后</div>
    <div><b>{mode_counts['ready']}</b>可直接推荐</div><div><b>{mode_counts['review']}</b>需切片/审核</div><div><b>{mode_counts['disabled']}</b>暂不自动调用</div>
  </div>
  <div class="rules"><b>后续自动插入原则</b><ol>
    <li>文案模型只分析文案，把句子转换为“主题、情绪、场景、人物、动作”标签；素材匹配使用本目录的多标签。</li>
    <li>优先选“可直接推荐”的干净单镜头；长成片、内嵌字幕、横屏黑边和多镜头素材必须先切片审核。</li>
    <li>同一条视频不连续重复，同类画面保留间隔；情绪强度与文案强度一致。</li>
    <li>B-Roll 出现时保留标题和当前字幕，隐藏人名条；素材铺满 9:16 画面，不遮盖文字安全区。</li>
  </ol></div>
  {''.join(sections)}
</main></body></html>"""


def main() -> None:
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    by_id = {item["id"]: item for item in data["assets"]}
    missing = sorted(set(by_id) - set(REVIEWS))
    unknown = sorted(set(REVIEWS) - set(by_id))
    if missing or unknown:
        raise RuntimeError(f"review id mismatch; missing={missing}, unknown={unknown}")

    for asset_id, fields in REVIEWS.items():
        item = by_id[asset_id]
        existing_flags = item.get("qualityFlags", [])
        item.update(fields)
        item["qualityFlags"] = list(dict.fromkeys(existing_flags + fields["qualityFlags"]))
        item["usable"] = fields["useMode"] == "ready"
        item["reviewStatus"] = "人工初审完成"
        item["searchText"] = " ".join(
            [
                item["visualSummary"],
                item["primaryCategory"],
                *item["sceneTags"],
                *item["emotionTags"],
                *item["subjectTags"],
                *item["actionTags"],
                *item["themeTags"],
            ]
        )

    data["catalogVersion"] = 2
    data["classificationSchema"] = {
        "primaryCategory": "主分类",
        "visualSummary": "画面摘要",
        "sceneTags": "场景标签",
        "emotionTags": "情绪标签",
        "subjectTags": "主体标签",
        "actionTags": "动作标签",
        "themeTags": "适用文案主题",
        "useMode": {"ready": "可直接推荐", "review": "需先切片/审核", "disabled": "暂不自动调用"},
    }
    data["localTextModelProbe"] = {
        "path": r"E:\讲师A数字人\本地附加文件3.1.0完整版\python-modules\voiceV2Module\checkpoints\qwen0.6bemo4-merge",
        "architecture": "Qwen3ForCausalLM",
        "approximateSize": "0.6B",
        "configuredRole": "IndexTTS V2 情绪分析模块（qwen_emo_path）",
        "offlineLoadTest": "成功",
        "cpuLoadSeconds": 6.46,
        "cpuInferenceSeconds": 8.04,
        "assessment": "可辅助声音情绪判断，但不适合单独承担 B-Roll 主题规划；完整文案理解建议另配通用指令版千问。",
    }
    data["reviewSummary"] = dict(Counter(item["useMode"] for item in data["assets"]))

    with INDEX_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    (ROOT / "初步分类报告.html").write_text(build_html(data), encoding="utf-8")
    build_overview_image(data)

    counts = Counter(item["primaryCategory"] for item in data["assets"])
    print(json.dumps({"modes": data["reviewSummary"], "categories": counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
