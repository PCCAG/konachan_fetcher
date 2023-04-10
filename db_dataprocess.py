import os
from sqlalchemy import create_engine

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
    connection.execute('select count(distinct tag) from tags;')
    
