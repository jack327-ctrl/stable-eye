import numpy as np
# import matplotlib.pyplot as plt



def get_coordinate(points,step_number,gap_step_l):
    # print('0000000000000000000*********************')
    # print(points)
    # print(step_number)
    # print('0000000000000000000*********************')
    # step_number=step_number*2
    gaps = (len(points)-1)         #间隔有多少个
    # every_gap_step = int(step_number/gaps)+1


    frames_range = gap_step_l[-1] - gap_step_l[0]
    # print("frames_range is: ")
    # print(frames_range)
    gap_arr = []
    
    for index in range(0,len(gap_step_l)):
        if(index != len(gap_step_l)-1):
            gap_arr.append(int(step_number*(gap_step_l[index+1]-gap_step_l[index])/frames_range))


    # print(gap_arr)
            



    print('get start')
    new_arrage_arr = []        
    for x in range(len(points)):
        new_arrage_arr.append(points[x])
        if x != len(points)-1:
            adder1 = int((points[x+1][0] - points[x][0])/gap_arr[x])
            adder2 = int((points[x+1][1] - points[x][1])/gap_arr[x])         
            for i in range(1,gap_arr[x]):
                new_arrage_arr.append([points[x][0]+i*adder1,points[x][1]+i*adder2])
                # print("i: %d",i)
    # print('linear_generate999999999999999999999999999999999999999999999999999999')
    print(new_arrage_arr)
    # print('linear_generate999999999999999999999999999999999999999999999999999999')
    return new_arrage_arr  
        




# points = np.random.rand(5, 2)
# point_a=[[1,1],[50,90],[100,100]]
# new_arrage_arr=get_coordinates(point_a,10)


# points=np.array(point_a)
# new_arrage_arr=np.array(new_arrage_arr)

# # print(points)
# # print(type(points))
# # fit the points with Bezier interpolation
# # use 50 points between each consecutive points to draw the curve


# # extract x & y coordinates of points
# # print(new_arrage_arr)
# # print(points)
# x, y = points[:,0], points[:,1]

# px, py = new_arrage_arr[:,0], new_arrage_arr[:,1]
# print(points)
# print(new_arrage_arr)



# # plot
# plt.figure(figsize=(11, 8))
# plt.plot(px, py, 'b-')
# plt.plot(x, y, 'ro')
# plt.show()
# if __name__ == '__main__':
# 	a = [[1,1],[100,100],[200,200]]
# 	c = 10

# 	d = [0,100,500]
# 	print(len(d))
# 	result = get_coordinate(a,c,d)

# 	print(result)
	