# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 15:46
# @Author  : WHS
# @File    : CodeRoadMatching.py
# @Software: PyCharm
"""
通过路网编码实现候选路段的查找
"""
import os
from RoadMatch import GridCode,Common_Functions
import pandas as pd
def FindPointCandidateWay_Grid(csvfilepath,candidatewaypath,candidatewayname):
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
    newdf = df.drop(drop_list)  # 删除相邻点在10米之内的点
    newdf = newdf.reset_index(drop=True)
    txtname = candidatewayname + ".txt"
    file = open(os.path.join(candidatewaypath,txtname), 'a')
    print("本轨迹段共查找坐标点数为：{}".format(newdf.shape[0]))
    for row in range(newdf.shape[0]):
        point_candidawayList  = []
        pointCode = GridCode.Encode(newdf.iloc[row, 1], newdf.iloc[row, 2])[1]
        print(newdf.iloc[row, 1], newdf.iloc[row, 2])
        waysets = list(Common_Functions.GetWay_ByGridCode(pointCode[1]))
        if waysets:
            point_candidawayList.extend(waysets)
        else:
            candidatacode = GridCode.Neighbor(newdf.iloc[row, 1], newdf.iloc[row, 2])  #查找附近八个区域
            for subcode in candidatacode:
                if subcode:
                    waysets = list(Common_Functions.GetWay_ByGridCode(subcode[1]))
                    point_candidawayList.extend(waysets)
        #file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(set(point_candidawayList)) + "\n")
        print(set(point_candidawayList))
    file.close()

#code = GridCode.Encode(116.438871,39.720601)
#way = Common_Functions.GetWay_ByGridCode('1534')
import time
start = time.time()
FindPointCandidateWay_Grid("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\cc4eb074-0041-4f6a-b553-6722331383e8.csv","H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid","cc4eb074-0041-4f6a-b553-6722331383e8")
print(time.time()-start)