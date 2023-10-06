## coding=utf-8
import asyncio
import concurrent.futures
import multiprocessing
import os
import random

# import sys

import pandas

# from queue import Queue
import tqdm
from dotenv import load_dotenv
from loguru import logger  # pip install loguru

from cellfunctions_ import (
    Counter,
    ensure_file_exists,  # counter_sync,
    get_source,
    parse,
    read_headers_from_json,
    save_img,
    count_rechange_files_directory,
)

# from tqdm.contrib.concurrent import process_map

# 加载配置文件
load_dotenv()
logger.add("k_spider/log/get_imags_data.log")
# proxies=None

# 主函数
# 3个大任务依次传递参数
# 这里可以用队列进一步改,懒得改了😅,我看得眼花
# 得到数据

# logger.disable("ERROR")
# logger.add(sys.stdout, level="INFO", enqueue=True)


@logger.catch()
def main(
    pids: list[int],
    sem_times: int = int(os.getenv("sem_times")),  # 并发数 在.env配置
    imgpath: str = os.getenv("IMG_PATH"),  # 保存图片路径,在.env配置
    headers: dict = read_headers_from_json(),  # 请求头
) -> list | list[tuple[int, str, str, str]]:  # [(pid,tags,img_path,img_link),....]
    #
    #

    imgpath = count_rechange_files_directory(imgpath)

    #
    #

    async def process_urls(pids: list[int]) -> set[tuple[int, str]]:
        sem = asyncio.Semaphore(sem_times)  # 并发数
        get_source_counter = Counter.counter_async(
            PROCESS_BAR=tqdm.tqdm(
                total=len(pids),
                desc="获取源码",
                unit="i",
                smoothing=0.5,
            )
        )(get_source)
        async with sem:
            tasks = {
                asyncio.create_task(
                    get_source_counter(
                        pid, f"https://konachan.com/post/show/{pid}/", headers
                    )
                )
                for pid in pids
            }

            r = await asyncio.gather(*tasks, return_exceptions=False)
            # 参数
            results = {
                (i, ii) for i, ii in r if ii != "寄"
            }  # pid_source=[(pid,source),......]
            return results

    # pid_source=[(pid,source),......]
    # tqdm.tqdm.write("")
    pid_source = asyncio.run(process_urls(pids))
    # tqdm.tqdm.write("")

    # PROCESS_BAR.close()
    if len(pid_source) == 0:
        return []  # 第一步没有东西后面也就没有必要继续了

    # 多进程解析
    # 😅
    def run_tasks(task, pid_source: set[tuple[int, str]]):
        max_workers = min(len(pid_source), multiprocessing.cpu_count())
        # results = set()  # 结果集合
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            futures = {
                executor.submit(task, pid, source)
                for pid, source in pid_source
                if source != "寄"
            }

            results = set()
            for future in tqdm.tqdm(
                concurrent.futures.as_completed(futures),
                total=len(pid_source),
                desc="解析地址",
                unit="i",
                smoothing=0.5,
            ):
                results.add(future.result())
        return results

    pid_img_link_tags = run_tasks(parse, pid_source)
    if len(pid_img_link_tags) == 0:
        return []  # 第二步没有东西后面也就没有必要继续了

    # 并发下载图片
    async def download_imgs(pid_img_link_tags: set[tuple[int, str, str]]):
        sem = asyncio.Semaphore(sem_times)  # 并发数
        save_img_counter = Counter.counter_async(
            tqdm.tqdm(
                total=len(pid_img_link_tags),
                desc="下载图片",
                unit="i",
                smoothing=0.5,
            )
        )(save_img)
        async with sem:
            tasks = {
                asyncio.create_task(
                    save_img_counter(pid, img_link, tags, headers, imgpath)
                )
                for pid, img_link, tags in pid_img_link_tags
            }
            results = await asyncio.gather(*tasks)

            results = [
                (pid, tags, img_path, img_link)
                for pid, tags, img_path, img_link in results
                if tags != "寄" and img_link != "寄" and img_path != "寄"
            ]

            logger.success(f"downloaded {len(results)} img to IMG_PATH......")
            return results

    pid_tags_img_link_img_path = asyncio.run(download_imgs(pid_img_link_tags))

    return pid_tags_img_link_img_path
    # 返回kimg表的很多行的信息


# example test
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
        # logger.s
        # logger.disable("ERROR")
        # logger.disable("WARNING")
        # logger.disable("DEBUG")

        pass
    for _ in range(int(os.getenv("times"))):
        pids = random.sample(
            list(range(int(os.getenv("low")), int(os.getenv("upper")) + 1)),
            int(os.getenv("down_number")),
        )
        # print(f"单次并发数量: {pids.__len__()}")
        # headers = read_headers_from_json()

        rows = main(pids)

        nowtime = pandas.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        data = [
            (pid, tags, img_link, img_path, 1, nowtime)
            for pid, tags, img_link, img_path in rows
        ]

        df = pandas.DataFrame(
            columns=("pid", "tags", "link", "path", "status", "time"), data=data
        )

        # 自定义函数确保文件存在
        if ensure_file_exists("./Data/kimg.csv") == False:
            df.to_csv("./Data/kimg.csv", index=False, mode="w")
        ensure_file_exists("./Data/tags.csv")

        df.to_csv(
            "./Data/kimg.csv",
            index=False,
            mode="a",
            header=False,
        )
        # ./Data/tags.csv

        row_tags: list = df["tags"].to_list()

        tags_set: set = set()
        # for tags in row_tags:
        #     for tag in tags.split(" "):
        #         tags_set.add(tag)
        # 使用内置的集合操作
        tags_set.update(tag for tags in row_tags for tag in tags.split(" "))

        try:
            alltags_existed_set: set = set(
                pandas.read_csv("./Data/tags.csv").iloc[:, 0].to_list()
            )
        except Exception as e:
            alltags_existed_set: set = set()
            pass

        need_add_tags: list = list(tags_set - alltags_existed_set)

        # 追加进去的是应该为原表中不存在的

        pandas.DataFrame(data=need_add_tags, index=None, columns=None).to_csv(
            "./Data/tags.csv", mode="a", index=False, header=False
        )

        # with open("./Data/tags.csv", "a", encoding="UTF-8") as f:
        #     f.writelines()
