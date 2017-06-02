import sys
import time
import PTTTelnetCrawlerLibrary

if __name__ == "__main__":
    print("Welcome to PTT Telnet Crawler Library Demo")

    ID = 'Your PTT ID'
    Password = 'Your PTT Password'
    KickOtherLogin = False
    PTTCrawler = PTTTelnetCrawlerLibrary.PTTTelnetCrawlerLibrary(ID, Password, KickOtherLogin)
    if not PTTCrawler.isLoginSuccess():
        PTTCrawler.Log("Login fail")
        sys.exit()
    
    BoardList = ["Wanted", "AllTogether", "Gossiping"]
    
    for Board in BoardList:
        NewestIndex = PTTCrawler.getNewestPostIndex(Board)
        if not NewestIndex == -1:
            PTTCrawler.Log("Get " + Board + " get newest post index success: " + str(NewestIndex))
        else:
            PTTCrawler.Log("Get " + Board + " get newest post index fail")
    
    for Board in BoardList:
        if PTTCrawler.gotoBoard(Board):
            PTTCrawler.Log("Go to " + Board + " success")
        else:
            PTTCrawler.Log("Go to " + Board + " fail")
    
    #發文類別       1
    #簽名檔        	0

    for i in range(3):
        if PTTCrawler.post("Test", "連續自動PO文測試 " + str(i), "自動PO文測試\r\n\r\n使用PTT Telnet Crawler Library 測試\r\n\r\nhttps://goo.gl/qlDRCt", 1, 0):
            PTTCrawler.Log("Post success")
        else:
            PTTCrawler.Log("Post fail")

    PostIDList = ["1PC1YXYj", "1PCBfel1", "1D89C0oV"]
    
    for PostID in PostIDList:
        Post = PTTCrawler.getPostInformationByID("Wanted", PostID)
        if not Post == None:
            PTTCrawler.Log("getPostInformationByID success")
        else:
            PTTCrawler.Log("getPostInformationByID fail")
    
    NewestIndex = PTTCrawler.getNewestPostIndex("Wanted")
    
    for i in range(3):
        Post = PTTCrawler.getPostInformationByIndex("Wanted", NewestIndex - i)
        if not Post == None:
            PTTCrawler.Log("getPostInformationByIndex success: " + str(NewestIndex - i))
        else:
            PTTCrawler.Log("getPostInformationByIndex fail: " + str(NewestIndex - i))
    
    LastIndex = NewestIndex - 5
    for i in range(3):
        #Return new post list LastIndex ~ newest without LastIndex
        LastIndexList = PTTCrawler.getNewPostIndex("Wanted", LastIndex)
        if not len(LastIndexList) == 0:
            for NewPostIndex in LastIndexList:
                PTTCrawler.Log("Detected new post: " + str(NewPostIndex))
            LastIndex = LastIndexList.pop()
    
    for i in range(3):
        NewestPostIndex = PTTCrawler.getNewestPostIndex("Test")
        if PTTCrawler.pushByIndex("Test", NewestPostIndex, PTTCrawler.PushType_Push, "https://goo.gl/qlDRCt by post index"):
            PTTCrawler.Log("pushByIndex Push success")
        else:
            PTTCrawler.Log("pushByIndex Push fail")
            
    for i in range(3):
        NewPost = PTTCrawler.getPostInformationByIndex("Test", NewestPostIndex)
        
        if NewPost == None:
            PTTCrawler.Log("getPostInformationByIndex fail")
            break
        if PTTCrawler.pushByID("Test", NewPost.getPostID(), PTTCrawler.PushType_Push, "https://goo.gl/qlDRCt by post id"):
            PTTCrawler.Log("pushByID Push success")
        else:
            PTTCrawler.Log("pushByID Push fail")
    #0 不加簽名檔
    for i in range(3):
        if PTTCrawler.mail(ID, "自動寄信測試標題", "自動測試 如有誤寄打擾 抱歉QQ", 0):
            PTTCrawler.Log("Mail to " + ID + " success")
        else:
            PTTCrawler.Log("Mail to " + ID + " fail")
    
    PTTCrawler.logout()