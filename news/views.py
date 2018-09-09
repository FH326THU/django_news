from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from news.models import *
import random
import string
import spider

spider_thread = None

def get_show_news():
    news = News.objects.filter(deleted=False)
    news = list(news)
    news.sort(key=lambda x: x.id)
    return news

def get_unshow_news():
    news = News.objects.filter(deleted=True)
    news = list(news)
    news.sort(key=lambda x: x.id)
    return news

def check_loggedini(request):
    sess = request.session.get('sess', None)
    if sess and User.objects.filter(sess=sess):
        return True
    else:
        return False

def render_params(request, **kwargs):
    ans = {'loggedin': check_loggedini(request)}
    for t in kwargs:
        ans[t] = kwargs[t]
    return ans

def index(request):
    # return render(request, 'index.html', render_params(request))
    return HttpResponseRedirect('/news/1')

def login(request):
    if request.method == 'POST':
        try:
            user = User.objects.filter(username=request.POST['username'], passwordmd5=request.POST['passwordmd5'])
            # user = User.objects.filter(username=request.POST['username'])
            if len(user) > 0:
                sess = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))
                request.session['sess'] = sess
                user.update(sess=sess)
                return JsonResponse({'state': 'ok'})
        except:
            pass
        return JsonResponse({'state': 'error'})
    elif request.method == 'GET':
        return render(request, 'login.html', render_params(request))

def news(request, id=-1):
    if id <= 0 or not isinstance(id, int):
        return HttpResponseRedirect('/news/1')
    news = get_show_news()
    pagesize = 20
    pages = (len(news) + pagesize - 1) // pagesize
    if id > pages and pages > 0:
        return HttpResponseRedirect('/news/' + str(pages))
    news = news[(id - 1) * pagesize:id * pagesize]
    return render(request, 'news.html', render_params(request, news=news, haspre=id>1, hasnext=id<pages,
                                                        nowid=id, preid=id-1, nextid=id+1, total=pages))


def notfound(request):
    return render(request, '404.html', render_params(request))

def news_content(request, id):
    if check_loggedini(request):
        news = News.objects.filter(id=id)
    else:
        news = News.objects.filter(deleted=False).filter(id=id)
    if len(news) > 0:
        data = news[0]
        data.content = data.content.split('\n')[1:]
        return render(request, 'news_content.html', render_params(request, data=data))
    else:
        return render(request, '404.html', render_params(request))


def del_news(request, id):
    try:
        if request.method == 'POST':
            sess = request.session.get('sess', None)
            if sess and User.objects.filter(sess=sess):
                news = News.objects.filter(id=int(id))
                if len(news) > 0:
                    # news.delete()
                    news.update(deleted=True)
                    return JsonResponse({'state': 'ok'})
    except:
        pass
    return JsonResponse({'state': 'error'})


def recover_news(request, id):
    try:
        if request.method == 'POST':
            sess = request.session.get('sess', None)
            if sess and User.objects.filter(sess=sess):
                news = News.objects.filter(id=int(id))
                if len(news) > 0:
                    # news.delete()
                    news.update(deleted=False)
                    return JsonResponse({'state': 'ok'})
    except:
        pass
    return JsonResponse({'state': 'error'})


def admin(request):
    if check_loggedini(request):
        return render(request, 'admin.html', render_params(request, news=get_show_news()))
    return HttpResponseRedirect('/login')


def logout(request):
    request.session.clear()
    return render(request, 'logout.html', render_params(request))


def getnew(request):
    global spider_thread
    if spider_thread and spider_thread.is_alive():
        print("Already one!")
    else:
        spider_thread = spider.spider_thread()
        spider_thread.start()
    return render(request, 'loading.html', render_params(request))


def del_many(request):
    try:
        if request.method == 'POST':
            sess = request.session.get('sess', None)
            if sess and User.objects.filter(sess=sess):
                oris = request.POST['data'].split(',')
                ids = [int(i) for i in oris if i.isdigit()]
                news = News.objects.filter(id__in=ids)
                if len(news) > 0:
                    # news.delete()
                    news.update(deleted=True)
                    return JsonResponse({'state': 'ok'})
    except:
        pass
    return JsonResponse({'state': 'error'})


def recover_many(request):
    try:
        if request.method == 'POST':
            sess = request.session.get('sess', None)
            if sess and User.objects.filter(sess=sess):
                oris = request.POST['data'].split(',')
                ids = [int(i) for i in oris if i.isdigit()]
                news = News.objects.filter(id__in=ids)
                if len(news) > 0:
                    # news.delete()
                    news.update(deleted=False)
                    return JsonResponse({'state': 'ok'})
    except:
        pass
    return JsonResponse({'state': 'error'})


def admin_recover(request):
    if check_loggedini(request):
        return render(request, 'recover.html', render_params(request, news=get_unshow_news()))
    return HttpResponseRedirect('/login')


def query(request, s):
    news = News.objects.filter(deleted=False).filter(content__contains=s.replace("'", '"'))
    news = list(news)
    news.sort(key=lambda x: x.id)
    return render(request, 'query_ans.html', render_params(request, news=news, query_text=s))


def query_title(request, s):
    news = News.objects.filter(deleted=False).filter(title__contains=s.replace("'", '"'))
    news = list(news)
    news.sort(key=lambda x: x.id)
    return render(request, 'query_ans.html', render_params(request, news=news, query_text=s))
