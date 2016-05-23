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
    save_url = 'http://vdisk.weibo.com/api/weipan/fileopsCopyCount'
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
        return 'ok'
    else:
        return save.text

def save_account(link):
    # link='http://vdisk.weibo.com/u/2536363235'
    save_url = 'http://vdisk.weibo.com/api/weipan/fileopsCopyCount'
    session.headers.update({'referer': link})
    index=session.get(link)
    pattern=re.compile(r'\.\.\.</span><a href="\?page=(.*?)">')
    lastpage=''.join(re.findall(pattern,index.text))
    print('共%s页'%lastpage)
    start=int(input('从第几页开始：'))
    end=int(input('到第几页结束：'))
    for page_no in range(start-1,end):
        pagelink='http://vdisk.weibo.com/u/2536363235?page=%s'%str(page_no+1)
        find_pattern=re.compile(r'<a target="_blank" href="http://vdisk.weibo.com/s/(.+?)" title="(.+?)">')
        page=session.get(pagelink)
        page.encoding='utf-8'
        for e in re.findall(find_pattern,page.text):
            data={
                'from_copy_ref':e[0],
                'to_path':'/backup/%s'%e[1],
                'root':'basic',
            }
            result=session.post(save_url,data).text
            if result.find('modified')!=-1:
                print(e[1],'保存成功')
            else:
                print(e[1],'失败',result)



if __name__ == '__main__':
    account=input('账号')
    password=input('密码')
    session = login(account, password)
    with open('share.csv', newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='	', quotechar='|')
        for row in spamreader:
            print(row)
            if ''.join(row).find(r'/u/')!=-1:
                save_account(''.join(row))
            else:
                foldername = row[0].strip()
                try:
                    folder_pass = row[2].strip()
                except:
                    folder_pass=''
                folder_link = row[1].strip()
                ret=save_with_pass(foldername,folder_link,folder_pass)
                if ret.find('C50701')!=-1:
                    print(foldername)
                    break
                print(foldername,ret)
