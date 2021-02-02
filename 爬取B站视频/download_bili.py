import re
from contextlib import closing

import requests
from tqdm import tqdm

def get_video_audio_url(url):
    #按照浏览器中请求头填写，去掉部分
    headers = {
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'if-range': "lm-vGohi8aMA0bE4dtHLYBU9m_vs",
        'origin': 'https://www.bilibili.com',
        'cache-control': 'max-age=0',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53',
    }
    #timeout设置时间限制，超时报错
    h = requests.get(url, headers=headers, timeout=8)

    if h.status_code == 200:
        t = h.content.decode('utf-8')
        
        #匹配获取所有的视频链接、音频链接和视频名称
        video_pattern = re.compile(r'video.*?baseUrl":"(.*?)"')
        video_url_lists = re.findall(video_pattern, t)
        audio_pattern = re.compile(r'audio.*?baseUrl":"(.*?)"')
        audio_url_lists = re.findall(audio_pattern, t)
        title_pattern = re.compile(r'<span class="tit">(.*?)</span>')
        video_title = re.findall(title_pattern, t)[0]
        
        if len(video_url_lists) == 0 or len(audio_url_lists) == 0:
            print("没有找到视频的视频下载连接或音频下载链接，下载失败")
            return
        else:
            return video_url_lists, audio_url_lists, video_title

    else:
        print("请求失败，请求状态为{}".format(h.status_code))
        return


def download_video(video_url, audio_url, filename):
    headers = {
        'scheme': 'https',
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'if-range': "lm-vGohi8aMA0bE4dtHLYBU9m_vs",
        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53',
    }
   
    video_body = requests.get(video_url, headers=headers, timeout=8, verify=False)
    audio_body = requests.get(audio_url, headers=headers, timeout=8, verify=False)

    if video_body.status_code == 200:
        video_name = filename + "_video.mp4"
        with closing(video_body) as response:
            chunk_size = 1024
            #获取请求文件返回的大小
            content_size = int(response.headers['Content-Length'])
            print("视频文件总大小{}M".format(content_size/(1024*1024)))
            with open(video_name, "wb") as f:
                for data in tqdm(response.iter_content(chunk_size=chunk_size)):
                    f.write(data)
        print("视频下载成功")
    if audio_body.status_code == 200:
        audio_name = filename + "_audio.mp4"
        with closing(audio_body) as response:
            chunk_size = 1024
            
            content_size = int(response.headers['Content-Length'])
            print("音频文件总大小{}M".format(content_size / (1024 * 1024)))
            with open(audio_name, "wb") as f:
                for data in tqdm(response.iter_content(chunk_size=chunk_size)):
                    f.write(data)
        print("音频下载成功")

if __name__ == '__main__':
    
    url = 'https://www.bilibili.com/video/BV1hp4y1W7Hx/'
    video_url,audio_url,filename = get_video_audio_url(url)

    download_video(video_url[0],audio_url[0],filename)
