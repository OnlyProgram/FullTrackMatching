# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 15:33
# @Author  : WHS
# @File    : Common_Functions.py
# @Software: PyCharm
import pymysql
import math
from math import radians, cos, sin, asin, sqrt
import os
from RoadMatch import BigGridCode
def findcsvpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".csv"):
                ret.append(de_path)
    return ret
def findtxtpath(path):
    """Finding the *.txt file in specify path"""
    ret = []
    filelist = os.listdir(path)
    for filename in filelist:
        de_path = os.path.join(path, filename)
        if os.path.isfile(de_path):
            if de_path.endswith(".txt"):
                ret.append(de_path)
    return ret
def haversine(lon1, lat1, lon2, lat2):
    """
    :param lon1: 第一个点经度
    :param lat1: 第一个点纬度
    :param lon2: 第二个点经度
    :param lat2: 第二个点纬度
    :return: 返回距离，单位公里
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r
def list2kml(pointsList,filename,savepath):
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    fullname = filename + '.kml'
    with open(os.path.join(savepath, fullname), 'a') as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
        file.write('<kml xmlns="http://earth.google.com/kml/2.0">' + '\n')
        file.write('<Document>' + '\n')
        for num in pointsList:
            #print(str(num[0]) + "," + str(num[1]))
            file.write('<Placemark>' + '\n')
            coordinate = "<Point><coordinates>" + str(num[0]) + "," + str(num[1]) + ",0</coordinates></Point>"  # 此处0代表海拔，如果有海拔，可更改
            file.write(coordinate + '\n')
            file.write('</Placemark>' + '\n')
        file.write('</Document>' + '\n')
        file.write('</kml>' + '\n')
def Get_way_Nodes(way_id):
    """
    根据way_id得出此路段node,及对应的sequenceid
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
def Get_way_start_end_node(way_id):
    """
    获取路段的起始终点坐标
    :param way_id:
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT ways_nodes.node_id FROM ways_nodes WHERE way_id = {}'.format(way_id)

    try:
        cursor.execute(sql)
        result = cursor.fetchall()   #元组
        startnode = result[0][0]
        endnode = result[-1][0]
        return startnode,endnode
    except Exception as e:
        print(e)
        cursor.close()
    finally:
        connection.close()
def angle(v1, v2):
    """
    计算两个路段之间的夹角
    :param v1: 传入轨迹1的两个经纬度坐标
    :param v2: 传入轨迹2的两个经纬度坐标
    :return:  角度和余弦值
    """
    dx1 = v1[2] - v1[0]
    dy1 = v1[3] - v1[1]
    dx2 = v2[2] - v2[0]
    dy2 = v2[3] - v2[1]
    angle1 = math.atan2(dy1, dx1)
    angle1 = int(angle1 * 180/math.pi)
    # print(angle1)
    angle2 = math.atan2(dy2, dx2)
    angle2 = int(angle2 * 180/math.pi)
    # print(angle2)
    if angle1*angle2 >= 0:
        included_angle = abs(angle1-angle2)
    else:
        included_angle = abs(angle1) + abs(angle2)
        if included_angle > 180:
            included_angle = 360 - included_angle
    # included_angle  角度
    #print(included_angle)
    return included_angle  #返回角度
    #return math.sin((included_angle/180)*math.pi)
def Point_Line_Distance(x,y,z):
    """
    点到线的距离
    :param x: 线的第一个坐标 如[x1,y1]
    :param y: 线的第二个坐标  如[x2,y2]
    :param z: 此点到线的距离
    :return: 距离
    b = (x1-x2)/y2-y1
    """
    if (y[0]-x[0])==0:  # 此线垂直x轴
        d = abs(z[0]-x[0])
    elif (y[1]-x[1]) == 0:#垂直y轴
        d = abs(z[1]-x[1])
    else:
        a = 1
        k = (y[1] - x[1]) / (y[0] - x[0])
        b = -1 / k
        c = x[1] / k - x[0]
        d = abs(a * z[0] + b * z[1] + c) / math.sqrt(a ** 2 + b ** 2)
    return d
def Calcul_Dis_Foot(coordinate1,coordinate2,coordinate3):
    """
    计算点到直线的距离，并判断垂足是否在线段coordinate1与coordinate2之上
    :param coordinate1: 路段的起始坐标
    :param coordinate2: 路段的终点坐标
    :param coordinate3: 原始轨迹点
    :return:
    """

    if coordinate1[0] > coordinate2[0]:
        min_x = coordinate2[0]
        max_x = coordinate1[0]
    else:
        min_x = coordinate1[0]
        max_x = coordinate2[0]
    if coordinate1[1] > coordinate2[1]:
        min_y = coordinate2[1]
        max_y = coordinate1[1]
    else:
        min_y = coordinate1[1]
        max_y = coordinate2[1]
    if (coordinate1[0]-coordinate2[0])==0:  # 此线垂直x轴
        if min_y <= coordinate3[1] <= max_y:
            return True
        else:
            return False
    elif (coordinate1[1]-coordinate2[1]) == 0:#垂直y轴
        if min_x <= coordinate3[0] <= max_x:

            return True
        else:
            return False
    else:
        a = 1
        k = (coordinate2[1] - coordinate1[1]) / (coordinate2[0] - coordinate1[0])  #斜率
        b = -1 / k
        c = coordinate1[1] / k - coordinate1[0]
        distance = abs(a * coordinate3[0] + b * coordinate3[1] + c) / math.sqrt(a ** 2 + b ** 2)  #点到线距离
        k2 = b   #垂线的斜率
        intercept =coordinate3[1]-k2*coordinate3[0] #截距
        footx = (k*intercept -k**2*c)/(1+k**2)  #垂足的x坐标
        #footy = b*footx+intercept
        if min_x<=footx<=max_x:
            return True
        else:
            return False#float('inf')
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
def Find_two_Point(Candidate_way_lis,lon,lat):
    """
    从候选路段中的点集中选出距轨迹点最近的两个
    :param Candidate_way_lis 某候选路段的坐标点集合 如：[[4611240391, 68], [4611240390, 69], [4611240389, 70]]
    :param lon 原始轨迹点经度
    :param lat 原始轨迹点维度
    :return:
    """
    tem_lis = []
    for i in range(len(Candidate_way_lis)):
        tem_coor = Get_Coordinate(Candidate_way_lis[i][0])  #坐标点
        tem_lis.append(haversine(lon,lat,tem_coor[0],tem_coor[1]))
    index_lis = sorted(range(len(tem_lis)), key=lambda k: tem_lis[k])
    return index_lis[0],index_lis[1]
def Find_next_Point(sequence_id,way_id):
    """
    根据路段和坐标点，找到该路段的下一个点
    :param sequence_id: 序列编号
    :param way_id:  路段编号
    :return: 返回下一个坐标点编号 及其序列号
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = """SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE ways_nodes.way_id={} AND ways_nodes.sequence_id={}""".format(str(way_id),str(sequence_id+1))
    cursor.execute(sql)
    result = cursor.fetchone()
    if  result:
        pass
    else:
        sql = "SELECT ways_nodes.node_id,ways_nodes.sequence_id FROM ways_nodes WHERE ways_nodes.way_id={} AND ways_nodes.sequence_id={}".format(
            str(way_id), str(sequence_id - 1))
        cursor.execute(sql)
        result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result
def Find_nearby_Point(x_grid,y_grid,difference = 3):
    """
    找出该坐标点相邻格子中的所有坐标点，一个格子为100米，
    :param x_greid:
    :param y_grid:
    :param difference 相邻格子数，默认为1，即以改坐标所在的格子为中心，向外扩展一圈
    :return:返回字典 键为way_id  值为node_id
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")

    sql = """ SELECT a.way_id,b.Node_id,a.sequence_id FROM ways_nodes a,(
		SELECT nodes.Node_id FROM nodes WHERE nodes.X_Grid >= {}
		AND nodes.X_Grid <= {} AND nodes.Y_Grid >= {} AND nodes.Y_Grid <= {}) b
        WHERE a.node_id = b.Node_id""".format(x_grid-difference,x_grid+difference,y_grid-difference,y_grid+difference)
    node_id_dict = {}
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            #print(row)
            tem_lis = [row[1], row[2]]
            if row[0] in node_id_dict:
                node_id_dict[row[0]].append(tem_lis)
            else:
                node_id_dict[row[0]] = [tem_lis]
            #node_id_lists.append(row[0])
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    return  node_id_dict
def Find_Candiate_Point(dic,coordinate1,coordinate2,flag=1):
    """
    返回某个坐标该归属于哪条路段，可返回多条
    :param dic:
    :param coordinate1:
    :param coordinate2:
    :return:
    """
    Candidate_dic = {}  # 存储待选路段与轨迹的方余弦值和距离
    v1 = [coordinate1[0], coordinate1[1], coordinate2[0], coordinate2[1]]  # 轨迹向量
    #print("轨迹向量V1{}".format(v1))
    for key in dic.keys():
        startnode, endnode = Get_way_start_end_node(key)
        te_coor1 = Get_Coordinate(startnode)
        te_coor2 = Get_Coordinate(endnode)
        if len(dic[key]) == 1:  #如果候选路段只有一个点
            tem_coor1 =  Get_Coordinate(dic[key][0][0])#临时坐标1
            tem_li = Find_next_Point(dic[key][0][1],key) #接受返回的查询结果 node_id  sequence_id (2207731639, 17)
            tem_coor2 = Get_Coordinate(tem_li[0])

            if dic[key][0][1]>tem_li[1]:
                #tem_coor1的sequence_id 大于tem_coor2的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]

            Cosine =  angle(v1,v2)  #接受角度
            #print("{}轨迹向量V2:{}".format(key,v2))
            if flag==1:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                [coordinate1[0], coordinate1[1]])  #首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                  [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            else:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                            [coordinate2[0], coordinate2[1]])  # 首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            Candidate_dic[key] = [distance,Cosine]
        elif len(dic[key])==2:

            tem_coor1 = Get_Coordinate(dic[key][0][0])  # 临时坐标1
            tem_coor2 = Get_Coordinate(dic[key][1][0])  # 临时坐标1
            if dic[key][0][1] > dic[key][1][1]:  # 第一个点的sequence_id 大于 第二点的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]
            #print("{}轨迹向量V2:{}".format(key, v2))

            Cosine = angle(v1, v2)
            if flag == 1:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                            [coordinate1[0], coordinate1[1]])  # 首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                   [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            else:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                            [coordinate2[0], coordinate2[1]])  # 首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                   [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            Candidate_dic[key] = [distance, Cosine]
        else:
            # 候选路段有三个点及以上
            if flag==1:
                num1, num2 = Find_two_Point(dic[key], coordinate1[0], coordinate1[1])  #在路段上选出距离轨迹点最近的两个node
            else:
                num1, num2 = Find_two_Point(dic[key], coordinate2[0], coordinate2[1])
            tem_coor1 = Get_Coordinate(dic[key][num1][0])  # 临时坐标1
            tem_coor2 = Get_Coordinate(dic[key][num2][0])  # 临时坐标1
            if dic[key][num1][1] > dic[key][num2][1]:  # 第一个点的sequence_id 大于 第二点的sequence_id
                v2 = [tem_coor2[0], tem_coor2[1], tem_coor1[0], tem_coor1[1]]
            else:
                v2 = [tem_coor1[0], tem_coor1[1], tem_coor2[0], tem_coor2[1]]
            #print("{}轨迹向量V2:{}".format(key, v2))
            Cosine = angle(v1, v2)
            if flag == 1:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                            [coordinate1[0], coordinate1[1]])  # 首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                   [coordinate1[0], coordinate1[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            else:
                Is_inFlag = Calcul_Dis_Foot([te_coor1[0], te_coor1[1]], [te_coor2[0], te_coor2[1]],
                                            [coordinate2[0], coordinate2[1]])  # 首先计算垂足是否在路段上，该坐标采用路段的首尾坐标
                if Is_inFlag:
                    distance = Point_Line_Distance([tem_coor1[0], tem_coor1[1]], [tem_coor2[0], tem_coor2[1]],
                                                   [coordinate2[0], coordinate2[1]])  # 计算轨迹点到道路的距离
                else:
                    distance = float('inf')
            Candidate_dic[key] = [distance, Cosine]
    return Candidate_dic
def Find_Candidate_Route(coordinate1,coordinate2,flag=1):
    """
    通过车辆轨迹的两个坐标选出匹配的候选路段
    :param coordinate1: 坐标1 及其编号   如[116.5256651,39.7467991，1526,747]
    :param coordinate2: 坐标2 及其编号   如[116.5256651,39.7467991，1526,747]
    :param flag 如果flag==1 计算coordinate1 ==2 计算coordinate2
    :return: 返回候选路段编号  way_id及其序列编号sequence
    """
    dic = {} #候选路段，没有距离，方向约束
    if flag == 1:  # 计算该路段的起点归属相近点
        #print(f"计算坐标{coordinate1[0], coordinate1[1]}")
        dic = Find_nearby_Point(coordinate1[2], coordinate1[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2, flag=1)
    # print(dic)
    elif flag == 2:  # 计算该路段的终点相近点
        #print(f"计算坐标{coordinate2[0], coordinate2[1]}")
        dic = Find_nearby_Point(coordinate2[2], coordinate2[3])
        Candidate_Route_dic = Find_Candiate_Point(dic, coordinate1, coordinate2, flag=2)
    else:
        return None
    point_Candidate = {}
    #print(Candidate_Route_dic)
    for key in Candidate_Route_dic.keys():
        # 两个原始轨迹点方向与道路轨迹方向夹角大于90 或者轨迹点到地图道路距离大于30米
        if Candidate_Route_dic[key][1] <=90 and Candidate_Route_dic[key][0] <= 0.0003:
            point_Candidate[key] = Candidate_Route_dic[key]
        else:
            pass
    #print(point_Candidate)
    return point_Candidate
def Double_layer_list(doublelist:list):
    """
    双层列表去重
    :param doublelist:  双层列表
    :return:
    """
    new_list = [list(t) for t in set(tuple(_) for _ in doublelist)]  # 嵌套列表去重
    new_list.sort(key=doublelist.index)
    return new_list
def Is_List_Prefix(list1:list,list2:list):
    """
    判断两个是否为另一个前缀,
    :param list1:
    :param list2:
    :return:返回长度较长的
    """
    len1 = len(list1)
    len2 = len(list2)
    flag = 1
    if len1<=len2:
        for index in range(len1):
            if list1[index]==list2[index]:
                pass
            else:
                flag=0
        if flag==1:
            return list2
        else:return None
    elif len1>len2:
        for index in range(len2):
            if list1[index]==list2[index]:
                pass
            else:
                flag=0
        if flag==1:
            return list1
        else:return None
def Sequential_subset(slist):
    """
    #传入时不会有重复子列表
    如果有两个及以上的路线是其前缀 则此路线会被删除
    #如果一个列表是两个及以上的前缀，则会被删除，如果只是一个列表的前缀，则不会被删除（路口）

    去除子集  如[[1,2,3],[1,2]]
    :param slist: 为双层嵌套列表
    :return:
    """
    del_list = []  # 要删除的子列表
    index_list = [i for i in range(len(slist))]
    # print(index_list)
    compared = []  # 已经比较的
    for index in index_list:
        compared.append(index)
        for index2 in index_list:
            if index2 in compared:  # 不比较本身
                pass
            else:
                temdel = Is_List_Prefix(slist[index], slist[index2])
                if temdel:
                    del_list.append(temdel)
    # print(del_list)
    seta = Double_layer_list(del_list)   #去重
    n = [del_list.count(i) for i in seta]  # 统计频率
    z = zip(seta, n)
    z = sorted(z, key=lambda t: t[1], reverse=True)
    # 统计出每个前缀出现的次数
    del_list = [i[0] for i in z if i[1] > 1]
    #print(del_list)
    for subdellist in del_list:
        slist.remove(subdellist)
    # print(slist)
    return slist
def del_adjacent(alist):
    """
    删除相邻重复元素
    :param alist:
    :return:
    """
    for i in range(len(alist) - 1, 0, -1):
         if alist[i] == alist[i-1]:
             del alist[i]
    return alist
def DoubleDel(dlist:list):
    """
    对双层列表的每一个子列表进行相邻元素去重，然后去重
    :param dlist: 双层列表
    :return:
    """
    for sub in dlist:
        sub = del_adjacent(sub)
    dlist = Double_layer_list(dlist)
    return dlist
def Main_Auxiliary_road(slist:list):
    """
    传入双层列表 ，去除类似[47574526, 318323104, 47574526], [47574526, 210697572, 318323104, 47574526]种的路段，即通过某个路段之后又回到此路段
    先只考虑头尾
    :param slist:双层列表
    :return:
    """
    startenddel_waylist = []  #路段头尾路段编号相同 待删除路段
    if len(slist)==1:   #只有一个路段
        return slist
    for sub in slist:
        if len(sub)==1:   #路线中只有一个路段  不经过以下处理
            continue
        if sub[0]==sub[-1]:
            startenddel_waylist.append(sub)
    for subdel in startenddel_waylist:
        slist.remove(subdel)
    # 以上的去除同一条候选路线头尾路段编号相同的路线
    return  slist
def Start_End(slist:list):
    # 以下为去除 ：对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
    del_list = []  # 要删除的子列表
    index_list = [i for i in range(len(slist))]
    # print(index_list)
    compared = []  # 已经比较的
    for index in index_list:
        compared.append(index)
        for index2 in index_list:
            if index2 in compared:  # 不比较本身
                pass
            else:
                # 候选路线slist[index] slist[index2] 的头尾路段编号是一样的
                if slist[index][0] == slist[index2][0] and slist[index][-1] == slist[index2][-1]:
                    if len(slist[index]) > len(slist[index2]):
                        del_list.append(slist[index])
                    elif len(slist[index]) < len(slist[index2]):
                        del_list.append(slist[index2])
                    else:
                        pass
                else:
                    pass
    del_list = Double_layer_list(del_list)
    for delsub in del_list:
        slist.remove(delsub)
    return slist
def SaveRoutesConn(tablename,wayid1,wayid2,flag):
    """
    存储wayid1 wayid2的通行关系  能通过flag为1 否则为0
    :param tablename: 存储此关系的表名，  #测试表为 connects
    :param wayid1: 路段编号
    :param wayid2:
    :param flag: wayid1 wayid2的通行关系  能通过flag为1 否则为0
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456',db='bjosmmap', charset='utf8')
    cursor = connection.cursor()
    #cursor.execute("use bjosmmap;")
    if wayid1==wayid2:
        flag=1
    sql_insert = """insert into {}(`Startway`, `Endway`, `Flag`) values({},{},{});""".format(tablename, wayid1,wayid2,flag)
    try:
        cursor.execute(sql_insert)  # 执行sql语句
        connection.commit()  # 提交
    except Exception as e:
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
def InquireConn(wayid1,wayid2,tablename="connects"):
    """
    查询wayid1能否到达wayid2
    :param wayid1:
    :param wayid2:
    :return: 能通过返回True 否则返回False
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = """ SELECT connects.Flag FROM {}  WHERE connects.Startway ={}  AND connects.Endway = {}""".format(tablename,wayid1,wayid2)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()  # 元组

        if not result:   #没有此记录
            return -1
        #a =result[0]
        #print(type(a))
        if len(result)==1:    #如果查到两条及以上信息，证明数据库表中出现错误 返回错误
            if result[0][0]==1:
                return 1
            else:
                return 0
        else:
            return -1
    except Exception as e:
        print(e)
        return -1
    finally:
        cursor.close()
        connection.close()
def GetWay_ByGridCode(code):
    """
    根据编码查找所属路段
    :param code: 轨迹点编码
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT WayID FROM firstleveltable WHERE GridCode={}'.format(code)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()
def GetWayAllCode(way):
    """
    获取way的所有编码
    :param way:
    :return:
    """
    connection = pymysql.connect(host='127.0.0.1', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use bjosmmap;")
    sql = 'SELECT GridCode FROM firstleveltable WHERE WayID={}'.format(way)
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        waycodelsit = []
        for sub in result:
            waycodelsit.append(sub[0])
        return waycodelsit
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()


def GetTwoCoor_ByGrid(code, way):
    """
    获取way中code及其相邻单元格的坐标
    :param code: 道路编码
    :param way: 路网Id
    :return:路way的两个坐标
    """
    waycodes_list = GetWayAllCode(way)
    if waycodes_list:
        index = waycodes_list.index(code)
        if index ==len(waycodes_list)-1:
            neighborcode = waycodes_list[index-1]
            lon2,lat2 = BigGridCode.Coordinate_Decode(code)  #后一个坐标点
            lon1,lat1 = BigGridCode.Coordinate_Decode(neighborcode)  #前一个坐标点
        else:
            neighborcode = waycodes_list[index+1]
            lon2, lat2 = BigGridCode.Coordinate_Decode(neighborcode)  # 后一个坐标点
            lon1, lat1 = BigGridCode.Coordinate_Decode(code)  # 前一个坐标点
        return [lon1,lat1,lon2,lat2]
    else:
        return False
#Find_Candidate_Route([116.5556,39.747,1556,747],[116.555183,39.746883,1556,747],2)
#print(angle([0,0,1,0],[0,0,0,1]))






