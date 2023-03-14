import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import os
from os import path
import re
import sys
import time
import multiprocessing
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


a = 1.932
b = 10.729
c = 17.937
t = 1.912

consts = [a,b,c,t]

a_std_rel = 0.017
b_std_rel = 0.176
c_std_rel = 0.650
t_std_rel = 0.343

# a_std_rel = 0.097
# b_std_rel = 0.176
# c_std_rel = 0.650
# t_std_rel = 0.343

std_rels = [a_std_rel, b_std_rel, c_std_rel, t_std_rel]

dir_out = "./test/cal_mat_sim/"
matrix_names = ["a.txt", "b.txt", "c.txt", "t.txt"]

def create_const_matrix(const, matrix_width = 256, matrix_height = 256):

	matrix = np.empty((matrix_width, matrix_height))

	for i in range(len(matrix)):
		for j in range(len(matrix[i])):
			matrix[i][j] = const

	return matrix

def write_matrix_file(matrix, file_path_name):

	try:
		with open(file_path_name, 'w') as file_out:
			for i in range(len(matrix)):
				for j in range(len(matrix[i])):
					file_out.write("%.5f " % (matrix[i][j]))
				file_out.write("\n")

	except IOError:
		print("Can not open file: " + file_path_name )	
		return -1
	print("Matrix exported into file: " + file_path_name)
	return 0



def write_const_matrix_file(const, file_path_name, matrix_width = 256, matrix_height = 256):

	try:
		with open(file_path_name, 'w') as file_out:
			for i in range(matrix_height):
				for j in range(matrix_width):
					file_out.write("%.5f " % (const))
				file_out.write("\n")

	except IOError:
		print("Can not open file: " + file_path_name )	
		return -1
	print("Matrix exported into file: " + file_path_name)
	return 0

def write_gauss_matrix_file(mu, sigma, file_path_name, matrix_width = 256, matrix_height = 256):

	pix_val = np.random.normal(mu, sigma, matrix_width*matrix_height)

	try:
		with open(file_path_name, 'w') as file_out:
			for i in range(matrix_height):
				for j in range(matrix_width):
					file_out.write("%.5f " % (pix_val[i + j*matrix_width]))
				file_out.write("\n")

	except IOError:
		print("Can not open file: " + file_path_name )	
		return -1
	print("Matrix exported into file: " + file_path_name)
	return 0	

if __name__ == '__main__':

	# Simple constant val into each pixel
	# for i in range(len(consts)):
	# 	rc = write_const_matrix_file(consts[i], dir_out + matrix_names[i])
	# 	if rc:
	# 		print("Export matrix into file failed.")


	# Pixel values are geenrated based on Gauss
	for i in range(len(consts)):
		rc = write_gauss_matrix_file(consts[i], abs(std_rels[i]*consts[i]), dir_out + matrix_names[i])
		if rc:
			print("Export matrix into file failed.")			