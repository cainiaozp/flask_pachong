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

@app.route("/home")  # 定义一个路由，当用户访问网站的"/home"路径时，会触发这个函数
def home():
    email = session['email']  # 获取用户的电子邮件地址
    # 查询数据库中招聘信息表中所有工作的数量
    allCount = dbsession.query(func.count(Job.id)).scalar()
    # 查询数据库中招聘信息表中本科学历工作的数量
    benkeCount = dbsession.query(Job).filter(Job.education.like("%本科%")).count()
    # 查询数据库中招聘信息表中大专学历工作的数量
    dazhuanCount = dbsession.query(Job).filter(Job.education.like("%大专%")).count()
    # 查询数据库中招聘信息表中中专学历工作的数量
    zhongzhuanCount = dbsession.query(Job).filter(Job.education.like("%中专%")).count()
    # 查询数据库中招聘信息表中博士学历工作的数量
    boshiCount = dbsession.query(Job).filter(Job.education.like("%博士%")).count()
    # 查询数据库中招聘信息表中硕士学历工作的数量
    shuoshiCount = dbsession.query(Job).filter(Job.education.like("%硕士%")).count()

    # 渲染模板并返回结果，将查询结果传递到模板中
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

@app.route("/index_data")  # 定义一个路由，当用户访问网站的"/index_data"路径时，会触发这个函数
def index_data():
    res = {}  # 定义一个空字典
    # 查询数据库中招聘信息表中所有工作的数量
    allCount = querys('select count(1) from jobs', [], 'select')
    # 查询数据库中招聘信息表中本科学历工作的数量
    benkeCount = querys('select count(1) from jobs where education like "%%本科%%"', [], 'select')
    # 查询数据库中招聘信息表中大专学历工作的数量
    dazhuanCount = querys('select count(1) from jobs where education like "%%大专%%"', [], 'select')
    # 查询数据库中招聘信息表中中专学历工作的数量
    zhongzhuanCount = querys('select count(1) from jobs where education like "%%中专%%"', [], 'select')
    # 查询数据库中招聘信息表中博士学历工作的数量
    boshiCount = querys('select count(1) from jobs where education like "%%博士%%"', [], 'select')
    # 查询数据库中招聘信息表中硕士学历工作的数量
    shuoshiCount = querys('select count(1) from jobs where education like "%%硕士%%"', [], 'select')

    # 将查询到的数据添加到字典中
    res["allCount"] = tuple(allCount)[0:1][0][0]
    res["benkeCount"] = tuple(benkeCount)[0:1][0][0]
    res["dazhuanCount"] = tuple(dazhuanCount)[0:1][0][0]
    res["zhongzhuanCount"] = tuple(zhongzhuanCount)[0:1][0][0]
    res["boshiCount"] = tuple(boshiCount)[0:1][0][0]
    res["shuoshiCount"] = tuple(shuoshiCount)[0:1][0][0]

    return jsonify(res)

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST': # 如果请求方法为POST
        request.form = dict(request.form) # 获取表单数据
        # 定义一个过滤函数，返回表单中的email和password在用户信息中是否匹配
        def filter_fns(item):
            return request.form['email'] in item and request.form['password'] in item

        users = querys('select * from user', [], 'select') # 查询用户信息
        login_success = list(filter(filter_fns, users)) # 利用过滤函数筛选匹配的用户
        if not len(login_success): # 如果匹配用户列表为空，说明账号或密码错误
            return '账号或密码错误'

        session['email'] = request.form['email'] # 将email存入session中
        return redirect('/home', 301) # 跳转到home页面

    else: # 如果请求方法为GET
        return render_template('./login.html') # 返回渲染后的login.html页面
@app.route("/registry",methods=['GET','POST'])
def registry():
    if request.method == 'POST':  # 判断请求是否是 POST
        request.form = dict(request.form)  # 将表单数据转换为字典形式
        if request.form['password'] != request.form['passwordCheked']:  # 判断两次输入的密码是否一致
            return '两次密码不符'
        else:
            def filter_fn(item):  # 定义一个过滤函数
                return request.form['email'] in item  # 判断输入的邮箱是否在 item 中

            users = querys('select * from user', [], 'select')  # 从数据库中查询用户表
            filter_list = list(filter(filter_fn, users))  # 过滤出符合条件的用户列表
            if len(filter_list):  # 如果用户列表不为空，则说明该邮箱已被注册
                return '该用户名已被注册'
            else:  # 否则将邮箱和密码插入到用户表中
                querys('insert into user(email,password) values(%s,%s)',
                       [request.form['email'], request.form['password']])

            session['email'] = request.form['email']  # 将邮箱存入 session 中
            return redirect('/home', 301)  # 重定向到首页

    else:  # 如果请求不是 POST，则返回注册页面
        return render_template('./register.html')
"""
这段代码是一个Python Flask Web应用程序的一部分，其中包含了一些路由函数。

第一个路由函数是`home()`，当浏览器访问`/home`时，它会从会话中获取当前用户的电子邮件地址，然后查询数据库以获取职位数量的统计信息。它最终渲染名为`index.html`的模板，并将数据作为模板的参数传递给它。其中`allCount`是职位总数，`benkeCount`是本科职位数量，`dazhuanCount`是大专职位数量，`zhongzhuanCount`是中专职位数量，`boshiCount`是博士职位数量，`shuoshiCount`是硕士职位数量。

第二个路由函数是`index_data()`，当浏览器访问`/index_data`时，它将从数据库中获取与`home()`相同的职位数量统计信息。但是，它将返回一个JSON格式的响应，而不是渲染模板。

第三个路由函数是`login()`，当浏览器访问`/login`时，它将检查用户是否已经提交了一个POST请求，如果是，它将验证用户名和密码是否匹配数据库中的用户信息。如果用户名和密码验证成功，它将在会话中设置电子邮件地址，并将用户重定向到`home()`页面。如果用户名或密码无效，则返回一个错误消息。

第四个路由函数是`registry()`，当浏览器访问`/registry`时，它将检查用户是否已经提交了一个POST请求，如果是，它将验证输入的电子邮件地址是否已经存在于数据库中。如果是，它将返回一个错误消息。如果电子邮件地址尚未被注册，它将在数据库中创建一个新用户记录，并在会话中设置电子邮件地址。最后，它将用户重定向到`home()`页面。

这些路由函数使用Flask框架的装饰器来将它们绑定到特定的URL路径。它们使用查询函数`querys()`来查询数据库，但是这个函数的具体实现不在提供的代码段中。
"""
@app.route("/search/<int:searchId>", methods=['GET', 'POST'])
def search(searchId):
    # 获取当前登录用户的email
    email = session['email']
    data = []
    if request.method == 'GET':
        # 如果是GET请求，且searchId为0，返回search.html页面，idData为空列表，email为当前登录用户的email
        if searchId == 0:
            return render_template(
                'search.html',
                idData=data,
                email=email
            )
    else:
        # 如果是POST请求，获取前端表单提交的searchIpt参数，即搜索关键字
        searchWord = dict(request.form)['searchIpt']
        # 定义过滤函数filter_fn，用于过滤查询结果
        def filter_fn(item):
            if item[3].find(searchWord) == -1:
                return False
            else:
                return True
        # 使用ORM查询，筛选job_name中包含关键字的记录
        jobList = dbsession.query(Job).filter(Job.job_name.like("%{}%".format(searchWord))).all()
        print(jobList)
        # 返回search.html页面，data为查询到的jobList列表，email为当前登录用户的email
        return render_template(
            'search.html',
            data=jobList,
            email=email
        )
# 定义函数 startJiaXingSpider，该函数将 "start" 放入队列中，实例化 JxSpider 并启动
def startJiaXingSpider():
    queue.put("start")
    s = JxSpider()
    s.start()

# 定义函数 stopJiaXingSpider，该函数将 "stop" 放入队列中
def stopJiaXingSpider():
    queue.put("stop")

# 定义路由 /jxStart，当收到 GET 或 POST 请求时执行 jiaXingStartSpider 函数
# 该函数将清空队列并启动爬虫，返回 JSON 数据，表示启动成功或失败
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

# 定义路由 /jxStop，当收到 GET 或 POST 请求时执行 jiaXingStopSpider 函数
# 该函数将停止爬虫并返回 JSON 数据，表示停止成功或失败以及队列中剩余的页数
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

# 定义路由 /time_t，当收到 GET 或 POST 请求时执行 top20 函数
# 该函数从数据库中获取职位数据，并按照地区统计薪资情况，返回 JSON 数据，
# 表示各个地区的平均薪资情况，以及将薪资最高的 20 个地区显示在页面上
@app.route("/time_t",methods=['GET','POST'])
def top20():
    area_set = set()  # 定义一个集合用于存储地区
    job_list =  dbsession.query(Job).all()  # 从数据库中获取职位数据
    for job in job_list:
        area_set.add(job.area)  # 将职位数据中的地区添加到集合中
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
                    salary_count = salary_count + average_salary  # 统计该地区的职位数量和薪资情况
        if salary_count != 0:
            area_top20[addr] = int(salary_count / job_count)  # 将该地区的平均薪资添加到字典中

    area_top20 = sorted(area_top20.items(), key=lambda x: x[-1], reverse=True)#排序得出前20
    area_top20 = area_top20[0:20]
    top20 = []
    for item in area_top20:#遍历显示前20个
        top20.append({
            'name': item[0],
            'value': item[1]
        })
    email = session['email']
    return render_template(
        'time_t.html',
        email=email,
        top20=top20
    )
@app.route('/type_t',methods=['GET','POST'])#定义了一个路由 '/type_t', 采用了 GET 和 POST 请求方法
def type_t():
    email = session['email']#获取当前用户的 email
    engine = DbHandler().create_engine()#创建数据库引擎
    with engine.connect() as con:
        rs = con.execute(text("SELECT count(1),area FROM jobs GROUP BY area limit 20"))#使用 execute() 方法执行 SQL 查询
        result = []
        for item in rs:
            result.append({
                'name': item[1],
                'value': item[0]
            })#获取结果并将其转换为字典形式的数据列表

    return render_template('type_t.html',result=result,type_t=type_t,email=email)#返回渲染好的 type_t.html 模板，并将查询结果、type_t 和 email 一同传递给模板


@app.route("/address_t", methods=['GET', 'POST'])#定义了一个路由 '/address_t', 采用了 GET 和 POST 请求方法
def address_t():
    email = session['email']
    engine = DbHandler().create_engine()
    with engine.connect() as con:
        rs = con.execute(text("SELECT count(1),education FROM jobs GROUP BY education limit 20"))
        row = []
        column = []

        for item in rs:
            row.append(item[1])
            column.append(item[0])#循环遍历结果集，将每条记录的 education 字段值添加到 row 列表，将每条记录的 count 字段值添加到 column 列表
    return render_template('address_t.html', row=row, column=column, email=email)#返回渲染好的 address_t.html 模板，并将查询结果、row、column 和 email 一同传递给模板
@app.route('/title_c')
def title_c():
    # 显示职位名称的页面
    return render_template('job_name.html')

@app.route('/summary_c')
def summary_c():
    # 显示职位摘要信息的页面
    return render_template('summary_c.html')

@app.route('/welfare')
def welfare():
    # 显示福利待遇信息的页面
    return render_template('welfare.html')

@app.before_request
def before_requre():
    # 拦截请求，在进入视图函数之前做些处理
    # 正则表达式用于匹配静态文件的请求路径
    pat = re.compile(r'^/static')
    # 如果请求路径匹配到静态文件的路径，则直接返回，不做拦截处理
    if re.search(pat,request.path):
        return
    # 如果请求路径为登录，则直接返回，不做拦截处理
    if request.path == "/login" :
        return
    # 如果请求路径为注册，则直接返回，不做拦截处理
    if request.path == '/registry':
        return
    # 获取用户的会话信息，如果会话信息存在，则返回None，继续访问视图函数，否则跳转到登录页面
    uname = session.get('email')
    if uname:
        return None

    return redirect("/login")
if __name__ == '__main__':
    app.run()
