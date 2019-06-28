# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 15:37
# @Author  : WHS
# @File    : MainFunc.py
# @Software: PyCharm
import os
from RoadMatch import RoadMatching
from RoadMatch import Common_Functions
def Batchprocess(sourcecsvpath,splitsavepath,candidatewaypath):
    if not os.path.isdir(splitsavepath):
        os.mkdir(splitsavepath)
    sourcecsvfilelist = Common_Functions.findcsvpath(sourcecsvpath)   #找出所有的网格化之后的单车文件路径
    # for singlefile in sourcecsvfilelist:
    #     RoadMatching.TrajectorySplit(singlefile,splitsavepath)    #完整轨迹分段
    folderlist = os.listdir(splitsavepath)    #文件夹列表
    print(folderlist)
    #dicflag = {00000000:"BreakPoint"}
    for folder in folderlist:
        tempath = os.path.join(splitsavepath,folder)
        if os.path.isdir(tempath):
            print(f"正在处理车辆{folder}")
            if folder =="10706a7b-3d56-4551-9a09-debda7d2c032":
                continue
            partcsvlists = Common_Functions.findcsvpath(tempath)  #每个文件夹中的分段轨迹csv文件
            for index in range(len(partcsvlists)):
                RoadMatching.FindPointCandidateWays(partcsvlists[index],candidatewaypath,folder)
                txtname = folder + ".txt"
                if index!=len(partcsvlists)-1:
                    with open(os.path.join(candidatewaypath, txtname), 'a') as file:
                        file.write("PointIDCandidateWay>>>BreakPoint\n")
        else:
            pass



# if __name__ == '__main__':
#     sourcecsvpath = "H:\GPS_Data\\20170901\Top20\Meshed"
#     splitsavepath = "H:\GPS_Data\Road_Network\BYQBridge\SplitRoadMatch"
#     candidatewaypath ="H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\FullTrack"
#     Batchprocess(sourcecsvpath, splitsavepath,candidatewaypath)
    #RoadMatching.SelectFinalRoute("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\FullTrack\\10706a7b-3d56-4551-9a09-debda7d2c032.txt",
                                  #"H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\FullTrack")
sourcecsvpath = "H:\GPS_Data\\20170901\Top20\Meshed"
splitsavepath = "H:\GPS_Data\Road_Network\BYQBridge\SplitRoadMatch"
candidatewaypath ="H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\FullTrack"
#RoadMatching.TrajectorySplit("H:\GPS_Data\\20170901\Top20\Meshed\\d715ea8d-7059-423a-893d-5792ec4d0fbf.csv",splitsavepath)
#fdba1f79-6a58-4b2d-abd2-b2f37dd228d0
#d715ea8d-7059-423a-893d-5792ec4d0fbf
Batchprocess(sourcecsvpath, splitsavepath,candidatewaypath)