## coding=utf-8
import asyncio
import functools

# import json
import os
import random

# import re as re__

# import types

# 异步保存文件的库
# pip install aiofiles
import aiofiles
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fake_useragent import UserAgent
from loguru import logger

# from playwright.sync_api import sync_playwright  # , Playwright

# 一个playwright的插件用来伪装无头模式
# pip install playwright-stealth
# from playwright_stealth import stealth_sync

from parse_tags_link import f_link, f_tags


# 加载配置文件
load_dotenv()


##k站主页
host = "https://konachan.com"

# # 利用clash代理转发
# proxies = {"http://": "http://127.0.0.1:10809", "https://": "http://127.0.0.1:10809"}
http_proxy = os.getenv("http_proxy")

proxies = {"http://": http_proxy, "https://": http_proxy}

# logger.warning(f"代理: {http_proxy}")

# # httpx的socks5代理好像有问题
# socks5_proxies = {
#     "http://": "socks5://127.0.0.1:62333",
#     "https://": "socks5://127.0.0.1:62333",
# }

# proxies=None


# def read_headers_from_json(
#     cookie_json_filepath="_cookies_.json", headers_example="_headers_example.json"
# ) -> dict:
#     """
#     默认:
#     从 headers_example="_headers_ example.json" 获取headers模板,
#     从 cookie_json_filepath="cookies.json" 更新headers的cookie字段,
#     如果失败调用get_headers(),
#     返回: headers
#     """

#     # logger.debug("尝试从cookies.json获取headers 的cookie.......")
#     with open(cookie_json_filepath, encoding="utf-8") as f:
#         try:
#             # dread = dict(json.load(f))
#             d_list: list = json.load(f)
#             # dict().keys()
#             # print(list(dread.keys())[0])
#             headers_cookie = "; ".join([f'{d["name"]}={d["value"]}' for d in d_list])
#             with open(headers_example, encoding="utf-8") as h:
#                 headers = dict(json.load(h))
#                 headers["cookie"] = headers_cookie
#             # print(headers)
#         except Exception as e:
#             # raise e
#             # raise NameError("Not found headers") from e
#             logger.warning(
#                 "尝试从cookies.json获取headers 的cookie失败,将用函数get_headers()采用playwright无头模式下自动获取headers"
#             )
#             headers = get_headers()
#             # headers = {}

#         # logger.success("获取headers成功......")

#         return headers


# # 一个获取当前ip的函数
# async def current_ip():
#     """
#     一个获取当前ip的函数
#     """
#     async with httpx.AsyncClient() as c:
#         try:
#             re = await c.get(
#                 "http://whois.pconline.com.cn/ipJson.jsp", params={"json": "true"}
#             )
#             return re.json() if len(re.json()["ip"]) > 4 else {"ip": "没有获取到"}
#         except Exception as e:
#             raise e


# # 利用playwright获取cookie及headers
# @logger.catch()
# def get_headers() -> dict[str, str]:
#     """
#     利用playwright获取cookie及headers
#     """
#     # 启动演奏
#     with sync_playwright() as p:
#         try:
#             logger.debug("利用playwright获取cookie及headers......")
#             # 启动浏览器
#             b = p.webkit.launch(
#                 headless=True, proxy={"server": proxies[list(proxies.keys())[0]]}  # type: ignore
#             )
#             logger.debug("启动浏览器上下文....")
#             # 启动浏览器上下文
#             context = b.new_context()

#             page = context.new_page()
#             # 无头模式伪装
#             stealth_sync(page)

#             # 路由,流产图片,实现无图模式
#             page.route(
#                 re__.compile(r"(\.png$)|(\.jpg$)|(\.gif$)", re__.S),
#                 lambda route: route.abort(),
#             )

#             re = page.goto(host)
#             page.click("#links > a:nth-child(1)")

#             page.wait_for_load_state("domcontentloaded", timeout=10000)
#             page.click("#post-list-posts > li > div > a")

#             page.wait_for_load_state("domcontentloaded", timeout=10000)

#             # 获取所有cookie
#             cookies = context.cookies()
#             # 获取请求头
#             headers = re.request.headers  # type: ignore
#             headers["cookie"] = "".join(
#                 (
#                     f"{i['name']}={i['value']};"
#                     if pin != len(cookies) - 1
#                     else f"{i['name']}={i['value']}"
#                 )
#                 for pin, i in enumerate(cookies)
#             )
#             headers["Referer"] = r"https://konachan.com/post"

#             with open("_headers_.json", "w", encoding="UTF-8", errors="ignore") as f:
#                 json.dump(headers, fp=f, ensure_ascii=False, indent=2)

#             page.close()
#             context.close()
#             b.close

#             logger.success("获取cookie及headers成功")

#             return headers
#         except Exception as e:
#             logger.error("取cookie及headers失败,请尝试检查代理是否出错")
#             breakpoint()
#             raise e


class Counter:
    def __init__(self) -> None:
        pass

    # 默认
    class PROCESS_BAR_NONE:
        def update(*arg, **kwargs):
            pass

    @staticmethod
    def counter_async(PROCESS_BAR=PROCESS_BAR_NONE()):
        """
        参数装饰器 : 传入PROCESS_BAR 实现对原函数进度控制.
        例如: PROCESS_BAR = tqdm.tqdm(total=200, desc="Processing", unit="item"),
        tqdm.tqdm进度条(import tqdm),
        需要在其他文件导入并覆写原异步函数,
        newfunc = counter_async(PROCESS_BAR=tqdm.tqdm(total=200, desc="Test", unit="item"))(example)
        """
        ##PROCESS_BAR = tqdm.tqdm()

        def async_counter(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                wrapper.processcount.update(1)  # type: ignore
                if wrapper.processcount.n == wrapper.processcount.total:  # type: ignore
                    wrapper.processcount.close()  # type: ignore

                return result

            wrapper.processcount = async_counter.processcount  # type: ignore
            return wrapper

        async_counter.processcount = PROCESS_BAR  # type: ignore
        return async_counter

    @staticmethod
    def counter_sync(PROCESS_BAR=PROCESS_BAR_NONE()):
        """
        不支持多进程😅
        """

        def sync_counter(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                r = func(*args, **kwargs)
                wrapper.processcount.update(1)  # type: ignore
                if wrapper.processcount.n == wrapper.processcount.total:  # type: ignore
                    wrapper.processcount.close()  # type: ignore
                return r

            wrapper.processcount = sync_counter.processcount  # type: ignore
            return wrapper

        sync_counter.processcount = PROCESS_BAR  # type: ignore
        return sync_counter


async def get_source(
    pid: int, url: str, headers: dict, proxies: dict = proxies
) -> tuple[int, str]:
    """
    获取单个页面源码
    return: pid, source

    """
    # sourcery skip: remove-unreachable-code
    # 异步上下文菜单管理器
    async with httpx.AsyncClient(proxies=proxies) as client:
        # 这个是重试四次,2333🤣
        for i in range(4):
            try:
                headers["user-agent"] = UserAgent().random
                re = await client.get(url, headers=headers, timeout=(i + 1) * 50)
                res = re.text
                if "<p>This post does not exist.</p>" in res or (
                    "This post was deleted." in res
                    and """<div class="status-notice">""" in res
                ):
                    logger.error(f"{pid}图片不存在或者被删除了")
                    logger.error(f"https://konachan.com/post/show/{pid}/")
                    return (pid, "寄")
                elif len(res) < 2000:
                    logger.warning("源码长度不对")
                    await asyncio.sleep(random.randint(1, 4))
                    logger.warning(f"https://konachan.com/post/show/{pid}/")
                    continue
                elif re.status_code == 403:
                    logger.error("403无法访问")
                    return (pid, "寄")
                elif re.status_code == 200:
                    logger.success("获取源码成功")
                    return (pid, res)
            except Exception as e:
                # raise e
                logger.warning(f"下载源码重试: https://konachan.com/post/show/{pid}")
                await asyncio.sleep(random.randint(1, 4))
                # raise e
                # lg.warning("re link")
                continue
        logger.error("源码 nothing!")
        logger.error(f"https://konachan.com/post/show/{pid}/")
        return (pid, "寄")


# 解析源码得到图片地址和tags
# @counter
def parse(pid: int, source: str) -> tuple[int, str, str]:
    """
    解析源码得到图片地址和tags.
    return: pid,tags,img_link
    """
    # sourcery skip: remove-redundant-continue, remove-unnecessary-else
    # global df_error
    try:
        tags_link = [
            pid,
        ]
        # 所有解析器试一遍.23333🤣
        for param_features in (
            "lxml",
            "html.parser",
            "html5lib",
            "html",
            "html5",
            "xml",
            "lxml-xml",
        ):
            soup = BeautifulSoup(source, features=param_features)
            tags = f_tags(soup)
            link = f_link(soup)
            if (tags != False) and (link != False):
                tags_link.extend((link, tags))  # type: ignore
                break
            else:
                continue
        if len(tags_link) == 3:
            return tuple(tags_link)  # type: ignore
        else:
            logger.error(f"解析错误last: https://konachan.com/post/show/{pid}/")
            return (pid, "寄", "寄")
    except Exception as e:
        logger.error(f"解析错误all:  https://konachan.com/post/show/{pid}/")
        return (pid, "寄", "寄")
        # raise e


# 下载图片
# @counter
async def save_img(
    pid: int,
    img_link: str,
    tags: str,
    headers: dict,
    imgpath: str,
    proxies: dict = proxies,
) -> tuple[int, str, str, str]:
    """
    下载图片.
    返回: return (pid, tags, img_link, img_path)
    """

    async def check_ifsuccess_return_responce():
        async with httpx.AsyncClient(proxies=proxies) as clinet:
            for _ in range(3):
                try:
                    headers["user-agent"] = UserAgent().random
                    re = await clinet.get(img_link, headers=headers, timeout=300)
                    assert re.status_code == 200, "请求图片状态码:{re.status_code}"
                    return re
                except Exception:
                    logger.warning(
                        f"下载图片重试: https://konachan.com/post/show/{pid}"
                    )
                    await asyncio.sleep(random.randint(1, 4))
                    continue
            return False

    try:
        re = await check_ifsuccess_return_responce()

        # 这里非异步

        if re == False:
            logger.error("请求图片链接错误")
            logger.error(f"https://konachan.com/post/show/{pid}/")
            return (pid, "寄", "寄", "寄")
        # logger.debug(f"请求图片状态码:{re.status_code}")

        elif re.status_code != 200:
            logger.error(f"请求图片状态码:{re.status_code}")
            logger.error(f"https://konachan.com/post/show/{pid}/")
            return (pid, "寄", "寄", "寄")
        else:
            img_type = img_link.split(".")[-1]
            # logger.info(f"图片类型: {img_type}")

            # 图片路径
            img_path = f"{imgpath}/{pid}.{img_type}"

            # logger.info(f"图片流类型: {type(re.content)}") 二进制

            # 使用异步写入文件

            async with aiofiles.open(img_path, "wb") as f:
                await f.write(re.content)
                # logger.debug(f"保存图片中......{pid}")

            if tags != "寄" and img_link != "寄" and img_path != "寄":
                logger.success(f"下载图片成功: {img_path}")
                return (pid, tags, img_link, img_path)

            else:
                logger.error("没有有效的值,下载图片失败")

                logger.error(f"https://konachan.com/post/show/{pid}/")

                return (pid, "寄", "寄", "寄")

    except Exception as e:
        logger.error("保存图片到路径错误")

        logger.error(f"https://konachan.com/post/show/{pid}/")

        breakpoint()

        return (pid, "寄", "寄", "寄")


# 😅
def ensure_file_exists(filepath, file_ecoding="UTF-8") -> bool:  # type: ignore
    """
    检测文件路径是否存在，如果不存在则创建文件。

    参数：
    - filepath: 文件路径
    - file_ecoding: 创建的文件编码
    return:
    Ture 这个文件存在
    False 反之
    """
    try:
        with open(filepath, "r", errors="ignore"):
            pass
        return True
    except FileNotFoundError:
        # os.makedirs("/".join(filepath.split("/")[:-1]))
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", errors="ignore", encoding=file_ecoding):
            pass
        return False
    except Exception:
        print("constom function:  ensure_file_exists,  raise an unknown error ! ?")


# # 检测并创建文件路径
# file_path = r"path\to\your\file.txt"
# ensure_file_exists(file_path)
