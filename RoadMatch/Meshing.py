# -*- coding: utf-8 -*-
# @Time    : 2019/6/18 15:42
# @Author  : WHS
# @File    : Meshing.py
# @Software: PyCharm
import pandas as pd
import datetime
import math
import os
def Meshed(filepath,savepath,filename):
    """

    :param filepath: csv文件
    :param savepath: 保存路径
    :param filename: 保存的文件名
    :return:
    """
    if not os.path.isdir(savepath):
        os.mkdir(savepath)
    df = pd.read_csv(filepath, header=None,
                     usecols=[0, 1, 2, 3],encoding='utf-8')
    if df.nunique()[1] < 5 or df.nunique()[2] < 5:
        print("*********该车辆坐标点过少，没有网格化**********")
    else:
        # df = df.iloc[:, 2].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S'))
        df.iloc[:, 1] = pd.to_datetime(df.iloc[:, 1], format="%Y%m%d ", errors='coerce')
        start = datetime.datetime.strptime("2000-01-01", '%Y-%m-%d')
        end = datetime.datetime.strptime("2099-12-31", '%Y-%m-%d')
        df = df.dropna(axis=0, how='any')  # 删除表中含有任何NaN的行 ,subset=[1]可添加 只关注时间这一列，不添加也会处理其他列为空的行
        df = (df[(df.iloc[:, 1] >= start) & (df.iloc[:, 1] <= end)])  # 筛选某个是时间段
        df = df[
            (df.iloc[:, 2] < 118) & (df.iloc[:, 2] > 115) & (df.iloc[:, 3] < 42) & (df.iloc[:, 3] > 39)]  # 去除北京外GPS坐标
        df = df.sort_values(by=1)  # 时间排序
        row = 0
        df[4] = None  # 添加列
        df[5] = None
        for num in df.iloc[:, 0]:
            x_grid = math.ceil((df.iloc[row, 2] - 115) / 0.001)  # x方向格子编号
            y_grid = math.ceil((df.iloc[row, 3] - 39) / 0.001)  # y方向格子编号
            df.iloc[row, 4] = str(x_grid)
            df.iloc[row, 5] = str(y_grid)
            row += 1
        filenames = filename + ".csv"
        resultpath = os.path.join(savepath, filenames)
        df.to_csv(resultpath, index=0, header=0, encoding='utf_8_sig')
        print("**********网格化完成**********")