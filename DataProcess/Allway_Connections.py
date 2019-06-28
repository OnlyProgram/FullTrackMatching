# -*- coding: utf-8 -*-
# @Time    : 2019/6/25 19:14
# @Author  : WHS
# @File    : Allway_Connections.py
# @Software: PyCharm
from itertools import permutations
import json
from RoadMatch import Common_Functions,MapNavigation
def Getway_startendnode_coordi(wayid,flag = 0):
    """
    得到路段的网格编号
    flag=0 代表获取路段起点的编号
    flag = 1代表获取路段末尾点的网格编号
    :return:
    """
    wayids = MapNavigation.Get_way_NodesSequenceId(wayid)
    if wayids:
        if flag==0:
            processnodeid = wayids[0][0]
        else:
            processnodeid = wayids[-1][0]
        coor = MapNavigation.Get_Coordinate(processnodeid)
        return coor
    else:
        return [0,0]
def AllwayConn(waysjsonpath):
    """
    对左右的路段进行连通性判断
    permutations(Allwayset,2) 二二组合，（A,B,C）->AB AC BA BC CA CB
    :param waysjsonpath:所有路段json文件路径
    :return:
    """
    AllwaysLists = []
    with open(waysjsonpath, 'r') as file:
        dic = json.loads(file.read())
    for key in dic.keys():
        AllwaysLists.append(key)
    Allwaysset = set(AllwaysLists)
    for twowaytuple in permutations(Allwaysset,2):
        try:
            print(f"正在查看路段:{twowaytuple[0]}与路段:{twowaytuple[1]}的连通性......")
            way1_x, way1_y = Getway_startendnode_coordi(twowaytuple[0])  # 路段1的起点坐标
            way2_x, way2_y = Getway_startendnode_coordi(twowaytuple[1])  # 路段2的起始坐标
            print(way1_x, way1_y, way2_x, way2_y)
            if way1_x != 0 and way1_y != 0 and way2_x != 0 and way2_y != 0:
                waydis = Common_Functions.haversine(way1_x, way1_y, way2_x, way2_y)
                print(waydis)
                if waydis < 3:
                    connectroute = Common_Functions.InquireConn(twowaytuple[0], twowaytuple[1], "connects")  # 先查表
                    # connectroute = -1
                    if connectroute != 0 and connectroute != 1:  # 表中没有记录 再用简易导航
                        connectroute = MapNavigation.waytoway(twowaytuple[0], twowaytuple[1])  # 为列表
                        if connectroute:
                            print(f"路段{twowaytuple[0]}---->{twowaytuple[1]}的路线：{connectroute}")
                        else:
                            print(f"路段{twowaytuple[0]}不能到达路段{twowaytuple[1]}")
                    else:
                        print("数据库中已存在，跳过")
                else:
                    pass
        except Exception as e:
            print(e)

import time
start = time.time()
AllwayConn('C:\\Users\Administrator\Desktop\wayslist.json')
#way1_x, way1_y = Getway_startendnode_coordi(25339174)  # 路段1的起点坐标
#way2_x, way2_y = Getway_startendnode_coordi(127464448)  # 路段2的起始坐标
#print(way1_x,way1_y,way2_x, way2_y)
# waydis = Common_Functions.haversine(way1_x,way1_y,way2_x, way2_y)
# print(waydis)
# print(MapNavigation.waytoway(162586486,4231223))
print(time.time()-start)
