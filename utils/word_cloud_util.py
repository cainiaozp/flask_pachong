import jieba  # 分词
from matplotlib import pylab as plt     # 绘图，数据可视化
from wordcloud import WordCloud         # 词云
from PIL import Image                   # 图片处理
import numpy as np                      # 矩阵运算
from config.DBInit import DbHandler     #导入包
from model.JobModel import Job  #导入包
dbsession = DbHandler().create_session()# 创建数据库会话，用于对数据进行增删改查操作

def createWordCloudjpg(text,targetImgSrc,resImgSrc):
    # 分词
    cut = jieba.cut(text)
    string = ' '.join(cut)
    print(string)

    # 图片
    img = Image.open(targetImgSrc)  # 打开遮罩图片
    img_arr = np.array(img)  # 将图片转化为列表
    wc = WordCloud(
        background_color='white',
        mask=img_arr,
        font_path='C:\Windows\Fonts\simsun.ttc'
    )
    wc.generate_from_text(string)

    # 绘制图片
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')  # 不显示坐标轴


    # 显示生成的词语图片
    # plt.show()

    # 输入词语图片到文件
    plt.savefig(resImgSrc, dpi=500)

def create_jpg():
    job_list =  dbsession.query(Job).all()
    # job_name_text = ''
    # for job in job_list:
    #     job_name_text = job_name_text + job.job_name
    # createWordCloudjpg(job_name_text,'../static/4.jpg','../static/job_name.jpg')
    # company_text = ''
    # for job in job_list:
    #     company_text = company_text + job.company
    # createWordCloudjpg(company_text,'../static/3.jpg','../static/company.jpg')
    welfare = set()

    for job in job_list:
        if job.welfare != None:
            welfare.add(job.welfare)
    welfare_text = ''
    for item in welfare:
        welfare_text = welfare_text + item
    createWordCloudjpg(welfare_text,'../static/2.jpg','../static/welfare.jpg')
    """
    这是定义一个函数create_jpg，它首先从数据库中获取所有职位信息job_list，然后遍历job_list获取所有福利信息，
    并将它们以字符串形式连接成welfare_text。最后调用createWordCloudjpg函数生成福利词云图并保存到指定路径中。
    """

if __name__ == '__main__':
    create_jpg()