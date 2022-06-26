import sys
from time import time
from types import coroutine
import requests
import bs4 


def blogToCome(a):
    #博客來 取購買連結 價格 作者 出版社 出版日期 分類 書簡介 
    #=============================================================================搜尋頁面跟傳送給網站的資訊
    url = 'https://search.books.com.tw/search/query/key/' + str(a) +'/cat/all'  
    headers = { 'Referer': 'https://search.books.com.tw/',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows",
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                'AppleWebKit/537.36 (KHTML, like Gecko)'
                                'Chrome/103.0.0.0 Safari/537.36',}
    #=============================================================================取得網頁html所有資訊
    response = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    soupstr = str(soup)
    #print(soupstr)
    #=============================================================================抱歉，找不到您所查詢的的 ISBN書的資訊 error1
    blogToComeBookerror1 = soupstr.find('抱歉，找不到您所查詢的')
    if blogToComeBookerror1>=1:
        #print("博客來無此書存在")
        blogToComebookinfo={
            'BtcUrl':'Null',
            'BtcPrice':'Null',
            'BtcWriter':'Null',
            'BtcPress':'Null',
            'BtcDate':'Null',
            'BtcClass':'Null',
            'BtcIntroduction':'Null',
        }
        return blogToComebookinfo
    try:
        #=============================================================================尋找特定標籤的內容
        findALLbook = soup.find('div', class_="mod2 table-container")
        findbook = findALLbook.find('div', class_="box")
        #=============================================================================取出博客來書籍的商品碼
        oneitemhead = str(findbook).find('/item/')
        oneitemtail = str(findbook).find('/page/')
        oneitemmid = str(findbook)[oneitemhead+6:oneitemtail]
        #print(oneitemmid)
        #=============================================================================利用其物品碼取得該書網站 網頁html所有資訊
        BtcUrl = 'https://www.books.com.tw/products/'+str(oneitemmid)
        response = requests.get(BtcUrl, headers=headers)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        soupstr = str(soup)
        #=============================================================================尋找特定標籤的內容 書特定資訊區域
        bookinfo = soup.find('div', class_="container_24 main_wrap clearfix") 
        #=============================================================================尋找特定標籤的內容 書特定資訊區域 書作者、譯者、出版社、出版日期、語言路徑  區域資料
        bookAreaInfo = bookinfo.find('div', class_="type02_p003 clearfix") 
        bookAreaInfo = bookAreaInfo.find('ul')
        #print(bookAreaInfo)
        #=============================================================================價格欄
        bookPrice = bookinfo.find('div', class_="cnt_prod002 clearfix")
        bookPrice = bookPrice.find('strong', class_="price01")
        bookPricehead = str(bookPrice).find('class="price01">')
        bookPricetail = str(bookPrice).find('</b>')
        bookPrice = str(bookPrice)[bookPricehead:bookPricetail]
        bookPrice= bookPrice.strip('class="price01"><b>')
        BtcPrice = bookPrice
        #=============================================================================作者欄
        bookWriter = bookAreaInfo.find('li') #取作者bookWriter
        bookWriterfirst =  str(bookAreaInfo).find('</div>    作者：')#取前頭
        bookWriter = str(bookWriter)[int(bookWriterfirst):]
        bookWritersecond = bookWriter.find('</a>')#取後頭
        bookWriter = str(bookWriter)[:int(bookWritersecond)]
        bookWriterthird = bookWriter.find('/">')#第二次取前頭
        bookWriter = str(bookWriter)[int(bookWriterthird):]
        bookWriter = bookWriter.strip('/">')#消除
        BtcWriter = bookWriter
        #=============================================================================出版社欄
        bookPressfirst = str(bookAreaInfo).find('出版社：')#取出版社前頭bookPressfirst
        bookPress = str(bookAreaInfo)[int(bookPressfirst):]
        bookPresssecond = bookPress.find('</span>')#取出版社後頭bookPresssecond
        bookPress = str(bookPress)[:int(bookPresssecond)]
        bookPressRedundant = str(bookPress).find('<span>')#清除多餘資料
        bookPress = str(bookPress)[int(bookPressRedundant)+6:]
        BtcPress = bookPress
        #=============================================================================出版日期欄
        bookDatefirst = str(bookAreaInfo).find('出版日期：')#取出版日期前頭bookDatefirst
        bookDate = str(bookAreaInfo)[int(bookDatefirst):]
        bookDatesecond = bookDate.find('</li>')#取出版日期後頭bookDatesecond
        bookDate = str(bookDate)[:int(bookDatesecond)]
        bookDate = bookDate.strip('出版日期：')#清除多餘資料
        BtcDate = bookDate
        #=============================================================================書簡介欄
        bookIntroduction = bookinfo.find('div', class_="content")#取簡介bookIntroduction
        try:
            bookIntroduction = bookIntroduction.text.strip()
            bookIntroduction = bookIntroduction.replace('▓','')
            bookIntroduction = bookIntroduction.replace('\u3000','')
            BtcIntroduction = bookIntroduction
        except:
            bookIntroduction = ' '
        #=============================================================================書分類欄
        BtcClass = ['文學小說', '商業理財', '藝術設計', '人文社科', '心理勵志', '宗教命理', '自然科普', '醫療保健', '飲食', '生活風格', '旅遊', '童書/青少年文學', '國中小參考書', '親子教養', '影視偶像', '輕小說', '漫畫/圖文書', '語言學習', '考試用書', '電腦資訊', '專業/教科書/政府出版品']
        i=0
        while i<=len(BtcClass)-1:
            bookClass = soup.find('ul', class_="container_24 type04_breadcrumb")
            bookClass=str(bookClass).find(BtcClass[i])
            if bookClass>=1:
                break
            i=i+1
        #=============================================================================博客來 單本書購買連結 價格 作者 出版社 出版日期 分類 書簡介
        #print('#===================================================================博客來 單本書購買連結 價格 作者 出版社 出版日期 分類 書簡介 ')
        #print(BtcUrl)
        #print(bookPrice)
        #print(bookWriter)
        #print(bookPress)
        #print(bookDate)
        #print(classbook[i])
        #print(bookIntroduction)
        blogToComebookinfo={
                'BtcUrl':BtcUrl,
                'BtcPrice':BtcPrice,
                'BtcWriter':BtcWriter,
                'BtcPress':BtcPress,
                'BtcDate':BtcDate,
                'BtcClass':BtcClass[i],
                'BtcIntroduction':BtcIntroduction,
            }
        return blogToComebookinfo
    except:
        #print("博客來無此書存在 跑太慢")
        blogToComebookinfo={
            'BtcUrl':'Null',
            'BtcPrice':'Null',
            'BtcWriter':'Null',
            'BtcPress':'Null',
            'BtcDate':'Null',
            'BtcClass':'Null',
            'BtcIntroduction':'Null',
        }
        return blogToComebookinfo

def Pchome(a):
    #PChome 取購買連結
    #=============================================================================搜尋頁面跟傳送給網站的資訊 需要利用特殊方式F12>xhr>搜尋欄輸入>RESULT點下去>去找其網址規律性
    PChomeurl = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q='+str(a)+'&page=1&sort=sale/dc'
    headers = {     'User-Agent': 'https://24h.pchome.com.tw/',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows",
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                'AppleWebKit/537.36 (KHTML, like Gecko)'
                                'Chrome/103.0.0.0 Safari/537.36',}
    #=============================================================================取得搜尋網頁html所有資訊
    response = requests.get(PChomeurl, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    soupstr = str(soup)
    #print(soupstr)
    #=============================================================================抱歉，找不到您所查詢的的 ISBN書的資訊 error1
    pchomeBookerror1 = soupstr.find('"totalPage":0,')
    if pchomeBookerror1>=1:
        #print("PChome無此書存在")
        Pchomebookinfo={
            'PchUrl':'Null',
            'PchPrice':'Null',
        }
        return Pchomebookinfo
    try:
        #=============================================================================這所有碼 其裡面就有pchome商品碼跟價格等等 只取商品碼並加上連結網址
        PcHomemidhead = soupstr.find('"Id":"')
        PcHomemidtail = soupstr.find('","cateId"')
        PcHomemid = soupstr[PcHomemidhead:PcHomemidtail]
        PcHomemid = PcHomemid.strip('"Id":"')
        PcHomemidurl = 'https://24h.pchome.com.tw/books/prod/'+ str(PcHomemid)
        #=============================================================================這所有碼 其裡面就有pchome商品碼跟價格等等 只取價格
        PcHomepricehead = soupstr.find('"price":')
        PcHomepricehtail = soupstr.find(',"originPrice"')
        PcHomeprice = soupstr[PcHomepricehead:PcHomepricehtail]
        PcHomeprice = PcHomeprice.strip('"price":')
        #=============================================================================PChome 單本書連結跟價格
        #print('#===================================================================PChome 單本書連結跟價格')
        #print(PcHomemidurl)
        #print(PcHomeprice)
        Pchomebookinfo={
            'PchUrl':PcHomemidurl,
            'PchPrice':PcHomeprice,
        }
        return Pchomebookinfo
    except:
        #print("PChome無此書存在")
        Pchomebookinfo={
            'PchUrl':'Null',
            'PchPrice':'Null',
        }
        return Pchomebookinfo

def TAAZE(a):
    #TAAZE讀冊生活
    #=============================================================================搜尋頁面跟傳送給網站的資訊
    TAAZEurl = 'https://www.taaze.tw/rwd_searchResult.html?keyType%5B%5D=0&keyword%5B%5D='+str(a)+'&prodKind=0&prodCatId=0&catId=0&saleDiscStart=0&saleDiscEnd=0&salePriceStart=&salePriceEnd=&publishDateStart=&publishDateEnd=&prodRank=0&addMarkFlg=0&force=0&catFocus=&orgFocus=&mainCatFocus=&catNmFocus=&catIdFocus=&layout=A&nowPage=1&sort=price'
    headers = { 'Referer': 'https://www.taaze.tw/',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': "Windows",
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                'AppleWebKit/537.36 (KHTML, like Gecko)'
                                'Chrome/103.0.0.0 Safari/537.36',}
    #=============================================================================取得搜尋網頁html的最低價格跟第一個便宜書連結
    response = requests.get(TAAZEurl, headers=headers)
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    souperror=soup
    soup = soup.find('div', class_="media")
    soupstr = str(soup)
    #print(soupstr)
    #=============================================================================抱歉，找不到您所查詢的的 ISBN書的資訊 error1
    souperror = souperror.findAll('div', class_="col-xs-12")
    #print(souperror)
    errr = "索結果：<!--共<span class='r'>0</span>筆"
    TAAZEerror1 = str(souperror).find(errr)
    if TAAZEerror1>=1:
        #print("TAAZE讀冊生活無此書存在 跑太慢")
        TAAZEbookinfo={
            'TaazeUrl':'Null',
            'TaazePrice':'Null',
        }
        return TAAZEbookinfo
    try:
        #=============================================================================取連結
        Taazeurlhead = soupstr.find('href')
        Taazeurltail = soupstr.find('" onclick="historyStatByListView')
        Taazeurl = soupstr[Taazeurlhead:Taazeurltail]
        Taazeurl = Taazeurl.strip('href=')
        Taazeurl = Taazeurl.strip('"')
        #=============================================================================取價格
        Taazepricetail = soupstr.find('" itemprop="price"/>')
        Taazepricehead = soupstr[:Taazepricetail]
        Taazepricehead = Taazepricehead.rfind('content="')
        Taazeprice = soupstr[Taazepricehead:Taazepricetail]
        Taazeprice = Taazeprice.strip('content="')
        #=============================================================================TAAZE讀冊生活 單本書連結跟價格
        #print('#===================================================================TAAZE讀冊生活 單本書連結跟價格')
        #print(Taazeurl)
        #print(Taazeprice)
        TAAZEbookinfo={
            'TaazeUrl':Taazeurl,
            'TaazePrice':Taazeprice,
        }
        return TAAZEbookinfo
    except:
        #print("TAAZE讀冊生活無此書存在 跑太慢")
        TAAZEbookinfo={
            'TaazeUrl':'Null',
            'TaazePrice':'Null',
        }
        return TAAZEbookinfo

def ISBNimport(a):
    ALLMerchant={**blogToCome(a),**Pchome(a),**TAAZE(a)}#全部資料
    ALLMerchant = str(ALLMerchant).replace("'","\"")
    #print(ALLMerchant)
    return ALLMerchant
    
#取三家 博客來 pchome Taaze
#=============================================================================輸入ISBN
#print("請輸入ISBN:")
#ISBNimport(a = input())
#a=9789861755465
#print(ISBNimport(9789861755465))



