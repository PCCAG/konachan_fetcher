#### 这个程序完成如下功能 启动 main.py
##### 爬k站图片 仅当自己数据处理练习用用
##### 保存图片到本地 保存运行日志
##### 保存图片数据到数据库两个表中 mysql或者其他关系数据库 
##### 在.env文件配置信息

##### 代码可能写的很shi山,在学习中

#### 在本地的kimg表
##### .\k_grab\k_spider\Kimg.csv
##### 在本地的tags表
##### .\k_spider\tags.csv
##### log
##### .\k_spider\log\xx.log

#### 设置保存图片的绝对路径
##### IMG_PATH=C:\Users\S\Desktop\database_learn\k_spider\pictures

#### MYSQL 连接信息
mysql_user=S  \
mysql_password=xxxxx  \
mysql_host=xx.xx.xx.xx  \
mysql_database=kimgdb  \
**保存的表**  \  
mysql_img_table=kimg \ 
mysql_tags_table=tags \

#### 下载配置
##### 随机范围下载模式
##### 单次下载数量 不能太大
down_number=10
#### 每个并发数后的等待时间
wait_time=3
#### 下载源码,图片的最大并发数 不能太大
sem_times=10
#### 下载范围[low,upper]
low=300000
upper=350000
#### 指定模式 a(随机范围下载模式) 或者 b(指定pid_kist列表下载模式) 
pid_list=[331516]
mode=b

## 注
##### 利用clash api 来作代理访问 需安装clash且已有配置 或者在 cellfunction_.py自己修改代理
##### 没有数据库就用模式b或者自己看着来改

