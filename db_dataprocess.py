## coding=utf-8
import os
from sqlalchemy import create_engine,text
import pandas 
from loguru import logger

mysql_user=os.getenv("mysql_user")
#input("输入mysql用户名:")
mysql_password=os.getenv("mysql_password")
#input("输入mysql用户密码:")
mysql_host=os.getenv("mysql_host")
#input("输入host,本地则localhost:")
mysql_database=os.getenv("mysql_database")
#input("输入要连接的数据库:")

engine=create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}")

with engine.connect() as connection:
    print("链接成功")
    re=connection.execute(text('select count(distinct tag) from tags;'))
    re2=connection.execute(text('select count(tag) from tags;'))
    print(re.fetchall()[0][0])
    print(re2.fetchall()[0][0]) ##执行一次fetch后里面没有东西了
    print(re2.fetchall()) # []
    """ a=re2.fetchall()
    b=re.fetchall()[0][0]
    print(a-b) """

with engine.connect() as connection:
    print("链接成功")
    re=connection.execute(text('select count(distinct pid) from kimg;'))
    re2=connection.execute(text('select count(pid) from kimg;'))
    a=re.fetchall()[0][0]
    b=re2.fetchall()[0][0]
    print(a,b)
    print(b-a)

with engine.connect() as connection:
    print("链接成功")
    re=connection.execute(text('select count(distinct pid) from kimg;'))
    re2=connection.execute(text('select count(pid) from kimg;'))
    a=re.fetchall()[0][0]
    b=re2.fetchall()[0][0]
    print(a,b)
    print(b-a)

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
    

"""
connection.execute("select tag from tags limit 20;")

发生异常: ObjectNotExecutableError
Not an executable object: 'select tag from tags limit 20;'
AttributeError: 'str' object has no attribute '_execute_on_connection'

这个异常是由于sqlalchemy不接受字符串作为可执行对象1。你需要使用sqlalchemy.text()函数来包装你的sql语句，使其可执行。例如：

from sqlalchemy import create_engine, text

# 创建Engine对象
engine = create_engine('sqlite:///testdb.db')

# 获取Connection对象
conn = engine.connect()

# 执行查询语句，使用text()函数
result_proxy = conn.execute(text("select tag from tags limit 20;"))
result = result_proxy.fetchall()
for item in result:
    print(item)

# 关闭连接
conn.close()
"""