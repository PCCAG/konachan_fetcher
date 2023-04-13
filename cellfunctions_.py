import httpx
from loguru import logger
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import asyncio
import random
from bs4 import BeautifulSoup
from parse_tags_link import f_link,f_tags
from fake_useragent import UserAgent
##k站主页
host="https://konachan.com"

#利用clash代理转发
proxies={
"http://": "http://127.0.0.1:7890",
"https://": "http://127.0.0.1:7890"}

#proxies=None

async def current_ip():
    async with httpx.AsyncClient() as c:
        try:
            re= await c.get("http://whois.pconline.com.cn/ipJson.jsp",params={"json":"true"})
            return re.json() if len(re.json()["ip"]) > 4 else {"ip":"没有获取到"}
        except Exception as e:
            raise e
    
def get_headers():#使用selenium获取cookie
    # sourcery skip: inline-immediately-returned-variable
    
    service = Service("chromedriver.exe")
    chrome_options= Options()
    chrome_options.add_argument("--headless")
    with webdriver.Chrome(service=service,options=chrome_options) as driver :
        
        try :
            #设置隐式等待
            driver.implicitly_wait(10) 
            driver.get(host)
            #设置显式等待
            WebDriverWait(driver=driver,timeout=10).until(
                expected_conditions.presence_of_element_located(
                    (By.TAG_NAME,'html')
                )
            )
            cookies=driver.get_cookies()
            #logger.info("RUNNING.....")
            logger.success("get cookie success..")
        except Exception as e:
            logger.error("get cookie error..")
            raise e
    cookie = "".join(
        f"{i['name']}={i['value']};"
        if pin != len(cookies) - 1
        else f"{i['name']}={i['value']}"
        for pin, i in enumerate(cookies)
    )
    headers={
    #":authority": "konachan.com",
    #":method": "GET",
    #":scheme": "https",
    "cookie": cookie,
    #"referer": r"https://konachan.com/post",
    "dnt": "1",
    #"sec-fetch-site": "same-origin",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"
    }
    return headers


#获取单个页面源码
async def get_source(pid:int,url:str,headers:dict):
    #异步上下文菜单管理器
    async with httpx.AsyncClient(proxies=proxies) as client:
        for i in range(3):
            try:
                headers["user-agent"]=UserAgent().random
                re = await client.get(url,headers=headers,timeout=(i+1)*50)
                res= re.text
                if (
                    "<p>This post does not exist.</p>" in res
                    or 
                    ("This post was deleted." in res
                    and """<div class="status-notice">""" in res)
                ):
                    logger.error("图片不存在或者被删除了")
                    logger.error(f"https://konachan.com/post/show/{pid}/")
                    return (pid,"寄")
                elif len(res) < 2000:
                    #logger.warning("源码长度不对")
                    await asyncio.sleep(random.randint(1,3))
                    #logger.warning(f"https://konachan.com/post/show/{pid}/")
                    continue
                elif re.status_code == 403:
                    logger.error("403无法访问")
                    return (pid,"寄")
                elif re.status_code == 200:
                    logger.success("获取源码成功")
                    return (pid,res)
            except Exception as e :
                await asyncio.sleep(random.randint(1,3))
                #raise e
                #lg.warning("re link")
                continue
        logger.error("nothing!")
        return (pid,"寄")
    
    
#解析源码得到图片地址和tags
def parse(pid:int,source:str):
    # sourcery skip: remove-redundant-continue, remove-unnecessary-else
    #global df_error
    try:
        tags_link=[pid,]
        for param_features in ("lxml","html.parser","html5lib","html","html5","xml","lxml-xml"):
            soup=BeautifulSoup(source,features=param_features)
            tags=f_tags(soup)
            link=f_link(soup)
            if (tags != False) and (link != False):
                tags_link.extend((link, tags))
                break
            else:
                continue
        if len(tags_link)==3:
            return tuple(tags_link)
        else:
            logger.error(f"https://konachan.com/post/show/{pid}/")
            return (pid,"寄","寄")
    except Exception as e:
        logger.error(f"https://konachan.com/post/show/{pid}/")
        raise e

        
#下载图片
async def save_img(pid:int,img_link:str,tags:str,headers:dict,imgpath:str):
    async def check():
        async with httpx.AsyncClient(proxies=proxies) as clinet:
            for _ in range(3):
                try:
                    headers["user-agent"]=UserAgent().random
                    re = await clinet.get(img_link,headers=headers,timeout=300)
                    return re
                except Exception:
                    await asyncio.sleep(random.randint(1,3))
                    continue
            return False
    try:
        try:
            re = await check()
            if re == False:
                logger.error("请求图片链接错误")
                logger.error(f"https://konachan.com/post/show/{pid}/")
                return (pid,"寄","寄","寄")
            #logger.debug(f"请求图片状态码:{re.status_code}")
            elif re.status_code != 200:
                logger.error("请求图片状态码错误")
                logger.error(f"https://konachan.com/post/show/{pid}/")
                return (pid,"寄","寄","寄")
            img_type=img_link.split(".")[-1]
            #logger.info(f"图片类型: {img_type}")
            #图片路径
            img_path = f"{imgpath}\\{pid}.{img_type}"
            #logger.info(f"图片流类型: {type(re.content)}") 二进制
            with open(img_path,"wb") as f:
                f.write(re.content)
        except Exception as e :
            logger.error("保存图片到路径错误")
            logger.error(f"https://konachan.com/post/show/{pid}/")
            status_code=re.status_code
            logger.error(f"{status_code}")
            breakpoint()
            return (pid,"寄","寄","寄")

        try:
            if tags != "寄" and img_link != "寄" and img_path != "寄":
                return (pid,tags,img_link,img_path)
            logger.error('没有有效的值')
            logger.error(f"https://konachan.com/post/show/{pid}/")
            return (pid,"寄","寄","寄")
        except Exception as e:
            logger.error('未知错误1')
            logger.error(f"https://konachan.com/post/show/{pid}/")
            breakpoint()
            return (pid,"寄","寄","寄")
    except Exception as e :
        logger.error('未知错误2')
        logger.error(f"https://konachan.com/post/show/{pid}/")
        breakpoint()
                
            
        