## coding=utf-8
import asyncio
from sqlalchemy import create_engine, text
import pandas
from loguru import logger  # pip install loguru
from get_imags_data import main
import contextlib
import random
import os
from dotenv import load_dotenv  # pip install python-dotenv

## from cellfunctions_ import read_headers_from_json

## import json


# 记录日志
logger.add("k_spider\\log\\main.log")

# 加载配置文件
load_dotenv()


# 连接数据库 mysql
@logger.catch()
def link_db():  # return engine, kimg_table, tags_table
    logger.debug("连接数据库中...........")

    # 连接数据库
    try:
        mysql_user = os.getenv("mysql_user")
        # input("输入mysql用户名:")
        mysql_password = os.getenv("mysql_password")
        # input("输入mysql用户密码:")
        mysql_host = os.getenv("mysql_host")
        # input("输入host,本地则localhost:")
        mysql_database = os.getenv("mysql_database")
        # input("输入要连接的数据库:")

        engine = create_engine(
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
        )
        engine = engine.connect()

        kimg_table = os.getenv(
            "mysql_img_table"
        )  # mysql_img_table=kimg mysql_tags_table=tags
        tags_table = os.getenv("mysql_tags_table")

        logger.success(f"数据表: {mysql_database}")
        logger.success(f"图像数据表: {kimg_table}")
        logger.success(f"tag数据表: {tags_table}")

        logger.success("link dbas 准备导入数据.....")
        return engine, kimg_table, tags_table

    except Exception as e:
        logger.error("连接数据库失败")
        breakpoint()
        # raise e


# 保存数据到本地与数据库
@logger.catch()
def save_img_and_todb(pids, engine, kimg_table, tags_table):
    total_add_db_data_number__ = 0  # 内部变量

    # 初始化
    # 表结构
    # 表数据添加到数据库
    columns = ("pid", "tags", "link", "path", "status", "time")
    df = pandas.DataFrame(columns=columns)
    # 执行main 得到数据
    try:
        if len(pids) == 0:
            logger.warning("pids为空")
            return False
        pid_tags_img_path_img_link = asyncio.run(main(pids=pids))
        assert len(pid_tags_img_path_img_link) > 0, "最后从main函数没有得到数据"
    except AssertionError as e:  # AssertionError: 最后没有得到数据
        logger.warning("没有得到数据")
        return False
    except Exception as e:
        logger.error("未知错误:save_img_and_todb执行main最后从main函数没有得到数据")
        breakpoint()
        raise e
        # logger.error(e)

    # (pymysql.err.ProgrammingError) (1146, "Table 'kimgdb.kimg' doesn't exist")
    # [SQL: select distinct pid from kimg;]
    # (Background on this error at: https://sqlalche.me/e/20/f405)
    # 保存所有tag
    set_tags = set()  # 用集合保存唯一tag

    # 排除无效数据
    for pid, tags, img_path, img_link in pid_tags_img_path_img_link:
        if (
            (tags == "寄")
            or ("plicit.png" in img_link)  # k站特殊的图片
            or (img_path == "寄")
            or (img_link == "寄")
        ):
            # status=0
            logger.warning("no add error img data....")
            continue
        else:
            # status=1
            times = pandas.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            df.loc[pid] = [pid, tags, img_path, img_link, 1, times]
            logger.success(f"imported: {img_link}")
            total_add_db_data_number__ += 1

            for tag in tags.split(" "):
                if len(tag.strip()) != 0:
                    set_tags.add(tag.strip())
                    # print(tag.strip())

    df_tags = pandas.DataFrame(set_tags, columns=["tag"])

    # print(df_tags)
    # 保存tags到数据库
    # 可以不用创建表,没有自动建表有则添加
    df_tags.to_sql(tags_table, engine, if_exists="append", index=False)
    df_tags.to_csv(f"k_spider\\{tags_table}.csv", mode="a", index=False, header=False)
    # engine.execute(text())

    # 查看有效添加tag数量(tag唯一,排除重复)
    # engine.excute(text())
    # pandas.read_sql_table(table_name=tags_table,con=engine)

    # 防止频繁连接更改数据库

    # logger.success(f"保存{df_tags.shape[0]-uni_tag()}个tag到数据库")
    # 考虑用数据库的存储过程实现 或者后面自己处理排重tag😅
    # SQl语句
    """
    #查看kmigdb数据库
    SELECT COUNT(DISTINCT a.pid) 数量 from kimg a
    UNION
    SELECT COUNT(DISTINCT b.tag) from tags b;
    
    #排重tag,
    DROP TABLE if EXISTS tags_unique;
    CREATE TABLE if not EXISTS tags_unique LIKE tags;
    INSERT into tags_unique SELECT DISTINCT tag from tags;
    SELECT count(DISTINCT tag) from tags_unique;
    """

    # breakpoint()

    # 决定这里创建一个tags_unique表,保存唯一tag,😅
    try:
        logger.debug("创建一个tags_unique表并保存")

        engine.execute(text("DROP TABLE if EXISTS tags_unique;"))
        engine.execute(
            text(f"CREATE TABLE if not EXISTS tags_unique LIKE {tags_table};")
        )
        engine.execute(
            text(f"INSERT into tags_unique SELECT DISTINCT * from {tags_table};")
        )

        tags_unique_number: tuple = engine.execute(
            text("SELECT count(*) FROM tags_unique;")
        ).fetchone()
        logger.info(f"{tags_table} 表当前唯一tag数为 : {tags_unique_number[0]}")

        pandas.read_sql(text("SELECT * FROM tags_unique"), engine).to_csv(
            "k_spider/tags_unique.csv", header=False, index=False
        )

    except Exception as e:
        logger.warning("创建一个tags_unique表并保存.....失败")

    # 保存图像数据到数据库
    # 可以不用创建表,没有自动建表有则添加
    df.to_sql(kimg_table, engine, if_exists="append", index=False)

    # 文件备份一下
    df.to_csv(f"k_spider\\{kimg_table}.csv", mode="a", index=False, header=False)
    # ,header=["pid","tags","path","link","status"])

    """logger.info("wait 3 s .......")
    sleep(3)"""

    ##这里可能会出兼容问题,有的没有这个方法,有的有这个方法,但最终都是提交数据更新到数据库中
    with contextlib.suppress(
        AttributeError
    ):  # AttributeError: 'Connection' object has no attribute 'commit'
        engine.commit()
    logger.success(f"DataBase had added {total_add_db_data_number__} img data...")

    addition = int(total_add_db_data_number__)
    # 增加的部分
    del total_add_db_data_number__  # 删除内部变量

    global total_add_db_data_number  # 外部变量

    total_add_db_data_number += addition


# 封装一个下载模式
@logger.catch()
def mode_a():  # 随机范围下载模式 从范围内生成一堆数量的图片任务
    # 获取一些变量 单次下载数量 等待时间 并发获取源码与下载图片的并发数
    try:
        down_number = os.getenv("down_number")
        down_number = int(down_number)

        sem_times = os.getenv("sem_times")
        sem_times = int(sem_times)

        low, upper = os.getenv("low"), os.getenv("upper")
        low, upper = int(low), int(upper) + 1

        times = os.getenv("times")
        times = int(times)

        assert isinstance(down_number, int), "单次下载数量请输入整数"
        assert isinstance(sem_times, int), "并发数请输出整数"
        assert isinstance(low, int), "下标请输入整数"
        assert isinstance(upper, int), "上标请输出整数"
        assert isinstance(times, int), "下载次数请输入整数"
    except Exception as e:
        raise e

    logger.success(f"单次下载数量:{down_number}")
    logger.success(f"并发数:{sem_times}")
    logger.success(f"下载图片路径:{os.getenv('IMG_PATH')}")
    logger.success(f"下载次数:{times}")

    # for _ in tqdm(range(int(os.getenv("times"))),desc="import_db"):#类似无限循环
    for _ in range(times):
        # 如果没有数据库连接,会出现 TypeError: cannot unpack non-iterable NoneType object
        try:
            engine, kimg_table, tags_table = link_db()
        except Exception as e:
            logger.error("没有数据库连接,请检查数据库是否启用")
            breakpoint()
            raise e
        with engine:
            # 排除重复pid
            try:
                df_pid = pandas.read_sql(
                    text(f"select distinct pid from {kimg_table};"), engine
                )
                df_pid = df_pid["pid"]
            except Exception as e:
                df_pid = []
                logger.warning(f"无法从{kimg_table}找到pid,可能为新表")
                # breakpoint()
                # raise e

            logger.info(f"数据库共有{len(df_pid)}条图像数据")

            # pid_list = df_pid.iloc[:, 0].tolist()

            # 生成随机pid列表
            pids0 = random.sample(range(low, upper), down_number)
            # pids0=[253158,206200] 失败下载错误重试 (已完成)
            # 单次下载的pid列表,并从列表pids0中移除与列表pid_list中相等的元素
            # pids = [x for x in pids0 if x not in pid_list]
            # 优化为集合运算

            # logger.info(f"前pids长度{len(pids0)}")
            # OK test结果一致

            pids = list(set(pids0) - set(df_pid))

            # logger.info(f"后pids长度{len(pids)}")
            # logger.info(len(pids0))
            # logger.info(len(df_pid["pid"]))

            # 防止pids为空 为空进入下一个
            # if len(pids)==0:
            if not pids:
                continue

            # 输出排除的重复pid数
            if len(pids0) - len(pids) > 0:
                logger.info(f"排除{len(pids0)-len(pids)}个重复pid....")

            save_img_and_todb(pids, engine, kimg_table, tags_table)

        logger.warning(f"数据库一共添加了 {total_add_db_data_number} img data....")


# 封装一个下载模式 这个拿来测试的
# @logger.catch()
# def mode_b(pids: list = eval(os.getenv("pid_list"))):  # 指定下载模式
#     # print(pids)
#     engine, kimg_table, tags_table = link_db()
#     with engine:
#         try:  # 这里也需要排重处理
#             df_pid = pandas.read_sql(
#                 text(f"select distinct pid from {kimg_table};"), engine
#             )
#             df_pid = df_pid["pid"]
#             front = len(pids)
#             pids = list(set(pids) - set(df_pid))
#             later = len(pids)
#             if front - later > 0:
#                 logger.info(f"排除{front-later}个重复pid....")
#         except Exception as e:
#             raise e
#         save_img_and_todb(
#             pids,
#             int(os.getenv("sem_times")),
#             engine,
#             kimg_table,
#             tags_table,
#         )


# sourcery skip: remove-unreachable-code
if __name__ == "__main__":
    # logger.disable("ERROR")
    # logger.add(sys.stdout, level="INFO", enqueue=True)
    # 移除所有输出目标，禁用所有日志输出
    if int(os.getenv("EnableLog")) == 0:
        logger.remove()
        print("关闭日志")
    else:
        print("打开日志")
        logger.disable("SUCCESS")
        pass
    # 外部全局变量 记录一次运行加入数据库数据量

    total_add_db_data_number = 0

    for _ in range(1):  # 可能会出现cookie过期
        try:
            mode = os.getenv("mode")
            if mode == "a":
                mode_a()
            # elif mode == "b":
            #     # mode_b()
            #     pass
            else:
                continue
        except Exception as e:
            logger.error("在main.py 起始位置出错.......")
            breakpoint()
            raise e
            # continue
    # raise TimeoutError("下载已完成")
    logger.success("下载任务完成")
