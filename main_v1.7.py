## coding=utf-8
import asyncio
from sqlalchemy import create_engine,text
import pandas
from loguru import logger
import multiprocessing
import concurrent.futures
import random
import os
from dotenv import load_dotenv # pip install python-dotenv
from cellfunctions_ import get_headers,get_source,parse,save_img 
#import httpx 
#from bs4 import BeautifulSoup
#from tqdm import tqdm
#from selenium import webdriver
#from selenium.webdriver.edge.service import Service
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.support import expected_conditions
#from selenium.webdriver.common.by import By
#import queue 
#from importlib.resources import path
#from fake_useragent import UserAgent
#from PIL import ImageSS
#from io import BytesIO


#记录日志
logger.add("k_spider\log\main_log_v1.7.log")

#加载配置文件
load_dotenv()

#图片路径 这是绝对路径记得在不同文件夹下 不同设备下记得修改
if __name__ == "__main__":
    imgpath=os.getenv("IMG_PATH")
    headers=get_headers()


#不存在则创建文件夹
if __name__ == "__main__" and not os.path.exists(imgpath):
    os.mkdir(imgpath)

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
                    tasks.append(asyncio.create_task(get_source(pid,host_path,headers)))
                    
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
                        tasks.append(asyncio.create_task(save_img(pid,img_link,tags,headers,imgpath)))
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
    def link_db(): 
        logger.info("连接数据库中...........")

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

            kimg_table=os.getenv("mysql_img_table") #mysql_img_table=kimg mysql_tags_table=tags
            tags_table=os.getenv("mysql_tags_table")

            logger.success(f"图像数据表: {kimg_table}")
            logger.success(f"tag数据表: {tags_table}")

            logger.success("link dbas 准备导入数据.....")
            return engine,kimg_table,tags_table
        
        except Exception as e:
            
            raise e
                
        
            
        
    

    #外部全局变量 记录加入数据库数据量
    number=0

    def save_img_and_todb(pids,wait_time:int,sem_times:int,engine,kimg_table,tags_table):
        global df
        global number

        #初始化
        #表结构
        #表数据添加到数据库
        columns=('pid', 'tags', 'link', 'path', 'status', 'time')
        df=pandas.DataFrame(columns=columns)
        #执行main 得到数据
        try:      
            pid_tags_img_path_img_link=main(pids=pids,wait_time=wait_time,sem_times=sem_times)
            assert len(pid_tags_img_path_img_link)>0,"最后没有得到数据"
        except Exception as e:
            #logger.error(e)
            raise e
        #(pymysql.err.ProgrammingError) (1146, "Table 'kimgdb.kimg' doesn't exist")
        #[SQL: select distinct pid from kimg;]
        #(Background on this error at: https://sqlalche.me/e/20/f405)
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
        df_tags.to_sql(tags_table,engine,if_exists="append",index=False)
        df_tags.to_csv(f"k_spider\\{tags_table}.csv",mode="a",index=False,header=False)
        #engine.execute(text())
        #查看有效添加tag数量(tag唯一,排除重复)
        #logger.success(f"保存{df_tags.shape[0]-uni_tag()}个tag到数据库")
        #考虑用数据库的存储过程实现

        #保存图像数据到数据库
        df.to_sql(kimg_table,engine,if_exists="append",index=False)

        #文件备份一下
        df.to_csv(f"k_spider\\{kimg_table}.csv",mode="a",index=False,header=False)
        #,header=["pid","tags","path","link","status"])

        """logger.info("wait 3 s .......")
        sleep(3)"""
        engine.commit()
        logger.success(f"added {number} img data...")
        
    def mode_a():#随机范围下载模式
        #获取一些变量 单次下载数量 等待时间 并发获取源码与下载图片的并发数
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
        except Exception as e:
            raise e
       
        logger.success(f"单次下载数量:{down_number}")
        logger.success(f"等待时间:{wait_time} 并发数:{sem_times}")
        logger.success(f"下载图片路径:{imgpath}")
        

        #for _ in tqdm(range(int(os.getenv("times"))),desc="import_db"):#类似无限循环
        for _ in range(int(os.getenv("times"))):
            engine,kimg_table,tags_table=link_db()
            with engine:
                #排除重复pid
                try:
                    df_pid=pandas.read_sql(text(f"select distinct pid from {kimg_table};"),engine)
                    df_pid=df_pid["pid"]
                except Exception as e:
                    df_pid=[]
                    print(e)

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
            
                pids = list(set(pids0)-set(df_pid))
            
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
                
                save_img_and_todb(pids,wait_time,sem_times,engine,kimg_table,tags_table)

            logger.success(f"added {number} img data....")

    def mode_b(pids:list=eval(os.getenv("pid_list"))):#指定下载模式
        #print(pids)
        engine,kimg_table,tags_table=link_db()
        with engine:
            save_img_and_todb(pids,int(os.getenv("wait_time")),int(os.getenv("sem_times")),engine,kimg_table,tags_table)

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

    
        
    
    
    
    


