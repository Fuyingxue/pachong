import os
import requests
from pyquery import PyQuery as pq


# 自定义log，代替print
def log(*args, **kwargs):
    print(*args, **kwargs)


# 可以伪装客户端及登录
# 替换 cookie
cookie = ''
accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
useragent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'

headers = {
    'Cookie': cookie,
    'User-Agent': useragent,
    'Accept': accept,
}


class Model(object):
    """
    基类, 用来显示类的信息
    """

    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    """
    存储电影信息
    """

    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'
    filename = url.split('=', 1)[-1] + '.html'
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)

        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url, headers)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def movie_from_div(div):
    """
    从一个 div 里面获取到一个电影信息
    """
    e = pq(div)

    # 小作用域变量用单字符
    m = Movie()
    m.name = e('.title').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic').find('em').text()

    return m


def movies_from_url(url):
    """
    从 url 中下载网页并解析出页面内所有的电影

    只下载一次

    1. 解析 dom
    2. 找到父亲节点
    3. 每个子节点拿一个movie
    """

    page = cached_url(url)
    e = pq(page)
    # log(page.decode())
    # 2.父节点
    items = e('.item')
    # 调用 movie_from_div
    # list comprehension
    movies = [movie_from_div(i) for i in items]
    return movies


def download_image(url, name):
    folder = "img"
    names = name.split("/")[0] + '.jpg'
    path = os.path.join(folder, names)

    if not os.path.exists(folder):
        os.makedirs(folder)

    if os.path.exists(path):
        return

    # 发送网络请求, 把结果写入到文件夹中
    r = requests.get(url, headers)
    with open(path, 'wb') as f:
        f.write(r.content)


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies = movies_from_url(url)
        log('top250 movies', movies)
        [download_image(m.cover_url, m.name) for m in movies]


if __name__ == '__main__':
    main()
