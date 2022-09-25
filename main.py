import datetime as dt
import json
import os
import random
import re
import sys
import time
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from fstate_generator import *
from login import login

RETRY = 5
RETRY_TIMEOUT = 120


# 获取东八区时间
def get_time():
    # 获取0时区时间，变换为东八区时间
    # 原因：运行程序的服务器所处时区不确定
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)

    # 或者：
    # t = dt.datetime.utcnow()
    # tz_utc_8 = dt.timezone(dt.timedelta(hours=8))
    # t = t.astimezone(tz_utc_8)

    # 如果服务器位于东八区，也可用：
    # t = dt.datetime.now()

    return t


def report_day(sess, t):
    url = f'https://selfreport.shu.edu.cn/XiaoYJC202207/XueSLXSQ.aspx'

    for _ in range(RETRY):
        try:
            r = sess.get(url, allow_redirects=False)
        except Exception as e:
            print(e)
            time.sleep(RETRY_TIMEOUT)
            continue
        break
    else:
        print('获取每日一报起始页超时')
        return False

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
        if '上海大学统一身份认证' in r.text:
            print('登录信息过期')
        else:
            print(r.text)
        return False
    else:
        view_state = view_state['value']

    for _ in range(RETRY):
        try:
            r = sess.post(url, data={
                "__EVENTTARGET": "p1$ctl01$btnSubmit",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": view_state,
                "__VIEWSTATEGENERATOR": "7AD7E509",
                "persinfo$XiZhi": "persinfo_XiZhi",
                "persinfo$SuoZXQ": "宝山",
                "persinfo$YuanYin": "其他原因",
                "persinfo$TeSYY_QiTa": "实习",
                "persinfo$ddlSheng": "上海",
                "persinfo$ddlShi": "上海市",
                "persinfo$ddlXian": "杨浦区",
                "persinfo$XiangXDZ": "安联大厦",
                "persinfo$DangTHX": "是",
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)
        except Exception as e:
            print(e)
            time.sleep(RETRY_TIMEOUT)
            continue

        if any(i in r.text for i in ['成功']):
            return True
        elif '数据库有点忙' in r.text:
            print('数据库有点忙，重试')
            time.sleep(RETRY_TIMEOUT)
            continue
        else:
            print(r.text)
            return False

    else:
        print('离校申请超时')
        return False

if __name__ == "__main__":
    with open(Path(__file__).resolve().parent.joinpath('config.yaml'), encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if 'USERS' in os.environ:
        for user_password in os.environ['USERS'].split(';'):
            user, password = user_password.split(',')
            config[user] = {
                'pwd': password
            }

        user_abbr = user[-4:]
        sess = login(user, config[user]['pwd'])

        if sess:
            print('登录成功')

            fake_ip = '59.79.' + '.'.join(str(random.randint(0, 255)) for _ in range(2))
            print('生成了随机IP: %s' % fake_ip)
            headers = {
                'X-Forwarded-For': fake_ip,
            }
            sess.headers.update(headers)

            now = get_time()
            
            if report_day(sess, now):
                print(f'{now} 离校申请提交成功')
            else:
                print(f'{now} 离校申请提交失败')
        else:
            print('登录失败')
            failed_users.append(user_abbr)

        if i < len(config) - 1:
            time.sleep(RETRY_TIMEOUT)

