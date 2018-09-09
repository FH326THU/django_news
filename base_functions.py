# Python3 version
# Change to automatically get website by changing get_urls_from_web into True
# by Feng Hao, 18.09.05

import threading
from bs4 import BeautifulSoup as bs
import requests
import json
import jieba
import re


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

all_words = []

re_date_compiled = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})|(\d{4})-(\d{1,2})-(\d{1,2})|(\d{4})年(\d{1,2})月(\d{1,2})日')
full_re_date_compiled = re.compile(r'^(\d{4})/(\d{1,2})/(\d{1,2})$|^(\d{4})-(\d{1,2})-(\d{1,2})$|^(\d{4})年(\d{1,2})月(\d{1,2})日$')


def check_date(date_str, full=False):
    if full:
        ans_dates = full_re_date_compiled.findall(date_str)
    else:
        ans_dates = re_date_compiled.findall(date_str)
    ans = []
    for i in ans_dates:
        for t in range(0, 9, 3):
            if i[t]:
                ans.append([int(i[t]), int(i[t + 1]), int(i[t + 2])])
                break
    return ans


def get_news_url(get_urls_from_web=False, len_news=10, blacklist=[]):
    # set default of blacklist into [] on purpose, because the used ones should put there
    base_url = 'http://news.qq.com/'
    urls = []
    if get_urls_from_web:
        try:
            print("Visiting web %s" % base_url)
            news = read_file(base_url)
            if not news:
                raise ConnectionRefusedError
            else:
                news = news.find("div", class_='news').find_all("div", class_='Q-tpWrap')
                # prevent the case that the url refers to a list or a video
                news = [t for t in news if str(t).find("template") < 0 and str(t).find("html") >= 0 and
                        t.find("div", class_='text').find("em").find("a").get("href") not in blacklist]
                news = news[:len_news]
                for k, news_info in enumerate(news):
                    url = news_info.find("div", class_='text').find("em").find("a").get("href")
                    # print("Got url NO.%d: %s" % (k + 1, url))
                    urls.append(url)
        except:
            print("Error! Can't get data from %s!" % base_url)
    if len(urls) < 1:
        urls = [
            'https://new.qq.com/omn/20180903/20180903A1Z1BM.html',
            'https://new.qq.com/omn/20180905/20180905A06ENK.html',
            'https://new.qq.com/cmsn/20180904/20180904002887.html',
            'https://new.qq.com/omn/20180905/20180905A0H3AS.html',
            'https://new.qq.com/cmsn/20180904/20180904000984.html',
            'https://new.qq.com/cmsn/20180905/20180905039088.html',
            'https://new.qq.com/omn/20180904/20180904G1MKI5.html',
            'https://new.qq.com/cmsn/20180905/20180905008025.html',
            'https://new.qq.com/omn/20180905/20180905A06RTC.html',
            'https://new.qq.com/omn/20180904/20180904A1XJM1.html',
        ]
    urls = [i for i in urls if i not in blacklist]
    return urls


def read_file(url, adder=0):
    ans = requests.get(url, headers=headers, timeout=5)
    if ans.status_code == 200:
        ans.encoding = 'gbk'
        # Save html files
        # raw = open("raw%d.html" %adder, 'w')
        # raw.write(ans.text)
        # raw.close()
        return bs(ans.text, 'html.parser')
    return None


def cancel_spaces(s):
    ans = ''
    start = True
    have_n = False
    have_space = False
    for i in s:
        if i in ' \t\r\n\u3000\xa0':
            have_space = True
            have_n = have_n or i == '\n'
        else:
            if have_space and not start:
                if have_n:
                    ans += '\n'
                else:
                    ans += ' '
            have_space = False
            have_n = False
            start = False
            ans += i
    return ans


def deal_with_souped(s, url):
    text_list = list(jieba.cut(raw_content(s)))
    title = s.find("h1").text
    o = {
        'title': title,
        'text': text_list,
        'url': url,
        'dates': check_date(raw_content(s))
    }
    return o


def raw_content(s):
    ans = str(s)
    ans.replace("<div ", "\n<div ")
    ans.replace("<div>", "\n<div>")
    ans.replace("</div>", "</div>\n")
    ans.replace("<p ", "\n<p ")
    ans.replace("<p>", "\n<p>")
    ans.replace("</p>", "</p>\n")
    ans.replace("<br>", "<br>\n")
    ans.replace("<br/>", "<br/>\n")
    ans.replace("<br />", "<br />\n")
    ans = bs(ans, 'html.parser').text
    return cancel_spaces(ans)


new_datas = []
class getWebThread(threading.Thread):
    def __init__(self, threadID, url):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url = url

    def run(self):
        print("Thread %d started!" % self.threadID)
        try:
            self.data = read_file(self.url, self.threadID)
            if self.data:
                print("Thread %d got website from %s" % (self.threadID, self.url))
                ans = self.data.find("body")
                scripts = ans.find_all(["script", "style"])
                for s in scripts:
                    s.extract()
                new_datas[self.threadID] = {'title': ans.find("h1").text, 'content': raw_content(ans), 'url': self.url}
                # print(new_datas)

            else:
                raise ConnectionRefusedError
        except Exception as t:
            print("ERROR! Thread %d can't get website from %s!\n  ErrorInfo: %s" % (self.threadID, self.url, t))
            new_datas[self.threadID] = {}


def load_files(len):
    object_list = []
    for i in range(len):
        object_list.append({})
        try:
            with open("fh%d.json" % (i + 1)) as f:
                object_list[i] = json.loads(f.read())
        except Exception as e:
            print("Error! Can't read file fh%d.json!\n  ErrorInfo: %s" % (i + 1, e))
            object_list[i] = {
                'title': '',
                'text': [],
                'url': '',
                'dates': []
            }
        else:
            print("Loaded file fh%d.json" % (i + 1))
    return object_list


def get_word_vector(text_list):
    ans = [0] * len(all_words)
    for t in text_list:
        if t in ['', ' ', '\n']:
            continue
        if t not in all_words:
            all_words.append(t)
            ans.append(0)
        ans[all_words.index(t)] += 1
    return ans


def get_words_vector(object_list):
    for k, o in enumerate(object_list):
        object_list[k]['vector'] = get_word_vector(o['text'])
    return object_list


def get_similar(object_list, text):
    # use Cosine similarity to get
    text_vector = get_word_vector(list(jieba.cut(text)))
    text_model_square = 0
    for i in text_vector:
        text_model_square += i * i
    if text_model_square == 0:
        return None
    sortable = []
    for k_object, v in enumerate(object_list):
        sortable.append({
            'title': v['title'],
            'score': -1,
            'url': v['url'],
            'dates': v['dates']
        })
        v_model_square = 0
        cross = 0
        for k, i in enumerate(v['vector']):
            v_model_square += i * i
            cross += i * text_vector[k]
        if v_model_square == 0:
            continue
        # use the square of cos
        sortable[k_object]['score'] = 1. * cross * cross / v_model_square / text_model_square
    sortable = [i for i in sortable if i['score'] > 0]
    sortable.sort(key=(lambda x: x['score']), reverse=True)
    return sortable


if __name__ == '__main__':
    print("Please run 'spider.py'")
