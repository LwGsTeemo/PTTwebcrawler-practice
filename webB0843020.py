import requests,csv,time,datetime
from bs4 import BeautifulSoup
payload = {"from": "https://www.ptt.cc/bbs/Gossiping/index.html","yes": "yes"}  #將18歲以上的dataForm複製下來
myheaders = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"} #自身來源
rs = requests.Session()
rs.post("https://www.ptt.cc/ask/over18", data=payload, headers=myheaders)   #Line6、7 為伺服端
title,header,time,u = [0],[0],[0],[0]
score=[[0 for j in range(2)] for k in range(30)]
yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%m/%d")   #昨天
beforeyesterday = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%m/%d") #前天
url = "https://www.ptt.cc/bbs/Gossiping/index.html"
exit=0
while(1): #  date:10/22     #開始找每一頁
    res = rs.get(url, headers=myheaders)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.find_all("div",class_="title")
    time = soup.find_all("div",class_="date")
    j=0
    TitleURL=[]
    for i in time:
        if(yesterday in i):     #找出每一頁中的每個標題的日期是否為昨天
            if(title[j].a):     #查看標題是否還健在(有些被刪文後會不存在)
                TitleURL.append("https://www.ptt.cc"+title[j].find("a").get("href"))  
        elif(beforeyesterday in i):
            exit=1
        j=j+1
    if(exit==1):    #爬到前天的文後就可以跳出while迴圈
        break
    u = soup.find_all("a",class_="btn wide")    #上一頁按鈕的a標籤(有"最舊","上一頁","下一頁","最新")
    url = "https://www.ptt.cc"+u[1].get("href") #組合出上一頁的網址

    for j in range(len(TitleURL)):  #找每一個標題網站的樓層數
        res = rs.get(TitleURL[j], headers=myheaders)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.find_all("div",class_="push")  #樓層數
        score[j][0] = len(title)    #利用list陣列，排出樓層數跟對應的標題網站
        score[j][1] = TitleURL[j]
    score.sort(key=(lambda x:x[0]),reverse=True)    #把全部(包含最後的10個位置)做由大到小的排序
    for j in range(20,30):
        score[j][0] = score[j-20][0]    #把排名前10的樓層數放到最後面的10個位置
        score[j][1] = score[j-20][1]
    del TitleURL

Author,Titles,Date,Article,Ip = [],[],[],[],[]
for i in range(10):
    res = rs.get(score[i][1], headers=myheaders)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    header = soup.find_all("span","article-meta-value")
    Author.append(header[0].text) #找作者
    Titles.append(header[2].text)  #找標題
    Date.append(header[3].text)   #找日期
    mainContainer = soup.find(id="main-container")  #找內文
    content = mainContainer.text.replace("\u3000","  ").replace("\n","")    #\n跟編碼問題排版
    content = content.split("※ 發信站: 批踢踢實業坊(ptt.cc)")[0] #先將整頁內容擷取下來，再把時間以後、結尾以前的真正內文給切割出來
    content = content.split(header[3].text)[1]
    content = content.strip()   #去除list首尾的\n
    Article.append(content)
    ipAddress = mainContainer.text.split("※ 文章網址:")[0] #找IP，方法跟找內文一樣，用切割的
    ipAddress = ipAddress.split("※ 發信站: 批踢踢實業坊(ptt.cc),")[1]
    Ip.append(ipAddress)

with open("B0843020.csv","w",newline="",encoding = "utf-8")as csvfile:  #轉成.csv檔 編碼為utf8
    writer = csv.writer(csvfile)
    writer.writerow(["作者","標題","時間","內文","IP"])
    for i in range(0,10):
        writer.writerow([Author[i],Titles[i],Date[i],Article[i],Ip[i]])
    writer.writerow([datetime.datetime.now()])
# :D