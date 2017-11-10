from astropy.io import ascii
from matplotlib import pyplot as plt
import numpy as np
import sys

def extract_columns(filename):
    """
    Parameters
    ----------
    filename: ascii
    
    Returns
    -------
    data: array-like object
    """
    data = ascii.read(filename)

    return data

def get_maximum(infiles):
    """
    Parameters
    ----------
    infiles: array of strings
            files of the chosen comparison stars
            
    Returns
    -------
    max_length: int
            maximum length
    """
    lengths = np.zeros(len(infiles), dtype = int)
    
    for k, infile in enumerate(infiles):
        data = extract_columns(infile)
        lengths[k] = len(data['col1'])
    
    max_idx = np.argmax(lengths)
    max_length = lengths[max_idx]

    return max_length

def get_mean(mult_arr):
    """
    Parameters
    ----------
    mult_arr: n-dimensional array
    
    Returns:
    --------
    mean: array
            mean of all the comparison stars, e.g (C1 + C2 + C3) / 3
    """

    return np.nanmean(mult_arr, axis = 0)

def main(infiles):
    """
    Parameters
    ----------
    infiles: array of strings
            files of the chosen comparison stars
            
    Returns
    -------
    """
    
    # get maximum length
    max_length = get_maximum(infiles)
    
    # initialize an n-dimensional array to hold magnitudes
    mult_arr = []

    # loop through input files
    for infile in infiles:
        data = extract_columns(infile)
        # fill temporary list with nan's
        temp_list = [np.NAN] * max_length
        # replace nan's where applicable
        for k, mag in enumerate(data['col6']):
            temp_list[k] = mag
        mult_arr.append(temp_list)

    # uncomment the below two lines if you want to use the mean as reference star
    #calc_mean = get_mean(mult_arr)
    #mult_arr.append(calc_mean)
    
    # choose reference frame 
    ref_frame = reference_frame(mult_arr)

    # convert to array
    ref_frame = np.array(ref_frame)
    # subtract reference from each frame
    dm = mult_arr - np.vstack(ref_frame)

    # inspect the results
    show_plots(dm, N = dm.shape[1])

    # choose if any, the reference star index from the plot above
    ref_idx = input('Enter the reference star index number (first being 0): ')

    # check for variable star(s)
    if ref_idx != '':
            check_variable_stars(dm, ref_idx)
    else:
        print('No reference star was selected')

def reference_frame(mult_arr, index = 0):
    """
    Parameters
    ----------
    mult_arr: n-dimensional array
    index: int
            index of the reference frame
            
    Returns:
    -------
    reference frame: array
    """
    return [row[index] for row in mult_arr]

def check_variable_stars(delta_m, ref_star_index):
    """
    Parameters
    ----------
    delta_m: n-dimensional array
    ref_star_index: int
            index of the reference star
            
    Returns:
    -------
    magnitude difference: n-dimensional array
    """
    
    # get ref star
    dm_ref = delta_m[ref_star_index]
    # dm
    diff = delta_m - dm_ref
    # plot
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
