
### 使用：

* 有数据库启动 main.py
* 如果没有数据库，启动 get_imags_data.py  (数据表：.\Data\kimg.csv)

### 配置：

* .env

### 依赖：

* packages.txt ,  requirements.txt

```bash
# -i https://pypi.tuna.tsinghua.edu.cn/simple

pip install sqlalchemy
pip install beautifulsoup4 httpx
pip install pandas loguru python-dotenv fake_useragent playwright playwright-stealth
pip install aiofiles
python -m playwright install
pip install html5lib lxml html.parser html5
pip install pymysql mysql
```

### 保存图片的路径：

**最好是绝对路径**

* IMG_PATH=.\pictures

### MYSQL 连接信息 ，如：

**没数据库链接可以不填**

* mysql_user=root
* mysql_password=xxxxxxx
* mysql_host=localhost
* mysql_database=kimgdb
* mysql_img_table=kimg
* mysql_tags_table=tags

**本地数据表：**

.\k_spider\\{kimg_table}.csv

.\k_spider\\{tags_table}.csv

### 下载配置：

#### 单次下载数量

* down_number=10

#### 下载源码,图片的最大并发数

* sem_times=10

#### 下载范围[low,upper]

* low=300000
* upper=350000

#### 单次循环次数

* times=10

#### 代理(http):

* http_proxy=http://127.0.0.1:10809

### 表样式:

数据库会产生三个表:

* kimg
* tags
* tags_unique

![1693236442027](image/readme/1693236442027.png)

![1693236410201](image/readme/1693236410201.png)![1693236471373](image/readme/1693236471373.png)

### 其他:

测试选项无需修改

* pid_list=[343131,344094,344095,344096,344097,344098,35543]
* mode=a
