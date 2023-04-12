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

##k站主页
host="https://konachan.com"

#输出随机可用的代理ip

def random_ip():
    pass
    #暂定
    
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
            logger.error(e)
            logger.error("get cookie error..")
    cookie = "".join(
        f"{i['name']}={i['value']};"
        if pin != len(cookies) - 1
        else f"{i['name']}={i['value']}"
        for pin, i in enumerate(cookies)
    )
    headers={
    "cookie": cookie,
    "dnt": "1",
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
    async with httpx.AsyncClient() as client :
        # 设置请求头
        #headers ={"User-Agent":UserAgent().random}
        try:
            #sleep(random.random())  
            re= await client.get(url,headers=headers,timeout=120)
            #logger.info(f"状态码:{re.status_code}")
            #encoding = re.encoding
            #res = re.content.decode(encoding)#返回网页源码
            res = re.text
        except Exception as e:
            logger.warning("relink get source.....")
            logger.error(e)
            try:
                #sleep(random.random())
                await asyncio.sleep(random.random())
                re= await client.get(url,headers=headers,timeout=200)
                #encoding = re.encoding
                #res = re.content.decode(encoding)
                res = re.text
            except Exception as e2:
                logger.error("relink get source failed...")
                logger.warning(f"https://konachan.com/post/show/{pid}/")
                return (pid,"寄")
        finally:
            if "<p>This post does not exist.</p>" in res:
                logger.error("This post does not exist")
                logger.warning(f"https://konachan.com/post/show/{pid}/")
                return (pid,"寄")
            #elif ("Either you are not logged in, or your account is less than 2 weeks old. <br>" in res) and \
            #     ("For more information on how to comment, head to" in res):
            #    logger.error("This post was deleted.")
            #    return (pid,"寄")
            elif ("This post was deleted." in res) and ("""<div class="status-notice">""" in res):
                logger.error("This post was deleted.")
                logger.warning(f"https://konachan.com/post/show/{pid}/")
                return (pid,"寄")
            else:
                return (pid,res)
    
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
                tags_link.append(link)
                tags_link.append(tags)
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
    
    async with httpx.AsyncClient() as clinet:
        try:
            #sleep(random.random())
            re = await clinet.get(img_link,headers=headers,timeout=120)
        except Exception:
            logger.warning("relink dowmload img 1次.....")
            try:
                #sleep(random.random())
                try:
                    await asyncio.sleep(random.random())
                    re = await clinet.get(img_link,headers=headers,timeout=150)
                except Exception as e:
                    logger.warning("relink dowmload img 2 次.....")
                    await asyncio.sleep(random.randint(3,5))
                    re = await clinet.get(img_link,headers=headers,timeout=300)
            except Exception as e:
                logger.error("download failed...")
                logger.error(f"https://konachan.com/post/show/{pid}/")
                logger.error(img_link)
                return (pid,"寄","寄","寄")

        finally:
            try:
                img_type=img_link.split(".")[-1]
                #logger.info(f"图片类型: {img_type}")
                #图片路径
                img_path=imgpath+f"\\{pid}.{img_type}"
                #logger.info(f"图片流类型: {type(re.content)}") 二进制
                with open(img_path,"wb") as f:
                    f.write(re.content)
            except Exception:
                try:
                    re = await clinet.get(img_link,headers=headers,timeout=300)
                    img_type=img_link.split(".")[-1]
                    #图片路径
                    img_path=imgpath+f"\\{pid}.{img_type}"
                    with open(img_path,"wb") as f:
                        f.write(re.content)

                    #return (pid,tags,img_link,img_path)

                except Exception as e:
                    img_path="寄"
                    logger.error(e)
                    logger.error("保存图片失败")
                    logger.error(f"https://konachan.com/post/show/{pid}/")
                    logger.error(img_link)
                    return (pid,"寄","寄","寄")

            finally:
                if tags != "寄" and img_link != "寄" and img_path != "寄": 
                    return (pid,tags,img_link,img_path)
                else:
                    return (pid,"寄","寄","寄")
            
        