import os
import re
import sys
import urllib.request

import requests
from bs4 import BeautifulSoup

_urls_file_path = "urls.txt"
__out_dir_name = "offline_pages"
__src_save_dir_suffix = "_files"
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


def save_src(title, name, src_url):
    src_save_dir_name = title + __src_save_dir_suffix
    src_save_dir = __out_dir_name + os.path.sep + src_save_dir_name
    if not os.path.exists(src_save_dir):
        os.mkdir(src_save_dir)
    elif os.path.isfile(src_save_dir):
        os.mkdir(src_save_dir)

    src = src_save_dir_name + os.path.sep + name
    src_file_path = __out_dir_name + os.path.sep + src
    # print("下载资源： ", src_url)
    urllib.request.urlretrieve(src_url, src_file_path)
    return src


def get_title_from_soup(soup):
    title_el = soup.find('title') \
               or soup.find('h2') \
               or soup.find('h4') \
               or soup.find('h3') \
               or soup.find('h1') \
               or soup.find('h5') \
               or soup.find('h6') \
               or soup.find('h7')
    if title_el is None:
        raise EOFError
    title = title_el.get_text()
    title = re.sub('\s', '', title)
    title = re.sub('\n', '', title)
    title = re.sub('[\/:*?"<>|]', '-', title)
    return title



def draw_from_url(url):


    img_lable_pattern = "(<img .*?src=\")(.*?)(\")"
    js_lable_pattern = "(<script .*?src=\")(.*?)(\")"
    css_lable_pattern = "(<link .*?href=\")(.*?)(\")"

    def re_change_img_url(m):
        return re_change_src_url(m, img_lable_pattern)

    def re_change_js_url(m):
        return re_change_src_url(m, js_lable_pattern)

    def re_change_css_url(m):
        return re_change_src_url(m, css_lable_pattern)

    # 资源下载到本地， 同时替换成本地路径
    def re_change_src_url(m, pattern):
        if len(m.group(2)) == 0:
            return m.group(1) + m.group(2) + m.group(3)
        proto, rest = urllib.request.splittype(url)
        res, rest = urllib.request.splithost(rest)
        if not m.group(2).startswith("http") and not m.group(2).startswith("https"):
            if m.group(2).startswith("//"):
                url_head = url.split(":")[0]
                src_url = url_head + ":" + m.group(2)
            else:
                src_url = proto + "://" + res + m.group(2)
        else:
            src_url = m.group(2)
        src_name = re.sub('[\/:*?"<>|]', '-', src_url)
        src = save_src(title, src_name, src_url)

        if pattern == img_lable_pattern:
            src_el = '<img src="' + src + '" >'
        elif pattern == js_lable_pattern:
            src_el = '<script src="' + src + '" >'
        elif pattern == css_lable_pattern:
            src_el = '<link href="' + src + '" >'
        else:
            print("unkonwn error")
            return None

        src_el = src_el.split(">")[0]
        return src_el

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
    # body中的资源标签的src相对路径的改成绝对路径
    html = re.compile(img_lable_pattern).sub(re_change_img_url, html)
    # try:
    #     html = re.compile(js_lable_pattern).sub(re_change_js_url, html)
    # except:
    #     print("handle js failed")
    # try:
    #     html = re.compile(css_lable_pattern).sub(re_change_css_url, html)
    # except:
    #     print("handle css failed")
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


def match_urls():
    if sys.argv is not None and len(sys.argv) > 1 \
            and sys.argv[1] is not None and sys.argv[1].strip():
        if re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', sys.argv[1]):
            urls = [sys.argv[1]]
        else:
            urls = get_urls_from_file(sys.argv[1])
    else:
        urls = get_urls_from_file(_urls_file_path)
    return urls


def main():
    init()
    urls = match_urls()
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
