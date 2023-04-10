## coding=utf-8
import httpx 
import asyncio
from sqlalchemy import create_engine
import pandas
from bs4 import BeautifulSoup
from loguru import logger
import multiprocessing
import concurrent.futures
import random
from tqdm import tqdm
import os
from dotenv import load_dotenv # pip install python-dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import queue 
#from importlib.resources import path
#from fake_useragent import UserAgent
#from PIL import ImageSS
#from io import BytesIO

#记录日志
logger.add("k_spider\log\main_log_v1.6.log")

##k站主页
host="https://konachan.com"

#加载配置文件
load_dotenv()

#图片路径 这是绝对路径记得在不同文件夹下 不同设备下记得修改
imgpath=os.getenv("IMG_PATH")

#不存在则创建文件夹
if __name__ == "__main__" and not os.path.exists(imgpath):
    os.mkdir(imgpath)

#输出随机可用的代理ip

def random_ip():
    pass
    #暂定
    
def get_cookie():#使用selenium获取cookie
    # sourcery skip: inline-immediately-returned-variable
    
    service = Service("chromedriver.exe")
    with webdriver.Chrome(service=service) as driver :
        
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
    
    return cookie

if __name__=="__main__":
    headers={
    "cookie": get_cookie(),
    "dnt": "1",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"
    }
    


#获取单个页面源码
async def get_source(pid:int,url:str):
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
                res="寄"
                logger.error(e2)
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
def parse(pid:int,source):
    # sourcery skip: remove-redundant-continue, remove-unnecessary-else

    #global df_error
    try:
        #收集错误链接
        #df_error=pandas.DataFrame(columns=("pid","link","error"))
        #确保选择正确的解码器
        for param_features in ("lxml","html.parser","html5lib","html","html5","xml","lxml-xml"):
            try:
                soup=BeautifulSoup(source,param_features)
                try:
                    tag=soup.find("meta",attrs=dict(property="og:description"))
                    tags=tag["content"]
                except Exception:
                    logger.warning("好像未匹配到tags..")
                    logger.warning("再次匹配tags....")
                    logger.error(source)
                    """ | konachan.com" property="og:title" />"""
                    try:
                        tag=soup.find("meta",attrs=dict(property="og:title"))
                        tags=tag["content"].split("|")[0].strip()
                        print(tags)
                    except Exception:
                        logger.warning("匹配失败..")
                        logger.warning(f"https://konachan.com/post/show/{pid}/")
                        continue
                if isinstance(tags,str) and len(tags) != 0:
                    break
                logger.warning("param tags error change param_features...")
                continue
            except Exception:
                logger.warning("param_features error change param_features...")
                logger.warning(f"https://konachan.com/post/show/{pid}/")

                #df_error.add([pid,f"https://konachan.com/post/show/{pid}/","param_features error"])
                continue

            """
            <li><a class="original-file-unchanged" href=".jpg" id="highres">Image (731 KB JPG)</a>
            """
        try:
            img_link={}
            for imgs in [soup.select('li > a.original-file-unchanged.highres-show[href$=".jpg"][id="highres-show"]'),
                         soup.select('li > a.original-file-changed.highres-show[href$=".jpg"][id="highres-show"]'),
                        soup.find_all("a",attrs={"class":"original-file-unchanged","id":"highres"}),
                        soup.find_all("a",attrs={"class":"original-file-unchanged highres-show","id":"highres-show"}),
                        soup.find_all("a",attrs={"class":"original-file-changed","id":"highres"}),
                        soup.find_all("a",attrs={"class":"original-file-changed highres-show","id":"highres-show"}),
                        soup.find_all("link",attrs={"rel":"image_src"})] :


                if len(imgs) == 0:
                    continue
                else:

                    """ for img in imgs:
                        img_link["link"]=img["href"] 
                        
                        if not isinstance(img_link["link"], str):#判断是不是字符串
                            continue
                        
                        if (len(img_link["link"]) < 10) or ("plicit.png" in img_link["link"]):
                            
                            #logger.info("其他 imglink 类型 ?....")
                            #logger.info(img_link["link"])
                            #logger.info(f"https://konachan.com/post/show/{pid}/")
                            continue """

                    img_link["link"]=imgs[0]["href"]  

                    if not isinstance(img_link["link"], str) \
                    or (len(img_link["link"]) < 10) \
                    or ("plicit.png" in img_link["link"]):
                        continue
                        #是字符串 长度大于10
                    else:
                        break

                        #logger.info("查看 过滤 img....")
                        #print(img)
        except Exception as e:
            logger.warning("""img_link["link"]=img["href"] ?""")
            logger.warning(e)
            try:
                img=soup.find_all("meta",attrs={"property":"og:image"})
                img_link["link"]=img[0]["href"]
            except Exception as e:
                logger.error("parse error好像没有找到图片链....")
                return _extracted_from_parse_90(e, pid)
                            #df_error.to_excel("k_spider\error_img.xlsx",index=False)


        try:
            if (
                not isinstance(img_link["link"], str)
                or len(img_link["link"]) <= 10
                or "plicit.png" in img_link["link"]
            ):
                logger.error("未知 parse error 1....")
                logger.error(img_link["link"])
                logger.error(f"https://konachan.com/post/show/{pid}/")
                #df_error.add([pid,f"https://konachan.com/post/show/{pid}/","未知 parse error 1"])
                return (pid,"寄","寄")

        except Exception as e:
            logger.error("未知 parse error 2....")
            logger.error(e)
            logger.error(type(img_link["link"]))
            logger.error(f"https://konachan.com/post/show/{pid}/")
            #df_error.add([pid,f"https://konachan.com/post/show/{pid}/","未知 parse error 2"])
            return (pid,"寄","寄")


        finally:

            return (pid,img_link["link"],tags)

    except Exception:
        return _extracted_from_parse_90("未知 parse error 3....", pid)
    finally:
        pass


# TODO Rename this here and in `parse`
def _extracted_from_parse_90(arg0, pid):
    logger.error(arg0)
    logger.error(f"https://konachan.com/post/show/{pid}/")
    #df_error.add([pid,f"https://konachan.com/post/show/{pid}/","好像没有找到图片链接"])
    return (pid,"寄","寄")
        #保存错误连接
        #df_error.to_excel("k_spider\error_img.xlsx")
        
        
#下载图片
async def save_img(pid:int,img_link:str,tags:str):
    
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
                except Exception:
                    logger.warning("relink dowmload img 2 次.....")
                    await asyncio.sleep(random.randint(3,5))
                    re = await clinet.get(img_link,headers=headers,timeout=300)
            except Exception as e:
                logger.error(e)
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
            
        
if __name__ == "__main__":
    
    #主函数
    #3个大任务依次传递参数
    #这里可以用队列进一步改,懒得改了
    
    def main(pids,sem_times:int=15,wait_time:int=3):
        
        #并发获取源码
        #pids是一个pid列表
        async def process_urls(pids):
          
            sem= asyncio.Semaphore(sem_times) #并发数

            #current_sem= sem.__reduce__()
            #可以使用sem._value来获取当前可用的 Semaphore 的数量。
            #不过，需要注意的是，_value是 Semaphore 对象的内部属性，
            #Semaphore 对象的 _value 属性是私有的
            #因此最好不要在生产环境中使用它，以避免潜在的不兼容性和可维护性问题。

            #但可以通过 Semaphore 对象的 .__reduce__() 方法将其转换为一个元组 (Semaphore类，(初始计数，))，
            #然后再访问元组的第二个元素来获取 Semaphore 的初始计数，即当前可用的 Semaphore 的数量。

            #__reduce__()是Python中一个特殊的魔法方法，用于pickle（序列化）和unpickle（反序列化）对象。当对象需要被序列化时，pickle会调用对象的__reduce__()方法来得到一个包含对象状态的可序列化对象。在反序列化时，pickle会通过这个可序列化对象来还原对象状态。

            #  对于Semaphore对象，它的状态包括了semaphore的初始值和当前值。在序列化时，Semaphore对象可以通过__reduce__()方法将其状态序列化为一个元组，元组中包含了Semaphore的初始值和当前值，以及一个标志用于标识Semaphore类型。在反序列化时，pickle会使用这个元组来还原Semaphore对象的状态。

            async with sem:
                tasks = []#并发任务列表
                
                for i,pid in enumerate(pids):
                    
                    host_path=f"https://konachan.com/post/show/{pid}/"
                
                    #tasks.append(asyncio.ensure_future(get_source(pid,host_path)))
                    #The asyncio.ensure_future() function is deprecated in Python 3.10 in favor of asyncio.create_task().
                    tasks.append(asyncio.create_task(get_source(pid,host_path)))
                    
                    if (i+1) % sem_times == 0:
                        #每并发15个等待n秒
                        logger.info(f"等待{wait_time}秒继续并发")
                        await asyncio.sleep(wait_time)
                    
                results = await asyncio.gather(*tasks,return_exceptions=False)
                #参数
                return results
        
        
        #pid_source=[(pid,source),......]
        pid_source=asyncio.run(process_urls(pids))
        
        #多进程解析
        def run_tasks(task,pid_source):
            max_workers = min(len(pid_source), multiprocessing.cpu_count(), 6)
            results = []#结果列表
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(task,pid,source) for pid,source in pid_source if source != "寄"]
                for future in concurrent.futures.as_completed(futures):#all futures完成时的iterable对象
                    try:
                        results.append(future.result())
                        #logger.success("parse......")
                    except Exception as e:
                        logger.warning("引发 一个 parse error...")
                        #print(future.result())
                        logger.warning(e)
                        continue
            return results
        
        pid_img_link_tags=run_tasks(parse,pid_source)
        
        
        #并发下载图片
        async def download_imgs(pid_img_link_tags):
            
            sem= asyncio.Semaphore(sem_times) #并发数
            async with sem:
                tasks = []#并发任务列表
                
                pin=1
                for pid,img_link,tags in pid_img_link_tags:
                    if tags == "寄" or img_link == "寄":
                        logger.error("未知解析或下载错误引起...寄")
                        continue
                    else:
                        if pin % sem_times == 0:
                            logger.info(f"等待{wait_time}秒继续并发下载图片")
                            await asyncio.sleep(wait_time) 
                        tasks.append(asyncio.create_task(save_img(pid,img_link,tags)))
                        pin+=1
                    #logger.info("append download img task.....")
                results = await asyncio.gather(*tasks)

                results = \
                [(pid,tags,img_path,img_link)
                 for pid,tags,img_path,img_link in results
                 if tags != "寄" and img_link != "寄" and img_path != "寄"]

                #print(results)

                logger.success(f"downloaded {len(results)} img ......")
                return results
        
        pid_tags_img_path_img_link=asyncio.run(download_imgs(pid_img_link_tags))
        
        return pid_tags_img_path_img_link
    
    
    
    #数据的进一步操作

    #连接数据库 mysql 
    logger.info("连接数据库中...........")
    while True:
        #连接数据库
        try:
            mysql_user=os.getenv("mysql_user")
            #input("输入mysql用户名:")
            mysql_password=os.getenv("mysql_password")
            #input("输入mysql用户密码:")
            mysql_host=os.getenv("mysql_host")
            #input("输入host,本地则localhost:")
            mysql_database=os.getenv("mysql_database")
            #input("输入要连接的数据库:")
    
            engine=\
            create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}")
            engine=engine.connect()

            break
        
        except Exception as e:
            
            logger.error(e)
            logger.error("连接失败重试")

    
    logger.success("link dbas 准备导入数据.....")
    
    #表结构
    #表数据添加到数据库
    columns=("pid","tags","path","link","status","time")
    df=pandas.DataFrame(columns=columns)
    
    #排除重复tag 返回删除的数量
    def uni_tag():
        
        global engine

            #从数据库加载tags表到dataframe
        try:
            df = pandas.read_sql_table('tags', engine)
        except Exception:
            #没有则创建一个tags表
            tagstable=pandas.DataFrame(columns=["tag"])
            tagstable.to_sql("tags",engine,if_exists="append",index=False)
            df = pandas.read_sql_table('tags', engine)

        #记录tag之前数量
        num_rows_before = len(df)

        #去除重复tag(修改了df)
        df.drop_duplicates(subset='tag', keep='first', inplace=True)

        #记录删除重复tag后的数量
        num_rows_after = len(df)

        #得到排除的重复tag数量
        num_rows_deleted = num_rows_before - num_rows_after

        logger.info(f"数据库tag表共有{len(df)}条tag")
        #把去重的tags表重新保存到数据库
        df.to_sql('tags', engine, if_exists='replace', index=False)
        df.to_csv(r"k_spider\tags.csv",mode="w",index=False,header=False)
        logger.info(f"排除{num_rows_deleted}个重复tag")

        return num_rows_deleted
    
    #外部全局变量 记录加入数据库数据量
    number=0
    
    def save_img_and_todb(pids,wait_time:int,sem_times:int):
        
        global df
        global number
        
        #执行main 得到数据
        try:      
            pid_tags_img_path_img_link=main(pids=pids,wait_time=wait_time,sem_times=sem_times)
            assert len(pid_tags_img_path_img_link)>0,"最后没有得到数据"
        except Exception as e:
            logger.error(e)
            raise e

        #保存所有tag
        set_tags=set() #用集合保存唯一tag

        #排除无效数据
        for pid,tags,img_path,img_link in pid_tags_img_path_img_link:
            if  (tags == "寄") or \
                ("plicit.png" in img_link) or \
                (img_path == "寄") or \
                (img_link == "寄"):
                #status=0
                logger.warning("no add error img data....")
                continue
            else:
                #status=1
                times=pandas.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                df.loc[pid]=[pid,tags,img_path,img_link,1,times]
                logger.success(f"imported: {img_link}")
                number+=1
        
                for tag in tags.split(" "):
                    if len(tag.strip()) != 0 :
                        set_tags.add(tag.strip())
                        #print(tag.strip())

            
        df_tags=pandas.DataFrame(set_tags,columns=["tag"])

        #print(df_tags)
        #保存tags到数据库
        df_tags.to_sql("tags",engine,if_exists="append",index=False)

        #查看有效添加tag数量(tag唯一,排除重复)
        logger.success(f"保存{df_tags.shape[0]-uni_tag()}个tag到数据库")

        #保存图像数据到数据库
        df.to_sql("kimg",engine,if_exists="append",index=False)

        #文件备份一下
        df.to_csv("k_spider\kimg.csv",mode="a",index=False,header=False)
        #,header=["pid","tags","path","link","status"])

        """logger.info("wait 3 s .......")
        sleep(3)"""
        logger.success(f"added {number} img data into {mysql_database}....")
        
    def mode_a():#随机范围下载模式
        #获取一些变量 单次下载数量 等待时间 并发获取源码与下载图片的并发数
        while True:
            try:
                down_number=os.getenv("down_number")
                down_number=int(down_number)
      
                wait_time,sem_times=os.getenv("wait_time"),os.getenv("sem_times")
                wait_time,sem_times=int(wait_time),int(sem_times)

                low,upper=os.getenv("low"),os.getenv("upper")
                low,upper=int(low),int(upper)+1
            
                assert isinstance(down_number,int),"单次下载数量请输入整数"
                assert isinstance(wait_time,int),"等待时间请输入整数"
                assert isinstance(sem_times,int),"并发数请输出整数"
                assert isinstance(low,int),"下标请输入整数"
                assert isinstance(upper,int),"上标请输出整数"
                break
        
            except Exception as e:
                logger.error(e)
                continue
       
        logger.success(f"单次下载数量:{down_number}")
        logger.success(f"等待时间:{wait_time} 并发数:{sem_times}")
        logger.success(f"下载图片路径:{imgpath}")
        

        #for _ in tqdm(range(int(os.getenv("times"))),desc="import_db"):#类似无限循环
        for _ in range(int(os.getenv("times"))):

            #排除重复pid
            try:
                df_pid=pandas.read_sql("select pid from kimg;",engine)
            except Exception: 
                #没有kimg表则先创建
                df.to_sql("kimg",engine,if_exists="append",index=False)
                df_pid=pandas.read_sql("select pid from kimg;",engine)
        
        
            logger.info(f"数据库共有{len(df_pid)}条图像数据")
        
            #pid_list = df_pid.iloc[:, 0].tolist()
        
            #生成随机pid列表
            pids0=random.sample(range(low,upper), down_number)
            #pids0=[253158,206200] 失败下载错误重试 (已完成)
            #单次下载的pid列表,并从列表pids0中移除与列表pid_list中相等的元素
            #pids = [x for x in pids0 if x not in pid_list]
            #优化为集合运算
        
            #logger.info(f"前pids长度{len(pids0)}") 
            # OK test结果一致
        
            pids = list(set(pids0)-set(df_pid["pid"]))
        
            #logger.info(f"后pids长度{len(pids)}")
            #logger.info(len(pids0))
            #logger.info(len(df_pid["pid"]))
        
            #防止pids为空 为空进入下一个
            #if len(pids)==0:
            if not pids:
                continue
        
            #输出排除的重复pid数
            if len(pids0)-len(pids) >0 :
                logger.info(f"排除{len(pids0)-len(pids)}个重复pid....")
            
            save_img_and_todb(pids,wait_time,sem_times)

        logger.success(f"added {number} img data into {mysql_database}....")

    def mode_b(pids:list=eval(os.getenv("pid_list"))):#指定下载模式
        #print(pids)
        save_img_and_todb(pids,int(os.getenv("wait_time")),int(os.getenv("sem_times")))

    try:
        mode=os.getenv("mode")
        if mode=="a":
            mode_a()
        elif mode=="b":
            mode_b()
        else:
            raise 'mode_a or mode_b Error'

    except Exception as e:
        
        raise e

    
        
    
    
    
    


