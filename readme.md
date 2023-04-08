# 这个程序完成如下功能
#爬k站图片
#保存图片到本地 保存运行日志
#保存图片数据到数据库 kimg tag 两个表中
#在.env文件配置信息 不可为空

# 在本地的kimg表
#k_grab\k_spider\Kimg.csv
# 在本地的tags表
#k_spider\tags.csv

# 保存图片的绝对路径
IMG_PATH=C:\Users\S\Desktop\database_learn\k_spider\pictures

# MYSQL 连接信息
mysql_user=S
mysql_password=778899vvbbnnmm
mysql_host=43.139.243.213
mysql_database=kimgdb

# 下载配置
## 单次下载数量
down_number=10
## 每个并发数后的等待时间
wait_time=1
## 下载源码,图片的最大并发数
sem_times=10
## 下载范围[low,upper]
low=300000
upper=350000
## 指定模式 a(随机范围下载模式) 或者 b(指定pid_kist列表下载模式) 
pid_list=[331516]
mode=b


cookie: """__utmz=235754395.1668606749.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); vote=1; hide_resized_notice=1; cf_clearance=x0.xPDSvJl4UX0X3wvS8xwTSTppfKd5ym.x8KeDAbEQ-1678080244-0-160; __utma=235754395.457949892.1668606749.1678080245.1678089608.45; country=CN; blacklisted_tags=%5B%22%22%5D; konachan.com=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTFhZmI1MWEyM2M0NDQ2YWY0MGQzNjcyMDc4ZmNmZTNlBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUtyWVI5aVJIZ1l5NE5POFJnakJ4enBCblFhbUt3d25uUFBGTVc0YlMyODQ9BjsARg%3D%3D--6f6e24cd1ee80ff847033a28f57eb639c4bf6da8; __utmc=235754395; forum_post_last_read_at=%222023-03-06T09%3A13%3A50%2B01%3A00%22; __utmt=1; __utmb=235754395.6.10.1678089608""",
dnt: 1,
sec-ch-ua-platform: "Windows",
sec-fetch-dest: "document",
sec-fetch-mode: "navigate",
upgrade-insecure-requests: 1,
user-agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"