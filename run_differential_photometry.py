# Differential Photometry

from astropy.io import ascii
import numpy as np
import pylab as pl
import sys


# Read in light curves

def readfile(filename):
    
    data = ascii.read(filename)
    
    return data

# Get indices

def get_indices(ref_data, data):
    
    idx1 = np.searchsorted(ref_data, data,'left')
    idx2 = np.searchsorted(ref_data, data,'right')
    out = idx1[idx1 != idx2]
    
    return out

# Make arrays be of equal length, put nan where no measurement was detected

def make_equal(filenames, max_length = None, assoc_idx = None):
    if len(filenames) > 0 and max_length is not None and assoc_idx is not None:
        mags = []
        mag_errs = []
        
        ref_data = readfile(filenames[assoc_idx])
        
        ref_frames = ref_data['CAT']
        ref_hjd = ref_data['HJD']
        observ = ref_data['OBS']
        
        for filename in filenames:
            
            data = readfile(filename)
            
            temp_list_m = [np.NAN] * max_length
            temp_list_merr = [np.NAN] * max_length
            
            matches = get_indices(ref_frames, data['CAT'])
            
            N = len(matches)
            
            for k in range(N):
                temp_list_m[matches[k]] = data['M'][k]
                temp_list_merr[matches[k]] = data['MERR'][k]
            
            mags.append(temp_list_m)
            mag_errs.append(temp_list_merr)
        
        return np.array(mags), np.array(mag_errs), ref_hjd, observ

# Choose reference frame

def reference_frame(mags, idx_frame = None):
    if idx_frame is not None:
        frame = np.array([row[idx_frame] for row in mags])
    
    return frame

# subtract reference frame

def dphot(mags, mag_errs, frame_num = 0):
    ref_frame_mags = reference_frame(mags, idx_frame = frame_num)
    ref_frame_mag_errs = reference_frame(mag_errs, idx_frame = frame_num)
    
    dm = mags - np.vstack(ref_frame_mags)
    
    # propagate errors
    dmerr = np.sqrt(np.square(mag_errs) + np.square(np.vstack(ref_frame_mag_errs)))
    
    plot_lcurves(dm, dmerr)
    
    return dm, dmerr

# Check for variable stars

def check_variable_stars(mags, mag_errs, ref_star_idx = None):
    if ref_star_idx is not None:
        ref_star_dm = mags[ref_star_idx]
        ref_star_dmerr = mag_errs[ref_star_idx]
        
        subtract_ref_star_dm = mags - ref_star_dm
        
        # propagate errors
        subtract_ref_star_dmerr = np.sqrt(np.square(mag_errs) + np.square(ref_star_dmerr))
        
        plot_lcurves(subtract_ref_star_dm, subtract_ref_star_dmerr)


def plot_lcurves(mags, mag_errs):
    star_num = 1
    
    print('#####################################################')
    
    pl.figure()
    
    for k in range(len(mags)):
        
        frame_number = np.arange(1, len(mags[k]) + 1)
        
        print(np.nanstd(mags[k]))
        
        pl.errorbar(frame_number, mags[k], yerr = mag_errs[k], fmt = '.', label = '%s' % (star_num))
        
        star_num += 1
    
    pl.gca().invert_yaxis()
    pl.xlabel('Frame Number', fontweight = 'bold')
    pl.ylabel('$\mathbf{\Delta m}$')
    pl.legend(loc = 'best')
    pl.grid()
    #pl.show()

def subtract_from_target(target_mags, target_mag_errs, dm, dmerr, hjd, observ, ref_idx = None):

    if ref_idx is not None:
        corrected_mag = target_mags - dm[ref_idx]
        corrected_mag_errs = np.sqrt(np.square(dmerr[ref_idx]) + np.square(target_mag_errs))
        
        x, y, ye, observ = hjd, corrected_mag[0], corrected_mag_errs[0], observ
        
        N = len(x)
        
        frame_num = np.arange(1, N + 1, 1)

        mcd_idx = (observ == 'McD')
        cfht_idx = (observ == 'CFHT')
        
        pl.figure()

        pl.errorbar(x[mcd_idx] - 2450000, y[mcd_idx], yerr = ye[mcd_idx], fmt = '.', color = 'red', label = 'McD')
        pl.errorbar(x[cfht_idx] - 2450000, y[cfht_idx], yerr = ye[cfht_idx], fmt = '.', color = 'blue', label = 'CFHT')
        pl.gca().invert_yaxis()
        pl.legend(loc = 'best')
        pl.grid()

        pl.figure()

        pl.errorbar(frame_num, y, yerr = ye, fmt = '.', color = 'blue')
        pl.xlim([1, N])
        pl.gca().invert_yaxis()

        #pl.show()

if __name__ == '__main__':
    
    # Load in data
    filenames = sys.argv[1:]

    # Unpack
    mags, mag_errs, hjd, observatories = make_equal(filenames, max_length = 359, assoc_idx = 0)
    
    # Separate target from comparison stars

    target_mags = mags[np.arange(len(mags)) == 3]   # target magnitude
    target_mag_errs = mag_errs[np.arange(len(mag_errs)) == 3]   # target magnitude errors
    comp_mags = mags[np.arange(len(mags)) != 3]     # comparison stars magnitudes
    comp_mag_errs = mag_errs[np.arange(len(mag_errs)) != 3]     # comparison stars magnitudes errors

    dm, dmerr = dphot(comp_mags, comp_mag_errs, frame_num = 0)

    check_variable_stars(dm, dmerr, ref_star_idx = 0)

    subtract_from_target(target_mags, target_mag_errs, dm, dmerr, hjd, observatories, ref_idx = 0)

    pl.show()
