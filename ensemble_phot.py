import numpy as np
from astropy.io import ascii
from matplotlib import pyplot as plt
import sys

def extract_columns(filename):
    data = ascii.read(filename)

    return data

def get_sorted(arr1, arr2, arr3):
    create_tuple = zip(arr1, arr2, arr3)

    create_tuple.sort(key = lambda x: x[0])
    
    arr1 = np.array([x for x, y, z in create_tuple])
    arr2 = np.array([y for x, y, z in create_tuple])
    arr3 = np.array([z for x, y, z in create_tuple])

    return arr1, arr2, arr3

def get_maximum(infiles):
    lengths = np.zeros(len(infiles), dtype = int)

    for k, infile in enumerate(infiles):
        lengths[k] = len(extract_columns(infile)['col1'])

    max_idx = np.argmax(lengths)
    max_length = lengths[max_idx]

    return max_length, max_idx

def get_indices(arr1, arr2):
    return np.searchsorted(arr1, arr2)

def main(infiles):
    max_length, max_idx = get_maximum(infiles)
    
    mult_m, mult_merr = [], []

    reference_cs = extract_columns(infiles[max_idx])
    reference_cs_hjd, reference_cs_m, reference_cs_merr = reference_cs['col2'], reference_cs['col5'], reference_cs['col6']
    reference_cs_hjd, reference_cs_m, reference_cs_merr = get_sorted(reference_cs['col2'], reference_cs['col5'], reference_cs['col6'])

    for k, infile in enumerate(infiles):
        cs = extract_columns(infile)
        cs_hjd, cs_m, cs_merr = cs['col2'], cs['col5'], cs['col6']
        cs_hjd, cs_m, cs_merr = get_sorted(cs['col2'], cs['col5'], cs['col6'])
        
        indices = get_indices(reference_cs_hjd, cs_hjd)
        
        temp_list_m = [np.NAN] * max_length
        temp_list_merr = [np.NAN] * max_length
        
        for i, j in enumerate(indices):
            temp_list_m[j] = cs_m[i]
            temp_list_merr[j] = cs_merr[i]
        
        mult_m.append(temp_list_m)
        mult_merr.append(temp_list_merr)
    
    mult_m, mult_merr = np.array(mult_m), np.array(mult_merr)
    
    mean_cs = np.nanmean(mult_m, axis = 0)

    np.savetxt('mean_value_option.txt', np.transpose([reference_cs_hjd, mean_cs]))

    show_plot(reference_cs_hjd, mean_cs)

def show_plot(x, y):
    plt.figure()
    plt.plot(x - 2450000, y, '.')
    plt.show()

main(sys.argv[1:])
