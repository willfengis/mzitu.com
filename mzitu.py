import requests
import hashlib
import os
from requests import RequestException
from lxml import etree
from multiprocessing import Pool
from com.it.config_mzitu import *

# 返回首页html.text
def search_parse(searchUrl):
    print('正在获取主页信息...')
    try:
        html = requests.get(url=searchUrl, headers=headers)
        if html.status_code == 200:
            return html.text
        print('searchUrl status_code error')
        return None
    except RequestException:
        print('searchUrl request error')
        return None

# 返回首页字典包含详情页url
def page_urls(response):
    print('正在解析主页关键字...')
    html = etree.HTML(response)
    title = html.xpath('//ul[@id="pins"]/li/span/a/text()')
    time = html.xpath('//ul[@id="pins"]/li/span[@class="time"]/text()')
    url = html.xpath('//ul[@id="pins"]/li/span/a/@href')
    for i in range(len(title)):
        yield {'title': title[i], 'time': time[i], 'url': url[i]}

# 返回详情页总数
def max_page(detaiPage):
    detailUrl = detaiPage['url']
    try:
        html = requests.get(url=detailUrl, headers=headers)
        if html.status_code == 200:
            html = etree.HTML(html.text)
            return html.xpath('//div[@class="pagenavi"]//span/text()')[-2]
        print('detailUrl status_code error')
        return None
    except RequestException:
        print('detailUrl request error')
        return None

# 拿到每一页的图片url地址
def img_url(detailUrl, maxPage):
    print('正在解析详情页url...')
    for pageNmu in range(int(maxPage)):
        pageUrl = '{}/{}'.format(detailUrl['url'], pageNmu + 1)  # 构建每一页url
        try:
            html = requests.get(url=pageUrl, headers=headers)
            if html.status_code == 200:
                html = etree.HTML(html.text)
                return html.xpath("//div[@class='main-image']//img/@src")[0]
            print('status_code error', pageUrl)
            return None
        except RequestException:
            print('request error', pageUrl)
            return None

# 请求真实图片地址,并将图片保存到本地
def download_img(imgUrl):
    print('正在下载图片...')
    try:
        html = requests.get(url=imgUrl, headers=headers)
        if html.status_code == 200:
            save_img(html, imgUrl)  # 调用保存图片函数
            print('保存图片成功', imgUrl)
            return
        print('imgUrl status_code error')
        return None
    except RequestException:
        print('imglUrl request error')
        return None

# 保存图片到当前路径,将图片url转换为md5命名保存去重
def save_img(html, imgUrl):
    path = '{}/image/{}.jpg'.format(os.getcwd(), hashlib.md5(imgUrl.encode('utf8')).hexdigest())
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(html.content)
            f.close()

def main(Num):
    print('开启进程',Num)
    searchUrl = 'http://www.mzitu.com/search/{0}/page/{1}/'.format(keyWord, Num)
    response = search_parse(searchUrl)
    for detailPage in page_urls(response):
        print(detailPage)
        maxPage = max_page(detailPage)
        imgUrl = img_url(detailPage, maxPage)
        download_img(imgUrl)

if __name__ == '__main__':
    Num = [i for i in range(1, pageNum+1)]  #构建查询页数
    mypool = Pool()  #开启多进程池
    mypool.map(main, Num)

