# coding: utf-8
from sqlalchemy import Column, String#导入所需的包
from sqlalchemy.dialects.mysql import INTEGER#导入所需的包
from sqlalchemy.ext.declarative import declarative_base#导入所需的包

Base = declarative_base()# 定义Base类，用于生成和映射相应的数据表结构
metadata = Base.metadata# 获取base类的metadata属性，即数据表结构的元数据

# C:\Users\lzz\AppData\Local\Programs\Python\Python39\Scripts> sqlacodegen mysql+pymysql://root:12345678@127.0.0.1:3306/job --tables jobs > D:\study\jobAnalyseSystem\model\JobModel.py


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(INTEGER(11), primary_key=True)
    job_name = Column(String(255))
    job_salary = Column(String(255))
    company = Column(String(255))
    area = Column(String(255))
    num = Column(String(255))
    education = Column(String(255))
    work_experience = Column(String(255))
    welfare  = Column(String(255))
"""
创建jobs表，表中分别有以上9列信息，这个与用哪个Na软件查看的可视化表一样
"""