'''
This file will store some of the paramters of the whole LAAFU program
Author: Robert ZHAO Ziqi
'''

# This controls the ratio of data that will be trained in one iteration of GP
# Used in gaussian_process.py
data_ratio = 0.7

# This controls the number of iterations in GP
# Used in gaussian_process.py
num_ite = 8

# This controls when to discard AP with small number of corresponding positions
# Used in ap_map_rp() in test_gp.py
min_size_to_process = 5 

# This determines whether to consider z value of AP's location or not
# Used in constructor of GP
with_z = 1

# This is the conversion ratio from pixel to meter
# Used in test_gp.py
ptm_ratio = 13.3
