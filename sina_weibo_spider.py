#coding:utf-8
import requests
import random
import re
import traceback
import os 
from bs4 import BeautifulSoup
from cqhttp import CQHttp
from time import sleep

username = "your_weibo_username"
password = "your_weibo_password"
target_qq = "target_qq"
ID = ""
qqbot_server_host = "qqbot_server_host"
qqbot_server_port = 5700 # "qqbot_server_port"

bot = CQHttp(api_root='http://{server}:{port}/'.format(server = qqbot_server_host , port = qqbot_server_port))
user_agents = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 '
    'Mobile/13B143 Safari/601.1]',
    'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/48.0.2564.23 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/48.0.2564.23 Mobile Safari/537.36']

headers = {
    'User_Agent': random.choice(user_agents),
    'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F',
    'Origin': 'https://passport.weibo.cn',
    'Host': 'passport.weibo.cn'
}
post_data = {
    'username': '',
    'password': '',
    'savestate': '1',
    'ec': '0',
    'pagerefer': 'https://passport.weibo.cn/signin/welcome?entry=mweibo&r=http%3A%2F%2Fm.weibo.cn%2F&wm=3349&vt=4',
    'entry': 'mweibo'
}
# 这个入口仍然有效
login_url = 'https://passport.weibo.cn/sso/login'

def login(username , password):
    session = requests.session()
    post_data['username'] = username
    post_data['password'] = password
    r = session.post(login_url, data=post_data, headers=headers)
    print(r.json())
    if r.status_code != 200 or r.json()['msg'] != "":
        raise Exception('模拟登陆失败')
    else:
        print("模拟登陆成功,当前登陆账号为：" + username)
    return session

def get_now_flag_id():
    if not os.path.exists("flag.txt"):
        f = open("flag.txt" , "w+" , encoding = "utf-8")
        f.close()
        return []
    else:
        flag_text = get_text("flag.txt")
        return flag_text.split("\n")


def get_img_list(se , url):
    resp = se.get(url)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.content, "lxml")
    img_list = [i.get("src").split("/")[-1] for i in soup.find_all("img")]
    return img_list

def write_img(filename , content):
    f = open(filename , "wb")
    f.write(content)
    f.close()

def write_text(filename, text):
    f = open(filename , "w+" , encoding = "utf-8")
    f.write(text)
    f.close()

def send_message(qq,message):
    context = {"font": 117104704 , "message" : 1 , "user_id": qq , "message_type" : "private" , "post_type" : "message" }
    bot.send(context , message = message)
    sleep(1)

def get_text(filename):
    f = open(filename , "r" , encoding = "utf-8")
    text = f.read()
    f.close()
    return text

def write_new_flag(new_ids , history_ids):
    flag_txt = "\n".join(new_ids)
    if flag_txt != "":
        flag_txt += "\n"
    flag_txt += "\n".join(history_ids)
    write_text("flag.txt" , flag_txt) # write new flag

if __name__ == "__main__":
    image_regex = re.compile("(.*?)https://weibo.cn/mblog/picAll(.*?)")
    exit_flag = True
    while exit_flag == True:
        try:
            s = login(username, password)
            url_tweets = "https://weibo.cn/%s/profile?filter=1&page={}" % ID
            weibo_url = "https://weibo.cn/%s/{weibo_id}" % ID
            resp = s.get(url_tweets.format(1))
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.content, "lxml")
            max_page = soup.find("div", attrs = {"class": "pa"})
            if max_page == None:
                print("目标用户没有可以被爬取的微博")
                raise Exception("Invalid WeiboId")
            max_page_num = int(max_page.text.split("/")[-1][:-1])
            result = []
            flag_continue = True
            # for content store
            if not os.path.exists("content"):
                os.mkdir("content")
            # get lastest flag_id and flag_list for check 
            flag_history_list = get_now_flag_id()
            new_ids = []
            history_ids = []
            for i in range(1, max_page_num + 1):
                resp = s.get(url_tweets.format(i))
                resp.encoding = resp.apparent_encoding
                soup = BeautifulSoup(resp.content, "lxml")
                divs = soup.find_all("div", attrs = {"class": "c"})
                for div in divs[1:-2]:
                    m_id = div.get("id")
                    if m_id not in flag_history_list: # get_info
                        new_ids.append(m_id)
                        time = div.find("span" , attrs = {"class" : "ct"}).text
                        divs = div.find_all("div")
                        img = None
                        if len(divs) != 2:
                            div = divs[0]
                            img_list = []
                        else:
                            div , img_div = divs
                            img_list = [img_div.find("img").get("src").split("/")[-1]] 
                        content = div.find("span" , attrs = {"class" : "ctt"})
                        a_list = div.find_all("a")
                        if (len(a_list) != 4):
                            for a in a_list:
                                href = a.get("href")
                                if image_regex.match(href) is not None:
                                    img_list.extend(get_img_list(s , href))
                        print("title : " + content.text)
                        if img_list != []:
                            img_list = [ "http://ww4.sinaimg.cn/thumb180/{}".format(img) for img in set(img_list)]
                        
                        result_format = "{content}\ntime : {time}\nimg_list : {img_list_str}\nweibo_detail_url : {weibo_url}"
                        result = result_format.format(content = content.text , time = time , img_list_str = "\n".join(img_list) , weibo_url = weibo_url.format(weibo_id = m_id[2:]))
                        write_text("content/{}.txt".format(m_id) , result)
                    else:
                        history_ids.append(m_id)
                        flag_history_list.remove(m_id)
            write_new_flag(new_ids , history_ids)   
            if new_ids != []:
                send_message(target_qq , "new weibo")
                for new_id in new_ids[::-1]:
                    send_message(target_qq ,  get_text("content/{}.txt".format(new_id)))
            if flag_history_list != []:
                send_message(target_qq , "recalled weibo")
                for history_id in flag_history_list:
                    send_message(target_qq ,  get_text("content/{}.txt".format(history_id)))
            else:
                print("nothing new")
        except Exception as errinfo:
            send_message(target_qq , "get exception {} , please fix now".format(str(errinfo)))
            if str(errinfo) == "Invalid WeiboId":
                exit_flag = False
        finally:
            s.close()
        if exit_flag == True:
        	sleep(1800)
