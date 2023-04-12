#### 这个程序完成如下功能
##### 爬k站图片 仅当数据处理练习用
##### 保存图片到本地 保存运行日志
##### 保存图片数据到数据库两个表中
##### 在.env文件配置信息

#### 在本地的kimg表
##### k_grab\k_spider\Kimg.csv
##### 在本地的tags表
##### k_spider\tags.csv

#### 保存图片的绝对路径
##### IMG_PATH=C:\Users\S\Desktop\database_learn\k_spider\pictures

#### MYSQL 连接信息
mysql_user=S
mysql_password=xxxxx
mysql_host=xx.xx.xx.xx
mysql_database=kimgdb
**保存的表**
mysql_img_table=kimg 
mysql_tags_table=tags

#### 下载配置
##### 单次下载数量
down_number=10
#### 每个并发数后的等待时间
wait_time=1
#### 下载源码,图片的最大并发数
sem_times=10
#### 下载范围[low,upper]
low=300000
upper=350000
#### 指定模式 a(随机范围下载模式) 或者 b(指定pid_kist列表下载模式) 
pid_list=[331516]
mode=b

