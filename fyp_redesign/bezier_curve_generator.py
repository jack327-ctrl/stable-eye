import numpy as np
import matplotlib.pyplot as plt

# find the a & b points
def get_bezier_coef(points):
    # since the formulas work given that we have n+1 points
    # then n must be this:
    n = len(points) - 1

    # build coefficents matrix
    C = 4 * np.identity(n)
    np.fill_diagonal(C[1:], 1)
    np.fill_diagonal(C[:, 1:], 1)
    C[0, 0] = 2
    C[n - 1, n - 1] = 7
    C[n - 1, n - 2] = 2

    # build points vector
    P = [2 * (2 * points[i] + points[i + 1]) for i in range(n)]
    P[0] = points[0] + 2 * points[1]
    P[n - 1] = 8 * points[n - 1] + points[n]

    # solve system, find a & b
    A = np.linalg.solve(C, P)
    B = [0] * n
    for i in range(n - 1):
        B[i] = 2 * points[i + 1] - A[i + 1]
    B[n - 1] = (A[n - 1] + points[n]) / 2

    return A, B

# returns the general Bezier cubic formula given 4 control points
def get_cubic(a, b, c, d):
    return lambda t: np.power(1 - t, 3) * a + 3 * np.power(1 - t, 2) * t * b + 3 * (1 - t) * np.power(t, 2) * c + np.power(t, 3) * d

# return one cubic curve for each consecutive points
def get_bezier_cubic(points):
    A, B = get_bezier_coef(points)
    return [
        get_cubic(points[i], A[i], B[i], points[i + 1])
        for i in range(len(points) - 1)
    ]

# evalute each cubic curve on the range [0, 1] sliced in n points
def evaluate_bezier(points, n):
    curves = get_bezier_cubic(points)
    return np.array([fun(t) for fun in curves for t in np.linspace(0, 1, n)])

def get_coordinates(points,step_number):
    print(points)
    print('************')
    if len(points)==2:
        print('step_number')
        print(step_number)
        point_tmp1=points[0]
        point_tmp2=points[1]
        point_a_x,point_a_y=point_tmp1
        point_b_x,point_b_y=point_tmp2
        point_x,point_y=int((point_b_x-point_a_x)/2)+5,int((point_b_y-point_a_y)/2)+5
        point=[point_x,point_y]
        points.clear()
        points.append(point_tmp1)
        points.append(point)
        points.append(point_tmp2)
        
    point=np.array(points)
    path = evaluate_bezier(point, int(step_number/2))
    final_coordinates=[[int(points[0]),int(points[1])] for points in path.tolist()]
    print(final_coordinates)
    return final_coordinates


# points = np.random.rand(5, 2)
# point_a=[[1,1],[50,90],[100,100]]
# c=get_coordinates(point_a,10)
# for index in c:
#     print(index)

# points=np.array(point_a)
# print(points)
# print(type(points))
# fit the points with Bezier interpolation
# use 50 points between each consecutive points to draw the curve
# path = evaluate_bezier(points, 5)

# # extract x & y coordinates of points
# x, y = points[:,0], points[:,1]
# px, py = path[:,0], path[:,1]
# print(points)
# print(path)

# cd=path.tolist()
# print(cd)
# b=[[int(points[0]),int(points[1])] for points in path.tolist()]
# print(b)
# print(len(path))
# print('------------')

# # plot
# plt.figure(figsize=(11, 8))
# plt.plot(px, py, 'b-')
# plt.plot(x, y, 'ro')
# plt.show()