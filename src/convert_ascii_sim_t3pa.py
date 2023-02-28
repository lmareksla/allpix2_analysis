import os
from os import path
import re
import sys


file_in_name_path = 	"./in/PixelHitCharge_6keV.txt"
file_out_name_path = 	["./out/PixelHit_6keV.t3pa", "./out/PixelCharge_6keV.t3pa"]	# if file contains bot hit and charge then first is hit then charge t3pa file
matrix_width = 			256		# Width of the matrix
toa_step = 				2000	# Offset of individual toa values for different events

def recognize_ascii_file(file_path_name):
	rc = 0

	do_ascii_pxhit = False
	do_ascii_pxcharge = False

	try:
		with open(file_path_name, 'r') as file_in:

			n_line = 0
			for line in file_in:
				n_line += 1

				if "PixelHit" in line:
					print(line)
					do_ascii_pxhit = True
					break

				if "Charge" in line:
					print(line)
					do_ascii_pxcharge = True

				if n_line == 1000:
					break

	except IOError:
		print("Can not open file: " + file_path_name )	
		return (-1, do_ascii_pxhit, do_ascii_pxcharge)

	return (rc, do_ascii_pxhit, do_ascii_pxcharge)

def convert_ascii_pxhit_t3pa(file_in_name_path, file_out_name_path):
	rc = 0

	file_out = open(file_out_name_path ,'w')
	file_out.write("Index\tMatrix\tIndex\tToA\tToT\tFToA\tOverflow\n")

	n_px = 0 			# pixel count starting from 0
	toa_sum = -toa_step	# sum of toa offsets, set to minus of step to start at 0
	n_event = 0			# count of evetns

	try:
		with open(file_in_name_path, 'r') as file_in:
			print("\t* Converting hit file" + file_in_name_path + " into t3pa file " + file_out_name_path)

			for line in file_in:

				if "===" in line:
					n_event += 1
					toa_sum += toa_step

				if "PixelHit" in line:

					line_list=line[9:].split(', ')
					matrix_index = int(line_list[0]) - 1 + (int(line_list[1]) - 1)*(matrix_width)
					toa = toa_sum + int(int(line_list[3])/16) + 1
					ftoa = 16 - int(line_list[3])%16

					file_out.write('{}\t{}\t{}\t{}\t{}\t0\n'.format(
							n_px,			# Index
	                        matrix_index,	# Matrix Index
	                        toa,			# ToA
	                        line_list[2],	# ToT
	                        ftoa 			# fToA
	                        ))

					n_px += 1

	except IOError:
		print("File " + file_in_name_path + " can not be open.")
		return -1

	file_out.close()

	return rc

def write_px_t3pa(px, file_out):
	file_out.write('{}\t{}\t{}\t{}\t{}\t0\n'.format(
			px[0],	# Index
	        px[1],	# Matrix Index
	        px[2],	# ToA
	        px[3],	# ToT
	        px[4] 	# fToA
	        ))

def convert_ascii_pxcharge_t3pa(file_in_name_path, file_out_name_path):
	rc = 0

	file_out = open(file_out_name_path ,'w')
	file_out.write("Index\tMatrix\tIndex\tToA\tToT\tFToA\tOverflow\n")

	n_px = 0 			# pixel count starting from 0
	n_event = -1		# count of evetns, -1 to start at 0 in file reading

	try:
		with open(file_in_name_path, 'r') as file_in:
			print("\t* Converting charge file" + file_in_name_path + " into t3pa file " + file_out_name_path)

			px = [-1, 0, -toa_step, 0, 0]

			for line in file_in:

				if "===" in line:
					n_event += 1
					px[2] += toa_step

				if "Pixel:" in line:
					line_list = re.findall(r'\d+', re.sub("\,|\)|\s", " ", line[8:]))
					px[1] = int(line_list[0]) - 1 + (int(line_list[1]) - 1)*(matrix_width)

				if "Charge:" in line:
					px[3] = int(re.findall(r'\d+', line[7:])[0])
					px[0] += 1
					write_px_t3pa(px, file_out)

			# Write last px
			if len(px) != 0:
				px[0] += 1
				write_px_t3pa(px, file_out)

	except IOError:
		print("File " + file_in_name_path + " can not be open.")
		return -1

	file_out.close()
	return rc


def convert_ascii_t3pa(file_in_name_path, file_out_name_path, do_ascii_pxcharge = False, do_ascii_pxhit = False):
	rc = 0

	print("------------------------------------------------")
	print("CONVERSION ASCII TO T3PA\n")
	print("Input file:\t\t" + file_in_name_path)
	print("Output file:\t\t"); print(file_out_name_path)
	print("Step in ToA offset:\t" + str(toa_step) + "ns")

	if not do_ascii_pxhit and not do_ascii_pxcharge:
		rc, do_ascii_pxhit, do_ascii_pxcharge = recognize_ascii_file(file_in_name_path)

	if rc:
		print("Recognition of file failed")
		return rc

	if do_ascii_pxhit and do_ascii_pxcharge:
		print("\n* File regonized as ASCII with pixel hit and charge.")
	elif do_ascii_pxhit:
		print("\n* File regonized as ASCII with pixel hit.")
	elif do_ascii_pxcharge:
		print("\n* File regonized as ASCII with pixel charge.")
	else:
		print("\n* Unknown format. Processing terminated.")
		return rc

	print("* Converting file.")
	if do_ascii_pxhit and do_ascii_pxcharge:
		rc += convert_ascii_pxhit_t3pa(file_in_name_path, file_out_name_path[0])
		rc += convert_ascii_pxcharge_t3pa(file_in_name_path, file_out_name_path[1])
	elif do_ascii_pxhit:
		rc += convert_ascii_pxhit_t3pa(file_in_name_path, file_out_name_path[0])
	elif do_ascii_pxcharge:
		rc += convert_ascii_pxcharge_t3pa(file_in_name_path, file_out_name_path[0])

	if rc:
		print("Error occured during processing.")
	else:
		print("* Processing finished.")

	return rc	

if __name__ == '__main__':
	convert_ascii_t3pa(file_in_name_path, file_out_name_path)