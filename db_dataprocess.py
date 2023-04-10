## coding=utf-8
import os
from sqlalchemy import create_engine,text

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