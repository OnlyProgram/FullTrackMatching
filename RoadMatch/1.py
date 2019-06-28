# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 12:38
# @Author  : WHS
# @File    : Project.py
# @Software: PyCharm
"""
matplotlib轨迹可视化，输入csv文件，输入：对应轨迹
"""
from matplotlib import pyplot as plt
import pandas as pd
#df = pd.read_csv(r'H:\GPS_Data\20170901\Top20\AllFilled\865242ce-d55e-47e7-ae2b-ef060ad3312f.csv',header=None)
df = pd.read_csv(r'H:\GPS_Data\\20170901\\text\Trunk0803\LSHY_20180803_PX_1\AllFilled\Combine\\conbine.csv',usecols=[2,3,4],names=['lon','lat','Flag'])  #补点文件
#df = pd.read_csv(r'H:\GPS_Data\\20170901\Top20\classRoute\\4e3dae9e-6dc6-4fe0-875d-dc29af45ab5b-1569-832-1576-829.csv',names=['lon','lat','Flag'])  #路线类别
#df = pd.read_csv(r'H:\GPS_Data\20170901\Top20\AllFilled\\4e3dae9e-6dc6-4fe0-875d-dc29af45ab5b.csv',names=['lon','lat','Flag'])  #补点文件,含原始轨迹
plt.grid(True)
plt.xlabel('lon')
plt.ylabel('lat')
plt.title('Road')
print(df.Flag.unique())
color_map = dict(zip(df.Flag.unique(),['black','red','blue']))
#color_map = dict(zip(df.Flag.unique(),['yellow','red','blue','black']))#[ 1.  2.  0. -1.] 路线类别，，起始点终点，原始点
for species, group in df.groupby('Flag'):
    plt.scatter(group['lon'], group['lat'],
               color=color_map[species],
               label=species,marker='.')
plt.show()