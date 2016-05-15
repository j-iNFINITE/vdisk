import csv
import requests
import json
import base64
import re
import logging
import urllib.parse
logging.basicConfig(level=logging.DEBUG)
def login(username, password):
    username = base64.b64encode(username.encode('utf-8')).decode('utf-8')
    postData = {
        "entry": "sso",
        "gateway": "1",
        "from": "null",
        "savestate": "30",
        "useticket": "0",
        "pagerefer": "",
        "vsnf": "1",
        "su": username,
        "service": "sso",
        "sp": password,
        "sr": "1440*900",
        "encoding": "UTF-8",
        "cdult": "3",
        "domain": "sina.com.cn",
        "prelt": "0",
        "returntype": "TEXT",
    }
    loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    session = requests.Session()
    res = session.post(loginURL, data = postData)
    jsonStr = res.content.decode('gbk')
    info = json.loads(jsonStr)
    if info["retcode"] == "0":
        print("登录成功")
        # 把cookies添加到headers中，必须写这一步，否则后面调用API失败
        cookies = session.cookies.get_dict()
        cookies = [key + "=" + value for key, value in cookies.items()]
        cookies = "; ".join(cookies)
        session.headers["cookie"] = cookies
    else:
        print("登录失败，原因： %s" % info["reason"])
    return session


def get_one(link,pd,ref):
    acc = link
    acc_date = {
        'file': ref,
        'access_code': pd
    }
    print(link.split('/')[-1].split('?')[0])
    acce=session.post(acc,acc_date)
    acce.encoding='utf-8'
    pattern = re.compile(r'"保存到微盘".+?"path":"(.+?)"')
    links=[eval("u"+"'%s'"%e)[1:] for e in re.findall(pattern, acce.text)]
    return links

def save_one(link,ref,code):
    links=get_one(link,code,ref)
    for e in links:
        e=e.replace('\\','')
        date={
            'root': 'basic',
            'parent_path':'/backup',
            'access_code':code,
            'from_copy_ref':ref,
            'paths[]':e,
        }
        save=session.post('http://vdisk.weibo.com/share/linkfolderSave',date)
        print(save.text)
        if save.text.find('C40603')!=-1:
            nlink=link+'?path='+e
            save_one(nlink,ref,code)
        else:
             print(e)
    return

def save_with_pass(name,link,pd):
    save_url = 'http://vdisk.weibo.com/share/linkfolderSave'
    ref=link.split('/')[-1]
    session.headers.update({'referer': link})
    pdate = {
        'root': 'basic',
        'to_path': '/backup/%s'%name,
        'access_code': pd,
        'from_copy_ref': ref,}
    save = session.post(save_url, data=pdate)
    st = save.text
    if st.find('C40603')!=-1:
        save_one(link,ref,pd)
    else:
        return name

if __name__ == '__main__':
    account=input('账号')
    password=input('密码')
    session = login(account, password)
    with open('share.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='	', quotechar='|')
        for row in spamreader:
            foldername = row[0].strip()
            folder_pass = row[2].strip()
            folder_link = row[1].strip()
            print(foldername,save_with_pass(foldername,folder_link,folder_pass))
