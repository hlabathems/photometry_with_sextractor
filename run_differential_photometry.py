from astropy.io import ascii
from matplotlib import pyplot as plt
import numpy as np
import sys

def extract_columns(filename):
    data = ascii.read(filename)

    return data

def get_maximum(infiles):
    lengths = np.zeros(len(infiles), dtype = int)
    
    for k, infile in enumerate(infiles):
        data = extract_columns(infile)
        lengths[k] = len(data['col1'])
    
    max_idx = np.argmax(lengths)
    max_length = lengths[max_idx]

    return max_length

def get_mean(mult_arr):

    return np.nanmean(mult_arr, axis = 0)

def main(infiles):
    max_length = get_maximum(infiles)
    
    mult_arr = []

    for infile in infiles:
        data = extract_columns(infile)
        temp_list = [np.NAN] * max_length
        for k, mag in enumerate(data['col6']):
            temp_list[k] = mag
        mult_arr.append(temp_list)

    #calc_mean = get_mean(mult_arr)
    #mult_arr.append(calc_mean)
    ref_frame = reference_frame(mult_arr)

    ref_frame = np.array(ref_frame)
    dm = mult_arr - np.vstack(ref_frame)

    show_plots(dm, N = dm.shape[1])

    ref_idx = input('Enter the reference star index number (first being 0): ')

    if ref_idx != '':
            check_variable_stars(dm, ref_idx)
    else:
        print('No reference star was selected')

def reference_frame(mult_arr, index = 0):
    return [row[index] for row in mult_arr]

def check_variable_stars(delta_m, ref_star_index):
    dm_ref = delta_m[ref_star_index]
    diff = delta_m - dm_ref
    show_plots(diff, N = diff.shape[1])


def show_plots(delta_m, N = 0):
    
    star_num = 1
    
    for y in delta_m:
        x = np.arange(1, N + 1)

        plt.plot(x, y, '.', label = 'star_%s' % (star_num))
    
        star_num += 1

    plt.xlim([1, N])
    plt.gca().invert_yaxis()
    plt.xlabel('Frame Number', fontweight = 'bold')
    plt.ylabel(r'$\mathbf{\Delta m}$')
    plt.legend(loc = 'best')
    plt.grid()
    plt.show()

main(sys.argv[1:])
