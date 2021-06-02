import random
import sys
from decord import VideoReader
from decord import cpu
import time
from cross_point import *

# directory='E:/电影/[电影天堂www.dy2018.com]毒液HD中英双字.mp4'

# video_meta= VideoReader(directory, ctx=cpu(0))
# print(sys.getsizeof(video_meta))
# print(len(video_meta))
# total_frame_num=len(video_meta)
# file_name=directory.split('/')[-1]

# for index,i in enumerate(range(len(video_meta))):
#     value_1=random.randint(0,1000)*30
#     value_2=random.randint(0,1000)*20
#     value=value_1+value_2
#     print(value)
#     ram=video_meta[value]
# bar=0
# for i in range(50000):
#     if i<10000:
#         print(i)
#         ram=video_meta[i+60000-bar]
#     else:
#         print(i+60000)
#         if i==30000:
#             bar=50000
#         ram=video_meta[i+60000-bar]
        # time.sleep(0.25)

# dictary={}

a=point_base(1,1,'red','-')
b=point_base(10,15,'black','+')
c=point_base(5,15,'blue','+')
tmp={'black':b}

combine={19:tmp}

def compare(component):
    print(component)
    return component
# combine.update(a)
# combine.update(b)

# dictary={1:combine}
# d=sorted(tmp,key=lambda p:tmp[p].x)

print(tmp.items())
# print(dictary[1])
