import sqlite3
import base_functions
import sys

def insert_into_db(data):
    with sqlite3.connect('db.sqlite3') as con:
        c = con.cursor()
        for d in data:
            if 'url' not in d:
                continue
            c.execute("SELECT * FROM news_news WHERE url='%s'" % d['url'].replace("'", '"'))
            if c.fetchall():
                # Don't update because it's already there
                pass
            else:
                c.execute("INSERT INTO news_news (title, content, url, deleted) VALUES ('%s', '%s', '%s', 0)" %
                          (d['title'].replace("'", '"'), d['content'].replace("'", '"'), d['url'].replace("'", '"')))

def get_all_urls():
    ans = []
    with sqlite3.connect('db.sqlite3') as con:
        c = con.cursor()
        c.execute("SELECT * FROM news_news")
        for t in c.fetchall():
            ans.append(t[3])
        # print(ans)
    return ans


def download_now(urls):
    len_urls = len(urls)
    print("Will download %d websites." %len_urls)
    base_functions.new_datas = [{}] * len_urls
    index = 0
    while index < len_urls:
        tarindex = index + 10 if index + 10 < len_urls else len_urls
        threads = []
        for i in range(index, tarindex):
            thread = base_functions.getWebThread(i, urls[i])
            threads.append(thread)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        index = tarindex
    print("Downloaded!")
    insert_into_db(base_functions.new_datas)


def run_download(download_new=True, num=30):
    already_urls = get_all_urls()
    urls = base_functions.get_news_url(download_new, num, already_urls)
    download_now(urls)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        run_download()
    elif len(sys.argv) > 2 and sys.argv[1] == '-f':
        with open(sys.argv[2]) as f:
            urls = f.readlines()
            already_urls = get_all_urls()
            urls = [t.strip() for t in urls if t.strip() not in already_urls]
            download_now(urls)
    elif len(sys.argv) > 2 and sys.argv[1] == '-url':
        urls = [sys.argv[2]]
        download_now(urls)
    elif sys.argv[1] == '-1':
        run_download(False)
    else:
        try:
            if int(sys.argv[1]) > 0:
                run_download(True, int(sys.argv[1]))
            else:
                raise AttributeError
        except:
            print("Usage:\n\tpython spider.py [num=30]\n\tpython spider.py -1\n\tpython spider.py -f filename\n\tpython spider.py -url url")


class spider_thread(base_functions.threading.Thread):
    def __init__(self):
        base_functions.threading.Thread.__init__(self)
    def run(self):
        run_download(True, 10)
