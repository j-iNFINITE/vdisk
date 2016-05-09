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

def save_one_by_one(link,pd):
    if link.find('path')==-1:
        link=link+'?path='
    session.headers.update({'referer': link})
    save_url = 'http://vdisk.weibo.com/share/linkfolderSave'
    acc = link
    acc_date = {
        'file': link.split('/')[-1].split('?')[0],
        'access_code': pd
    }
    acce=session.post(acc,acc_date)
    acce.encoding='utf-8'
    pattern = re.compile(r'"保存到微盘".+?"path":"(.+?)"')
    for e in re.findall(pattern, acce.text):
        print(eval("u"+"'%s'"%e)[1:])
        one_date={
            'root': 'basic',
            'parent_path': '/backup',
            'access_code': pd,
            'from_copy_ref': link.split('/')[-1].split('?')[0],
            'paths[]':eval("u"+"'%s'"%e)[1:]
        }
        save = session.post(save_url, data=one_date)
        if save.text.find('C40603')!=-1:
            link=link+urllib.parse.quote(eval("u"+"'%s'"%e)[1:])
            print(link)
            save_one_by_one(link, pd)
        print(save.text)

def save_with_pass(name,link,pd):
    save_url = 'http://vdisk.weibo.com/share/linkfolderSave'
    session.headers.update({'referer': link})
    pdate = {
        'root': 'basic',
        'to_path': '/backup/%s'%name,
        'access_code': pd,
        'from_copy_ref': link.split('/')[-1],}
    save = session.post(save_url, data=pdate)
    st = save.text
    if st.find('error')==-1:
        return 'ok'
    else:
        return 'fall'

if __name__ == '__main__':
    session = login('', '')
    # with open('share.csv', newline='', encoding='utf-8') as csvfile:
    #     spamreader = csv.reader(csvfile, delimiter='	', quotechar='|')
    #     for row in spamreader:
    #         foldername = row[0].strip()
    #         folder_pass = row[2].strip()
    #         folder_link = row[1].strip()
    #         print(foldername,save_with_pass(foldername,folder_link,folder_pass))
    save_one_by_one( 'http://vdisk.weibo.com/lc/2oLCHhNUZpUFqxU2W8', 'Y027')
