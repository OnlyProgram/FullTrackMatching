# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 15:46
# @Author  : WHS
# @File    : CodeRoadMatching.py
# @Software: PyCharm
"""
通过路网编码实现候选路段的查找
"""
import os
from RoadMatch import GridCode,Common_Functions,GridMapNavigation,BigGridCode
import pandas as pd
import copy
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
        predict = eval(filelines[0].strip('\n').split(">>>")[-1])
        # 遍历每个坐标点的候选路段
        print(f"需要处理坐标数为：{linesnum}")

        for lineindex in range(1,linesnum):
            templine = []   #存储临时路线
            curdict = eval(filelines[lineindex].strip('\n').split(">>>")[-1])
            flag = 0  #标记之前的路线与当前轨迹点的所有候选路段是否能连通，不能连通，舍弃该轨迹点
            newdic = {}
            for subline in finalline:   #遍历每一条的候选路线
                #print(f"ID{lineindex-1}:{predict},{curdict}")
                for key in curdict.keys(): #遍历每个轨迹点的候选路段
                    connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    if connectroute != 0:
                        #print(subline[-1], predict[subline[-1]], key, curdict[key])
                        connectroute = GridMapNavigation.CandidateWay_Connect(subline[-1], predict[subline[-1]], key,
                                                                              curdict[key])  # 双重列表
                        #print(f"next:{connectroute}")
                        if connectroute:
                            flag = 1
                            for line in connectroute:
                                temsubline = copy.deepcopy(subline)
                                temsubline.extend(line)  # 将走通的路线加入到子路线，扩展当前路线
                                templine.append(temsubline)
                                #newdic[line[-1]] = curdict[line[-1]]
                        else:
                            pass
                    else:pass

            if flag == 1:
                finalline.clear()
                predict = curdict
                templine = Common_Functions.DoubleDel(templine)
                templine = Common_Functions.Main_Auxiliary_road(templine)   #去除头尾路段一样的候选路线，路线只有一个路段 不会处理
                templine = Common_Functions.Start_End(
                    templine)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
                Common_Functions.Sequential_subset(finalline)  # 最后去路线（至少两个及以上的其他路线是其前缀）
                for sub in templine:
                    finalline.append(Common_Functions.del_adjacent(sub))
            else:pass
            #print(f"final:{finalline}")
        print("共选出{}条路".format(len(finalline)))
        for sub in finalline:
            print(sub)
            file.write(str(sub) + "\n")
        file.close()
def FindPointCandidateWay_Grid(csvfilepath,candidatewaypath,candidatewayname):
    """
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
        dic = {}
        #candidatacode = BigGridCode.Neighbor(newdf.iloc[row, 1], newdf.iloc[row, 2])  # 查找附近八个区域
        # for subcode in candidatacode:
        #     if subcode:
        #         waysets = list(Common_Functions.GetWay_ByGridCode(subcode[1]))
        #         for subway in waysets:
        #             dic[subway[0]] = subcode[1]
        pointCode = BigGridCode.Encode(newdf.iloc[row, 1], newdf.iloc[row, 2])
        waysets = list(Common_Functions.GetWay_ByGridCode(pointCode[1]))
        if waysets:
            for subway in waysets:
                dic[subway[0]] = pointCode[1]

        #print(f"{newdf.iloc[row, 1]},{newdf.iloc[row, 2]}CandidateWay>>>{str(dic)}")
        if dic:
            file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
    file.close()

def DirectionFindPointCandidateWay_Grid(csvfilepath,candidatewaypath,candidatewayname):
    """
    带方向的候选路段选取
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
        dic = {}
        pointCode = BigGridCode.Encode(newdf.iloc[row, 1], newdf.iloc[row, 2])
        waysets = list(Common_Functions.GetWay_ByGridCode(pointCode[1]))
        if waysets:
            for subway in waysets:
                dic[subway[0]] = pointCode[1]
        #print(f"{newdf.iloc[row, 1]},{newdf.iloc[row, 2]}CandidateWay>>>{str(dic)}")
        if dic:
            file.write("PointID-" + str(row + 1) + "CandidateWay>>>" + str(dic) + "\n")
    file.close()
import time
start = time.time()
#FindPointCandidateWay_Grid("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\b79a4749-6228-4e47-8c1e-4e5c5dce8a53.csv","H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC","b79a4749-6228-4e47-8c1e-4e5c5dce8a53")
#SelectFinalRoutes("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC\\10706a7b-3d56-4551-9a09-debda7d2c032.txt","H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\Grid\BYC")
# for subpath in Common_Functions.findtxtpath("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\\NewStrategy"):
#     (tempath, tempfilename) = os.path.split(subpath)  # tempfilename为txt文件名（包含后缀）
#     (trunkname, extension) = os.path.splitext(tempfilename)  # filename 为文件名 extension为后缀
#     csvfile = trunkname + ".csv"
#     FindPointCandidateWay_Grid(
#         os.path.join("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea",csvfile),
#         "H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC", trunkname)

#最终路线
for subpath in Common_Functions.findtxtpath("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC"):
    print(subpath)
    SelectFinalRoutes(subpath,"H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\Grid\BYC")
#FindPointCandidateWay_Grid("H:\GPS_Data\Road_Network\BYQBridge\TrunksArea\\334e4763-f125-425f-ae42-8028245764fe.csv","H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC","334e4763-f125-425f-ae42-8028245764fe")

#SelectFinalRoutes("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\Grid\BYC\\99b9e495-22f3-4dd2-81e1-a946b3805229.txt","H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\Grid\BYC")

print(time.time()-start)