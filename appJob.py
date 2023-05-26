from flask import Flask, request, render_template, session, redirect, jsonify, g
from spider.JxSpider import JxSpider
from utils.query import querys
import re
from config import queue
from config import queue_page
from config.DBInit import DbHandler
from model.JobModel import Job
from sqlalchemy import func
from sqlalchemy import text
app = Flask(__name__)
app.secret_key = 'This is a app.secret_Key , You Know ?'
dbsession = DbHandler().create_session()

@app.route('/')
def every():
    return render_template('login.html')

@app.route("/home")
def home():
    email = session['email']
    allCount = dbsession.query(func.count(Job.id)).scalar()
    benkeCount = dbsession.query(Job).filter(Job.education.like("%本科%")).count()
    dazhuanCount = dbsession.query(Job).filter(Job.education.like("%大专%")).count()
    zhongzhuanCount = dbsession.query(Job).filter(Job.education.like("%中专%")).count()
    boshiCount = dbsession.query(Job).filter(Job.education.like("%博士%")).count()
    shuoshiCount = dbsession.query(Job).filter(Job.education.like("%硕士%")).count()

    return render_template(
        "index.html",
        allCount = allCount,
        benkeCount = benkeCount,
        dazhuanCount = dazhuanCount,
        zhongzhuanCount = zhongzhuanCount,
        boshiCount = boshiCount,
        shuoshiCount = shuoshiCount,
        email=email,
    )

@app.route("/index_data")
def index_data():
    res = {}
    allCount = querys('select count(1) from jobs', [], 'select')
    benkeCount = querys('select count(1) from jobs where education like "%%本科%%"', [], 'select')
    dazhuanCount = querys('select count(1) from jobs where education like "%%大专%%"', [], 'select')
    zhongzhuanCount = querys('select count(1) from jobs where education like "%%中专%%"', [], 'select')
    boshiCount = querys('select count(1) from jobs where education like "%%博士%%"', [], 'select')
    shuoshiCount = querys('select count(1) from jobs where education like "%%硕士%%"', [], 'select')

    res["allCount"] = tuple(allCount)[0:1][0][0]
    res["benkeCount"] = tuple(benkeCount)[0:1][0][0]
    res["dazhuanCount"] = tuple(dazhuanCount)[0:1][0][0]
    res["zhongzhuanCount"] = tuple(zhongzhuanCount)[0:1][0][0]
    res["boshiCount"] = tuple(boshiCount)[0:1][0][0]
    res["shuoshiCount"] = tuple(shuoshiCount)[0:1][0][0]

    return jsonify(res)


@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        request.form = dict(request.form)

        def filter_fns(item):
            return request.form['email'] in item and request.form['password'] in item

        users = querys('select * from user', [], 'select')
        login_success = list(filter(filter_fns, users))
        if not len(login_success):
            return '账号或密码错误'

        session['email'] = request.form['email']
        return redirect('/home', 301)

    else:
        return render_template('./login.html')

@app.route("/registry",methods=['GET','POST'])
def registry():
    if request.method == 'POST':
        request.form = dict(request.form)
        if request.form['password'] != request.form['passwordCheked']:
            return '两次密码不符'
        else:
            def filter_fn(item):
                return request.form['email'] in item

            users = querys('select * from user', [], 'select')
            filter_list = list(filter(filter_fn, users))
            if len(filter_list):
                return '该用户名已被注册'
            else:
                querys('insert into user(email,password) values(%s,%s)',
                       [request.form['email'], request.form['password']])

        session['email'] = request.form['email']
        return redirect('/home', 301)

    else:
        return render_template('./register.html')


"""==========================================================================================="""

@app.route("/search/<int:searchId>",methods=['GET','POST'])
def search(searchId):
    email = session['email']
    data = []
    if request.method == 'GET':
        if searchId == 0:
            return render_template(
                'search.html',
                idData=data,
                email=email
            )
    else:
        searchWord = dict(request.form)['searchIpt']
        def filter_fn(item):
            if item[3].find(searchWord) == -1:
                return False
            else:
                return True
        jobList = dbsession.query(Job).filter(Job.job_name.like("%{}%".format(searchWord))).all()
        print(jobList)
        return render_template(
            'search.html',
            data=jobList,
            email=email
        )

# class Student(Thread):
#     def __init__(self, queue):
#         super().__init__()
#         self.queue = queue
#
#     def run(self):
#         i = 1
#         while (True):
#             if queue.get() == "stop":
#                 break
#             print(i)
#             time.sleep(1)
#             i = i + 1
#             queue.put("start")


def startJiaXingSpider():
    queue.put("start")
    s = JxSpider()
    s.start()

def stopJiaXingSpider():
    queue.put("stop")

@app.route("/jxStart", methods=['GET', 'POST'])
def jiaXingStartSpider():
    res = {}
    try:
        queue_page.queue.clear()
        startJiaXingSpider()
        res["code"] = "200"
    except:
        res["code"] = "400"
    return jsonify(res)

@app.route("/jxStop", methods=['GET', 'POST'])
def jiaXingStopSpider():
    res = {}
    try:
        stopJiaXingSpider()
        res["code"] = "200"
        res["page"] = queue_page.qsize()
    except:
        res["code"] = "400"
    return jsonify(res)


@app.route("/time_t",methods=['GET','POST'])
def top20():
    area_set = set()
    job_list =  dbsession.query(Job).all()
    for job in job_list:
        area_set.add(job.area)
    area_top20 = {}
    for addr in  area_set:
        salary_count = 0.00
        job_count = 0
        for job in job_list:
            if addr == str(job.area):
                job_count = job_count + 1
                if job.job_salary != "面议" and "~" in str(job.job_salary):
                    salary = str(job.job_salary).split("~")
                    average_salary = float(salary[0].replace("K","")) + float(salary[1].replace("K", "")) / 2
                    salary_count = salary_count + average_salary
        if salary_count != 0:
            area_top20[addr] = int(salary_count / job_count)

    area_top20 = sorted(area_top20.items(), key=lambda x: x[-1], reverse=True)
    area_top20 = area_top20[0:20]
    top20 = []
    for item in area_top20:
        top20.append({
        'name':item[0],
        'value':item[1]
    })
    email = session['email']
    return render_template(
        'time_t.html',
        email=email,
        top20=top20
    )

@app.route('/type_t',methods=['GET','POST'])
def type_t():
    email = session['email']
    engine = DbHandler().create_engine()
    with engine.connect() as con:
        rs = con.execute(text("SELECT count(1),area FROM jobs GROUP BY area limit 20"))
        result = []
        for item in rs:
            result.append({
                'name': item[1],
                'value': item[0]
            })

    return render_template('type_t.html',result=result,type_t=type_t,email=email)


@app.route("/address_t", methods=['GET', 'POST'])
def address_t():
    email = session['email']
    engine = DbHandler().create_engine()
    with engine.connect() as con:
        rs = con.execute(text("SELECT count(1),education FROM jobs GROUP BY education limit 20"))
        row = []
        column = []

        for item in rs:
            row.append(item[1])
            column.append(item[0])
    return render_template('address_t.html', row=row, column=column, email=email)

# ====================================================================

@app.route('/title_c')
def title_c():
    return render_template('job_name.html')

@app.route('/summary_c')
def summary_c():
    return render_template('summary_c.html')

@app.route('/welfare')
def welfare():
    return render_template('welfare.html')

@app.before_request
def before_requre():
    pat = re.compile(r'^/static')
    if re.search(pat,request.path):
        return
    if request.path == "/login" :
        return
    if request.path == '/registry':
        return
    uname = session.get('email')
    if uname:
        return None

    return redirect("/login")


if __name__ == '__main__':
    app.run()
