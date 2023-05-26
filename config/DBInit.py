from sqlalchemy import create_engine#导入需要的包
from sqlalchemy.orm import sessionmaker#导入需要的包
from sqlalchemy.pool import NullPool#导入需要的包
from config import USERNAME ,PASSWORD#导入需要的包


class DbHandler(object):# 定义一个数据库处理类
    def __init__(self):
        self.db_addr = "mysql+pymysql://"+USERNAME+":"+PASSWORD+"@localhost/job"# 数据库地址, USERNAME和PASSWORD为用户名及密码，job为数据库名

    def create_session(self):  # 创建数据库会话
        engine = create_engine(self.db_addr, poolclass=NullPool, echo=False)
        # poolclass=NullPool表示不开启连接池，echo=False表示不输出日志
        session = sessionmaker(bind=engine)()
        return session

    def create_engine(self):  # 创建数据库引擎
        engine = create_engine(self.db_addr, poolclass=NullPool, echo=False)
        return engine

# engine = DbHandler().create_engine()
#
#
# with engine.connect() as con:
#     # rs=con.execute(text("SELECT * FROM jobs"))
#     rs=con.execute(text("SELECT count(1),area FROM jobs GROUP BY area limit 20"))
#     for result in rs:
#         print(result)


