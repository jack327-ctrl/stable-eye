# -*- coding: utf-8 -*-
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from find_similar import *

def call_3d_graph(x,y,z,x1,y1,z1):
	mpl.rcParams['legend.fontsize'] = 20  # mpl模块载入的时候加载配置信息存储在rcParams变量中，rc_params_from_file()函数从文件加载配置信息
	font = {
	    'color': 'b',
	    'style': 'oblique',
	    'size': 20,
	    'weight': 'bold'
	}
	fig = plt.figure(figsize=(16, 12))  #参数为图片大小
	ax = fig.gca(projection='3d')  # get current axes，且坐标轴是3d的
	ax.set_aspect('auto')  # 坐标轴间比例一致

	ax1 = fig.gca(projection='3d')  # get current axes，且坐标轴是3d的
	ax1.set_aspect('auto')  # 坐标轴间比例一致



	# theta = np.linspace(-8 * np.pi, 8 * np.pi, 100)  # 生成等差数列，[-8π,8π]，个数为100
	# z = np.linspace(-2, 2, 100)  # [-2,2]容量为100的等差数列，这里的数量必须与theta保持一致，因为下面要做对应元素的运算
	# r = z ** 2 + 1
	# x = r * np.sin(theta)  # [-5,5]
	# y = r * np.cos(theta)  # [-5,5]



	ax.set_xlabel("X", fontdict=font)
	ax.set_ylabel("Y", fontdict=font)
	ax.set_zlabel("frame number", fontdict=font)
	similar=fine_similar(x,y,z,x1,y1,z1)
	ax.set_title("Line Plot", alpha=0.5, fontdict=font) #alpha参数指透明度transparent
	ax.plot(x, y, z)
	ax.legend(loc='upper right') #legend的位置可选：upper right/left/center,lower right/left/center,right,left,center,best等等

	ax1.set_title("difference: %f"%(similar), alpha=0.5, fontdict=font) #alpha参数指透明度transparent
	ax1.plot(x1, y1, z1)

	plt.show()


if __name__ == '__main__':
	z = [1,2,3,4]
	x = [1,2,3,4]
	y = [3,2,3,2]


	z1 = [4,3]
	x1 = [1,1]
	y1 = [3,3]

	call_3d_graph(x,y,z,x1,y1,z1)