## coding=utf-8
import asyncio
import json
import os
import random
import re as re__

# 异步保存文件的库
# pip install aiofiles
import aiofiles
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fake_useragent import UserAgent
from loguru import logger
from playwright.async_api import async_playwright

# 一个playwright的插件用来伪装无头模式
# pip install playwright-stealth
from playwright_stealth import stealth_async

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


# 一个获取当前ip的函数
async def current_ip():
    async with httpx.AsyncClient() as c:
        try:
            re = await c.get(
                "http://whois.pconline.com.cn/ipJson.jsp", params={"json": "true"}
            )
            return re.json() if len(re.json()["ip"]) > 4 else {"ip": "没有获取到"}
        except Exception as e:
            raise e


# 利用playwright获取cookie及headers
@logger.catch()
async def get_headers() -> dict[str, str]:
    # 启动演奏
    async with async_playwright() as p:
        try:
            logger.info("利用playwright获取cookie及headers......")
            # 启动浏览器
            b = await p.chromium.launch(
                headless=False, proxy={"server": proxies[list(proxies.keys())[0]]}
            )
            logger.info("启动浏览器上下文....")
            # 启动浏览器上下文
            context = await b.new_context()

            page = await context.new_page()
            # 无头模式伪装
            await stealth_async(page)

            # 路由,流产图片,实现无图模式
            # await page.route(
            #    re__.compile(r"(\.png$)|(\.jpg$)", re__.S),
            #    lambda route: route.abort(),
            # )

            re = await page.goto(host)
            await page.click("#links > a:nth-child(1)")

            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await page.click("#post-list-posts > li > div > a")

            await page.wait_for_load_state("load", timeout=10000)

            # 获取所有cookie
            cookies = await context.cookies()
            # 获取请求头
            headers = await re.request.all_headers()
            headers["cookie"] = "".join(
                f"{i['name']}={i['value']};"
                if pin != len(cookies) - 1
                else f"{i['name']}={i['value']}"
                for pin, i in enumerate(cookies)
            )

            with open("_headers_.json", "w", encoding="UTF-8", errors="ignore") as f:
                json.dump(headers, fp=f, ensure_ascii=False, indent=2)

            await context.close()
            b.close

            logger.success("获取cookie及headers成功")

            return headers
        except Exception as e:
            logger.error("取cookie及headers失败")
            breakpoint()
            raise e


# 获取单个页面源码
async def get_source(pid: int, url: str, headers: dict):
    # 异步上下文菜单管理器
    async with httpx.AsyncClient(proxies=proxies) as client:
        # 这个是重试四次
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
                    # logger.warning("源码长度不对")
                    await asyncio.sleep(random.randint(1, 4))
                    # logger.warning(f"https://konachan.com/post/show/{pid}/")
                    continue
                elif re.status_code == 403:
                    logger.error("403无法访问")
                    return (pid, "寄")
                elif re.status_code == 200:
                    logger.success("获取源码成功")
                    return (pid, res)
            except Exception as e:
                logger.warning(f"下载源码重试: https://konachan.com/post/show/{pid}")
                await asyncio.sleep(random.randint(1, 4))
                # raise e
                # lg.warning("re link")
                continue
        logger.error("nothing!")
        # logger.error(f"https://konachan.com/post/show/{pid}/")
        return (pid, "寄")


# 解析源码得到图片地址和tags
def parse(pid: int, source: str):
    # sourcery skip: remove-redundant-continue, remove-unnecessary-else
    # global df_error
    try:
        tags_link = [
            pid,
        ]
        # 所有解析器试一遍.23333
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
                tags_link.extend((link, tags))
                break
            else:
                continue
        if len(tags_link) == 3:
            return tuple(tags_link)
        else:
            logger.error(f"解析错误last: https://konachan.com/post/show/{pid}/")
            return (pid, "寄", "寄")
    except Exception as e:
        logger.error(f"解析错误all:  https://konachan.com/post/show/{pid}/")
        return (pid, "寄", "寄")
        # raise e


# 下载图片
async def save_img(pid: int, img_link: str, tags: str, headers: dict, imgpath: str):
    async def check():
        async with httpx.AsyncClient(proxies=proxies) as clinet:
            for _ in range(3):
                try:
                    headers["user-agent"] = UserAgent().random
                    re = await clinet.get(img_link, headers=headers, timeout=300)
                    return re
                except Exception:
                    logger.warning(f"下载图片重试: https://konachan.com/post/show/{pid}")
                    await asyncio.sleep(random.randint(1, 4))
                    continue
            return False

    try:
        try:
            re = await check()

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

            img_type = img_link.split(".")[-1]
            # logger.info(f"图片类型: {img_type}")

            # 图片路径
            img_path = f"{imgpath}\\{pid}.{img_type}"

            # logger.info(f"图片流类型: {type(re.content)}") 二进制

            # 使用异步写入文件

            async with aiofiles.open(img_path, "wb") as f:
                await f.write(re.content)
                logger.info(f"保存图片中......{pid}")

        except Exception as e:
            logger.error("保存图片到路径错误")

            logger.error(f"https://konachan.com/post/show/{pid}/")

            status_code = re.status_code

            logger.error(f"{status_code}")
            # breakpoint()

            return (pid, "寄", "寄", "寄")

        try:
            if tags != "寄" and img_link != "寄" and img_path != "寄":
                logger.success("下载图片成功")
                return (pid, tags, img_link, img_path)

            logger.error("没有有效的值")

            logger.error(f"https://konachan.com/post/show/{pid}/")

            return (pid, "寄", "寄", "寄")

        except Exception as e:
            logger.error("未知错误1")

            logger.error(f"https://konachan.com/post/show/{pid}/")

            breakpoint()

            return (pid, "寄", "寄", "寄")

    except Exception as e:
        logger.error("未知错误2")

        logger.error(f"https://konachan.com/post/show/{pid}/")

        # breakpoint()

        return (pid, "寄", "寄", "寄")
