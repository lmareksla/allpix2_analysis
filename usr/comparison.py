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

sys.path.append("/mnt/MainDisk/Soubory/Analysis/AllPix2/convert_ascii_t3pa/")
import convert_ascii_t3pa as con


do_conversion = True
do_clustering = True
do_comparison = True


var_key = "E" 
min_val = 15
max_val = 50
bin_width = 0.5

filter_var_key = "Size"
filter_max_val = 2
filter_min_val = 2

colors = ["C1", "C0", "C6"]

dir_data = 	"./test/comparison_xray_24keV/"
dir_out = 	"./usr/out_comparison/"
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

		self.hist_mean = 0
		self.hist_std = 0


data_1 = Data("", 							"RealMeas_24keV.t3pa", 		"RealMeas_24keV", 		"Measurement", 							dir_data + "cal_mat_meas")
data_2 = Data("PixelHitCharge_24keV.txt", 	"PixelHit_24keV.t3pa", 		"PixelHit_24keV", 		"Full simulation with CSA and physics", dir_data + "cal_mat_sim")
data_3 = Data("PixelHitCharge_24keV.txt", 	"PixelCharge_24keV.t3pa", 	"PixelCharge_24keV", 	"Only charge/only physics without CSA",  con_is_charge = True)

data = [  data_1, data_2, data_3 ]

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

def filter_data_frame(data_frame, var_key, min_val, max_val):
	return data_frame.loc[(data_frame[var_key] >= min_val) & (data_frame[var_key] <= max_val)] 	

if do_comparison:

	hist_bins = np.arange(min_val, max_val, bin_width)

	for dt in data:
		dt.elist = pd.read_csv(dt.dir + dt.elist_name + ".elist2", sep="\t", header=[0], skiprows = [1])

		if dt.is_charge:
			dt.elist = convert_charge_energy(dt.elist)

		dt.elist = filter_data_frame(dt.elist, "E", 1e-10, 1e200)

		if len(filter_var_key) != 0:
			dt.elist = filter_data_frame(dt.elist, filter_var_key, filter_min_val, filter_max_val)

		dt.hist_bin, dt.hist_count = np.histogram(dt.elist[var_key], bins = hist_bins)
		dt.hist_mean = dt.elist[var_key].mean()
		dt.hist_std = dt.elist[var_key].std()

# Compare created histograms

def norm_hist(bins):	
	bins = bins / np.linalg.norm(bins)
	return bins

def norm_max_hist(bins):	
	bins = bins / np.max(bins)
	return bins


def plot_hist(bins, counts, color, legend_label):
	bins = np.append(bins, 0)	
	plt.hist(x=counts, bins=counts, weights=bins, color=color, histtype='step', 
				linewidth=1.6, label=legend_label, alpha = 0.8)

if do_comparison:

	for i in range(len(data)):
		data[i].hist_bin = norm_max_hist(data[i].hist_bin)
		label = data[i].dsc + " , mean = " + "%.2f" % (data[i].hist_mean) + " , std = " + "%.2f" % (data[i].hist_std)
		plot_hist(data[i].hist_bin, data[i].hist_count, colors[i], label)

	plt.ylim(0, 1.3)
	plt.grid(visible = True, color ='grey',  linestyle ='-.', linewidth = 0.5,  alpha = 0.6) #Grid on background
	plt.title("Comparison between simulations and measurement") #Add legend into plot	
	plt.legend(title="") #Add legend into plot	
	plt.xlabel(var_key, fontsize=12)  #Set label of X axis
	plt.ylabel("N norm to max [-]", fontsize=12)  #Set label of Y axis
	# plt.yscale('log')
	# plt.xscale('log')
	plt.savefig(dir_out + "comparison.png", dpi=600) #Save plot into FileOut_PathName
	plt.show()


# plt.hist2d(data[2].elist["E"], data[2].elist["Size"], bins=[100,10], range=[[15,50], [0,10]], norm=matplotlib.colors.LogNorm())
# # plt.zscale('log')
# plt.show()