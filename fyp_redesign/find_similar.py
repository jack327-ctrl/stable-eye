import numpy as np
import similaritymeasures
import matplotlib.pyplot as plt

def fine_similar(x,y,z,x1,y1,z1):
	
	# Generate random experimental data
	# x = np.random.random(100)
	# y = np.random.random(100)

	exp_data = np.zeros((len(x), 3))
	print(exp_data.shape)
	exp_data[:, 0] = x
	exp_data[:, 1] = y


	# Generate random numerical data

	num_data = np.zeros((len(x1), 3))
	print(num_data.shape)
	num_data[:, 0] = x1
	num_data[:, 1] = y1




	# quantify the difference between the two curves using
	# Curve Length based similarity measure
	cl = similaritymeasures.curve_length_measure(exp_data, num_data)

	exp_data[:, 0] = x
	exp_data[:, 1] = z

	num_data[:, 0] = x1
	num_data[:, 1] = z1


	cl1 = similaritymeasures.curve_length_measure(exp_data, num_data)

	exp_data[:, 0] = y
	exp_data[:, 1] = z

	num_data[:, 0] = y1
	num_data[:, 1] = z1


	cl2 = similaritymeasures.curve_length_measure(exp_data, num_data)


	ctotal = (cl + cl1 + cl2)/3 


	# print the results
	print(ctotal)
	return ctotal

if __name__ == '__main__':
	
	x = [1,2,5,4,5]
	y = [5,4,3,2,1]
	z = [1,2,3,4,5]

	x1 = [1,2,5,4,5]
	y1 = [5,4,3,2,1]
	z1 = [3,4,5,600,7]

	fine_similar(x,y,z,x1,y1,z1)