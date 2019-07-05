# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 15:36
# @Author  : WHS
# @File    : RoadMatching.py
# @Software: PyCharm
"""
此模块不采用滑动窗口式方法
思路：
（1）选出所有点的候选路段
（2）根据车的行驶方向减少候选路段

完整轨迹分段策略：
1、如果两个点相邻距离大于5公里
"""
import pandas as pd
import os
from RoadMatch import Common_Functions
from RoadMatch import MapNavigation
import copy
from itertools import permutations
import time,json
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
        print(f"正在查看路段:{twowaytuple[0]}与路段:{twowaytuple[1]}的连通性......")
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

def TrajectorySplit(csvfilepath,processpath):
    """
    :param csvfilepath: 原始轨迹csv文件
    :param processpath: 存储原轨迹分段之后的csv文件
    :return:
    """
    (path,file) = os.path.split(csvfilepath)
    (filename,extension) = os.path.splitext(file)
    filesavepath = os.path.join(processpath,filename)  #文件分段之后保存的路径
    if not os.path.isdir(filesavepath):
        os.mkdir(filesavepath)
    df = pd.read_csv(csvfilepath, header=None, usecols=[1, 2, 3, 4, 5],names=[0,1,2,3,4])

    df = df.sort_values(by= 0)  # 时间排序
    points_num = df.shape[0]  # 坐标数量
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    drop_list = []  # 要删除的索引列表
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format="%Y%m%d ")
    for row in range(1, points_num):
        if row == points_num:
            break
        points_dis = Common_Functions.haversine(df.iloc[row, 1], df.iloc[row, 2], df.iloc[row - 1, 1],
                                                df.iloc[row - 1, 2])  # 相邻坐标点之间的距离
        Time_difference = (df.iloc[row, 0] - df.iloc[row-1, 0]).seconds #相邻两个坐标点的时间差,单位：秒
        if points_dis < 0.01:  # 距离小于10米
            drop_list.append(row)
        if Time_difference!=0:
            speed = points_dis/Time_difference   #速度 秒
        else:
            speed = 0
        if speed >= 0.034:
            drop_list.append(row)       #时速大于120 ，0.034时速为122

    newdf = df.drop(drop_list)  # 删除相邻点在10米之内的点和时速大于120的异常点
    newdf = newdf.reset_index(drop=True)
    #Candidate_pointName = filename + ".csv"
    #newdf.to_csv(os.path.join(filesavepath, os.path.join()), index=0,header=0, encoding='utf_8_sig')  #筛选出的被匹配的轨迹点
    #以上为处理所有的相邻点距离小于10米的坐标
    #以下循环为分段
    start_row = 0  #文件分割的起始行数
    endrow = 0  #结束行数
    part_num = 1
    part_name = "part" + str(part_num) +".csv"
    #tem_df = pd.DataFrame(None)
    Is_Save_flag = 0  #记录该轨迹段是否保存
    for row in range(1, newdf.shape[0]):
        #Time_difference = (newdf.iloc[row, 0] - newdf.iloc[row - 1, 0]).seconds  # 相邻两个坐标点的时间差,单位：秒
        Adjacent_two_points_dis = Common_Functions.haversine(newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row - 1, 1],
                                                newdf.iloc[row - 1, 2])  # 相邻坐标点之间的距离
        if Adjacent_two_points_dis > 5:
            endrow = row-1
            Is_Save_flag = 1
        if row == newdf.shape[0]-1:
            #tem_df = newdf.loc[start_row:row+1, :]
            endrow = row
            Is_Save_flag = 1
        if Is_Save_flag == 1:
            newdf.loc[start_row:endrow, :].to_csv(os.path.join(filesavepath,part_name),index=0,
                      header=0, encoding='utf_8_sig')
            start_row = endrow+1
            Is_Save_flag = 0
            #tem_df.drop(tem_df.index, inplace=True)
            part_num += 1
            part_name = "part" + str(part_num) +".csv"
def FindPointCandidateWays(csvfilepath,candidatewaypath,candidatewayname):
    """
    处理完整轨迹
    找出坐标点的候选路段，此部分已经通过角度（大于90）、距离（大于30米）筛除一部分候选路段
    :param csvfilepath: csv文件路径 例：H:\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv"
    :param candidatewaypath:  轨迹点候选路段保存路径
    :param candidatewayname: 候选路段保存的文件名

    :return:
    """
    if not os.path.isdir(candidatewaypath):
        os.mkdir(candidatewaypath)
    # 读时间 经纬度 网格编号
    #df = pd.read_csv("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv",header=None, usecols=[1, 2, 3, 4, 5])
    df = pd.read_csv(csvfilepath,header=None, usecols=[0,1, 2, 3, 4],names=[0,1,2,3,4]) #时间经纬度网格
    points_num = df.shape[0]  # 坐标数量
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # file = open("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')
    txtname = candidatewayname + ".txt"
    file = open(os.path.join(candidatewaypath, txtname), 'a')
    print("本轨迹段共查找坐标点数为：{}".format(df.shape[0]))
    for row in range(df.shape[0]):
        if row == 0:
            # print("处理起始坐标点{}".format([newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]]))
            dic = Common_Functions.Find_Candidate_Route(
                [df.iloc[row, 1], df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4]],
                [df.iloc[row + 1, 1], df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4]],
                flag=1)
            if dic:  # 有候选路段才保存
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
                file.flush()
        elif row == df.shape[0] - 1:
            # print("处理终点坐标点{}".format([df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
            dic = Common_Functions.Find_Candidate_Route(
                [df.iloc[row - 1, 1], df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4]],
                [df.iloc[row, 1], df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4]], flag=2)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
                file.flush()
        else:
            dis1 = Common_Functions.haversine(df.iloc[row, 1], df.iloc[row, 2], df.iloc[row - 1, 1],
                                              df.iloc[row - 1, 2])
            dis2 = Common_Functions.haversine(df.iloc[row, 1], df.iloc[row, 2], df.iloc[row + 1, 1],
                                              df.iloc[row + 1, 2])
            # 找相邻最近的点做为轨迹方向
            if dis2 > dis1:
                # print("处理终点坐标点{}".format([newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [df.iloc[row - 1, 1], df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row - 1, 4]],
                    [df.iloc[row, 1], df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4]], flag=2)

            else:
                # print("处理起始坐标点{}".format([newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [df.iloc[row, 1], df.iloc[row, 2], df.iloc[row, 3], df.iloc[row, 4]],
                    [df.iloc[row + 1, 1], df.iloc[row + 1, 2], df.iloc[row + 1, 3], df.iloc[row + 1, 4]],
                    flag=1)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
                file.flush()
    file.close()
def FindPointCandidateWay(csvfilepath,candidatewaypath,candidatewayname):
    """
    处理北野场桥
    找出坐标点的候选路段，此部分已经通过角度（大于90）、距离（大于30米）筛除一部分候选路段
    :param csvfilepath: csv文件路径 例：H:\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv"
    :param candidatewaypath:  轨迹点候选路段保存路径
    :param candidatewayname: 候选路段保存的文件名

    :return:
    """
    if not os.path.isdir(candidatewaypath):
        os.mkdir(candidatewaypath)
    # 读时间 经纬度 网格编号
    #df = pd.read_csv("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv",header=None, usecols=[1, 2, 3, 4, 5])
    df = pd.read_csv(csvfilepath,header=None, usecols=[1, 2, 3, 4, 5])
    points_num = df.shape[0]  # 坐标数量
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # print(df.iloc[:,1:4])
    drop_list = []  # 要删除的索引列表
    for row in range(1, points_num):
        if row == points_num:
            break
        points_dis = Common_Functions.haversine(df.iloc[row, 1], df.iloc[row, 2], df.iloc[row - 1, 1],
                                                df.iloc[row - 1, 2])  # 相邻坐标点之间的距离
        if points_dis < 0.01:  # 距离小于10米
            drop_list.append(row)
    # print(drop_list)
    newdf = df.drop(drop_list)  # 删除相邻点在10米之内的点
    # print(newdf.iloc[:,1:3])
    newdf = newdf.reset_index(drop=True)
    #file = open("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')
    txtname = candidatewayname + ".txt"
    file = open(os.path.join(candidatewaypath,txtname), 'a')
    print("本轨迹段共查找坐标点数为：{}".format(newdf.shape[0]))
    for row in range(newdf.shape[0]):
        if row == 0:
            #print("处理起始坐标点{}".format([newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]]))
            dic = Common_Functions.Find_Candidate_Route(
                [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]],
                [newdf.iloc[row + 1, 1], newdf.iloc[row + 1, 2], newdf.iloc[row + 1, 3], newdf.iloc[row + 1, 4]],
                flag=1)
            if dic:  # 有候选路段才保存
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
        elif row == newdf.shape[0] - 1:
            #print("处理终点坐标点{}".format([df.iloc[row - 1, 2], df.iloc[row - 1, 3], df.iloc[row, 2], df.iloc[row, 3]]))
            dic = Common_Functions.Find_Candidate_Route(
                [newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]],
                [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]], flag=2)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")

        else:
            dis1 = Common_Functions.haversine(newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row - 1, 1],
                                              newdf.iloc[row - 1, 2])
            dis2 = Common_Functions.haversine(newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row + 1, 1],
                                              newdf.iloc[row + 1, 2])
            # 找相邻最近的点做为轨迹方向
            if dis2 > dis1:
                #print("处理终点坐标点{}".format([newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [newdf.iloc[row - 1, 1], newdf.iloc[row - 1, 2], newdf.iloc[row - 1, 3], newdf.iloc[row - 1, 4]],
                    [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]], flag=2)

            else:
                #print("处理起始坐标点{}".format([newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]]))
                dic = Common_Functions.Find_Candidate_Route(
                    [newdf.iloc[row, 1], newdf.iloc[row, 2], newdf.iloc[row, 3], newdf.iloc[row, 4]],
                    [newdf.iloc[row + 1, 1], newdf.iloc[row + 1, 2], newdf.iloc[row + 1, 3], newdf.iloc[row + 1, 4]],
                    flag=1)
            if dic:
                file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")

    file.close()
def SelectFinalRoute(candidatewaypath,savefinalroutespath):
    """
    根据坐标点的候选路段选出路网的匹配路线
    保存格式为：车辆名：路线（如果不确定，可能为多条），车辆名为txt文件名
    :param candidatewaypath:  坐标点候选路段的txt文件路径，如H:\\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt
    :param savefinalroutespath: 最终路线保存路径
    :return:
    """
    #file = open("H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')

    (tempath, tempfilename) = os.path.split(candidatewaypath)  # tempfilename为txt文件名（包含后缀）
    (trunkname, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    savetxtfilename = trunkname +'.txt'
    file = open(os.path.join(savefinalroutespath,savetxtfilename), 'a')
    with open(candidatewaypath) as candidatewayfile:
        filelines = candidatewayfile.readlines()
        linesnum = len(filelines)
        finalline = []     #存储最终路线，可能为多条，随着坐标点的迭代，会变化，直到处理完最有一个坐标点
        for key in eval(filelines[0].strip('\n').split(">>>")[-1]).keys():
            finalline.append([key])
        #print(finalline)
        # 遍历每个坐标点的候选路段
        print("需要处理坐标数为：{}".format(linesnum))
        for lineindex in range(1,linesnum):
            templine = []   #存储临时路线
            # 遍历到最后一行
            print(len(finalline))
            print(finalline)
            print("处理坐标{}:{}".format(lineindex,eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            #print("处理路段{}".format(eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            for subline in finalline:
                for key in eval(filelines[lineindex].strip('\n').split(">>>")[-1]).keys():
                    temsubline = []

                    #此代码块只加入key，不加入完整路线
                    print("路段:{}匹配key:{}".format(subline[-1], key))
                    # 只需要查看subline的最后一个路段与路段key是否连通即可，因为subline的连通性是通过测试的
                    connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    #connectroute = -1
                    if connectroute !=0 and connectroute!= 1:   #表中没有记录 再用简易导航
                        connectroute = MapNavigation.waytoway(subline[-1], key)  # 为列表
                    if connectroute:
                        temsubline = copy.deepcopy(subline)
                        temsubline.append(key)  # 只加入轨迹点所属路段，而不加入这两个路段走通的路线
                        templine.append(temsubline)
                    else:
                        # 此路线不连通，舍弃当前路段key
                        pass
                    """
                    #此代码块是加入完整路线
                    #connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    #connectroute = -1
                    connectroute = MapNavigation.Nodirectionwaytoway(subline[-1], key)  # 为列表
                    if subline[-1] == key:
                        temsubline = copy.deepcopy(subline)
                        templine.append(temsubline)
                    #elif connectroute !=0 and connectroute!= 1:   #表中没有记录 再用简易导航
                        #connectroute = MapNavigation.Nodirectionwaytoway(subline[-1], key)  # 为列表
                    elif connectroute:
                        #路段可连通
                        temsubline = copy.deepcopy(subline)
                        temsubline.extend(connectroute[1:])   #将走通的路线加入到子路线，扩展当前路线
                        templine.append(temsubline)
                    else:pass
                    """

                    # print(temsubline)
                    # print(templine)
            finalline.clear()
            #print(templine)
            finalline = Common_Functions.DoubleDel(templine) #去相邻重复 再去重
            finalline = Common_Functions.Main_Auxiliary_road(finalline)   #去除头尾路段一样的候选路线，路线只有一个路段 不会处理
            #print(finalline)
            finalline = Common_Functions.Start_End(finalline)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            finalline = Common_Functions.Sequential_subset(finalline)  # 最后去路线（至少两个及以上的其他路线是其前缀）
        print("共选出{}条路".format(len(finalline)))
        for sub in finalline:
            file.write(str(sub) + "\n")
            file.flush()
        print(finalline)
        file.close()
def SelectFinalRoutes(candidatewaypath,savefinalroutespath):
    """
    本函数与SelectFinalRoute功能相同，只是本函数处理完整的轨迹时，如果大于50.会重新开始计算最大连通性
    根据坐标点的候选路段选出路网的匹配路线
    保存格式为：车辆名：路线（如果不确定，可能为多条），车辆名为txt文件名
    :param candidatewaypath:  坐标点候选路段的txt文件路径，如H:\\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt
    :param savefinalroutespath: 最终路线保存路径
    :return:
    """
    #file = open("H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\\334e4763-f125-425f-ae42-8028245764fe.txt", 'a')
    max_connect = 0
    (tempath, tempfilename) = os.path.split(candidatewaypath)  # tempfilename为txt文件名（包含后缀）
    (trunkname, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    savetxtfilename = trunkname +'.txt'
    file = open(os.path.join(savefinalroutespath,savetxtfilename), 'a')
    with open(candidatewaypath) as candidatewayfile:
        filelines = candidatewayfile.readlines()
        linesnum = len(filelines)
        finalline = []     #存储最终路线，可能为多条，随着坐标点的迭代，会变化，直到处理完最有一个坐标点
        for key in eval(filelines[0].strip('\n').split(">>>")[-1]).keys():
            finalline.append([key])
        #print(finalline)
        # 遍历每个坐标点的候选路段
        print("需要处理坐标数为：{}".format(linesnum))
        for lineindex in range(1,linesnum):
            templine = []   #存储临时路线
            # 遍历到最后一行
            print(len(finalline))
            print(finalline)
            print("处理坐标{}:{}".format(lineindex,eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            #print("处理路段{}".format(eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            for subline in finalline:   #遍历每一条的候选路线
                for key in eval(filelines[lineindex].strip('\n').split(">>>")[-1]).keys(): #遍历每个轨迹点的候选路段
                    temsubline = []

                    #此代码块只加入key，不加入完整路线
                    print("路段:{}匹配key:{}".format(subline[-1], key))
                    # 只需要查看subline的最后一个路段与路段key是否连通即可，因为subline的连通性是通过测试的
                    connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    #connectroute = -1
                    if connectroute !=0 and connectroute!= 1:   #表中没有记录 再用简易导航
                        connectroute = MapNavigation.waytoway(subline[-1], key)  # 为列表
                    if connectroute:
                        temsubline = copy.deepcopy(subline)
                        temsubline.append(key)  # 只加入轨迹点所属路段，而不加入这两个路段走通的路线
                        templine.append(temsubline)
                    else:
                        # 此路线不连通，舍弃当前路段key
                        pass
                    """
                    #此代码块是加入完整路线
                    #connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    #connectroute = -1
                    connectroute = MapNavigation.Nodirectionwaytoway(subline[-1], key)  # 为列表
                    if subline[-1] == key:
                        temsubline = copy.deepcopy(subline)
                        templine.append(temsubline)
                    #elif connectroute !=0 and connectroute!= 1:   #表中没有记录 再用简易导航
                        #connectroute = MapNavigation.Nodirectionwaytoway(subline[-1], key)  # 为列表
                    elif connectroute:
                        #路段可连通
                        temsubline = copy.deepcopy(subline)
                        temsubline.extend(connectroute[1:])   #将走通的路线加入到子路线，扩展当前路线
                        templine.append(temsubline)
                    else:pass
                    """

                    # print(temsubline)
                    # print(templine)
            finalline.clear()
            #print(templine)
            finalline = Common_Functions.DoubleDel(templine) #去相邻重复 再去重
            finalline = Common_Functions.Main_Auxiliary_road(finalline)   #去除头尾路段一样的候选路线，路线只有一个路段 不会处理
            #print(finalline)
            finalline = Common_Functions.Start_End(finalline)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
            finalline = Common_Functions.Sequential_subset(finalline)  # 最后去路线（至少两个及以上的其他路线是其前缀）
            #print(finalline)
            # finalline = Common_Functions.Double_layer_list(templine)  #去重
            # finalline = Common_Functions.Sequential_subset(finalline)  #去除前缀（两个及以上）
            #file.write(str(finalline) + "\n")
            #file.flush()
        print("共选出{}条路".format(len(finalline)))
        for sub in finalline:
            file.write(str(sub) + "\n")
            file.flush()
        print(finalline)
        file.close()
#SelectFinalRoute("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy\\334e4763-f125-425f-ae42-8028245764fe.txt","H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes","final")


def BatchProcesCandidateWay(csvpath,txtpath):
    """
    批量处理所有车辆，找出轨迹点的候补路段
    :param csvpath: 车辆csv路径
    :param txtpath: 候选路段保存路径
    :return:
    """
    if not os.path.isdir(txtpath):
        os.mkdir(txtpath)
    file = open(r"H:\GPS_Data\Road_Network\BYQBridge\Roadmathtest.txt",'r')
    csvnamelist = file.readlines()
    for csvname in csvnamelist:
        name = csvname.strip("\n") + ".csv"
        print(name)
        csvfilepath = os.path.join(csvpath, name)
        FindPointCandidateWay(csvfilepath, txtpath, csvname.strip("\n"))
def BatchSelectFinalRoute(Candidatewaypath,finalroutepath):
    candidatetxts = Common_Functions.findtxtpath(Candidatewaypath)
    for subway in candidatetxts:
        print(subway)
        SelectFinalRoute(subway,finalroutepath)
Candidatewaypath ="H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy"
csvpath = "H:\GPS_Data\Road_Network\BYQBridge\TrunksArea"
areacsvpath = "H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy"
finalroutespath = "H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes"
#BatchSelectFinalRoute(Candidatewaypath,finalroutespath)
#BatchProcesCandidateWay(csvpath,areacsvpath)
#AllwayConn('H:\GPS_Data\Road_Network\BYQBridge\JSON\BigBYCQ\Delfootwayetc\wayslist.json')
#TrajectorySplit("H:\GPS_Data\\20170901\Top20\Meshed\\10706a7b-3d56-4551-9a09-debda7d2c032.csv","H:\GPS_Data\Road_Network\BYQBridge\SplitRoadMatch")