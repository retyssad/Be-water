# -*- coding: utf-8 -*-
"""种子数据脚本：插入示例用户、术语、知识库和配置"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.db import SessionLocal, init_database
from app.utils.helpers import generate_id, now_str


def seed_users(session):
    """插入默认用户"""
    from app.models.user import User

    if session.query(User).count() > 0:
        return

    users = [
        User(
            user_id=generate_id(),
            username="admin",
            password_hash="scrypt:0000:changeme",  # 占位符，生产环境需加密
            role="admin",
            email="admin@water.gov.cn",
            status="active",
        ),
        User(
            user_id=generate_id(),
            username="engineer",
            password_hash="scrypt:0000:changeme",
            role="user",
            email="engineer@water.gov.cn",
            status="active",
        ),
    ]
    session.add_all(users)
    session.commit()
    print(f"  [OK] 插入 {len(users)} 个用户")


def seed_terminology(session):
    """插入示例术语"""
    from app.models.terminology import Terminology

    if session.query(Terminology).count() > 0:
        return

    terms = [
        Terminology(
            term_id=generate_id(),
            term="帷幕灌浆",
            pinyin="weimu guanjiang",
            definition="在坝基或岸坡中钻孔，用压力灌注浆液形成防渗帷幕的工程措施。",
            category="基础处理",
            source="SL 570-2013",
        ),
        Terminology(
            term_id=generate_id(),
            term="戗堤",
            pinyin="qiang di",
            definition="在河道中修筑的临时围堰，用于截流施工。",
            category="施工导流",
            source="SL 252-2017",
        ),
        Terminology(
            term_id=generate_id(),
            term="混凝土",
            pinyin="hunningtu",
            definition="由水泥、骨料和水按一定比例混合，经硬化而成的人造石材。",
            category="建筑材料",
            source="SL 352-2006",
            synonyms="砼",
        ),
        Terminology(
            term_id=generate_id(),
            term="围岩",
            pinyin="weiyan",
            definition="隧道或地下洞室开挖后，周围受扰动的那部分岩体。",
            category="地下工程",
            source="SL 279-2016",
        ),
        Terminology(
            term_id=generate_id(),
            term="水锤",
            pinyin="shuichui",
            definition="压力管道中因流速突然变化而引起压力急剧波动的现象。",
            category="水力机械",
            source="SL 655-2014",
            synonyms="水击",
        ),
    ]
    session.add_all(terms)
    session.commit()
    print(f"  [OK] 插入 {len(terms)} 条术语")


def seed_knowledge_base(session):
    """插入示例知识库文档"""
    from app.models.knowledge_base import KnowledgeBase

    if session.query(KnowledgeBase).count() > 0:
        return

    docs = [
        KnowledgeBase(
            doc_id=generate_id(),
            title="SL 319-2018 混凝土重力坝设计规范",
            content="""混凝土重力坝的设计应满足以下要求：
1. 坝体强度：按承载能力极限状态和正常使用极限状态进行设计
2. 坝基稳定：抗滑稳定安全系数不小于规范规定值
3. 防渗排水：设置帷幕灌浆和排水孔幕
4. 温度控制：采取温控措施防止裂缝""",
            doc_type="规范",
            category="水工建筑物",
            source="SL 319-2018",
            publish_year=2018,
            chunk_index=0,
            total_chunks=1,
        ),
        KnowledgeBase(
            doc_id=generate_id(),
            title="SL 252-2017 水利水电工程等级划分及洪水标准",
            content="""水利水电工程根据其工程规模、效益及在国民经济中的重要性，划分为五等：
Ⅰ等工程：大型，库容≥10亿m³，装机容量≥120万kW
Ⅱ等工程：中大型，库容1~10亿m³，装机容量30~120万kW
Ⅲ等工程：中型，库容0.1~1亿m³，装机容量5~30万kW
Ⅳ等工程：中小型，库容0.01~0.1亿m³，装机容量1~5万kW
Ⅴ等工程：小型，库容<0.01亿m³，装机容量<1万kW""",
            doc_type="规范",
            category="工程等级",
            source="SL 252-2017",
            publish_year=2017,
            chunk_index=0,
            total_chunks=1,
        ),
        KnowledgeBase(
            doc_id=generate_id(),
            title="SL 551-2012 土石坝安全监测技术规范",
            content="""土石坝安全监测应包括以下项目：
1. 变形监测：坝体表面位移、内部位移、接缝裂缝
2. 渗流监测：坝体渗流量、坝基渗压力、绕坝渗流
3. 应力应变监测：土压力、孔隙水压力
4. 水文气象监测：库水位、降雨量、气温
监测频率应根据施工期、初蓄期和运行期分别确定。""",
            doc_type="规范",
            category="安全监测",
            source="SL 551-2012",
            publish_year=2012,
            chunk_index=0,
            total_chunks=1,
        ),
        KnowledgeBase(
            doc_id=generate_id(),
            title="水利工程混凝土抗裂性能评估",
            content="""混凝土抗裂性能评估的主要指标：
1. 抗拉强度：直接影响混凝土抵抗开裂的能力
2. 极限拉伸值：反映混凝土在受拉状态下的变形能力
3. 弹性模量：影响混凝土在温度应力下的应变
4. 绝热温升：控制混凝土内部最高温度
5. 干缩率：反映混凝土在干燥条件下的体积稳定性
抗裂评估可采用温度-应力试验方法，综合评定混凝土的抗裂性能。""",
            doc_type="技术论文",
            category="建筑材料",
            source="水利学报",
            publish_year=2020,
            chunk_index=0,
            total_chunks=1,
        ),
    ]
    session.add_all(docs)
    session.commit()
    print(f"  [OK] 插入 {len(docs)} 篇知识库文档")


def seed_configs(session):
    """插入默认配置项"""
    from app.models.config import Config

    if session.query(Config).count() > 0:
        return

    configs = [
        Config(config_id=generate_id(), key="temperature",
               value="0.7", type="float", description="LLM 温度参数"),
        Config(config_id=generate_id(), key="top_p",
               value="0.9", type="float", description="LLM top_p 参数"),
        Config(config_id=generate_id(), key="max_tokens",
               value="2048", type="int", description="最大生成 token 数"),
    ]
    session.add_all(configs)
    session.commit()
    print(f"  [OK] 插入 {len(configs)} 条配置项")


def main():
    print("=" * 50)
    print("水利工程技术语音问答助手 - 种子数据导入")
    print("=" * 50)

    # 确保数据库已初始化
    print("\n[1/5] 初始化数据库...")
    init_database()

    # 创建会话
    session = SessionLocal()
    try:
        print("[2/5] 插入用户数据...")
        seed_users(session)

        print("[3/5] 插入术语数据...")
        seed_terminology(session)

        print("[4/5] 插入知识库文档...")
        seed_knowledge_base(session)

        print("[5/5] 插入配置项...")
        seed_configs(session)

        print("\n[完成] 种子数据导入成功！")
    except Exception as e:
        session.rollback()
        print(f"\n[失败] 导入出错: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
