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

sys.path.append("/mnt/MainDisk/Soubory/Programy/Vlastni/python/aplikace/advacam/dpe/src/")
import run_clusterer as clst

sys.path.append("/mnt/MainDisk/Soubory/Analysis/AllPix2/analysis/src/")
import convert_ascii_sim_t3pa as con

do_conversion = False
do_clustering = False
do_comparison = True


# var_key = "E" 
# min_val = 0
# max_val = 20
# bin_width = 0.5

var_key = "Size" 
min_val = 0
max_val = 10
bin_width = 1

filter_var_key = "Size"
filter_min_val = 1
filter_max_val = 10

colors = ["C1", "C0", "C6"]

dir_data = 	"./test/comparison_xray_6p4keV/"
dir_out = 	"./usr/out_comparison/"
fig_name = 	"comparison_6keV.png"
clusterer = "./bin/clusterer"
rc = 0


class Data(object):
	def __init__(	self, con_ascii_name, con_t3pa_name, con_elist_name, con_dsc, 
					con_calib_dir = "", con_is_charge = False):
		super(Data, self).__init__()

		self.dir = ""
		
		self.ascii_name = con_ascii_name
		self.t3pa_name = con_t3pa_name
		self.elist_name = con_elist_name
		self.calib_dir = con_calib_dir

		self.is_charge = con_is_charge

		self.dsc = con_dsc

		self.elist = pd.DataFrame()			# pandas data frame for elist
		self.hist_bin = np.empty([1])	 	# empty tuple for plt.hist() which returns  (n, bins, patches)
		self.hist_count = np.empty([1])	 	# empty tuple for plt.hist() which returns  (n, bins, patches)
		self.hist_shift = 0
		self.hist_mean = 0
		self.hist_std = 0


data_1 = Data("", 							"RealMeas_6keV.t3pa", 		"RealMeas_6keV", 		"Measurement", 							dir_data + "cal_mat_meas")
# data_2 = Data("PixelHitCharge_6keV.txt", 	"PixelHit_6keV.t3pa", 		"PixelHit_6keV", 		"Full simulation with CSA and physics", dir_data + "cal_mat_sim")
data_3 = Data("PixelHitCharge_6keV.txt", 	"PixelCharge_6keV.t3pa", 	"PixelCharge_6keV", 	"Only charge/only physics without CSA", dir_data + "/../cal_mat_sim",  con_is_charge = True)

# data_1.hist_shift = 0.5


data = [  data_1, data_3 ]

for dt in data:
	dt.dir = dir_data

# Convert data from ASCII AllPix2 to t3pa

if do_conversion:
	for dt in data:
		if len(dt.ascii_name) == 0:
			continue
		rc = con.convert_ascii_t3pa(dt.dir + dt.ascii_name, [dt.dir + dt.t3pa_name], dt.is_charge, not dt.is_charge)

# Process t3pa with clusterer into ClusterLog and Elist

if do_clustering:
	print("------------------------------------------------")
	print("CLUSTERING")

	for dt in data:
		if os.path.isfile(dt.dir + dt.elist_name + ".elist2"):
			print("Removing old elist, it already exists:" + dt.dir + dt.elist_name + ".elist2")
			os.remove(dt.dir + dt.elist_name + ".elist2")

		rc = clst.run_clusterer(clusterer, dt.dir + dt.t3pa_name, dt.dir, dt.calib_dir, "", dt.elist_name)


# Load Elist and convert it to hist and 

def convert_charge_energy(data_frame, e_eh = 0.00364 ):
	data_frame["E"] = data_frame["E"]*e_eh
	return data_frame 

def convert_charge_tot_thl(data_frame, a, b, c, t, thl = 3, e_eh = 0.00364 ):
	data_frame["E"] = data_frame["E"]*e_eh
	return data_frame 

def filter_data_frame(data_frame, var_key, min_val, max_val):
	return data_frame.loc[(data_frame[var_key] >= min_val) & (data_frame[var_key] <= max_val)] 	

if do_comparison:

	hist_bins = np.arange(min_val, max_val, bin_width)

	for dt in data:
		dt.elist = pd.read_csv(dt.dir + dt.elist_name + ".elist2", sep="\t", header=[0], skiprows = [1])

		if dt.is_charge and len(dt.calib_dir) == 0:
			dt.elist = convert_charge_energy(dt.elist)

		dt.elist = filter_data_frame(dt.elist, "E", 1e-10, 1e200)

		if len(filter_var_key) != 0:
			dt.elist = filter_data_frame(dt.elist, filter_var_key, filter_min_val, filter_max_val)

		dt.hist_bin, dt.hist_count = np.histogram(dt.elist[var_key], bins = hist_bins)
		dt.hist_mean = dt.elist[var_key].mean()
		dt.hist_std = dt.elist[var_key].std()

# Compare created histograms

def norm_hist(bins):	
	bins = bins / np.sum(bins)
	return bins

def norm_max_hist(bins):	
	bins = bins / np.max(bins)
	return bins



def shift_histogram(shift, bins, low_edges):
	print("-----------")

	if shift == 0:
		return bins

	low_wdge_min = low_edges[0]
	bin_width = low_edges[1] - low_edges[0]
	i_shift = int(shift/bin_width)

	print(bins)
	print(bin_width)
	print(low_edges)

	for i in range(len(bins)):
		if i+i_shift < len(bins):
			bins[i] = bins[i + i_shift]
		else:
			bins[i] = 0

	print("\t")
	print(bins)
	print(bin_width)
	print(low_edges)

	return bins

def plot_hist(bins, counts, color, legend_label):
	bins = np.append(bins, 0)	
	plt.hist(x=counts, bins=counts, weights=bins, color=color, histtype='step', 
				linewidth=1.6, label=legend_label, alpha = 0.8)

if do_comparison:

	for i in range(len(data)):

		data[i].hist_bin = norm_hist(data[i].hist_bin)
		print(np.sum(data[i].hist_bin))
		# data[i].hist_bin = norm_max_hist(data[i].hist_bin)
		data[i].hist_bin = shift_histogram(data[i].hist_shift, data[i].hist_bin , data[i].hist_count)

		label = data[i].dsc + " , mean = " + "%.2f" % (data[i].hist_mean) + " , std = " + "%.2f" % (data[i].hist_std)
		plot_hist(data[i].hist_bin, data[i].hist_count, colors[i], label)

	plt.ylim(0, 1.3)
	# plt.ylim(1e-4, 1e1)
	plt.grid(visible = True, color ='grey',  linestyle ='-.', linewidth = 0.5,  alpha = 0.6) #Grid on background
	plt.title("Comparison between simulations and measurement") #Add legend into plot	
	plt.legend(title="") #Add legend into plot	
	plt.xlabel(var_key, fontsize=12)  #Set label of X axis
	plt.ylabel("N norm to max [-]", fontsize=12)  #Set label of Y axis
	# plt.yscale('log')
	# plt.xscale('log')
	plt.savefig(dir_out + fig_name, dpi=600) #Save plot into FileOut_PathName
	plt.show()


# plt.hist2d(data[2].elist["E"], data[2].elist["Size"], bins=[100,10], range=[[15,50], [0,10]], norm=matplotlib.colors.LogNorm())
# # plt.zscale('log')
# plt.show()