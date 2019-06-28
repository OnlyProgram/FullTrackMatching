# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 14:07
# @Author  : WHS
# @File    : OSM2SQL.py
# @Software: PyCharm
"""
OSM文件转到数据库,nodes表只存储路的节点，不存储所有节点（河流、人行道等），数据量太大

注意：并不是路网中的所有点都有坐标
"""
import pymysql
import json
from tqdm import tqdm
import math
# 打开数据库连接
from RoadMatch import MapNavigation,Coor_GeoHash,GridCode,Common_Functions

def CreatMysqlDatabase(database_name):
    # 使用 cursor() 方法创建一个游标对象 cursor
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    sql = "create database {} character set utf8;".format(database_name)
    try:
        cursor.execute(sql)
        print('创建{}库完成'.format(database_name))
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connection.close()

def CreatTable(dbname,tablename,sql):
    """

    :param dbname: 数据库名
    :param tablename: 表名
    :param sql  sql语句
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    cursor.execute("DROP TABLE IF EXISTS {}".format(tablename))

    # 使用预处理语句创建表

    cursor.execute(sql)
    cursor.close()
    connection.close()
    print('表{}创建完成'.format(tablename))
def InsrtNodes(nodefilepath,wayslist,dbname,tablename):
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    print("Nodes开始导入数据库...")
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    count = 0
    nonodecount = 0  #记录路段中没有坐标点的node数目
    with open(nodefilepath, 'r') as file:
        dic = json.loads(file.read())
    with open(wayslist,'r') as file:
        waydic = json.loads(file.read())
        highnode_lsits = []   #存储路的node
        for key in waydic.keys():
            highnode_lsits.extend(waydic[key])
        print(len(set(highnode_lsits)))
        with tqdm(total=len(set(highnode_lsits))) as pbar:
            for key in set(highnode_lsits):
                if key in dic:   #在路网中的节点并不一定有坐标
                    x_grid = math.ceil((dic[key][1] - 115) / 0.001)  # x方向格子编号
                    y_grid = math.ceil((dic[key][0] - 39) / 0.001)  # y方向格子编号
                    sql_insert = 'insert into {}(Node_id,Lon,Lat,X_Grid,Y_Grid) values({},{},{},{},{});'.format(
                        tablename, key, dic[key][1],
                        dic[key][0], x_grid, y_grid)
                    try:
                        cursor.execute(sql_insert)  # 执行sql语句
                        connection.commit()  # 提交
                        count += 1
                        pbar.update(1)
                    except Exception as e:
                        print(e)
                        connection.rollback()
                        cursor.close()
                else:
                    print(key)
                    nonodecount += 1
        print(nonodecount)


    connection.close()
    #print("\n已成功添加{}条记录".format(count))
def InsrtWays(waylistpath,dbname,tablename):
    """
    将道路列表的json文件存入数据库
    :param waylistpath: waylsits的json文件路径
    :param dbname: 数据库名
    :param tablename: 表名
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    print("ways信息开始导入数据库...")
    count = 0
    with open(waylistpath, 'r') as file:
        dic = json.loads(file.read())
        with tqdm(total=len(dic)) as pbar:
            for key in dic.keys():
                if len(dic[key])==1:
                    sql_insert = 'insert into {}(way_id,node_id,sequence_id) values({},{},{},{});'.format(tablename,key, dic[key],1)
                    try:
                        cursor.execute(sql_insert)  # 执行sql语句
                        connection.commit()  # 提交
                        count += 1
                        pbar.update(1)
                    except Exception as e:
                        print(e)
                        connection.rollback()
                        cursor.close()
                else:
                    for num in range(len(dic[key])):  # sequence代表每条路中node的排序号
                        sequence = num + 1
                        sql_insert = 'insert into {}(way_id,node_id,sequence_id) values({},{},{});'.format(tablename,
                                                                                                              key,
                                                                                                              dic[key][num],
                                                                                                              sequence)
                        try:
                            cursor.execute(sql_insert)  # 执行sql语句
                            connection.commit()  # 提交
                            count += 1
                        except Exception as e:
                            print(e)
                            connection.rollback()
                            cursor.close()
                    pbar.update(1)
        connection.close()
def InsertGeoTable(waylistpath,dbname,tablename):
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    print("ways信息开始导入数据库...")
    with open(waylistpath, 'r') as file:
        dic = json.loads(file.read())
        with tqdm(total=len(dic)) as pbar:
            for key in dic.keys():
                for num in range(len(dic[key])):  # sequence代表每条路中node的排序号
                    coor = MapNavigation.Get_Coordinate(dic[key][num])  #有的点没有坐标
                    if coor:
                        sql_insert = 'insert into {}(WayId,NodeId,GeoCode) values({},{},{});'.format(tablename,
                                                                                                     key, dic[key][num],
                                                                                                     repr(Coor_GeoHash.encode(
                                                                                                             coor[1],
                                                                                                             coor[0])))
                        try:
                            cursor.execute(sql_insert)  # 执行sql语句
                            connection.commit()  # 提交
                        except Exception as e:
                            print(e)
                            connection.rollback()
                            cursor.close()
                    else:pass
                pbar.update(1)
    connection.close()
def Extract_Inflection_point(databasename,tablename):
    """
    从数据库的ways_nodes表中提取拐点,并保存到tablename表
    #返回字典  键为node_id   值为way_id  值为列表，代表此node_id是哪几个way的交叉点
    :param databasename 数据库名
    :param tablename 存储拐点的表名
    :return:
    """
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(databasename))
    sql =   """
    (SELECT a.node_id,a.way_id
    FROM ways_nodes a,(select way_id,node_id,COUNT(node_id)
    FROM ways_nodes
    GROUP BY node_id
    HAVING COUNT(node_id)>1
    ORDER BY way_id) b
    WHERE a.node_id =b.node_id AND a.way_id<>b.way_id )
    UNION
    (SELECT a.node_id,b.way_id
    FROM ways_nodes a,(select way_id,node_id,COUNT(node_id)
    FROM ways_nodes
    GROUP BY node_id
    HAVING COUNT(node_id)>1
    ORDER BY way_id) b
    WHERE a.node_id =b.node_id AND a.way_id<>b.way_id)
    """
    #node_way_dict ={}  #键为node_id，值为way_id
    index = 1
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            sql_insert = 'insert into {}(`Index_id`, `NodeID`, `WayID`) values({},{},{});'.format(tablename, index,
                                                                                                    row[0], row[1])
            try:
                cursor.execute(sql_insert)  # 执行sql语句
                connection.commit()  # 提交
                index += 1
            except Exception as e:
                print(e)
                connection.rollback()
                cursor.close()

            # tem_lis = [row[1]]
            # if row[0] in node_way_dict:
            #     node_way_dict[row[0]].extend(tem_lis)
            # else:
            #     node_way_dict[row[0]] = tem_lis
    except Exception as e:
        print(e)
        connection.rollback()

    finally:
        cursor.close()
        connection.close()
    #return node_way_dict
def InsertGridTable(waylistpath,dbname,tablename):
    connection = pymysql.connect(host='localhost', user='root', passwd='123456', charset='utf8')
    cursor = connection.cursor()
    cursor.execute("use {};".format(dbname))
    print("ways信息开始导入数据库...")
    with open(waylistpath, 'r') as file:
        dic = json.loads(file.read())
        with tqdm(total=len(dic)) as pbar:
            for key in dic.keys():
                Isflag = 1  #标记该路段是否有轨迹点没有坐标
                completeLineCode = []    #存储一条线路的完整编号
                for num in range(1,len(dic[key])):  # sequence代表每条路中node的排序号

                    coor1 = MapNavigation.Get_Coordinate(dic[key][num-1])  #有的点没有坐标
                    coor2 = MapNavigation.Get_Coordinate(dic[key][num])
                    if coor1 and coor2:
                        #print(coor1[0],coor1[1],coor2[0],coor2[1])
                        temcodelist = GridCode.GetGridCodes(coor1[0],coor1[1],coor2[0],coor2[1])
                        completeLineCode.extend(temcodelist)
                    else:
                        Isflag = 0
                        continue
                if Isflag == 1:
                    #`FirstLevelTable`(`WayID`, `GridCode`, `SequenceID`)
                    sequenceid = 0
                    Common_Functions.del_adjacent(completeLineCode)
                    for sub in completeLineCode:
                        sequenceid += 1
                        sql_insert = 'insert into {}(WayID,GridCode,SequenceID) values({},{},{});'.format(tablename,key,repr(sub[1]),sequenceid)
                        try:
                            cursor.execute(sql_insert)  # 执行sql语句
                            connection.commit()  # 提交
                        except Exception as e:
                            print(e)
                            connection.rollback()
                            cursor.close()
                else:pass
                pbar.update(1)
    connection.close()
#运行示例
#nodesql = """CREATE TABLE {}(`Node_id` BIGINT  NOT NULL PRIMARY KEY,`Lon` DOUBLE   NOT NULL,`Lat` DOUBLE   NOT NULL,`X_Grid` INT NOT NULL,`Y_Grid` INT NOT NULL)CHARSET=utf8;""".format(tablename)
#CreatMysqlDatabase("BJOSM")
#CreatTable("bjosmmap","Nodes",nodesql)
#InsrtNodes("H:\GPS_Data\Road_Network\Beijing\AllNodes.json","H:\GPS_Data\Road_Network\Beijing\wayslist.json","bjosmmap","Nodes")
#InsrtNodes("H:\GPS_Data\Road_Network\Beijing\\bjosm\AllNodes.json","H:\GPS_Data\Road_Network\Beijing\\bjosm\wayslist.json","bjosmmap","Nodes")
#InsrtWays("H:\GPS_Data\Road_Network\Beijing\\wayslist.json","bjosmmap","ways_nodes")
#Extract_Inflection_point("bjosmmap","inflectionpoint")
#InsertGeoTable("H:\GPS_Data\Road_Network\Beijing\wayslist.json","bjosmmap","Geotable")
#InsertGridTable("H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\ways.json","bjosmmap","FirstLevelTable")