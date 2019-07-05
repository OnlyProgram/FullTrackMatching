# -*- coding: utf-8 -*-
# @Time    : 2019/6/26 19:44
# @Author  : WHS
# @File    : GridCode.py
# @Software: PyCharm
"""
自行实现编码
X Y 方向 xNum和yNum都必须是四个字符串长度，不足的在前缀以0补充
以115,39为原点坐标，精度为0.001，即大约为边长为100方格
"""
import math
from RoadMatch import Common_Functions
def Encode(X,Y,minX=115,minY=39,gridXSize=0.001,gridYSize=0.001):
    """
    通过传入地图起始点，待编码坐标，编码的X和Y方向精确度，获取网格编码字符串
    :param minX: 地图起始点X坐标
    :param minY: 地图起始点Y坐标
    :param X:
    :param Y:
    :param gridXSize: X方向精度。
    :param gridYSize: Y方向精度。
    :return:
    """
    if (X < minX or Y < minY):
        print("小于原点坐标,已将编码设置为空!")
        return None,None


    xNum = math.ceil(round((X-minX)/gridXSize,7)) #x方向格子编号,向上取整
    yNum = math.ceil(round((Y-minY)/gridYSize,7))   #y方向格子编号
    if (10000*X - 10000*minX)%10 == 0.0:
        xNum += 1
        secondxNum = 1
    else:
        secondxNum = math.ceil(round(X - minX - (xNum - 1) * gridXSize, 7) / 0.0002)
        if (10000*X - 10000*minX)%2 == 0.0:
            secondxNum += 1
    if (10000*Y - 10000*minY)%10  == 0.0:
        yNum += 1
        secondyNum = 1
    else:
        secondyNum = math.ceil(round(Y - minY - (yNum - 1) * gridXSize, 7) / 0.0002)
        if (10000 * Y - 10000 * minY) % 2 == 0.0:
            secondyNum += 1


    #secondxNum = math.ceil(round((X-minX),5)/0.0002) - (xNum-1)*5
    #secondyNum = math.ceil(round((Y-minY),5)/0.0002) - (yNum-1)*5
    FirstCode = CreateLongCode(xNum, yNum)
    code = FirstCode + str(secondxNum) +str(secondyNum)
    return FirstCode,code  #字符串
def CreateLongCode(xNum:int, yNum:int,XLen=4,YLen=4):
    sx = str(xNum)
    sy = str(yNum)
    for i in range(len(sx),XLen):
        sx="0"+sx
    for i in range(len(sy),YLen):
        sy="0"+sy
    scode = sx + sy
    #code = int(scode)
    return scode
def Decode(code,minX=115,minY=39,gridXSize=0.001,gridYSize=0.001):
    #code 为完整code 如1422072223
    level1X = int(code[0:4])
    level1Y = int(code[4:8])
    level2X = int(code[8:9])
    level2Y = int(code[9:10])
    return level1X,level1Y,level2X,level2Y
def Coordinate_Decode(code,minX=115,minY=39,gridXSize=0.001,gridYSize=0.001):
    """
    根据编码返回坐标
    :param code:
    :return:
    """
    codes = Decode(str(code))
    lon = (codes[0]-1)*gridXSize + minX + (codes[2]-1)*0.0002 + 0.0001  #取格子中心
    lat = (codes[1]-1)*gridYSize + minY + (codes[3]-1)*0.0002 + 0.0001
    return lon,lat
def StrDecode(code,minX=115,minY=39,gridXSize=0.001,gridYSize=0.001):
    #code 为完整code 如1422072223
    level1X = code[0:4]
    level1Y = code[4:8]
    level2X = code[8:9]
    level2Y = code[9:10]
    return level1X, level1Y, level2X, level2Y
def Neighbor(x,y):
    """
    查找相邻的八个区域
    :param code:
    :return:
    """
    neighbors = []
    for i in range(1,-2,-1):
        for j in range(-1,2):
            neighbors.append(Encode(x+j*0.0002, y + 0.0002*i))
    return neighbors



def GetDirectneighbor(startcode,endcode,coor):
    """
    获取路段的完整网格编号,
    :param startcode: 起始区域
    :param endcode: 终点区域
    :return:
    """
    startlevelX1,startlevelY1,startlevelX2,startlevelY2 = Decode(startcode[1])
    endlevelX1,endlevelY1,endlevelX2,endlevelY2 = Decode(endcode[1])
    completeLineCode = [startcode]  #完整的相邻坐标点路段编号
    temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
    if coor[3]-coor[1]==0:
        #垂直Y轴
        if endlevelX1 > startlevelX1  or (startcode[0] == endcode[0] and startlevelX2 < endlevelX2 ):
            startx = coor[0] - 115 + 0.0002  # 与垂直X轴的直线 X = startx
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                completetemcode = Encode(startx + 115, coor[3])
                startx += 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
        else:
            startx = coor[0] - 115 - 0.0002  # 与垂直X轴的直线 X = startx
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                completetemcode = Encode(startx + 115, coor[3])
                startx -= 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
    elif coor[2]-coor[0]==0:
        #垂直X

       if  endlevelY1 > startlevelY1 or (startcode[0] == endcode[0] and startlevelY2 < endlevelY2):  # and endlevelX1 < startlevelX1:
           #上方
           starty = coor[1] - 39 + 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
               starty += 0.0002
       else:
           starty = coor[1] - 39 - 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               starty -= 0.0002
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
    else:
        k = (coor[3] - coor[1])/ (coor[2] - coor[0])
        b = coor[1] - k * coor[0]
        #判断右上
        if endlevelX1 > startlevelX1 and endlevelY1 > startlevelY1 or (endlevelX1 == startlevelX1 and endlevelY1 >= startlevelY1
                 and startlevelX2 <= endlevelX2 ) or (endlevelX1 >= startlevelX1 and endlevelY1 == startlevelY1
                 and startlevelX2 <= endlevelX2 ):
            startx = coor[0] + 0.0002  # 与垂直X轴的直线 X = startx

            #print("终点在起始点右上")
            while startx < coor[2]:
                completetemcode1 = Encode(startx, (k * startx + b))
                startx += 0.0002
                completeLineCode.append(completetemcode1)
                # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])
            starty = coor[1] + 0.0002
            while starty < coor[3] :
                completetemcode2 = Encode(((starty - b) / k), starty)
                starty += 0.0002
                completeLineCode.append(completetemcode2)
        #判断左上
        elif endlevelX1 < startlevelX1 and endlevelY1 > startlevelY1 or (endlevelX1 == startlevelX1 and endlevelY1 >= startlevelY1
                  ) or (endlevelX1 <= startlevelX1 and endlevelY1 == startlevelY1
                  ):
            startx = coor[0] - 0.0002  # 与垂直X轴的直线 X = startx
            starty = coor[1] + 0.0002
            #print("终点在起始点左上")
            while startx > coor[2] :
                completetemcode1 = Encode(startx , (k * startx + b))
                startx -= 0.0002
                completeLineCode.append(completetemcode1)
                # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])

            while starty < coor[3]:
                completetemcode2 = Encode(((starty - b) / k), starty)
                starty += 0.0002
                completeLineCode.append(completetemcode2)
        #判断左下
        elif endlevelX1 < startlevelX1 and endlevelY1 < startlevelY1 or (
                endlevelX1 == startlevelX1 and endlevelY1 <= startlevelY1
                and startlevelX2 > endlevelX2) or (endlevelX1 < startlevelX1 and endlevelY1 == startlevelY1
                                                   and startlevelY2 <= endlevelY2):
            #print("终点在起始点左下")
            startx = coor[0] - 0.0002
            starty = coor[1] - 0.0002
            while startx > coor[2]:
                completetemcode1 = Encode(startx, (k * startx + b))
                startx -= 0.0002
                completeLineCode.append(completetemcode1)
                #temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])

            while starty > coor[3]:
                completetemcode2 = Encode(((starty - b) / k) , starty)
                starty -= 0.0002
                completeLineCode.append(completetemcode2)

        # 判断右下
        elif endlevelX1 > startlevelX1 and endlevelY1 < startlevelY1 or (
                endlevelX1 == startlevelX1 and endlevelY1 <= startlevelY1
                and startlevelX2 <= endlevelX2) or (endlevelX1 >= startlevelX1 and endlevelY1 == startlevelY1
                                                    and endlevelY2>=startlevelY2):
            startx = coor[0]  + 0.0002  # 与垂直X轴的直线 X = startx
            starty = coor[1] - 0.0002
            #print("终点在起始点右下")
            while startx < coor[2]:
                completetemcode1 = Encode(startx , (k * startx + b))
                startx += 0.0002
                completeLineCode.append(completetemcode1)
                # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])

            while starty > coor[3] :
                completetemcode2 = Encode(((starty - b) / k) , starty)
                starty -= 0.0002
                completeLineCode.append(completetemcode2)
    completeLineCode.append(endcode)
    return completeLineCode

def Second_strategyGetDirectneighbor(startcode,endcode,coor):
    """
    获取路段的完整网格编号,
    :param startcode: 起始区域
    :param endcode: 终点区域
    :return:
    """
    startlevelX1,startlevelY1,startlevelX2,startlevelY2 = Decode(startcode[1])
    endlevelX1,endlevelY1,endlevelX2,endlevelY2 = Decode(endcode[1])
    completeLineCode = [startcode]  #完整的相邻坐标点路段编号
    temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
    if coor[3]-coor[1]==0:
        #垂直Y轴
        if endlevelX1 > startlevelX1  or (startcode[0] == endcode[0] and startlevelX2 < endlevelX2 ):
            startx = coor[0] - 115 + 0.0002  # 与垂直X轴的直线 X = startx
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                completetemcode = Encode(startx + 115, coor[3])
                startx += 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
        else:
            startx = coor[0] - 115 - 0.0002  # 与垂直X轴的直线 X = startx
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                completetemcode = Encode(startx + 115, coor[3])
                startx -= 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
    elif coor[2]-coor[0]==0:
        #垂直X

       if  endlevelY1 > startlevelY1 or (startcode[0] == endcode[0] and startlevelY2 < endlevelY2):  # and endlevelX1 < startlevelX1:
           #上方
           starty = coor[1] - 39 + 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
               starty += 0.0002
       else:
           starty = coor[1] - 39 - 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               starty -= 0.0002
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
    else:
        k = (coor[3] - coor[1])/ (coor[2] - coor[0])
        b = coor[1] - k * coor[0]
        #判断右上
        if endlevelX1 > startlevelX1 and endlevelY1 > startlevelY1 or (endlevelX1 == startlevelX1 and endlevelY1 >= startlevelY1
                 and startlevelX2 <= endlevelX2 ) or (endlevelX1 >= startlevelX1 and endlevelY1 == startlevelY1
                 and startlevelX2 <= endlevelX2 ):
            startx = coor[0] + 0.0002  # 与垂直X轴的直线 X = startx
            starty = coor[1] + 0.0002
            while(startx < coor[2] or starty < coor[3]):
                #print("终点在起始点右上")
                if startx < coor[2]:
                    completetemcode1 = Encode(startx, (k * startx + b))
                    startx += 0.0002
                    completeLineCode.append(completetemcode1)
                if starty < coor[3]:
                    completetemcode2 = Encode(((starty - b) / k), starty)
                    starty += 0.0002
                    completeLineCode.append(completetemcode2)

        #判断左上
        elif endlevelX1 < startlevelX1 and endlevelY1 > startlevelY1 or (endlevelX1 == startlevelX1 and endlevelY1 >= startlevelY1
                  ) or (endlevelX1 <= startlevelX1 and endlevelY1 == startlevelY1
                  ):
            startx = coor[0] - 0.0002  # 与垂直X轴的直线 X = startx
            starty = coor[1] + 0.0002
            #print("终点在起始点左上")
            while (startx > coor[2] or starty < coor[3]):
                if startx > coor[2]:
                    completetemcode1 = Encode(startx, (k * startx + b))
                    startx -= 0.0002
                    completeLineCode.append(completetemcode1)
                if starty < coor[3]:
                    completetemcode2 = Encode(((starty - b) / k), starty)
                    starty += 0.0002
                    completeLineCode.append(completetemcode2)
        #判断左下
        elif endlevelX1 < startlevelX1 and endlevelY1 < startlevelY1 or(endlevelX1 == startlevelX1 and endlevelY1 <= startlevelY1
        and startlevelX2>endlevelX2) or (endlevelX1 < startlevelX1 and endlevelY1 == startlevelY1
        and startlevelY2<=endlevelY2):
            #print("终点在起始点左下")
            startx = coor[0] - 0.0002
            starty = coor[1] - 0.0002
            while (startx > coor[2] or starty > coor[3]):
                if startx > coor[2]:
                    completetemcode1 = Encode(startx, (k * startx + b))
                    startx -= 0.0002
                    completeLineCode.append(completetemcode1)
                #temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])
                if starty > coor[3]:
                    completetemcode2 = Encode(((starty - b) / k) , starty)
                    starty -= 0.0002
                    completeLineCode.append(completetemcode2)

        # 判断右下
        elif endlevelX1 > startlevelX1 and endlevelY1 < startlevelY1 or (endlevelX1 == startlevelX1 and endlevelY1 <= startlevelY1
        and startlevelX2<=endlevelX2) or (endlevelX1 >= startlevelX1 and endlevelY1 == startlevelY1
        and endlevelY2>=startlevelY2) :
            startx = coor[0]  + 0.0002  # 与垂直X轴的直线 X = startx
            starty = coor[1] - 0.0002
            #print("终点在起始点右下")
            while (startx < coor[2] or starty > coor[3] ):
                if startx < coor[2]:
                    completetemcode1 = Encode(startx , (k * startx + b))
                    startx += 0.0002
                    completeLineCode.append(completetemcode1)
                # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode1[1])
                if starty > coor[3]:
                    completetemcode2 = Encode(((starty - b) / k) , starty)
                    starty -= 0.0002
                    completeLineCode.append(completetemcode2)
    completeLineCode.append(endcode)
    return completeLineCode
def GetCompletewayCodes(startcode,endcode,coor):
    """
    获取路段的完整网格编号
    :param startcode: 起始区域
    :param endcode: 终点区域
    :return:
    """
    startlevelX1,startlevelY1,startlevelX2,startlevelY2 = Decode(startcode[1])
    endlevelX1,endlevelY1,endlevelX2,endlevelY2 = Decode(endcode[1])
    completeLineCode = [startcode]  #完整的相邻坐标点路段编号

    temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
    if coor[3]-coor[1]==0:
        #垂直Y轴
        if coor[0] < coor[2]:
            startx = coor[0] + 0.0002  # 与垂直X轴的直线 X = startx
            while (startx<= coor[2]):
                completetemcode = Encode(startx, coor[3])
                startx += 0.0002
                completeLineCode.append(completetemcode)
        else:
            startx = coor[0] - 0.0002  # 与垂直X轴的直线 X = startx
            while (startx >= coor[2]):
                completetemcode = Encode(startx, coor[3])
                startx -= 0.0002
                completeLineCode.append(completetemcode)
    elif coor[2]-coor[0]==0:
        #垂直X

       if  coor[1] < coor[3]:
           #上方
           starty = coor[1]  + 0.0002
           while starty <= coor[3]:
               completetemcode = Encode(coor[0], starty)
               completeLineCode.append(completetemcode)
               starty += 0.0002
       else:
           #下方
           starty = coor[1] - 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while starty >= coor[3]:
               completetemcode = Encode(coor[0], starty)
               starty -= 0.0002
               completeLineCode.append(completetemcode)
    else:
        k = (coor[3] - coor[1])/ (coor[2] - coor[0])
        b = coor[1] - k * coor[0]
        codedic = {}
        newlist = []
        #判断右上
        if coor[0] < coor[2] and coor[1] < coor[3]:
            #processx = coor[0] + 0.0002  # 与垂直X轴的直线 X = startx
            #processy = coor[1] + 0.0002
            processx = round((temlevelX1-1)*0.001 + 115 + temlevelX2*0.0002,7)
            processy = round((temlevelY1 - 1) * 0.001 + 39 + temlevelY2 * 0.0002,7)
            #print("终点在起始点右上")


            """
            while(processx < coor[2] or processy < coor[3]):
                completetemcode1,completetemcode2 = None,None
                if processx < coor[2]:
                    completetemcode1 = Encode(processx, (k * processx + b))
                    print(processx, (k * processx + b),completetemcode1)
                    if completetemcode1!=startcode and completetemcode1!= endcode:
                        if completetemcode1 in codedic:
                            if processx < codedic[completetemcode1]:
                                codedic[completetemcode1] = processx
                        else:
                            codedic[completetemcode1] = processx
                    processx =round(0.0002 + processx,7)

                if processy < coor[3]:
                    completetemcode2 = Encode(((processy - b) / k), processy)
                    print(((processy - b) / k), processy,completetemcode2)
                    if completetemcode2!=startcode and completetemcode2!= endcode:
                        if completetemcode2 in codedic:
                            if ((processy - b) / k) < codedic[completetemcode1]:
                                codedic[completetemcode2] = ((processy - b) / k)

                        else:
                            codedic[completetemcode2] = ((processy - b) / k)
                    processy = round(processy+0.0002,7)
            newlist = sorted(codedic.items(), key=lambda x: x[1], reverse=False)
            """
            candidatex = set()
            while (processx < coor[2] or processy < coor[3]):
                if processx < coor[2]:
                    candidatex.add(processx)
                    processx = round(processx + 0.0002, 7)
                if processy < coor[3]:
                    candidatex.add(((processy - b) / k))
                    processy = round(processy + 0.0002, 7)
            newset = sorted(candidatex, reverse=False)  # 降序
            #print(f"newset:{newset}")
            for index in range(1, len(newset)):
                midx = (newset[index] + newset[index - 1]) / 2
                tempcode = Encode(midx, (k * midx + b))
                if tempcode != startcode and tempcode != endcode:
                    completeLineCode.append(tempcode)
            completeLineCode.append(endcode)
            #print(len(completeLineCode))
            return completeLineCode
            #判断左上
        elif coor[0] > coor[2] and coor[1] < coor[3]:
            processx = round((temlevelX1 - 1) * 0.001 + 115 + (temlevelX2-1) * 0.0002, 7)
            processy = round((temlevelY1 - 1) * 0.001 + 39 + temlevelY2 * 0.0002, 7)
            #print("终点在起始点左上")
            candidatex = set()
            while (processx > coor[2] or processy < coor[3]):
                if processx > coor[2]:
                    candidatex.add(processx)
                    processx = round(processx-0.0002, 7)
                if processy < coor[3]:
                    candidatex.add(((processy - b) / k))
                    processy = round(processy + 0.0002, 7)
            newset = sorted(candidatex,reverse=True)  # 降序
            #print(f"newset:{newset}")
            for index in range(1, len(newset)):
                midx = (newset[index] + newset[index-1])/2
                tempcode = Encode(midx, (k * midx + b))
                if tempcode != startcode and tempcode != endcode:
                    completeLineCode.append(tempcode)
            completeLineCode.append(endcode)
            #print(len(completeLineCode))
            return completeLineCode

        #判断左下
        elif coor[0] > coor[2] and coor[1] > coor[3]:
            #print("终点在起始点左下")
            processx = round((temlevelX1 - 1) * 0.001 + 115 + (temlevelX2 - 1) * 0.0002, 7)
            processy = round((temlevelY1 - 1) * 0.001 + 39 + (temlevelY2-1)* 0.0002, 7)
            candidatex = set()
            while (processx > coor[2] or processy > coor[3]):
                if processx > coor[2]:
                    candidatex.add(processx)
                    processx = round(processx - 0.0002, 7)
                if processy > coor[3]:
                    candidatex.add(((processy - b) / k))
                    processy = round(processy - 0.0002, 7)
            newset = sorted(candidatex, reverse=True)  # 降序
            #print(f"newset:{newset}")
            for index in range(1, len(newset)):
                midx = (newset[index] + newset[index - 1]) / 2
                tempcode = Encode(midx, (k * midx + b))
                if tempcode != startcode and tempcode != endcode:
                    completeLineCode.append(tempcode)
            completeLineCode.append(endcode)
            #print(len(completeLineCode))
            return completeLineCode

        # 判断右下
        elif coor[0] < coor[2] and coor[1] > coor[3] :

            processx = round((temlevelX1-1)*0.001 + 115 + temlevelX2*0.0002,7)
            processy = round((temlevelY1 - 1) * 0.001 + 39 + (temlevelY2 - 1) * 0.0002, 7)
            #print("终点在起始点右下")
            candidatex = set()
            while (processx < coor[2] or processy > coor[3]):
                if processx < coor[2]:
                    candidatex.add(processx)
                    processx = round(processx + 0.0002, 7)
                if processy > coor[3]:
                    candidatex.add(((processy - b) / k))
                    processy = round(processy - 0.0002, 7)
            newset = sorted(candidatex, reverse=False)  #升序
            #print(f"newset:{newset}")
            for index in range(1, len(newset)):
                midx = (newset[index] + newset[index - 1]) / 2
                tempcode = Encode(midx, (k * midx + b))
                if tempcode != startcode and tempcode != endcode:
                    completeLineCode.append(tempcode)
            completeLineCode.append(endcode)
            #print(len(completeLineCode))
            return completeLineCode

        #print(codedic)
        #print(newlist)
        #print(len(newlist))
    return completeLineCode
def GetGridCodes(startX,startY,endX,endY):
    """
    通过传入地图起始点，待编码坐标，编码的X和Y方向精确度，获取网格编码字符串
    :param minX: 地图起始点X坐标
    :param minY: 地图起始点Y坐标
    :param X:
    :param Y:
    :param gridXSize: X方向精度。
    :param gridYSize: Y方向精度。
    :return:
    """
    startcode= Encode(startX,startY)
    endcode = Encode(endX,endY)
    startlevelX1, startlevelY1, startlevelX2, startlevelY2 = Decode(startcode[1])
    endlevelX1, endlevelY1, endlevelX2, endlevelY2 = Decode(endcode[1])
    if startcode==endcode:
        return [startcode]
    elif startcode[0]==endcode[0] and (abs(startlevelX2-endlevelX2 )<=1 and abs(startlevelY2 - endlevelY2)<=1):
        return [startcode,endcode]
    else:
        #return GetDirectneighbor(startcode,endcode,[startX,startY,endX,endY])
        #return Second_strategyGetDirectneighbor(startcode, endcode, [startX, startY, endX, endY])
        return GetCompletewayCodes(startcode, endcode, [startX, startY, endX, endY])





coor = 116.4414549,39.721794,116.4420899,39.7224579
k = (coor[3] - coor[1]) / (coor[2] - coor[0])
b = coor[1] - k * coor[0]

# print(Encode(116.4414549,39.721794))
# print(Encode(116.4420899,39.7224579))
# print(GetGridCodes(116.4414549,39.721794,116.4420899,39.7224579))
# print(GetGridCodes(116.5756783,39.7414518,116.5915491,39.7314362))
# print(GetGridCodes(116.3965131,39.7195548,116.3936264,39.7196038))
# print(Encode(116.395046,39.719625))
#print(GetGridCodes(116.4420704,39.7163478,116.4419127,39.7168835))

