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
        print("超出原点坐标范围,已将编码设置为空!")
        return None,None
    xNum = math.ceil(round((X-minX),5)/gridXSize)  #x方向格子编号
    yNum = math.ceil(round((Y-minY),5)/gridYSize)   #y方向格子编号
    secondxNum = math.ceil(round((X-minX),5)/0.0002) - (xNum-1)*5
    secondyNum = math.ceil(round((Y-minY),5)/0.0002) - (yNum-1)*5
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
        #垂直X轴
        if endlevelX1 > startlevelX1  or (
                startcode[0] == endcode[0] and startlevelX2 < endlevelX2 ):
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
        #垂直Y轴

       if  endlevelY1 > startlevelY1 or (startcode[0] == endcode[0] and startlevelY2 < endlevelY2):  # and endlevelX1 < startlevelX1:
           #上方
           starty = coor[1] - 39 + 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
               starty += 0.0002
               print(completetemcode)
       else:
           starty = coor[1] - 39 - 0.0002
           # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
           while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
               completetemcode = Encode(coor[0], starty + 39)
               starty -= 0.0002
               temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
               completeLineCode.append(completetemcode)
    else:
        k = ((coor[3] - 39) - (coor[1] - 39)) / ((coor[2] - 115) - (coor[0] - 115))
        b = (coor[1] - 39) - k * (coor[0] - 115)
        if endlevelX1 > startlevelX1 and endlevelY1 == startlevelY1 or (
                startcode[0] == endcode[0] and startlevelX2 < endlevelX2 and startlevelY2 == endlevelY2):
            # 终点在起点的正右侧或者在同一大区域，但是终点小区域仍在起点小区域正右侧
            startx = coor[0] - 115 + 0.0002  # 与垂直X轴的直线 X = startx
            # starty = startlevelY1*0.001 #与y交点
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                starty = k * startx + b
                completetemcode = Encode(startx + 115, starty + 39)
                startx += 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
        elif endlevelX1 < startlevelX1 and endlevelY1 == startlevelY1 or (
                startcode[0] == endcode[0] and startlevelX2 > endlevelX2 and startlevelY2 == endlevelY2):
            # 终点在起点的正左侧
            startx = coor[0] - 115 - 0.0002  # 与垂直X轴的直线 X = startx
            # starty = startlevelY1*0.001 #与y交点
            while not (endlevelX1 == temlevelX1 and endlevelX2 == temlevelX2):
                starty = k * startx + b
                completetemcode = Encode(startx + 115, starty + 39 )
                startx -= 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
        # elif endlevelX1 == startlevelX1 and endlevelY1 > startlevelY1:
        #     # 终点在起点的正上方
        #     starty = (startlevelY1) * 0.001  # 与垂直y轴的直线 Y= starty
        #     while endcode[1] != temcode:
        #         startx = (starty - b) / k
        #         completetemcode = GetGridCode(startx + 115, starty + 39 + 0.00005)
        #         starty += 0.0002
        #         temcode = completetemcode[1]
        # elif endlevelX1 == startlevelX1 and endlevelY1 < startlevelY1:
        #     # 终点在起点的正下方
        #     starty = (startlevelY1-1) * 0.001  # 与垂直y轴的直线 Y= starty
        #     while endcode[1] != temcode:
        #         startx = (starty - b) / k
        #         completetemcode = GetGridCode(startx + 115, starty + 39 - 0.00005)
        #         starty -= 0.0002
        #         temcode = completetemcode[1]
        elif endlevelY1 > startlevelY1 or (
                startcode[0] == endcode[0] and startlevelY2 < endlevelY2):  # and endlevelX1 < startlevelX1:
            # 终点在起点上方
            starty = coor[1] - 39 + 0.0002
            # temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(startcode[1])
            while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
                startx = (starty - b) / k
                completetemcode = Encode(startx + 115, starty + 39)
                starty += 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)
        elif endlevelY1 < startlevelY1 or (startcode[0] == endcode[0] and startlevelY2 > endlevelY2):
            # 终点在起点下方
            # starty = (startlevelY1 - 1) * 0.001 + startlevelY2 * 0.0002'
            startx = coor[0]-115-0.0002
            #starty = coor[1] - 39 - 0.0002
            while not (endlevelY1 == temlevelY1 and endlevelY2 == temlevelY2):
                #startx = (starty - b) / k
                starty = k*(startx) + b
                completetemcode = Encode(startx + 115, starty + 39)
                #starty -= 0.0002
                startx -= 0.0002
                temlevelX1, temlevelY1, temlevelX2, temlevelY2 = Decode(completetemcode[1])
                completeLineCode.append(completetemcode)

    completeLineCode.append(endcode)
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
        return GetDirectneighbor(startcode,endcode,[startX,startY,endX,endY])


x = 116.4375358
y = 39.7206477

print(Encode(116.44491,39.723963))
# print(Neighbor(116.4330469,39.7210465))
print(GetGridCodes(116.4474821,39.7240476,116.4436357,39.7236821))
# prelist = GetGridCodes(116.4330469,39.7218465,116.4338469,39.7218465)
# li = list(set(prelist))
# li.sort(key=prelist.index)
# print(prelist)
# print(Common_Functions.del_adjacent(prelist))
# print(Encode(116.4248612,39.7214571))
#print(GetGridCodes(116.414737,39.7138631,116.414737,39.7136468))
#print(Neighbor(0,0))
#print(Encode(116.414737,39.7138631))
#print(Neighbor(116.414737,39.7138631))




