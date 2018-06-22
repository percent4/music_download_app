# -*- coding: utf-8 -*-

# 载入必要的模块
import os
import wx
import json
import requests
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

# 下载歌曲
# 传入参数： song_name: 歌曲名称, save_directory: 保存目录, platform: 音乐平台
def song_download(song_name, save_directory, platform):

    # 请求头部
    headers = {
        'Host': 'www.qmdai.cn',
        'Connection': 'keep-alive',
        'Content-Length': '43',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'http://www.qmdai.cn',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    # POST数据
    data = {'input':  song_name,
            'filter': 'name',
            'type':   platform,
            'page':   1
            }

    url = 'http://www.qmdai.cn/yinyuesou/'  # 网址
    # 提交POST请求
    r = requests.post(url=url, data=data, headers=headers)

    # print('获取数据成功！')
    first_song = json.loads(r.text)['data'][0] # 获取第一首歌的信息
    song_url = first_song['url'] # 歌曲下载网址

    print('%s开始下载...'%song_name)
    # 下载歌曲
    urllib.request.urlretrieve(song_url, '%s/%s.mp3' %(save_directory, song_name))


#事件处理，开始下载歌曲到指定保存目录
def login_process(save_directory, song_name, platform):

    # 下载歌曲，并给出相应的提示信息
    try:
        song_download(song_name, save_directory, platform)  # 开始歌曲下载
        print("歌曲%s下载成功！" % song_name)
    except Exception as e:
        print("歌曲%s下载失败，请重试~" % song_name)
        print("错误原因：")
        print(e)

#利用WxPython创建GUI
class Example(wx.Frame):
    def __init__(self, parent, title):
        #继承父类wx.Frame的初始化方法，并设置窗口大小为420*360
        super(Example, self).__init__(parent, title = title, size=(420, 360))
        self.InitUI()
        self.Centre()
        self.Show()

    def InitUI(self):

        #利用wxpython的GridBagSizer()进行页面布局
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(10, 20) #列间隔为10，行间隔为20

        # 第一行为空
        #title = wx.StaticText(panel, label="")
        #sizer.Add(title, pos=(0, 1), flag=wx.ALL, border=5)

        #添加账号字段，并加入页面布局，为第二行，第一列
        text = wx.StaticText(panel, label="歌曲名称")
        sizer.Add(text, pos=(1, 0), flag=wx.ALL, border=5)

        #添加文本框字段，并加入页面布局，为第二行，第2,3列
        self.tc =  wx.TextCtrl(panel, -1, size = (150,100), style = wx.TE_MULTILINE)
        sizer.Add(self.tc, pos=(1, 1), span=(1,3), flag=wx.EXPAND|wx.ALL, border=5)

        #添加密码字段，并加入页面布局，为第三行，第一列
        text1 = wx.StaticText(panel, label="保存目录")
        sizer.Add(text1, pos=(2,0), flag=wx.ALL, border=5)

        #添加文本框字段，以星号掩盖,并加入页面布局，为第三行，第2,3列
        self.tc1 = wx.TextCtrl(panel)
        sizer.Add(self.tc1, pos=(2,1), span=(1,3), flag=wx.EXPAND|wx.ALL, border=5)

        # 添加音乐平台及单选框组，并加入页面布局，为第三行
        platform_list = ["网易", "QQ", "酷狗", "酷我", "虾米", "百度"]
        self.radiobox = wx.RadioBox(panel, -1, "音乐平台", (150, 80), (310, 50), platform_list, 6, wx.RA_SPECIFY_COLS)
        sizer.Add(self.radiobox, pos=(3, 0), span=(0,3), flag=wx.ALL, border=5)

        #添加开始下载按钮，并加入页面布局，为第四行，第0,1列
        btn1 = wx.Button(panel, -1, "开始下载")
        sizer.Add(btn1, pos=(4,0), span=(0,1), flag=wx.ALL, border=5)

        # 添加清空按钮，并加入页面布局，为第四行，第2,3列
        btn2 = wx.Button(panel, -1, "清空输入")
        sizer.Add(btn2, pos=(4,2), span=(2,3), flag=wx.ALL, border=5)

        #为开始下载按钮绑定concurrency事件
        self.Bind(wx.EVT_BUTTON, self.concurrency, btn1)
        #为清空按钮绑定clear事件
        self.Bind(wx.EVT_BUTTON, self.clear, btn2)

        #将Panel适应GridBagSizer()放置
        panel.SetSizerAndFit(sizer)

    # 并发下载歌曲
    def concurrency(self, event):

        song_list = self.tc.GetValue().split('\n')  # 获取输入框中的歌曲名称
        save_directory = self.tc1.GetValue()  # 获取输入框中的保存目录
        platform_choice = self.radiobox.GetStringSelection() # 获取下载的音乐平台

        if not platform_choice: # 默认选择为'网易'
            platform_choice = '网易'

        # 音乐平台及其对应的网页中input的value
        platform_dict = {'网易': 'netease',
                         'QQ':   'qq',
                         '酷狗': 'kugou',
                         '酷我': 'kuwo',
                         '虾米': 'xiami',
                         '百度': 'baidu'
        }

        platform = platform_dict[platform_choice]

        if song_list and save_directory:  # 输入歌曲名称和保存目录不为空
            # 如果保存目录不存在，则新建目录
            if not os.path.exists(save_directory):
                os.mkdir(save_directory)

            print('\n'+'*'*30+'\n并发下载歌曲中...')
            # concurrent.futures模块进行并发下载
            executor = ThreadPoolExecutor(len(song_list))
            future_tasks = [executor.submit(login_process, save_directory, song, platform) for song in song_list]
            wait(future_tasks, return_when=ALL_COMPLETED)
            wx.MessageBox("全部歌曲下载完毕,请前往文件夹中查看！")

        else:  # 输入歌曲名称或保存目录为空
            wx.MessageBox("您的输入为空，请输入歌曲名称和保存目录！")

    # 清空输入框
    def clear(self, event):
        self.tc.SetValue("")
        self.tc1.SetValue("")

#主函数
def main():
    app = wx.App()
    Example(None, title = '简易歌曲下载APP')
    app.MainLoop()

main()