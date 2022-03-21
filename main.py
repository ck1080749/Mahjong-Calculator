import tkinter as tk
from tkinter import messagebox
from majButton import MajButton
import json
import time
from functools import reduce

# 預處理
jsonFileOfPointLists = open("point.json", "r", encoding="utf-8")  # 打開點數清單
terminals = [11, 19, 21, 29, 31, 39, 41,
             42, 43, 44, 45, 46, 47]  # 1:萬, 2:筒, 3:索
ofs = [11, 14, 17, 21, 24, 27, 31, 34, 37]  # 147
tfe = [12, 15, 18, 22, 25, 28, 32, 35, 38]  # 258
tsn = [13, 16, 19, 23, 26, 29, 33, 36, 39]  # 369
word = set(range(41, 48))  # 字牌 東南西北白發中
man = set(range(11, 20))  # 1:萬
pin = set(range(21, 30))  # 2:筒
so = set(range(31, 40))  # 3:索
wind = {"東": "E", "南": "S", "西": "W", "北": "N"}

POINT = json.load(jsonFileOfPointLists)  # 讀取點數清單作為變數
jsonFileOfPointLists.close()  # 關閉點數清單的檔案

# 輸入時用的全局變數
f = open("mahjong.json", "r", encoding="utf-8")
MAHJONG = json.load(f)
f.close()
started = False
inputTarget = None  # 當下輸入那一格的內容，也就是會顯示成麻將牌的標籤
inputArray = None  # 用來傳送資料用的，int array

# 計算池的全局變數：複製貼上
listen = 0
tsumo = True  # 自摸
sitPosition = ""  # 門風，也就是坐的位置
gameWind = ""  # 場風
lastCard = False  # 海底撈月／河底撈魚，加一番
chyankan = False  # 搶槓 + 一番
rinshan = False  # 嶺上開花：槓後補牌自摸
richi = 0  # 立直，加番 0 = 沒立直, 1 = 一般立直, 2 = 兩立直
ippatsu = False  # 一發：即立直後一巡內贏
# nagashimangan = False  # TODO:流局滿貫
winFirstRound = False  # 莊家：天和，閒家：地和
akaDora = 0  # 赤寶牌
kitaDora = 0  # 拔北寶牌，三人麻才有
hand = []
yakus = []  # 役種表
combination = []  # 拆分的組合
winType = ""  # 贏的類型


def toDict(d: dict, now):  # 有趣的功能
    d[now] = 1 if now not in d.keys() else d[now]+1
    return d


def startEvent():  # 開始計算的過程，等一下大概會有不少複製貼上的部分
    global inHand
    global onDesk
    global get
    global listen
    global hand
    global tsumo
    global sitPosition
    global gameWind
    global lastCard
    global chyankan
    global rinshan
    global richi
    global ippatsu
    global winFirstRound
    global akaDora
    global kitaDora
    global dora
    global uradora
    global resultViewer
    global winType
    global POINT
    global yakus
    global combination
    if start_but["state"] == tk.NORMAL:
        start_but["state"] = tk.DISABLED
        hand = inHand+onDesk+get  # 組合出完整的手牌

        if len(hand) != 14:  # 手牌數量不正確
            messagebox.showerror(title="輸入錯誤", message="手牌數量不正確")
            start_but["state"] = tk.NORMAL
            return

        inHand.append(get[0] if get[0] < 100 else get[0]-100)
        hand.sort()

        # some errorCheck is needed:
        try:
            listen = get[0]
        except:
            messagebox.showerror(title="輸入錯誤", message="未輸入胡的那張")
            start_but["state"] = tk.NORMAL
            return

        # 某一種牌的數量過多
        if sorted(reduce(toDict, hand.copy(), {}).values(), reverse=True)[0] > 4:
            messagebox.showerror(title="輸入錯誤", message="某一種牌數量不正確")
            start_but["state"] = tk.NORMAL
            return
        # 對應到紅寶牌及五的過多
        if hand.count(15) > 3 or hand.count(25) > 3 or hand.count(35) > 3 or hand.count(115) > 1 or hand.count(125) > 1 or hand.count(135) > 1:
            messagebox.showerror(title="輸入錯誤", message="某一種牌數量不正確")
            start_but["state"] = tk.NORMAL
            return

        if _richi.get() != "無" and _winround.get() == "第一巡":  # 天／地和又立直
            messagebox.showerror(title="輸入錯誤", message="不可能第一巡立直胡")
            start_but["state"] = tk.NORMAL
            return

        if _richi.get() == "無" and _winround.get() == "一發":  # 沒立直而一發
            messagebox.showerror(title="輸入錯誤", message="沒立直不會一發")
            start_but["state"] = tk.NORMAL
            return

        # 狀態檢視器：將使用者輸入轉換成程式可以看懂的輸入
        # 也可以說是兩個不同程式融合的痕跡
        gameWind = wind[_gamewind.get()]  # 處理場風
        sitPosition = wind[_sitpos.get()]  # 處理門風
        tsumo = _tsumo.get() == 1
        kitaDora = _kitadora.get()
        if _richi.get() == "兩立直":  # 處理立直
            richi = 2
        elif _richi.get() == "立直":
            richi = 1
        else:
            richi = 0

        if _winround.get() == "第一巡":  # 處理和牌時機
            winFirstRound = True
        elif _winround.get() == "一發":
            ippatsu = True
        elif _winround.get() == "最後一張":
            lastCard = True
        else:
            pass

        for i in range(len(hand)):  # for akadora 115 125 135h #另類赤寶
            if hand[i] > 100:
                hand[i] -= 100
                akaDora += 1
        # print(hand)
        # 尋找雀頭
        ones = (hand.count(11) + hand.count(14) + hand.count(17) + hand.count(21) +
                hand.count(24) + hand.count(27) + hand.count(31) + hand.count(34) + hand.count(37)) % 3
        twos = (hand.count(12) + hand.count(15) + hand.count(18) + hand.count(22) +
                hand.count(25) + hand.count(28) + hand.count(32) + hand.count(35) + hand.count(38)) % 3
        threes = (hand.count(13) + hand.count(16) + hand.count(19) + hand.count(23) +
                  hand.count(26) + hand.count(29) + hand.count(33) + hand.count(36) + hand.count(39)) % 3

        if ones == twos == threes:  # 如果雀頭在字牌
            win = checkRon(word)
        elif ones != twos == threes:  # 如果雀頭在147
            win = checkRon(ofs)
        elif twos != ones == threes:  # 如果雀頭在258
            win = checkRon(tfe)
        elif threes != ones == twos:  # 如果雀頭在369
            win = checkRon(tsn)
        # print(combination)  # TODO:
        winType = ""  # N=一般型 7=七對子 K=國士 因為會先判斷能否一般型，故不用擔心會有二盃口被判斷成七對子
        if win:
            winType = "N"
        else:
            han = 0
            fu = 0
            # 七對子判斷 #TODO:整合到checkYaku裡面？
            SP = True
            for i in hand[::2]:
                if hand.count(i) != 2:
                    SP = False
                    break
            if SP:
                # print("seven pairs")
                # han += 2
                # fu += 25
                # yakus.append("七對子")
                win = True
                winType = "7"
                combination.append([])
            else:
                kokushicheck = 0  # 國士無雙 # TODO:整合到checkYaku裡面？
                flag = False
                for i in hand:
                    if i in terminals:
                        kokushicheck += 1
                if kokushicheck == 14:
                    for i in range(len(hand)-1):
                        if hand[i] == hand[i+1]:
                            hand.append(hand.pop(i+1))
                            break
                    flag = True
                    for i in range(13):
                        if hand[i] != terminals[i]:
                            flag = False
                            break
                    if flag:
                        # if hand[-1] == listen:
                        #     # print("yakuman! kokushi jusanmenmachi!")
                        #     #han -= 2
                        #     yakus.append("**國士無雙十三面**")
                        # else:
                        #     # print("yakuman! kokushimusou!")
                        #     #han -= 1
                        #     yakus.append("**國士無雙**")
                        win = True
                        winType = "K"
                        combination.append([])
                    else:
                        # print("沒胡")
                        win = False
                        pass
                else:
                    pass
                    win = False
                    # print("沒胡")
        highest = {}
        resultString = ""
        if win:  # 開始判斷番數與符數，此處要實作高點法
            for i in hand:
                resultString += MAHJONG[str(i)]
            resultString += "\n"
            highestpoint = 0
            for elm in combination:
                point = checkYaku(checkType=winType, combi=elm)
                # 先這樣實作好了，應該不會有太大問題（？
                # TODO:改成真的以點數判斷而非目前的番數
                if point["han"] > highestpoint:
                    highestpoint = point["han"]
                    highest = point.copy()
                elif point["han"] < 0:
                    highest = point.copy()
                    break
            if highest["han"] > 0:
                resultString += "\n".join(highest["yakus"])
                resultString += "\n-------------------------\n"
                resultString += "{}番, {}符".format(
                    highest["han"], highest["fu"])
                resultString += "->"
                if highest["han"] >= 13:  # 13 han or more
                    resultString += "累計役滿\n"
                    if tsumo:
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 16000 點\n"
                        else:  # normal tsumo
                            resultString += "莊家給 16000 點\n"
                            resultString += "閒家一人給 8000 點\n"
                    else:
                        resultString += "放槍者給 {} 點 \n".format(
                            48000 if sitPosition == "E" else 32000)
                    # b:48000/16000
                    # n:32000/8000,16000
                elif highest["han"] >= 11:  # 11, 12 han
                    resultString += "三倍滿\n"
                    if tsumo:
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 12000 點\n"
                        else:  # normal tsumo
                            resultString += "莊家給 12000 點\n"
                            resultString += "閒家一人給 6000 點\n"
                    else:
                        resultString += "放槍者給 {} 點 \n".format(
                            36000 if sitPosition == "E" else 24000)
                    # b:36000/12000
                    # n:24000/6000,12000
                elif highest["han"] >= 8:  # 8, 9, 10 han
                    resultString += "倍滿\n"
                    if tsumo:
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 8000 點\n"
                        else:  # normal tsumo
                            resultString += "莊家給 8000 點\n"
                            resultString += "閒家一人給 4000 點\n"
                    else:
                        resultString += "放槍者給 {} 點 \n".format(
                            24000 if sitPosition == "E" else 16000)
                    # b:24000/8000
                    # n:16000/4000,8000
                elif highest["han"] >= 6:  # 6, 7 han
                    resultString += "跳滿\n"
                    if tsumo:
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 6000 點\n"
                        else:  # normal tsumo
                            resultString += "莊家給 6000 點\n"
                            resultString += "閒家一人給 3000 點\n"
                    else:
                        resultString += "放槍者給 {} 點 \n".format(
                            18000 if sitPosition == "E" else 12000)
                    # b:18000/6000
                    # n:12000/3000,6000
                elif (highest["han"] == 5) or (highest["han"] == 4 and highest["fu"] >= 40) or (highest["han"] == 3 and highest["fu"] > 70):
                    resultString += "滿貫\n"
                    if tsumo:
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 4000 點\n"
                        else:  # normal tsumo
                            resultString += "莊家給 8000 點\n"
                            resultString += "閒家一人給 4000 點\n"
                    else:
                        resultString += "放槍者給 {} 點 \n".format(
                            12000 if sitPosition == "E" else 8000)
                    # b:12000/4000
                    # n:8000/4000,8000
                else:
                    if tsumo:
                        # print(highest["fu"])
                        if sitPosition == "E":  # banker tsumo
                            resultString += "閒家一人給 {} 點\n".format(
                                POINT[1][highest["han"]][str(highest["fu"])]["tsumo"][0])
                        else:  # normal tsumo
                            resultString += "莊家給 {} 點\n".format(
                                POINT[0][highest["han"]][str(highest["fu"])]["tsumo"][1])
                            resultString += "閒家一人給 {} 點\n".format(
                                POINT[0][highest["han"]][str(highest["fu"])]["tsumo"][0])
                    else:
                        # print(point[1])
                        resultString += "放槍者給 {} 點 \n".format(
                            POINT[1 if sitPosition == "E" else 0][highest["han"]][str(
                                highest["fu"])]["ron"])
            elif highest["han"] < 0:
                resultString += "\n".join(highest["yakus"])
                resultString += "\n-------------------------\n"
                resultString += "役滿\n"
                resultString += "{}倍役滿\n".format(0-highest["han"])
                if tsumo:
                    if sitPosition == "E":  # banker tsumo
                        resultString += "閒家一人給 {} 點\n".format(
                            16000*(0-highest["han"]))
                    else:  # normal tsumo
                        resultString += "莊家給 {} 點\n".format(
                            16000*(0-highest["han"]))
                        resultString += "閒家一人給 {} 點\n".format(
                            8000*(0-highest["han"]))
                else:
                    resultString += "放槍者給 {} 點 \n".format(
                        48000*(0-highest["han"]) if sitPosition == "E" else 32000*(0-highest["han"]))
                # b:48000/16000
                # n:32000/8000,16000
            else:
                resultString += ("無役\n")
        else:
            resultString += ("沒有胡")
        # show
        resultViewer["text"] = resultString

        # reset calculator
        start_but["state"] = tk.NORMAL
        tsumo = False
        ippatsu = False
        richi = 0
        lastCard = False
        winFirstRound = False
        akaDora = 0
        kitaDora = 0
        dora = []
        dora_lbl["text"] = ""
        uradora = []
        uradora_lbl["text"] = ""
        winType = ""
        inHand = []
        inHand_lbl["text"] = ""
        onDesk = []
        onDesk_lbl["text"] = ""
        kantsu = []
        kantsu_lbl["text"] = ""
        get = []
        get_lbl["text"] = ""
        hand = []
        yakus = []
        combination = []


def importInHand(target=None, arr=None, maxlen=0):  # 輸入手中牌
    global inputTarget
    global inputArray
    inputTarget = target
    inputArray = arr
    for i in buttons.values():
        i.setInputArray(inputArray)
        i.setInputLength(maxlen)
        i.setShow(target)
    window2.deiconify()


def doneImport():  # 完成輸入手中牌，按下enter或者關閉視窗
    global inputTarget
    global inputArray
    global TargerArray
    window2.withdraw()
    # print(inputArray)
    inputTarget = None
    inputArray = None
    for i in buttons.values():
        i.setInputArray(None)
        i.setInputLength(0)
        i.setShow(None)


def removeInHand():  # backspace
    global inputTarget
    global inputArray
    try:
        inputArray.pop()
        inputTarget["text"] = inputTarget["text"][:-1]
    except:
        print("EMPTY!")
    finally:
        pass


def clearInHand():
    inputTarget["text"] = " "
    inputArray.clear()


def checkRon(checkKey: list):  # 檢查是否和牌，回傳
    global combination
    global hand
    ron = False
    combi = []
    ronCounter = 0
    for i in checkKey:
        ron = True  # 預設值
        combi = []
        tmpH = hand.copy()  # 全部手牌
        tmpD = onDesk.copy()  # 副露部分
        tmpI = inHand.copy()  # 沒副露的部分
        if tmpI.count(i) < 2:  # 如果該牌不是雀頭
            ron = False
            continue  # 跳過
        tmpH.remove(i)  # 移除雀頭...
        tmpH.remove(i)
        tmpI.remove(i)
        tmpI.remove(i)
        combi.append([i, i])  # 並加入到組合清單中

        while len(tmpH) > 0:  # 檢查剩下的組合
            tmpH.sort()
            # TODO:111122223333型的二盃口
            # 話雖如此但好像沒有必要⋯⋯？
            if tmpH.count(tmpH[0]) >= 3 and tmpD.count(tmpH[0]) >= 3:  # 如果有刻子在副露
                a = tmpH[0]  # 設定移除目標
                for i in range(3):  # 移除刻子...
                    tmpH.remove(a)
                    tmpD.remove(a)
                combi.append([a, a, a])  # 並加入到組合清單中
            elif tmpH.count(tmpH[0]) >= 3 and tmpI.count(tmpH[0]) >= 3:  # 如果有刻子在手牌
                a = tmpH[0]  # 設定移除目標
                for i in range(3):  # 移除刻子...
                    tmpH.remove(a)
                    tmpI.remove(a)
                combi.append([a, a, a])  # 並加入到組合清單中
            elif (tmpH[0]+1 in tmpH) and (tmpH[0]+2 in tmpH) and (tmpH[0] < 40) and (tmpH[0]+1 in tmpD) and (tmpH[0]+2 in tmpD):  # 如果有順子在副露
                a = tmpH[0]  # 設定移除目標
                for i in range(3):  # 移除順子...
                    print(a+i)
                    tmpH.remove(a+i)
                    tmpD.remove(a+i)
                combi.append([a, a+1, a+2])  # 並加入到組合清單中
            elif (tmpH[0]+1 in tmpH) and (tmpH[0]+2 in tmpH) and (tmpH[0] < 40) and (tmpH[0]+1 in tmpI) and (tmpH[0]+2 in tmpI):  # 如果有順子在手牌
                a = tmpH[0]  # 設定移除目標
                for i in range(3):  # 移除順子...
                    print(a+i)
                    tmpH.remove(a+i)
                    tmpI.remove(a+i)

                combi.append([a, a+1, a+2])  # 並加入到組合清單中
            else:  # 如果沒有順也沒有刻
                ron = False  # 沒有胡（非一般型）
                break  # 跳出迴圈（當前while）
        if ron:  # 一般和
            combination.append(combi)  # 放進判斷的組合清單中
            ronCounter += 1
    return True if ronCounter > 0 else False


def checkYaku(checkType="N", combi=[]) -> dict:  # TODO: 三色同刻跟三色同順的分別，但目前看起來似乎沒問題（？
    global winType
    global dora
    global uradora
    han = 0
    fu = 0
    yakus = []
    mensenchin = False
    if len(inHand) == len(hand):  # 門清
        mensenchin = True
    # 役滿先處理，因為通常來說有役滿就不會計算普通役；定義一倍役滿為-1，依此類推

    if winFirstRound:  # 天地和
        han -= 1
        if sitPosition == "east":  # 天和，必須是莊家才有
            yakus.append("**天和**")
        else:  # 地和，必須是閒家
            yakus.append("**地和**")
    if checkType == "K":
        if hand[-1] == listen:
            # print("yakuman! kokushi jusanmenmachi!")
            han -= 2
            yakus.append("**國士無雙十三面**")
        else:
            # print("yakuman! kokushimusou!")
            han -= 1
            yakus.append("**國士無雙**")
    if hand.count(45) == 3 and hand.count(46) == 3 and hand.count(47) == 3:  # 大三元
        han -= 1
        yakus.append("**大三元**")
    if checkType == "N":
        # 四暗刻／單騎
        if mensenchin and hand.count(combi[1][0]) == 3 and hand.count(combi[2][0]) == 3 and hand.count(combi[3][0]) == 3 and hand.count(combi[4][0]) == 3:
            if listen == combi[0][0]:  # 如果聽的是雀頭->四暗單
                han -= 2
                yakus.append("**四暗刻單騎**")
            elif tsumo:
                han -= 1
                yakus.append("**四暗刻**")
    if set(hand).issubset(set(word)):  # 字一色
        han -= 1
        yakus.append("**字一色**")
    if set(hand).issubset(set([32, 33, 34, 36, 38, 46])):  # 綠一色
        han -= 1
        yakus.append("**綠一色**")
    if set([41, 42, 43, 44]).issubset(set(hand)) and winType == "N":  # 四喜
        if hand.count(41) == 3 and hand.count(42) == 3 and hand.count(43) == 3 and hand.count(44) == 3:  # 大四喜
            han -= 2
            yakus.append("**大四喜**")
        else:  # shosushi
            han -= 1
            yakus.append("**小四喜**")
    if set(hand).issubset(set(terminals[:6])):  # 清老頭
        han -= 1
        yakus.append("**清老頭**")
    if ((set(hand) == set(range(11, 20)) and hand.count(11) >= 3 and hand.count(19) >= 3) or (set(hand) == set(range(21, 30)) and hand.count(21) >= 3 and hand.count(29) >= 3) or (set(hand) == set(range(31, 40)) and hand.count(31) >= 3 and hand.count(39) >= 3)) and mensenchin:  # 純正／九蓮
        t = hand.copy()
        try:
            t.remove(listen)
        except:
            pass
        if (set(t) == set(range(11, 20)) and t.count(11) == t.count(19) == 3) or (set(t) == set(range(21, 30)) and t.count(21) == t.count(29) == 3) or (set(t) == set(range(31, 40)) and t.count(31) == t.count(39) == 3):
            han -= 2
            yakus.append("**純正九蓮寶燈**")
        else:
            han -= 1
            yakus.append("**九蓮寶燈**")
    if len(kantsu) == 4:  # 四槓子 #TODO:具體寫法須參考槓子的寫法
        han -= 1
        yakus.append("**四槓子**")
    if han < 0:  # 如果有役滿就不需要考慮其他役
        return {"yakus": yakus, "han": han, "fu": fu}

    # 一般役，用正番
    if richi != 0:  # 兩／立直
        han += richi
        yakus.append("立直" if richi == 1 else "兩立直")
    if ippatsu:  # 一發
        han += 1
        yakus.append("一發")
    if mensenchin and tsumo:  # 門清自摸
        han += 1
        yakus.append("門前清自摸")
    if len(set(hand) & set(terminals)) == 0:
        han += 1
        yakus.append("斷幺九")

    if checkType == "N":
        # pinfu, hard, if mensenchin and ((everyone is shun) and (double sided))
        if mensenchin and ((combi[1].count(combi[1][0]) == 1 and combi[2].count(combi[2][0]) == 1 and combi[4].count(combi[4][0]) == 1 and combi[3].count(combi[3][0]) == 1) and (listen == combi[1][0] or listen == combi[1][2] or listen == combi[2][0] or listen == combi[2][2] or listen == combi[3][0] or listen == combi[3][2] or listen == combi[4][0] or listen == combi[4][2])):
            han += 1
            yakus.append("平胡")

        if mensenchin and ((combi[1] == combi[2] and combi[3] != combi[4]) or (combi[2] == combi[3] and combi[1] != combi[4]) or (combi[3] == combi[4] and combi[1] != combi[2])):  # ipeko(msc only)
            han += 1
            yakus.append("一盃口")

    if (sitPosition == "E" and hand.count(41) == 3) or (sitPosition == "S" and hand.count(42) == 3) or (sitPosition == "W" and hand.count(43) == 3) or (sitPosition == "N" and hand.count(44) == 3):  # personal wind
        han += 1
        yakus.append("門風 {}".format(sitPosition))

    if (gameWind == "E" and hand.count(41) == 3) or (gameWind == "S" and hand.count(42) == 3) or (gameWind == "W" and hand.count(43) == 3) or (gameWind == "N" and hand.count(44) == 3):  # game wind
        han += 1
        yakus.append("場風 {}".format(gameWind))
    # dragons
    if hand.count(45) == 3:  # haku
        han += 1
        yakus.append("白")
    if hand.count(46) == 3:  # hatsu
        han += 1
        yakus.append("發")
    if hand.count(47) == 3:  # chuu
        han += 1
        yakus.append("中")
    if rinshan:  # rinshan
        han += 1
        yakus.append("嶺上開花")
    if chyankan:  # chyankan
        han += 1
        yakus.append("搶槓")

    if lastCard:
        han += 1
        yakus.append("海底撈月" if tsumo else "河底撈魚")

    if checkType == "7":
        han += 2
        yakus.append("七對子")

    if checkType == "N":
        if ([combi[1][0]+10, combi[1][1]+10, combi[1][2]+10] in combi and [combi[1][0]+20, combi[1][1]+20, combi[1][2]+20] in combi and combi[1][0] < 20) or ([combi[2][0]+10, combi[2][1]+10, combi[2][2]+10] in combi and [combi[2][0]+20, combi[2][1]+20, combi[2][2]+20] in combi and combi[2][0] < 20):
            if combi[1].count(combi[1][0]) == 3 or (combi[2].count(combi[2][0]) == 3 and combi[3].count(combi[3][0]) == 3):  # sandonko
                han += 2
                yakus.append("三色同刻")

            else:  # sanshoku(msc 2, not 1), hard
                han += 2 if mensenchin else 1
                yakus.append("三色同順")

        if ([11, 12, 13] in combi and [14, 15, 16] in combi and [17, 18, 19] in combi) or ([21, 22, 23] in combi and [24, 25, 26] in combi and [27, 28, 29 in combi]) or ([31, 32, 33] in combi and [34, 35, 36] in combi and [37, 38, 39] in combi):  # ittsu(msc2, not 1)
            han += 2 if mensenchin else 1
            yakus.append("一氣通貫")

        if not mensenchin and hand.count(combi[1][0]) == 3 and hand.count(combi[2][0]) == 3 and hand.count(combi[3][0]) == 3 and hand.count(combi[4][0]) == 3:  # toitoi
            han += 2
            yakus.append("對對和")

        """
        sananko type
        three kotsu done, wait for two kotsu, ron (if tsumo, will be suanko)
        three kotsu done, wait for jantou (another combi mustn't be ankotsu)
        three kotsu done, wait for shun
        two kotsu done, wait for two kotsu, tsumo (if ron, will be nothing)
        """
        # sananko, very hard, not tested thoroughly, might be buggy
        # TODO:另一種做法：在拆項的時候判斷暗刻數量。如果目前方法出現問題再行修改
        if checkType == "N":
            ankotsu = 0
            for elm in combi[1:]:
                if elm.count(elm[0]) == 3 and inHand.count(elm[0]) >= 3:
                    ankotsu += 1
            isSananko = True
            if ankotsu >= 3:
                for elm in combi[1:]:
                    # if (only 3 ankotsu) and (listen is current combination) and (current combination is kotsu) and (ron) and (not like aaaabc listen a)
                    if ankotsu == 3 and (listen in elm) and (elm.count(elm[0]) == 3) and (not tsumo) and (inHand.count(listen) != 4):
                        isSananko = False
                if isSananko:
                    han += 2
                    yakus.append("三暗刻")

    if len(kantsu) == 3:  # TODO:三槓子，具體做法還要看槓子的實作方法
        han += 2
        yakus.append("三槓子")
    # chitoi(done)

    if checkType == "N":
        if (set(combi[0]) & set(terminals) != set()) and (set(combi[1]) & set(terminals) != set()) and (set(combi[2]) & set(terminals) != set()) and (set(combi[3]) & set(terminals) != set()) and (set(combi[4]) & set(terminals) != set()) and set(hand) - set(terminals) != set():  # chanta(msc 2, not 1)
            han += 2 if mensenchin else 1
            yakus.append("混全帶幺九")

    if set(hand).issubset(set(terminals)) and checkType != "K":  # honrouto, not kokushi
        yakus.append("混老頭")
        han += 2

    if 45 in hand and 46 in hand and 47 in hand and checkType == "N":  # shousangen
        han += 2
        yakus.append("小三元")

    if set(hand).issubset(set(range(11, 20)) | set(word)) or set(hand).issubset(set(range(21, 30)) | set(word)) or set(hand).issubset(set(range(31, 40)) | set(word)):  # honitsu(msc3, not 2)
        han += 3 if mensenchin else 2
        yakus.append("混一色")

    if checkType == "N":  # 純全帶幺九
        # TODO:或許有辦法不用移除純全的
        if (set(combi[0]) & set(terminals[:6]) != set()) and (set(combi[1]) & set(terminals[:6]) != set()) and (set(combi[2]) & set(terminals[:6]) != set()) and (set(combi[3]) & set(terminals[:6]) != set()) and (set(combi[4]) & set(terminals[:6]) != set()) and set(hand) - set(terminals[:6]) != set():  # junchan(msc 3, not 2)
            if "chanta" in yakus:
                yakus.remove("混全帶幺九")
                han -= 2 if mensenchin else 1
            han += 3 if mensenchin else 2
            yakus.append("純全帶幺九")

    if checkType == "N":  # ryanpeko(msc only)
        if mensenchin and (combi[2] == combi[1] and combi[3] == combi[4]):
            yakus.append("兩盃口")
            han += 3

    if set(hand).issubset(set(range(11, 20))) or set(hand).issubset(set(range(21, 30))) or set(hand).issubset(set(range(31, 40))):  # 清一色(msc 6, not 5)
        # TODO:或許有辦法不用移除（同混全／純全）
        han += 6 if mensenchin else 5
        if "混一色" in yakus:
            yakus.remove("混一色")
            han -= 3 if mensenchin else 2
        yakus.append("清一色")

    # 計算符數的部分
    if winType == "7":  # 七對子必25符
        fu = 25
    elif winType == "N":
        fu = 20  # 一般情形最少20符

        # process here
        for elm in combi:
            if listen in elm:
                if len(elm) == 2:  # 聽雀頭的話+2符
                    fu += 2
                    break
                else:
                    if listen == elm[1] and elm.count(listen) != 3:  # 聽中洞+2符
                        fu += 2
                        break
                    elif (listen == elm[0] and elm[2] == 19) or (listen == elm[0] and elm[2] == 29) or (listen == elm[0] and elm[2] == 39) or (listen == elm[2] and elm[0] == 11) or (listen == elm[2] and elm[0] == 21) or (listen == elm[2] and elm[0] == 31):  # 聽邊張+2符
                        fu += 2
                        break
        if (sitPosition == "E" and 41 in combi[0]) or (sitPosition == "S" and 42 in combi[0]) or (sitPosition == "W" and 42 in combi[0]) or (sitPosition == "N" and 43 in combi[0]):
            # 雀頭為門風 #TODO:應該可以修更精簡
            fu += 2

        if (gameWind == "E" and 41 in combi[0]) or (gameWind == "S" and 42 in combi[0]) or (gameWind == "W" and 43 in combi[0]) or (gameWind == "N" and 44 in combi[0]):
            # 雀頭為廠風 #TODO:應該可以修更精簡
            fu += 2

        if (45 in combi[0]) or (46 in combi[0]) or (47 in combi[0]):
            # 三元牌為雀頭
            fu += 2

        if tsumo:  # 字摸加兩符
            fu += 2
        if mensenchin and not tsumo:  # 門清胡
            fu += 10
        for elm in combi[1:]:
            if elm.count(elm[0]) == 3:
                if inHand.count(elm[0]) >= 3:  # 有暗刻
                    if elm[0] in terminals:
                        if elm[0] in kantsu:
                            fu += 32  # terminal ankantsu 32 fu
                        else:
                            fu += 8  # terminal ankotsu 8 fu
                    else:
                        if elm[0] in kantsu:
                            fu += 16  # normal ankantsu 16 fu
                        else:
                            fu += 4  # normal ankotsu 4 fu
                else:  # 有明刻
                    if elm[0] in terminals:
                        if elm[0] in kantsu:
                            fu += 16  # terminal minkantsu 16 fu
                        else:
                            fu += 4  # terminal minkotsu 4 fu
                    else:
                        if elm[0] in kantsu:
                            fu += 8  # normal minkantsu 8 fu
                        else:
                            fu += 2  # normal minkotsu 2 fu
        fu = ((fu-1)//10+1)*10  # 無條件進位到十位數
    # doras
    if han != 0:
        d = 0
        ud = 0
        for i in dora:  # 寶牌
            if i in hand:
                d += hand.count(i)
        if d != 0:
            yakus.append("寶牌*{}".format(d))
        if richi:
            for i in uradora:
                if i in hand:
                    ud += hand.count(i)
            yakus.append("裏寶牌*{}".format(ud))
        if akaDora != 0:
            yakus.append("紅寶牌*{}".format(akaDora))
        if kitaDora != 0:
            yakus.append("拔北寶牌*{}".format(kitaDora))
        han += (d+ud+akaDora+kitaDora)
    else:  # no han
        yakus.append("NONE")
    return {"yakus": yakus, "han": han, "fu": fu}


# 主視窗
window = tk.Tk()
window.title('日本麻將計算機')
window.geometry('600x400+100+100')

# 麻將鍵盤——子視窗
window2 = tk.Toplevel()  # 新增子視窗
window2.title("麻將鍵盤")
window2.geometry('650x150+300+100')
window2.protocol("WM_DELETE_WINDOW", doneImport)
window2.withdraw()  # 隱藏
# window2.deiconify() # 顯示

frm1 = tk.Frame(window).place(anchor=tk.W)  # 框架

# 輸入：手中牌
lbl_0 = tk.Label(frm1, text='手中牌：')
lbl_0.grid(column=0, row=0)
inHand_lbl = tk.Label(frm1, text='', font=('Arial', 20))
inHand_lbl.grid(column=1, row=0, columnspan=10)
inHand = []
but0 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=inHand_lbl, arr=inHand, maxlen=13)).grid(column=11, row=0)

# 輸入：副露
lbl_1 = tk.Label(frm1, text='副露牌：')
lbl_1.grid(column=0, row=1)
onDesk_lbl = tk.Label(frm1, text='', font=('Arial', 20))
onDesk_lbl.grid(column=1, row=1, columnspan=10)
onDesk = []
but1 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=onDesk_lbl, arr=onDesk, maxlen=12)).grid(column=11, row=1)

# 輸入：槓
lbl_2 = tk.Label(frm1, text='槓：')
lbl_2.grid(column=0, row=2)
kantsu_lbl = tk.Label(frm1, text="", font=('Arial', 20))
kantsu_lbl.grid(column=1, row=2, columnspan=10)
kantsu = []
but2 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=kantsu_lbl, arr=kantsu, maxlen=4)).grid(column=11, row=2)

# 輸入：寶牌
lbl_3 = tk.Label(frm1, text='寶牌：')
lbl_3.grid(column=0, row=3)
dora_lbl = tk.Label(frm1, text='', font=('Arial', 20))
dora_lbl.grid(column=1, row=3, columnspan=10)
dora = []
but3 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=dora_lbl, arr=dora, maxlen=5)).grid(column=11, row=3)

# 輸入：裏寶牌
lbl_4 = tk.Label(frm1, text='裏寶牌：')
lbl_4.grid(column=0, row=4)
uradora_lbl = tk.Label(frm1, text='', font=('Arial', 20))
uradora_lbl.grid(column=1, row=4, columnspan=10)
uradora = []
but4 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=uradora_lbl, arr=uradora, maxlen=5)).grid(column=11, row=4)

# 輸入：胡的牌
lbl_6_1 = tk.Label(frm1, text="胡的牌：").grid(column=9, row=6)
get_lbl = tk.Label(frm1, font=('Arial', 20), text=" ")
get_lbl.grid(column=10, row=6)
get = []
but5 = tk.Button(window, text="輸入", command=lambda: importInHand(
    target=get_lbl, maxlen=1, arr=get)).grid(column=11, row=6)

# 選項：立直
lbl_5_0 = tk.Label(frm1, text='立直：')
lbl_5_0.grid(column=0, row=5)
_richi = tk.StringVar()
list_richi = tk.OptionMenu(frm1, _richi, "無", "立直", "兩立直")
_richi.set("無")
richi = 0
list_richi.grid(column=1, row=5)

lbl_5_2 = tk.Label(frm1, text=' ')
lbl_5_2.grid(column=2, row=5)

# 選項：門風
lbl_5_3 = tk.Label(frm1, text='門風：')
lbl_5_3.grid(column=3, row=5)
_sitpos = tk.StringVar()
list_sitpos = tk.OptionMenu(frm1, _sitpos, "東", "南", "西", "北")
list_sitpos.grid(column=4, row=5)
_sitpos.set("東")

# 選項：場風
lbl_5_5 = tk.Label(frm1, text=' ')
lbl_5_5.grid(column=5, row=5)
lbl_5_6 = tk.Label(frm1, text='場風：')
lbl_5_6.grid(column=6, row=5)
_gamewind = tk.StringVar()
list_gamewind = tk.OptionMenu(frm1, _gamewind, "東", "南", "西", "北")
list_gamewind.grid(column=7, row=5)
_gamewind.set("東")

lbl_5_8 = tk.Label(frm1, text=' ')
lbl_5_8.grid(column=8, row=5)

# 選項：和牌時機
lbl_5_9 = tk.Label(frm1, text='和牌時機：')
lbl_5_9.grid(column=9, row=5)
_winround = tk.StringVar()
list_winround = tk.OptionMenu(frm1, _winround, "其他", "第一巡", "一發", "最後一張")
list_winround.grid(column=10, row=5)
_winround.set("其他")

# 選項：拔北數量
lbl_6_6 = tk.Label(frm1, text='拔北寶牌：')
lbl_6_6.grid(column=6, row=6)
_kitadora = tk.IntVar()
list_kitadora = tk.OptionMenu(frm1, _kitadora, 0, 1, 2, 3, 4)
list_kitadora.grid(column=7, row=6)
_kitadora.set(0)

# 選項：胡的方式
_tsumo = tk.IntVar()
ron_but = tk.Radiobutton(frm1, text="榮和", variable=_tsumo, value=0)
tsumo_but = tk.Radiobutton(frm1, text="自摸", variable=_tsumo, value=1)
ron_but.grid(column=1, row=6)
tsumo_but.grid(column=3, row=6)

# 開始按鈕
start_but = tk.Button(window, text="開始計算！", command=startEvent)
start_but.place(anchor=tk.S, relx=0.5, rely=1, y=-10)

resultViewer = tk.Label(window, anchor=tk.W, text="", relief=tk.SUNKEN)
resultViewer.grid(column=1, row=7, columnspan=10, sticky=tk.E+tk.W)

# 麻將鍵盤：一般牌的按鈕
buttons = {}
for i in range(1, 5):
    for j in range(10):
        if j == 0:
            continue
        if i == 4 and j == 8:
            break
        k = int(str(i)+str(j))
        tmp = MajButton(
            window2, i, j, MAHJONG[str(i)+str(j)], int(str(i)+str(j)))
        buttons[str(i)+str(j)] = tmp

# 麻將鍵盤：enter
but_enter = tk.Button(window2, text="↲",
                      fg='black', font=('Arial', 20), command=doneImport)
but_enter['width'] = 1
but_enter['height'] = 1
but_enter.grid(column=9, row=4)

# 麻將鍵盤：backspace
but_bkspace = tk.Button(window2, text="←", fg='black',
                        font=('Arial', 20), command=removeInHand)
but_bkspace['width'] = 1
but_bkspace['height'] = 1
but_bkspace.grid(column=8, row=4)


# 麻將鍵盤：backspace
but_clear = tk.Button(window2, text="❌", fg='black',
                      font=('Arial', 20), command=clearInHand)
but_clear['width'] = 1
but_clear['height'] = 1
but_clear.grid(column=10, row=4)

# 麻將鍵盤：紅寶牌按鈕
tmp = MajButton(window2, 1, 10, MAHJONG["15"], 115, color="red")
buttons["115"] = tmp
tmp = MajButton(window2, 2, 10, MAHJONG["25"], 125, color="red")
buttons["125"] = tmp
tmp = MajButton(window2, 3, 10, MAHJONG["35"], 135, color="red")
buttons["135"] = tmp

window.mainloop()
