### 使用 启动 main.py
#### 这个爬虫程序完成如下功能
##### 爬k站图片 , 仅当个人数据处理练习,学习用用
##### 保存图片到本地 保存运行日志
##### 保存图片数据到数据库两个表中 mysql或者其他关系数据库 
##### 在.env文件配置信息
- - - 
##### 代码可能写的很shi山,在学习中 , 思路如下:
##### 将一个图片爬取过程,分解为 获取源码 , 解析地址 , 下载及保存图片 三个小过程 由一个数字pid来标记每个唯一图片的爬取
##### 根据范围,每次给定随机一堆数量pid列表 ,然后再分三个过程, 异步多并发获取所有的源码 , 多进程解析所有源码内的图片链接 , 异步多并发下载及保存图片
##### 通过pandas保存图片pid,tags, link,保存path,状态,导入时间 为一个表 , 另一个表为tags 方便以后统计标签信息
##### 我还并没有写用tag下图片的功能 , 不过可以在下载大量图片后用tag在数据表中查询(模糊查询)相关的图片地址,图片链接,图片下载时间 . 或者可以结合tags表作外键链接
- - - 
##### 在本地的kimg表
##### .\k_grab\k_spider\Kimg.csv
##### 在本地的tags表
##### .\k_spider\tags.csv
##### log
##### .\k_spider\log\xx.log
 
#### 设置保存图片的绝对路径 如:
##### IMG_PATH=C:\Users\S\Desktop\database_learn\k_spider\pictures

#### MYSQL 连接信息
mysql_user=S  \
mysql_password=xxxxx  \
mysql_host=xx.xx.xx.xx  \
mysql_database=kimgdb  \
**保存的表**  \
mysql_img_table=kimg  \
mysql_tags_table=tags  

#### 下载配置
##### 随机范围下载模式
##### 单次下载数量 不能太大
down_number=10
#### 每个并发数后的等待时间
wait_time=3
#### 下载源码,图片的最大并发数 不能太大
sem_times=10
#### 下载范围[low,upper]
low=300000 \
upper=350000 
#### 指定模式 a(随机范围下载模式) 或者 b(指定pid_kist列表下载模式) 
pid_list=[331516] \
mode=b

## 注
- - -
##### 利用clash api 来做的代理访问 需安装clash且已有配置 或者在 cellfunction_.py自己修改代理
##### 没有数据库就用模式b或者自己看着来改
##### 利用selenium 无头模式来获取的cookie
##### 看报错安装相应的包
