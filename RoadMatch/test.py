# -*- coding: utf-8 -*-
# @Time    : 2019/6/20 13:52
# @Author  : WHS
# @File    : test.py
# @Software: PyCharm
import math,os,copy
from RoadMatch import Common_Functions,MapNavigation
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
    print(min_x,max_x,min_y,max_y)
    if (coordinate1[0]-coordinate2[0])==0:  # 此线垂直x轴
        distance = abs(coordinate3[0]-coordinate1[0])
        if min_y <= coordinate3[2] <= max_y:
            print(distance)
            return distance
        else:
            return float('inf')
    elif (coordinate1[1]-coordinate2[1]) == 0:#垂直y轴
        distance = abs(coordinate3[1]-coordinate1[1])
        if min_x <= coordinate3[1] <= max_y:
            print(distance)
            return distance
        else:
            return float('inf')
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
            print(distance)
            return distance
        else:
            return float('inf')
#print(Calcul_Dis_Foot([116.4923876,39.7435848],[116.4976448,39.7431262],[116.507495,39.742463]))
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
    max_connect = 0  #记录计算最大连通的轨迹点数
    (tempath, tempfilename) = os.path.split(candidatewaypath)  # tempfilename为txt文件名（包含后缀）
    (trunkname, extension) = os.path.splitext(tempfilename)  # filename 为传入的csv文件名 extension为后缀
    savetxtfilename = trunkname +'.txt'
    Resetflag = 0  #标记最终路段是否重新开始计算
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
            print(f"正在处理第{lineindex+1}个坐标")
            if filelines[lineindex].strip('\n').split(">>>")[-1]=="BreakPoint":  #轨迹分段，分开计算
                file.write("New_Road\n")
                for sub in finalline:
                    file.write(str(sub) + "\n")
                    file.flush()
                Resetflag = 1  #标记从下一个点要重新开始匹配轨迹了
                max_connect = 0
                continue
            if max_connect==100:
                file.write("New_Road\n")
                for sub in finalline:
                    file.write(str(sub) + "\n")
                    file.flush()
                Resetflag = 1 #标记从下一个点要重新开始匹配轨迹了
                max_connect = 0
                continue
            if Resetflag==1:
                finalline.clear()
                for key in eval(filelines[lineindex].strip('\n').split(">>>")[-1]).keys():
                    finalline.append([key])
                Resetflag = 0
                continue
            templine = []   #存储临时路线
            #print("处理坐标{}:{}".format(lineindex,eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            #print("处理路段{}".format(eval(filelines[lineindex].strip('\n').split(">>>")[-1])))
            connect_next_flag = 0  #记录下一步是否能有能走通的路段
            for subline in finalline:   #遍历每一条的候选路线
                for key in eval(filelines[lineindex].strip('\n').split(">>>")[-1]).keys(): #遍历每个轨迹点的候选路段
                    #此代码块只加入key，不加入完整路线
                    print("路段:{}匹配key:{}".format(subline[-1], key))
                    # 只需要查看subline的最后一个路段与路段key是否连通即可，因为subline的连通性是通过测试的
                    connectroute = Common_Functions.InquireConn(subline[-1], key,"connects")   #先查表
                    #connectroute = -1
                    if connectroute !=0 and connectroute!= 1:   #表中没有记录 再用简易导航
                        connectroute = MapNavigation.waytoway(subline[-1], key)  # 为列表
                    if connectroute:
                        connect_next_flag = 1
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
            if connect_next_flag==0:  #所有的候选路线与当前轨迹点的候选路段均不能相通，跳过此轨迹点
                pass
            else:
                finalline.clear()
                # print(templine)
                finalline = Common_Functions.DoubleDel(templine)  # 去相邻重复 再去重
                finalline = Common_Functions.Main_Auxiliary_road(finalline)  # 去除头尾路段一样的候选路线，路线只有一个路段 不会处理
                # print(finalline)
                #finalline = Common_Functions.Start_End(finalline)  # 对于[wayid1,wayid2,wayid3] [wayid1,wayid4,wayid5,wayid3]  去除路段多的,如果包含路段数量一致 暂不处理
                finalline = Common_Functions.Sequential_subset(finalline)  # 最后去路线（至少两个及以上的其他路线是其前缀）
                max_connect += 1
        file.write("New_Road\n")
        for sub in finalline:
            file.write(str(sub) + "\n")
            file.flush()
        file.close()
SelectFinalRoutes("H:\GPS_Data\Road_Network\BYQBridge\CandidateWay\FullTrack\\d715ea8d-7059-423a-893d-5792ec4d0fbf.txt",
                                  "H:\GPS_Data\Road_Network\BYQBridge\FinalRoutes\FullTrack")
# [256265174, 229521327, 258296019, 317889645, 317913828, 29136270, 152616718, 152616724, 437527024,
#  606768167, 606768159, 466839068, 508312922, 466839072, 466839071, 508147676, 508147677, 508312925,
#  508312926, 466839061, 466839062, 466839044, 466839045, 466839039, 332203313, 332203315, 332203310]
