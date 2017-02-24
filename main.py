# coding=utf-8
# 需要配置 pymongo pymysql beautifulsoup4 lxml

# nohup  python **.py

import copy
import threading
from multiprocessing import Queue
from getQueue import getQueue
from mysqlManage import DB
from putQueue import putQueue


# 多线程 中怎么同步 现在已经到哪个数据了
permanent_coll = ["shandong", "shanxi", "henan", "beijing", "hebei",
                  "shanghai", "zhejiang", "aomen", "fujian",
                  "anhui", "qinghai", "chongqing",
                  "gansu", "guangxi", "guizhou",
                  "heilongjiang", "hongkong", "jiangxi",
                  "jilin", "liaoning", "neimenggu",
                  "ningxia", "other", "qinghai",
                  "shanxi2", "taiwan", "tianjin",
                  "guangdong", "hainan", "hubei",
                  "hunan", "jiangsu", "sichuan",
                  "xinjiang", "xizang", "yunnan",
                  "cn1", "cn2", "cn3", "cn4", "cn5"]

contacttool_info = {
    'qiyukf.com': {'brand_id': 1, 'brand_name': '七鱼智能客服'},
    '53kf.com': {'brand_id': 2, 'brand_name': '53kf'},
    'udesk.cn': {'brand_id': 3, 'brand_name': 'U-desk'},
    'easemob.com': {'brand_id': 4, 'brand_name': '环信'},
    'meiqia.com': {'brand_id': 5, 'brand_name': '美洽'},
    'sobot.com': {'brand_id': 6, 'brand_name': '智齿'},
    'xiaoneng.cn': {'brand_id': 7, 'brand_name': '小能'},
    'youkesdk.com': {'brand_id': 8, 'brand_name': '有客云'},
    'live800.com': {'brand_id': 9, 'brand_name': 'Live800'},
    'b.qq.com': {'brand_id': 10, 'brand_name': '营销QQ'},
    'bizapp.qq.com': {'brand_id': 10, 'brand_name': '营销QQ2'},
    'workec.com': {'brand_id': 11, 'brand_name': 'EC企信'},
    'looyu.com': {'brand_id': 12, 'brand_name': '乐语'},
    'tq.cn': {'brand_id': 13, 'brand_name': 'TQ洽谈通'},
    'zoosnet.net': {'brand_id': 14, 'brand_name': '网站商务通'},
    'talk99.cn': {'brand_id': 15, 'brand_name': 'Talk99'},
    'kf5.com': {'brand_id': 16, 'brand_name': '逸创云客服'}
}

# 首先需要 浅复制数据 否则 coll 中的数据会被覆盖
coll = copy.copy(permanent_coll)
queueLock = threading.Lock()
queueCount = 1000
workQueue = Queue(queueCount)
threads = []
threadID = 1
# 消费者数量 也就是爬取 www mx的线程的数量
consumerThreadingCount = 100

# # 多线程更新数据
producerThread = putQueue(threadID, "取数据者", workQueue, queueCount, queueLock, coll)
producerThread.start()
threads.append(producerThread)

getWwwFlag = True
getMxFlag = True
getContactFlag = True

mxsuffix = {}
if getMxFlag:
    # 从数据库中获取 mx 以及品牌的相关数据
    db = DB()
    db.connect()
    # sql = "select s.mxsuffix,s.brand_id,b.name from sm_mx_suffix as s left join sm_mx_brand as b on b.id=s.brand_id"
    sql = "select s.mxsuffix,s.brand_id,b.name from sm_mx_suffix as s left join sm_mx_brand as b on b.id=s.brand_id"
    stepCursor = db.query(sql)
    rows = stepCursor.fetchall()
    for row in rows:
        mxsuffix[row['mxsuffix']] = {'brand_id': row['brand_id'], 'brand_name': row['name']}
    stepCursor.close()
    db.close()

# # 创建处理队列的进程 消费者
for t in range(consumerThreadingCount):
    thread = getQueue(threadID, "***" + str(threadID) + "号爬虫", workQueue, queueLock, coll, mxsuffix, contacttool_info,
                      getMxFlag, getWwwFlag, getContactFlag)
    thread.start()
    threads.append(thread)
    threadID += 1