import os
import random
import urllib.request
from threading import Thread
from time import sleep
import http.client
import util.mku
import io

import requests
import bs4
import re
my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
    ]
# 输入网址

next=0
template="https://www.bilibili.com/video/{}?p=%s"
save_dir="f:/videos/"
size=0

#获取保存的文件夹的名字
def get_dirname(url):
    # 获取页面
    html = str(requests.get(url).content, encoding="utf-8")
    # 载入bs
    bs = bs4.BeautifulSoup(html, features="lxml")
    # 创建文件夹
    dir = save_dir + bs.title.text[:12]+"/"
    return dir
#(template % ?)即？集的地址
def main():
    global template
    global save_dir
    global next
    index=input("网址:")
    # save_dir=input("保存的位置:")
    start=int(input("从多少集开始:"))
    end=int(input("到多少集:"))
    size=int(input("单此下载数量:"))
    template=template.format(index)
    save_dir=get_dirname(template % 1)
    print(save_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    #将每一波分开
    all_ps=list(util.mku.slice_range(start,end+1,size))
    length=len(all_ps)
    for index,ps in enumerate(all_ps):
        for p in ps:
            thread=Thread(target=downloadByP,args=(p,))
            thread.start()
        if index<length-1:
            while True:
                if next==size:
                    next=0
                    break
        print("第%s波完成" % str(index + 1),"休息10秒")
        sleep(8)
    util.mku.merge_dir(save_dir,limit=end)




def downloadByP(p):
    url=template % p
    downloadByUrl(url,str(p))


def downloadByUrl(url,filename):
    global next
    urls=get_mp4_and_mp3(url)
    mp3=urls[0]
    mp4=urls[1]
    mp3_path=save_dir+filename+".mp3"
    mp4_path=save_dir+filename+"p.mp4"
    reg=create_request(mp3)
    save_response(mp3_path,reg)
    reg2=create_request(mp4)
    save_response(mp4_path,reg2)
    print("第%s集下载完成" %filename)
    next+=1





def create_request(url):
    if url[len(url)-8:len(url)]=="80000000":
        max=get_max(url)
        reg = urllib.request.Request(url)
        reg.add_header("Range", "bytes={}-{}".format(0,max))
        reg.add_header("User-Agent",
                       random.choice(my_headers))
        reg.add_header("Referer", "https://www.bilibili.com/video/av38409964?p=1")
    else:
        reg=urllib.request.Request(url)
    return reg






# def do(p):
#     global next
#     sleep(1)
#     next+=1


# def save(urls):
#     mp3=urls[0]
#     mp4=urls[1]



# def downloadByurls(urls, dir, i):
#     video=urls[0]
#     sound=urls[-1]
#     v_max=get_max(video)
#     s_max=get_max(sound)
#     v_thread=Thread(target=downloadByTarget,args=(video,v_max,dir,i,"mp4"))
#     v_thread.start()
#     m_thread=Thread(target=downloadByTarget,args=(sound,s_max,dir,i,"mp3"))
#     m_thread.start()

def get_mp4_and_mp3(url):
    # 创建资源的正则
    # kodo_compile = re.compile('http((.{400,600}80{7})|(.{200,300}((A0{6}1)|(A0{6}2))))"')
    kodo_compile = re.compile('baseUrl":"(http.+?)"')
    audio_compile=re.compile('"audio":.+?baseUrl":"(http.+?)"')
    # kodo_compile = re.compile('http.{400,600}80{7}"')
    # 找出视频和音频
    html = requests.get(url).text
    urls = [g.group(1) for g in re.finditer(kodo_compile, html)]
    audio=audio_compile.search(html)
    urls=[audio.group(1),urls[0]]
    print(urls[0])
    return urls



def save_response(filename,request):
    content=urllib.request.urlopen(request).read()
    with open(filename,'wb') as f:
        f.write(content)


# def downloadByTarget(url,max,dir,i,t):
#     global next
#     reg = urllib.request.Request(url)
#     reg.add_header("Range", "bytes={}-{}".format(0,max))
#     reg.add_header("User-Agent",
#                    random.choice(my_headers))
#     reg.add_header("Referer", "https://www.bilibili.com/video/av38409964?p=1")
#     response = urllib.request.urlopen(reg)
#     filename=dir+"{}.{}".format(i,t)
#     with open(filename,"wb") as f:
#         f.write(response.read())
#     print(filename,"下载完成")
#     next+=1
#获取一集视频的字节范围n
def get_max(url):
    req_headers={
        'Range':"bytes={}-{}".format(0,0),
        'User-Agent':random.choice(my_headers),
        'Referer': "https://www.bilibili.com/video/av38409964?p=1"
    }
    rep_headers=requests.head(url,headers=req_headers).headers
    return rep_headers["Content-Range"].split("/")[1]

if __name__ == '__main__':
    main()
    # util.mku.merge_dir("T:/videos/ppt高手之路！（基础篇",src_mp4=".mp4",outPut_mp4="p.mp4")


