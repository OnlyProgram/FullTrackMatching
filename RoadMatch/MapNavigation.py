# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 15:32
# @Author  : WHS
# @File    : MapNavigation.py
# @Software: PyCharm
"""
实现导航功能（考虑了方向），从一路段到另一路段是否互通，注意方向，示例：210697572,403874396，
虽然这两个路段能通过318323104连接，但是通过方向所以路段210697572不能到达403874396

******需要多个路口检验**********
"""
import pymysql
from itertools import combinations
import os
import sys
import copy,math
from RoadMatch import Common_Functions
def Get_key_by_value(dic, value):
    for key in dic.keys():
        if value in dic[key]:
            return key
    return None
def Getway_start_node(wayid):
    """
    得到路段的起点坐标
    flag=0 代表获取路段起点的编号
    flag = 1代表获取路段末尾点的网格编号
    :return:
    """
    wayids = Get_way_NodeID(wayid)
    if wayids:
        processnodeid = wayids[0]
        return processnodeid
    else:
        return False
def TwoPoints_distance(coor1,coor2):
    return math.sqrt((coor1[0]-coor2[0])**2 +(coor1[1]-coor2[1])**2)
def twoway_distance(wayid1,wayid2):
    """
    计算wayid1的起点->wayid2起点之间的距离
    :param wayid1:
    :param wayid2:
    :return:
    """
    node1 = Getway_start_node(wayid1)
    node2 = Getway_start_node(wayid2)
    Coordinate1 = Get_Coordinate(node1)
    Coordinate2 = Get_Coordinate(node2)
    return TwoPoints_distance(Coordinate1,Coordinate2)
def Get_Coordinate(node_id):
    """
    根据node_id查坐标
    :param node_id:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT Lon,Lat FROM nodes WHERE nodes.Node_id={}'.format(node_id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
def Get_way_NodeID(way_id):
    """
    根据way_id得出此路段node
    :param way_id:
    :return: node列表
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT ways_nodes.node_id FROM ways_nodes WHERE way_id = {}'.format(way_id)
    way_nodes_list = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()   #元组
        for row in result:
            way_nodes_list.append(row[0])
        return way_nodes_list
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
def TwoWay_intersection(wayid1, wayid2):
    """
    判断两个way是否有交集
    :param wayid1:
    :param wayid2:
    :return: 返回交叉点

    """
    if wayid1==wayid2:
        print("两条路段相同，如果想判断两个路段是否有交点，请输入两个不同的wayid")
        return None
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    SQL = """(SELECT a.NodeID FROM
            (SELECT * FROM inflectionpoint WHERE inflectionpoint.WayID={}) as a,
            (SELECT * FROM inflectionpoint WHERE inflectionpoint.WayID={}) as b
            WHERE a.NodeID = b.NodeID)""".format(wayid1, wayid2)
    cursor.execute(SQL)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if result:
        # 有交集
        return result
    else:
        return None
def Find_inflectionpoint(way):
    """
    找路段way的所有拐点
    :param way: 路段的编号
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    SQL = """(SELECT inflectionpoint.NodeID FROM
            inflectionpoint
            WHERE inflectionpoint.WayID = {})""".format(way)
    cursor.execute(SQL)
    point_list = []
    result = cursor.fetchall()
    for row in result:
        point_list.append(row[0])
    cursor.close()
    connection.close()
    return point_list
def Find_way_By_inflectionpoint(node):
    """
    根据拐点找出其所在的way
    :param node:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    SQL = """(SELECT inflectionpoint.WayID FROM
                inflectionpoint
                WHERE inflectionpoint.NodeID = {})""".format(node)
    cursor.execute(SQL)
    way_list = []
    result = cursor.fetchall()
    for row in result:
        way_list.append(row[0])
    cursor.close()
    connection.close()
    return way_list
def Get_way_NodesSequenceId(way_id):
    """
    根据way_id得出此路段node sequenceid
    :param way_id:
    :return: 饭后node列表
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE way_id = {}'.format(way_id)
    way_nodes_list = []
    try:
        cursor.execute(sql)
        result = cursor.fetchall()   #元组
        for row in result:
            way_nodes_list.append([row[0],row[1]])
        return way_nodes_list
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
class myException(Exception):
    def __init__(self,error):
        self.error = error
    def __str__(self,*args,**kwargs):
        return self.error
def JudgeLines(slist:list):
    """
    判断连通性，传入的路段都有交点 这部分主要判断方向,至少传入三个路段
    注意  如果只传入两个路段，默认判别为不能通行
    :param slist: 路段列表
    :return:
    """

    try:
        listlen = len(slist)
        if listlen <= 2:
            raise myException("自定义异常>>>{}函数连通性判断，传入的路线列表中要至少含有三个路段！！".format(sys._getframe().f_code.co_name))
        First_intersection_sequenceId = None
        Second_intersection_sequenceId = None

        for index in range(listlen):
            if index == listlen - 2:
                break
            if slist[index]!=slist[index + 1] and slist[index + 1]!=slist[index + 2]:
                #相邻三个路段均不相同
                midway_oneway_flag = Getway_Direction(slist[index + 1])  # 标记中间路段是否为单向
                if JudgeTwoWay(slist[index], slist[index + 1]):
                    pass
                else:
                    return False
                if JudgeTwoWay(slist[index+1], slist[index + 2]):
                    pass
                else:
                    return False
                if midway_oneway_flag==0:  #中间路段为双向，以上已经判断相邻的两个路段能走通
                    return True
                First_intersection = TwoWay_intersection(slist[index],slist[index + 1])  # 注意First_intersection 为嵌套元组 ，如((320533913,),)
                Second_intersection = TwoWay_intersection(slist[index + 1], slist[index + 2])
                # print("{}与{}交点为{} {}与{}交点为{}".format(slist[index],slist[index+1],First_intersection,slist[index+1],slist[index+2],Second_intersection))
                Midwaylist = Get_way_NodesSequenceId(slist[index + 1])
                for sub in Midwaylist:
                    if First_intersection[0][0] == sub[0]:
                        First_intersection_sequenceId = sub[1]  # 第一个交点的sequenceId
                for sub in Midwaylist:
                    if Second_intersection[0][0] == sub[0]:
                        Second_intersection_sequenceId = sub[1]  # 第二个交点的sequenceId
                if Second_intersection_sequenceId >= First_intersection_sequenceId:
                    pass
                else:
                    return False
            elif slist[index]!=slist[index + 1]  and slist[index + 1]==slist[index + 2]:
                if JudgeTwoWay(slist[index],slist[index + 1]):
                    return True
                else:
                    return False
            elif slist[index]==slist[index + 1]  and slist[index + 1]!=slist[index + 2]:
                if JudgeTwoWay(slist[index + 1],slist[index + 2]):
                    return True
                else:
                    return False
            else:
                return True
        return True
    except myException as e:
        print(e)
        return False
def FindNextWay(curway,preways,wayid2):
    """
    返回curway下一步能走的路段列表,只要有交点则符合，不考虑方向
    要将路线之前中已有的way删除  避免形成环  造成无限循环
    :param curway:
    :return:
    """
    nextwaylists = []
    flag = 0   #标记，如果下一步有目标路段有wayid2,标记为1
    InflectionpointLists = Find_inflectionpoint(curway)  # 路段的所有拐点
    for subnode in InflectionpointLists:  # 遍历处理路段对应的拐点
        temways = Find_way_By_inflectionpoint(subnode)  # 通过节点找出下一步的路段
        # print(temways)
        if wayid2 in temways:
            flag = 1
        delways = []
        for presubway in preways:
            if presubway in temways:
                delways.append(presubway)
        for temsubway in temways:
            if not JudgeTwoWay(curway, temsubway):  # 路段key到temsubway不能通过
                delways.append(temsubway)
        for sub in set(delways):
            temways.remove(sub)  #
        if len(temways) != 0:  # 拐点subnode下一步有可走的路
            nextwaylists.extend(temways)
    if flag == 1:
        if wayid2 not in nextwaylists:
            return False,set(nextwaylists)
        else:return True,set(nextwaylists)
    else:
        return True,set(nextwaylists)

def Getway_Direction(wayid):
    """
    查询wayid是否为单向
    :param wayid:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT waydirection.oneway FROM waydirection WHERE way_id ={}'.format(wayid)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()  # 元组
        return result[0]
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
def JudgeTwoWay(wayid1,wayid2):
    """
    判断两个相邻有交点路段是否能够互通，即从way1 是否能到达way2
    注意：此部分只判断有交点的两个路段  没有交点的两个路段会直接判断为不能互通
    思路：
    1、无交点，判定为不通，两个路段ID相同，判定为相通
    2、
    :param wayid1:
    :param wayid2:
    :return:
    """
    if wayid1==wayid2:
        Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
        return True
    node_id = TwoWay_intersection(wayid1, wayid2)  # 两条路段交点
    if not node_id:     #两个路段没有交点
        return False
    try:
        wayid1_oneway_flag = Getway_Direction(wayid1)  # 标记wayid1是否为单向
        wayid2_oneway_flag = Getway_Direction(wayid2)  # 标记wayid2是否为单向
        wayslist1 = Get_way_NodeID(wayid1)
        wayslist2 = Get_way_NodeID(wayid2)  # 示例：[320524866, 2207731964, 320524867]
        index = wayslist2.index(node_id[0][0])  # node_id[0][0]为取出交点 node_id为嵌套元组
        if wayid1_oneway_flag == 0 and wayid2_oneway_flag == 0:
            # 两个路段均为双向
            Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
            return True
        elif wayid1_oneway_flag == 1 and wayid2_oneway_flag == 0:  # wayid1 为单向 wayid2 为双向
            # wayid1为单向 wayid2为双向
            if wayslist1.index(node_id[0][0]) == 0:  # 交点为wayid1的第一个点
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 0)
                return False
            else:
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
                return True
        elif wayid1_oneway_flag == 0 and wayid2_oneway_flag == 1:  # wayid1 为双向 wayid2 为单向
            if index == len(wayslist2) - 1:  # 交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 0)
                return False
            else:
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
                return True

        else:
            # 两个路段均为单向
            if index == len(wayslist2) - 1:  # 交点是way2的最后一个点，那么即使way1 way2有交点，则way1也是无法到达way2的
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 0)
                return False
            elif wayslist1.index(node_id[0][0]) == 0 and wayslist2.index(node_id[0][0]) == 0:  # 交点同时是way1 way2的第一个点
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
                return True
            elif wayslist1.index(node_id[0][0]) == 0:  # 交点是way1的第一个点
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 0)
                return False
            else:
                Common_Functions.SaveRoutesConn("connects", wayid1, wayid2, 1)
                return True
    except:
        return False

def Get_Crid(node_id):
    """
    根据node_id查坐标
    :param node_id:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT `X_Grid`, `Y_Grid` FROM nodes WHERE nodes.Node_id={}'.format(node_id)
    try:
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
def Getway_startendnode_grid(wayid,flag = 0):
    """
    得到路段的网格编号
    flag=0 代表获取路段起点的编号
    flag = 1代表获取路段末尾点的网格编号
    :return:
    """
    wayids = Get_way_NodesSequenceId(wayid)
    if wayids:
        if flag==0:
            processnodeid = wayids[0][0]
        else:
            processnodeid = wayids[-1][0]
        grid = Get_Crid(processnodeid)
        return grid
    else:
        return [0,0]


def waytoway(way_id1,way_id2,max_num=8):
    """
    实现从way_id1到way_id2的路线规划,当此函数完全用作简易导航，可设置max_num为无穷
    设置 max_num 与Count 的原因为防止查找完全不通的两个路段而耗费过长的时间
    有方向通行
    问题：即使很近的两个路段（实际短距离不能通行），但是会花费较多的时间去判断是否能通行
    47574526,403874395两个路段不能互通 但是只在北野场桥一部分就花费了5分钟去判断可行性
    :param way_id1:
    :param way_id2:
    :return:
    首先判断两个路段是否有交集，有交集则这两条路不需要经过其他路线的连接
    """
    if way_id1 == way_id2:
        return [way_id1,way_id2]
    finalroute = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        if JudgeTwoWay(way_id1,way_id2):
            finalroute.extend([way_id1, way_id2])
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 1)
            return finalroute
        else:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
    else:
        #两条路段没有直接交点
        Candidate_Routes = [[way_id1]]  # 候选路线
        flag = 0
        count = 0  # 迭代多少次之后仍然没有找到可行路线，则认为不可走
        exitflag = 0  #标记是否是通过找到满足条件的路线而退出的
        grid1 = Getway_startendnode_grid(way_id1, flag=0)
        startx = grid1[0]
        starty = grid1[1]
        grid2 = Getway_startendnode_grid(way_id1, flag=0)
        Endx = grid2[0]
        Endy = grid2[1]
        startendwaydis = twoway_distance(way_id1, way_id2)+ 0.01 # 加1000米弹性范围，0.0003为30米
        while True:
            print(Candidate_Routes)

            temCandidate_Routes = []  # 存储当前这一轮新的候选路线
            AllNextways = []
            print(count)
            for subroute in Candidate_Routes:
                # subroute 表示正在处理的路线
                processingway = subroute[-1]  # 表示要处理的路段
                wayflag,nextway = FindNextWay(processingway,subroute,way_id2)  # 下一步的可选路段
                #wayflag为FALSE 标记wayid2在nextway，但是由于方向问题，被删除，所以直接判定为不通
                if not wayflag:
                    Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
                    return False

                if len(nextway) == 0:
                    # 当前路线下一步没有能走的路
                    pass
                else:
                    AllNextways.extend(nextway)
                    for next in nextway:
                        temroute = copy.deepcopy(subroute)
                        temroute.append(next)
                        temCandidate_Routes.append(temroute)
            if len(AllNextways)==0:
                #所有的候选路线都没有下一步路可走
                flag=1
                exitflag = 1
            count += 1
            Candidate_Routes.clear()
            Candidate_Routes = temCandidate_Routes
            Candidate_Routes = Common_Functions.Double_layer_list(Candidate_Routes)
            Candidate_Routes = Common_Functions.Main_Auxiliary_road(Candidate_Routes)  # 去除头尾路段一样的候选路线
            Candidate_Routes = Common_Functions.Start_End(Candidate_Routes)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            Candidate_Routes = Common_Functions.Sequential_subset(Candidate_Routes)  # 最后去前缀
            delsub = []
            for sub in Candidate_Routes:
                if way_id2 in sub:
                    flag = 1
                    break
            if len(Candidate_Routes) == 0:
                flag = 1
                exitflag = 1
            if count == max_num:
                flag = 1
                exitflag = 1

            if flag == 1:
                break
            for sub in Candidate_Routes:
                if len(sub) >= 3:
                    if JudgeLines(sub):  # 判断当前路线是否能通
                        for i in combinations(sub,2):
                            Common_Functions.SaveRoutesConn("connects", i[0],i[1], 1)

                    elif not JudgeLines(sub) and way_id2 in sub:  # 目标路段在子路线中  但是不能走通
                        Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
                        return False
                    else:
                        delsub.append(sub)
                        continue
                elif len(sub) == 2:
                    if JudgeTwoWay(sub[0], sub[1]):
                        Common_Functions.SaveRoutesConn("connects", sub[0], sub[1], 1)
                        pass
                    elif JudgeTwoWay(sub[0], sub[1]) and way_id2 in sub:  # 目标路段在子路线中  但是不能走通
                        Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
                        return False
                    else:
                        delsub.append(sub)
                        continue
                else:
                    pass
            for sub in Candidate_Routes:
                # 判断行驶方向
                secondgrid = Getway_startendnode_grid(sub[-1], flag=0)
                if secondgrid:
                    curx = secondgrid[0]
                    cury = secondgrid[1]
                    if Endx > startx and Endy > starty:  # 路段way_id2 在way_id1 的右上部
                        if abs(startx - curx) <= 5 or abs(starty - cury) <= 5:  # 防止道路过近，出现偏差，方向加500米偏差
                            pass
                        elif curx <= startx and cury <= starty:
                            delsub.append(sub)  # 此路线方向向左下部走  删除此路线
                    if Endx > startx and Endy < starty:  # 路段way_id2 在way_id1 的右下部
                        if abs(startx - curx) <= 5 or abs(starty - cury) <= 5:  # 防止道路过近，出现偏差，方向加500米偏差
                            pass
                        elif curx < startx and cury > starty:
                            delsub.append(sub)  # 此路线方向向左上部走  删除此路线
                    if Endx < startx and Endy < starty:  # 路段way_id2 在way_id1 的左下部
                        if abs(startx - curx) <= 5 or abs(starty - cury) <= 5:  # 防止道路过近，出现偏差，方向加500米偏差
                            pass
                        elif curx > startx and cury > starty:
                            delsub.append(sub)  # 此路线方向向右上部走  删除此路线
                    if Endx < startx and Endy > starty:  # 路段way_id2 在way_id1 的左上部
                        if abs(startx - curx) <= 5 or abs(starty - cury) <= 5:  # 防止道路过近，出现偏差，方向加500米偏差
                            pass
                        elif curx > startx and cury < starty:
                            delsub.append(sub)  # 此路线方向向右上部走  删除此路线
                else:
                    pass

                temstaryendwaydis = twoway_distance(way_id1, sub[-1])
                if temstaryendwaydis > startendwaydis:
                    delsub.append(sub)
            for sub in Common_Functions.Double_layer_list(delsub):
                Candidate_Routes.remove(sub)

        if exitflag==1:
            #证明是循环跳出不是因为找到路径跳出的
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
        Deleteways = []
        for sub in Candidate_Routes:
            if way_id2 in sub:
                if len(sub) == 1:
                    return sub
                elif len(sub) == 2 and JudgeTwoWay(sub[0], sub[1]):
                    pass
                elif len(sub) >= 3 and JudgeLines(sub):
                    for i in combinations(sub, 2):
                        Common_Functions.SaveRoutesConn("connects", i[0], i[1], 1)
                    pass
                else:
                    Deleteways.append(sub)
            else:
                Deleteways.append(sub)
        if len(Deleteways)!=0:
            for delsub in Common_Functions.Double_layer_list(Deleteways):
                Candidate_Routes.remove(delsub)
        if len(Candidate_Routes)==0:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
        minnum = float("inf")
        for sub in Candidate_Routes:
            if way_id2 in sub:
                if len(sub) < minnum:
                    finalroute = sub
                    minnum = len(sub)
            else:
                pass
        if len(finalroute)==0:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False

        else:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 1)
            return finalroute
def NodirectionFindNextWay(curway,preways):
    """
    返回curway下一步能走的路段列表,只要有交点则符合，不考虑方向
    要将路线之前中已有的way删除  避免形成环  造成无限循环
    :param curway:
    :param preways  表示之前路线中已有的way
    :return:
    """
    nextwaylists = []
    InflectionpointLists = Find_inflectionpoint(curway)  # 路段的所有拐点
    for subnode in InflectionpointLists:  # 遍历处理路段对应的拐点
        temways = Find_way_By_inflectionpoint(subnode)  # 通过节点找出下一步的路段
        delways = []
        for presubway in preways:
            if presubway in temways:
                delways.append(presubway)
        for sub in set(delways):
            temways.remove(sub)  # 将下一路段删除
        if len(temways) != 0:  # 拐点subnode下一步有可走的路
            nextwaylists.extend(temways)
    return set(nextwaylists)
def Nodirectionwaytoway(way_id1,way_id2,max_sum=8):
    """
    无方向  有交点就会认为通行
    :param way_id1:
    :param way_id2:
    :param max_sum:
    :return:
    """
    if way_id1 == way_id2:
        return [way_id1,way_id2]
    finalroute = []
    node_id = TwoWay_intersection(way_id1, way_id2)  #两条路段交点
    if node_id:
        if JudgeTwoWay(way_id1,way_id2):
            finalroute.extend([way_id1, way_id2])
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 1)
            return finalroute
        else:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
    else:
        #两条路段没有直接交点
        Candidate_Routes = [[way_id1]]  # 候选路线
        flag = 0
        count = 0   #迭代多少次之后仍然没有找到可行路线，则认为不可走
        exitflag = 0   #标记是否是通过找到满足条件的路线而退出的
        grid1 = Getway_startendnode_grid(way_id1,flag=0)
        startx = grid1[0]
        starty = grid1[1]
        grid2 = Getway_startendnode_grid(way_id1, flag=0)
        Endx = grid2[0]
        Endy = grid2[1]
        while True:
            temCandidate_Routes = []  # 存储当前这一轮新的候选路线
            AllNextways = []
            MaxDel = []   #存因路段数目大于阈值，而筛除的路线
            for sub in Candidate_Routes:
                if way_id2 in sub:
                    flag = 1
                    break
                if len(sub) > max_sum:   #防止寻找时间过长，如果目的是为了查找路线，可将此条件删除
                    MaxDel.append(sub)
            for sub in MaxDel:
                Candidate_Routes.remove(sub)
            if len(Candidate_Routes)==0:
                flag = 1
                exitflag = 1
            if count==8:
                flag=1
                exitflag = 1
            if flag == 1:
                break
            for subroute in Candidate_Routes:
                # subroute 表示正在处理的路线
                preways = subroute   #表示当前路线已有的路段
                processingway = subroute[-1]  # 表示要处理的路段
                nextway = NodirectionFindNextWay(processingway,preways)  # 下一步的可选路段

                if len(nextway)==0:
                    #当前路线下一步没有能走的路
                    pass
                else:
                    AllNextways.extend(nextway)
                    for next in nextway:
                        temroute = copy.deepcopy(subroute)
                        temroute.append(next)
                        temCandidate_Routes.append(temroute)

            count += 1
            Candidate_Routes.clear()
            Candidate_Routes = temCandidate_Routes
            Candidate_Routes = Common_Functions.Double_layer_list(Candidate_Routes)
            Candidate_Routes = Common_Functions.Main_Auxiliary_road(Candidate_Routes)  # 去除头尾路段一样的候选路线
            Candidate_Routes = Common_Functions.Start_End(Candidate_Routes)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            Candidate_Routes = Common_Functions.Sequential_subset(Candidate_Routes)  # 最后去前缀
            #print(len(Candidate_Routes))
            delsub = []
            for sub in Candidate_Routes:
                #判断行驶方向
                secondgrid = Getway_startendnode_grid(sub[-1], flag=0)
                if secondgrid:
                    curx = secondgrid[0]
                    cury = secondgrid[1]
                    if Endx > startx and Endy>starty:   #路段way_id2 在way_id1 的右上部
                        if curx < startx and cury < starty:
                            delsub.append(sub)            #此路线方向向左下部走  删除此路线
                    if Endx > startx and Endy < starty:  # 路段way_id2 在way_id1 的右下部
                        if curx < startx and cury > starty:
                            delsub.append(sub)  # 此路线方向向左上部走  删除此路线
                    if Endx <startx and Endy < starty:  # 路段way_id2 在way_id1 的左下部
                        if curx > startx and cury > starty:
                            delsub.append(sub)  # 此路线方向向右上部走  删除此路线
                    if Endx < startx and Endy > starty:  # 路段way_id2 在way_id1 的左上部
                        if curx > startx and cury < starty:
                            delsub.append(sub)  # 此路线方向向右上部走  删除此路线
                else:
                    delsub.append(sub)


            for sub in Common_Functions.Double_layer_list(delsub):
                Candidate_Routes.remove(sub)
            #print(len(Candidate_Routes))
            if len(AllNextways)==0:
                #所有的候选路线都没有下一步路可走
                flag=1
                exitflag = 1
        minnum = float("inf")
        if exitflag==1:
            #证明是循环跳出不是因为找到路径跳出的
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
        Deleteways = []
        #print(Candidate_Routes)
        for sub in Candidate_Routes:
            #由于以上为没有方向的判断，所以在此循环中要加入方向的判断
            if way_id2 in sub:
                if len(sub)==1:
                    return sub
                elif len(sub)==2 and JudgeTwoWay(sub[0],sub[1]):
                    pass
                elif len(sub) >= 3 and JudgeLines(sub):
                    pass
                else:
                    Deleteways.append(sub)
            else:
                Deleteways.append(sub)
        if len(Deleteways)!=0:
            for delsub in Common_Functions.Double_layer_list(Deleteways):
                Candidate_Routes.remove(delsub)
        if len(Candidate_Routes)==0:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 0)
            return False
        for sub in Candidate_Routes:
            if way_id2 in sub:
                if len(sub) < minnum:
                    finalroute = sub
                    minnum = len(sub)
            else:
                pass
        if len(finalroute)==0:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2,0)
            return False
        else:
            Common_Functions.SaveRoutesConn("connects", way_id1, way_id2, 1)
            return finalroute
#print(JudgeTwoWay(362883454, 42725535))
#print(waytoway(251623172,42725546))
#print(JudgeLines([251623172, 251623159, 251623169, 251623168, 251623165, 113968808]))
#print(JudgeLines([568126170, 159812371, 176432985, 176432983, 176432987, 159810646, 30878138])) #true

