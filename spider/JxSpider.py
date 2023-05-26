import requests
from bs4 import BeautifulSoup
from config import jiaXingUrl
from model.JobModel import Job
import time
from threading import Thread
from config.DBInit import DbHandler
from config import queue
from config import queue_page
"""
使用了Python的requests库和BeautifulSoup库来进行网页爬取和解析。
requests库发送HTTP请求并获取响应,而BeautifulSoup库则用于解析HTML和XML文档。
"""
# 头部
headers = {
}

class JxSpider(Thread):#JxSpider类继承自Thread类，用于实现多线程。
    def __init__(self):
        super().__init__()

    def job_request(self,url):#job_request方法用于爬取页面信息，并将爬取到的信息封装到Job对象中，最终返回一个Job对象列表。
        """
        爬取信息
        :param url: 爬取页面地址
        :return: 封装后的爬取结果
        """
        print("爬取url ==> %s" % url)
        #发送 HTTP 请求
        #不验证SSL证书
        res = requests.get(url, verify=False, headers=headers)
        html = res.text
        bs = BeautifulSoup(html, "html.parser")
        tbody = bs.find("body")

        job_list = tbody.findAll(name='div', attrs={"class": "job_list2"})
        # print(job_list)
        jobList = []
        for job_html in job_list:
            """
            使用 BeautifulSoup 库解析 HTML 页面，
            找到class为job_title的div元素下的第一个a元素,然后获取它的contents列表中的第一个元素作为job_name。
            """
            # 岗位名称
            job_name = job_html.find('div', class_='job_title').find('a').contents[0]
            # 薪水 月/年
            job_salary = job_html.find('p', class_='job_salary').find('strong').contents[0]
            job_welfare = job_html.findAll('p', class_='job_welfare')

            res = []
            res.__len__()
            welfare = ""
            if job_welfare != None:
                for item in job_welfare:
                    if item != None:
                        if item.find('span') != None and item.find('span').contents.__len__() != 0:
                            welfare = welfare + " " + item.find('span').contents[0]

            #公司名称
            company = job_html.find('div', class_='company_title').find('a').contents[0]
            duty_title = job_html.find('div', class_='job_duty').find('div', class_='duty_title')

            spans = duty_title.find_all('span')    #取span,把第一二三四项分别赋值给area,num,education,work_experience
            # 地区, 招聘人数
            area = spans[0].contents[0]
            area = area.split('/')[-1:][0]  # 取‘/’最后一项避免重复
            num = spans[1].contents[0]
            # 学历 经验要求
            education = spans[2].contents[0]
            work_experience = spans[3].contents[0]
            job = Job(job_name = job_name,
                           job_salary = job_salary,
                           company = company,
                           area = area,
                           num = num,
                           education = education,
                           work_experience = work_experience,
                           welfare = welfare
                      )
            jobList.append(job)
        return jobList

    def run(self):#run方法为程序入口，创建数据库连接，并根据页码不断爬取招聘信息，将爬取到的信息存储到数据库中。
        session = DbHandler().create_session()
        """
        程序入口
        :return:
        """
        f = open("page.txt")  # 返回一个文件对象
        page = f.readline()  # 调用文件的 readline()方法
        print(page)
        f.close()
        while (True):
            if queue.get() == "stop":
                break
            url = jiaXingUrl.format(_page=int(page))
            jobList = self.job_request(url)
            print("===========")
            print(jobList)
            session.add_all(jobList)
            session.commit()
            page = int(page) + 1
            file2 = open("page.txt", 'w+')
            file2.write(str(page))
            file2.close()

            time.sleep(1)
            queue.put("start")
            queue_page.put(page)
"""
该代码是一个爬虫程序，用于爬取稼星人才网（http://www.jxrcw.cn/）上的招聘信息，并将爬取到的信息存储到数据库中。以下是代码的详细解释：

2. JxSpider类继承自Thread类，用于实现多线程。

3. job_request方法用于爬取页面信息，并将爬取到的信息封装到Job对象中，最终返回一个Job对象列表。

4. run方法为程序入口，创建数据库连接，并根据页码不断爬取招聘信息，将爬取到的信息存储到数据库中。

5. 在程序运行前，需要创建一个page.txt文件，并将其设置为网站上的第一页。当程序运行时，会从该文件中读取页码并开始爬取，每爬取完一页信息后，会将页码加1并将其写回到page.txt中。在运行过程中，可以通过queue来控制程序的启停，当从queue中获取到“stop”字符串时，程序会停止运行。

6. 基于以上代码，可以通过多线程的形式提高爬取数据的效率。
"""