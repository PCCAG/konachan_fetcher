## coding=utf-8
import asyncio
from loguru import logger  # pip install loguru
import multiprocessing
import concurrent.futures
import os
from cellfunctions_ import (
    get_source,
    parse,
    save_img,
    read_headers_from_json,
    ensure_file_exists,
)
import os
from dotenv import load_dotenv
import pandas
import random

# 加载配置文件
load_dotenv()
# proxies=None

# 主函数
# 3个大任务依次传递参数
# 这里可以用队列进一步改,懒得改了😅,我看得眼花
# 得到数据


@logger.catch()
async def main(
    pids: list[int],
    sem_times: int = int(os.getenv("sem_times")),  # 并发数 在.env配置
    imgpath: str = os.getenv("IMG_PATH"),  # 保存图片路径,在.env配置
    headers: dict = read_headers_from_json(),  # 请求头
) -> list | list[tuple[int, str, str, str]]:  # [(pid,tags,img_path,img_link),....]
    #
    #
    # 图片路径不存在，则创建
    if not os.path.exists(imgpath):
        os.mkdir(imgpath)
        logger.warning("图片路径不存在，已创建")
    #

    # 并发获取源码
    # pids是一个pid列表 [pid,...]
    # 如链接 https://konachan.com/post/show/361874 pid指的是361874 类型int
    async def process_urls(pids: list[int]):
        sem = asyncio.Semaphore(sem_times)  # 并发数
        async with sem:
            tasks = []  # 并发任务列表
            for pid in pids:
                host_path = f"https://konachan.com/post/show/{pid}/"

                # tasks.append(asyncio.ensure_future(get_source(pid,host_path)))
                # The asyncio.ensure_future() function is deprecated in Python 3.10 in favor of asyncio.create_task().
                tasks.append(asyncio.create_task(get_source(pid, host_path, headers)))

            r = await asyncio.gather(*tasks, return_exceptions=False)
            # 参数
            results = [
                (i, ii) for i, ii in r if ii != "寄"
            ]  # pid_source=[(pid,source),......]
            return results

    # pid_source=[(pid,source),......]
    pid_source = await process_urls(pids)
    if len(pid_source) == 0:
        return []  # 第一步没有东西后面也就没有必要继续了

    # 多进程解析
    def run_tasks(task, pid_source: list[tuple[int, str]]):
        max_workers = min(len(pid_source), multiprocessing.cpu_count())
        results = []  # 结果列表
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            futures = [
                executor.submit(task, pid, source)
                for pid, source in pid_source
                if source != "寄"
            ]
            for future in concurrent.futures.as_completed(
                futures
            ):  # all futures完成时的iterable对象
                try:
                    results.append(future.result())
                    # logger.success("parse......")
                except Exception as e:
                    logger.warning("引发 一个 parse error...")
                    # print(future.result())
                    # logger.warning(e)
                    continue
        return results

    pid_img_link_tags = run_tasks(parse, pid_source)
    if len(pid_img_link_tags) == 0:
        return []  # 第二步没有东西后面也就没有必要继续了

    # 并发下载图片
    async def download_imgs(pid_img_link_tags: list[tuple[int, str, str]]):
        sem = asyncio.Semaphore(sem_times)  # 并发数
        async with sem:
            tasks = []  # 并发任务列表

            for pid, img_link, tags in pid_img_link_tags:
                if tags == "寄" or img_link == "寄":
                    logger.error("未知解析或下载错误引起...寄")
                    continue
                else:
                    tasks.append(
                        asyncio.create_task(
                            save_img(pid, img_link, tags, headers, imgpath)
                        )
                    )
                    # pin += 1
                # logger.info("append download img task.....")
            results = await asyncio.gather(*tasks)

            results = [
                (pid, tags, img_path, img_link)
                for pid, tags, img_path, img_link in results
                if tags != "寄" and img_link != "寄" and img_path != "寄"
            ]

            # print(results)

            logger.success(f"downloaded {len(results)} img to IMG_PATH......")
            return results

    pid_tags_img_link_img_path = await download_imgs(pid_img_link_tags)

    return pid_tags_img_link_img_path
    # 返回kimg表的很多行的信息


# example test
if __name__ == "__main__":
    for _ in range(int(os.getenv("times"))):
        pids = random.sample(
            list(range(int(os.getenv("low")), int(os.getenv("upper")) + 1)),
            int(os.getenv("down_number")),
        )
        print(f"单次并发数量: {pids.__len__()}")
        # headers = read_headers_from_json()

        rows = asyncio.run(main(pids))

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
