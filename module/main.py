# This is a demo program for LAAFU with gaussian process and compressive sensing.
# Most of the parts are converted from LIN Wenbin's C++ version. Hope this python
# version is easier to use, develop and maintain.
#
# Author: Robert ZHAO Ziqi

from gaussian_process import gp
from utils import mkdir
import settings

import random
import shutil
import os.path
import matplotlib.pyplot as plt
import numpy as np

def ap_map_rp(file_path):
    """
    Args:
        file_path (str):
    """
    min_size_to_process = settings.min_size_to_process # change this to fit the data

    with open(file_path, 'r') as p_file:
        ap_rf = {}  # mac->{(x,y)->rssi}

        while True:
            line = p_file.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            # first record of each line. x,y,direction,id
            info = line.split(" ")[0]
            # convert pixel into meter 
            x = float(info.split(",")[0]) / settings.ptm_ratio
            y = float(info.split(",")[1]) / settings.ptm_ratio
            mac_rssi_list = line.split(" ")[1:]
            for mac_rssi in mac_rssi_list:
                # mac,rssi,std,freq
                mac = mac_rssi.split(",")[0]
                rssi = mac_rssi.split(",")[1]
                if mac not in ap_rf:
                    ap_rf[mac] = {}
                ap_rf[mac]["{}-{}".format(x,y)] = float(rssi)

    # ignore those APs with too few data
    delete_list = []
    for mac_key in ap_rf.keys():
        if len(ap_rf[mac_key]) < min_size_to_process:
            delete_list.append(mac_key)
    for key in delete_list:
        del ap_rf[key]

    # use filename as a new folder
    io_dir = os.path.splitext(file_path)[0]
    mkdir(io_dir)

    for mac_key in ap_rf.keys():
        # use AP's mac address as a file name
        io_file = os.path.join(io_dir, "{}.txt".format(mac_key))
        with open(io_file, 'w') as out_file: 
            for pos_key in ap_rf[mac_key].keys():
                [x,y] = pos_key.split("-")
                rssi = ap_rf[mac_key][pos_key]
                out_file.write("{} {} {}\n".format(x,y,rssi))

def ap_map_rp_std(file_path):
    """
    Args:
        file_path (str):
    """

    min_size_to_process = settings.min_size_to_process # change this to fit the data

    with open(file_path, 'r') as p_file:
        ap_rf = {}

        while True:
            line = p_file.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            # first record of each line. x,y,direction,id
            info = line.split(" ")[0]
            x = float(info.split(",")[0])
            y = float(info.split(",")[1])
            mac_rssi_list = line.split(" ")[1:]
            for mac_rssi in mac_rssi_list:
                # mac,rssi,std,freq
                mac = mac_rssi.split(",")[0]
                rssi = float(mac_rssi.split(",")[1])
                std = float(mac_rssi.split(",")[2])
                if mac not in ap_rf:
                    ap_rf[mac] = {}
                ap_rf[mac]["{}-{}".format(x,y)] = [rssi, std]

    # ignore those APs with too few data
    delete_list = []
    for mac_key in ap_rf.keys():
        if len(ap_rf[mac_key]) < min_size_to_process:
            delete_list.append(mac_key)
    for key in delete_list:
        del ap_rf[key]

    # use filename as a new folder
    io_dir = os.path.splitext(file_path)[0]
    mkdir(io_dir)

    for mac_key in ap_rf.keys():
        # use AP's mac address as a file name
        io_file = os.path.join(io_dir, "{}.txt".format(mac_key))
        with open(io_file, 'w') as out_file: 
            for pos_key in ap_rf[mac_key].keys():
                [x,y] = pos_key.split("-")
                [rssi,std] = ap_rf[mac_key][pos_key]
                out_file.write("{} {} {} {}\n".format(x,y,rssi,std))

    return io_dir

def find_size(filename):
    '''

    Args:
    filename(stirng): the path of the file
    '''
    count = 0
    with open(filename, 'r') as f_in:
        while True:
            line = f_in.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            count += 1
    return count

def discard_data(filename, data_size, ratio):
    path = os.path.dirname(filename)
    basename = os.path.basename(filename)
    out_filename = os.path.join(path,"reduced_{}".format(basename))
    idxs = sorted(random.sample(range(data_size),int(ratio*data_size)))
    # print(idxs)
    count = 0
    with open(filename, 'r') as f_in, open(out_filename, 'w') as f_out:
        while True:
            line = f_in.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            if count in idxs:
                f_out.write(line+"\n")
            count += 1
    print("Reduced file generated.")
    return out_filename

def clean(filename):
    basename = os.path.basename(filename)
    path = os.path.dirname(filename)
    reduced_file = os.path.join(path,"reduced_{}".format(basename))
    ap_original_path = os.path.splitext(filename)[0]
    ap_reduced_path = os.path.splitext(reduced_file)[0]
    generate_dir = os.path.join(os.path.dirname(filename),"generate_{}".format(os.path.splitext(filename)[0]))
    if os.path.exists(ap_original_path):
        shutil.rmtree(ap_original_path)
    if os.path.exists(ap_reduced_path):
        shutil.rmtree(ap_reduced_path)
    if os.path.exists(generate_dir):
        shutil.rmtree(generate_dir)
    if os.path.exists(reduced_file):
        os.remove(reduced_file)
    print("cleaning complete")  
    pass

def compare_sample(filename, ratio):
    # create directory for output
    root_path = os.path.dirname(filename)
    basename = os.path.basename(filename)
    generate_dir = os.path.join(root_path,"generate_{}".format(os.path.splitext(basename)[0]))
    mkdir(generate_dir)

    # generate sample from original data
    data_size = find_size(filename)
    reduced_file = discard_data(filename, data_size, ratio)

    # separate data by AP
    ap_reduced_path = ap_map_rp_std(reduced_file)
    ap_original_path = ap_map_rp_std(filename)
    print("=========> Preprocess done!")
    print("Original AP count: {}, Reduced AP count: {}".format(len(os.listdir(ap_original_path)),len(os.listdir(ap_reduced_path))))

    # store rssi difference and std difference for further processing
    rssi_err = []
    std_err = []

    # compare data based on APs
    for ap_name in os.listdir(ap_reduced_path):
        # print out AP's mac address
        print("-----{}".format(ap_name))

        ap_reduced_file = os.path.join(ap_reduced_path, ap_name)
        ap_original_file = os.path.join(ap_original_path, ap_name)
        ap_generated_file = os.path.join(generate_dir, ap_name)

        pos_train = []
        rssi_train = []
        with open(ap_reduced_file, 'r') as f_in:
            while True:
                line = f_in.readline().rstrip("\n").rstrip(" ")
                if not line:
                    break
                x,y,rssi,_ = line.split(" ")
                pos_train.append([float(x), float(y)])
                rssi_train.append(float(rssi))

        # start training
        gp_instance = gp(pos_train, rssi_train)
        gp_instance.train()

        # find all points
        ori_data = []
        loc = []
        with open(ap_original_file, 'r') as f_in:
            while True:
                line = f_in.readline().rstrip("\n").rstrip(" ")
                if not line:
                    break
                x,y,rssi,std = line.split(" ")
                ori_data.append([float(rssi), float(std)])
                loc.append([float(x),float(y)])

        # generate file output
        with open(ap_generated_file, 'w') as f_out:
            for idx in range(len(loc)):
                [x, y] = loc[idx]
                [rssi, std] = ori_data[idx]
                esti_rssi,esti_std = gp_instance.estimate_gp(x,y,sd_mode=True)

                f_out.write("{} {} {} {} {} {}\n".format(x,y,esti_rssi,esti_std,rssi,std))

                rssi_err.append(abs(rssi - esti_rssi))
                std_err.append(abs(std - esti_std))

    rssi_err_file = os.path.join(root_path, "rssi_err.txt")
    std_err_file = os.path.join(root_path, "std_err.txt")
    with open(rssi_err_file, 'w') as f_out:
        for err in rssi_err:
            f_out.write("{}\n".format(err))

    with open(std_err_file, 'w') as f_out:
        for err in std_err:
            f_out.write("{}\n".format(err))

    print("File generated")

def plot_cdf(error, name, folder):
    fontsize = 18
    linewidth = 5
    _, ax = plt.subplots()
    sorted_data = np.sort(error)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    ax.plot(sorted_data, yvals, '-', linewidth=linewidth, label="${}$".format(name))
    plt.ylim([0,1])
    plt.xlim(left=0)
    plt.xlabel("Error (dBm)", fontsize=fontsize)
    plt.ylabel("CDF", fontsize=fontsize)
    ax.grid(color='k', linestyle='--', linewidth=1)
    plt.xticks(fontsize=fontsize)
    plt.yticks(np.arange(0, 1.1, 0.1), fontsize=fontsize)
    ax.legend(loc='lower right', fontsize=fontsize)
    plt.tight_layout()
    plt.savefig(os.path.join(folder, "cdf_{}.png".format(name)), dpi=1000)
    plt.close()

if __name__ == "__main__":
    print("Please indicate your file name:")
    filename = input()
    print("clean workspace?(Y/n)")
    flag = input()
    if flag == "Y":
        clean(filename)
    
    root_path = os.path.dirname(filename)

    compare_sample(filename, ratio=0.6)

    rssi_err = []
    with open(os.path.join(root_path, "rssi_err.txt"), 'r') as f_in:
        while True:
            line = f_in.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            rssi_err.append(float(line))

    std_err = []
    with open(os.path.join(root_path, "std_err.txt"), 'r') as f_in:
        while True:
            line = f_in.readline().rstrip("\n").rstrip(" ")
            if not line:
                break
            std_err.append(float(line))

    plot_cdf(rssi_err, "rssi", root_path)
    plot_cdf(std_err, "std", root_path)
        

