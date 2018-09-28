import os
import re
import sys
import urllib.request

import requests
from bs4 import BeautifulSoup

_urls_file_path = "urls.txt"
__out_dir_name = "offline_pages"
__img_save_dir_suffix = "_files"
__bad_urls = []


def get_urls_from_file(file_path):
    urls = []
    if not os.path.exists(file_path):
        print("没有文件")
        return urls
    fp = open(file_path, "r")
    for count, line in enumerate(fp):
        line = re.sub('\n', '', line)
        if len(line) > 0:
            urls.append(line)
    return urls


def save_img(title, name, img_url):
    img_save_dir_name = title + __img_save_dir_suffix
    img_save_dir = __out_dir_name + os.path.sep + img_save_dir_name
    if not os.path.exists(img_save_dir):
        os.mkdir(img_save_dir)
    elif os.path.isfile(img_save_dir):
        os.mkdir(img_save_dir)

    img_src = img_save_dir_name + os.path.sep + name
    img_file_path = __out_dir_name + os.path.sep + img_src
    # print("下载图片： ", img_url)
    urllib.request.urlretrieve(img_url, img_file_path)
    return img_src


def get_title_from_soup(soup):
    title_el = soup.find('h2')
    if title_el is None:
        title_el = soup.find('h4')
    if title_el is None:
        title_el = soup.find('h3')
    if title_el is None:
        title_el = soup.find('h1')
    if title_el is None:
        title_el = soup.find('h5')
    if title_el is None:
        title_el = soup.find('h6')
    if title_el is None:
        title_el = soup.find('h7')
    if title_el is None:
        raise EOFError
    title = title_el.get_text()
    title = re.sub('\s', '', title)
    title = re.sub('\n', '', title)
    title = re.sub('[\/:*?"<>|]', '-', title)
    return title


def draw_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = ""
    try:
        title = get_title_from_soup(soup)
    except:
        __bad_urls.append(url)
        print(u"页面保存失败，链接无效或页面中没有标题，url：", url)
        return
    body = soup
    html = str(body)
    # body中的img标签的src相对路径的改成绝对路径
    pattern = "(<img .*?src=\")(.*?)(\")"
    url_head = url.split(":")[0]

    # 图片下载到本地， 同时替换成本地路径
    def func(m):
        if len(m.group(2)) == 0:
            return m.group(1) + m.group(2) + m.group(3)
        proto, rest = urllib.request.splittype(url)
        res, rest = urllib.request.splithost(rest)
        if not m.group(2).startswith("http") and not m.group(2).startswith("https"):
            if m.group(2).startswith("//"):
                img_url = url_head + ":" + m.group(2)
            else:
                img_url = proto + "://" + res + m.group(2)
        else:
            img_url = m.group(2)
        img_name = re.sub('[\/:*?"<>|]', '-', img_url)
        img_el = '<img src="' + save_img(title, img_name, img_url) + '" >'
        img_el = img_el.split(">")[0]
        return img_el

    html = re.compile(pattern).sub(func, html)
    path = __out_dir_name + os.path.sep + title + ".html"
    if os.path.exists(path):
        os.remove(path)
    os.mknod(path)
    fp = open(path, "w")
    fp.write(html)
    fp.flush()
    fp.close()
    print(u"end~~~~~ --> url: ", url)


def init():
    if not os.path.exists(__out_dir_name):
        os.mkdir(__out_dir_name)
    elif os.path.isfile(__out_dir_name):
        os.mkdir(__out_dir_name)


def main():
    init()
    if sys.argv is not None and len(sys.argv) > 1 \
            and sys.argv[1] is not None and sys.argv[1].strip():
        urls = get_urls_from_file(sys.argv[1])
    else:
        urls = get_urls_from_file(_urls_file_path)
    if len(urls) == 0:
        print("没有链接！！！")
        return
    for url in urls:
        draw_from_url(url)
    # drawFromUrl("https://www.v2ex.com/t/482250#reply20")
    if len(urls) > 1:
        print("全部完成～～～")
    if len(__bad_urls) > 0:
        print(u"失败链接(%s条)：" % len(__bad_urls))
        print(__bad_urls)


if __name__ == '__main__':
    main()
