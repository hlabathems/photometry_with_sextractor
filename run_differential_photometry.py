# Differential Photometry

from astropy.io import ascii
import numpy as np
import pylab as pl
import sys


# Read in light curves

def readfile(filename):

    data = ascii.read(filename)

    return data


# Make arrays be of equal length, put nan where no measurement was detected

def make_equal(filenames, max_length = None, assoc_idx = None):
    if len(filenames) > 0 and max_length is not None and assoc_idx is not None:
        mags = []
        mag_errs = []

        data = readfile(filenames[assoc_idx])
        
        ref_frames = data['CAT']
        ref_hjd = data['HJD']
        observ = data['OBS']
        
        for filename in filenames:
            
            data = readfile(filename)
                
            temp_list_m = [np.NAN] * max_length
            temp_list_merr = [np.NAN] * max_length
            
            matches = np.searchsorted(ref_frames, data['CAT'])
            
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
    
    pl.figure()
    
    for k in range(len(mags)):
        print(np.nanstd(mags[k]))
        
        frame_number = np.arange(1, len(mags[k]) + 1)
        
        pl.errorbar(frame_number, mags[k], yerr = mag_errs[k], fmt = '.', label = '%s' % (star_num))
    
        star_num += 1
        
    pl.gca().invert_yaxis()
    pl.xlabel('Frame Number', fontweight = 'bold')
    pl.ylabel('$\mathbf{\Delta m}$')
    pl.legend(loc = 'best')
    pl.grid()
    pl.show()

def subtract_from_target(target_mags, target_mag_errs, dm, dmerr, hjd, observ, ref_idx = None):
    zeropoint = 26
    if ref_idx is not None:
        corrected_mag = target_mags - dm[ref_idx] + zeropoint
        corrected_mag_errs = np.sqrt(np.square(dmerr[ref_idx]) + np.square(target_mag_errs))
        
        idx = ~np.isnan(corrected_mag[0])
        
        x = hjd[idx]
        y = corrected_mag[0][idx]
        ye = corrected_mag_errs[0][idx]
        observ = observ[idx]

        saao_idx = (observ == 'SAAO')
        mcd_idx = (observ == 'McD')
        sso_idx = (observ == 'SSO')
        ctio_idx = (observ == 'CTIO')
        
        # remove outliers
        mask = (y[saao_idx] < 24)
        
        pl.figure()

        pl.errorbar(x[saao_idx][mask] - 2450000, y[saao_idx][mask], yerr = ye[saao_idx][mask], fmt = '.', color = 'brown', label = 'SAAO')

        pl.errorbar(x[mcd_idx] - 2450000, y[mcd_idx], yerr = ye[mcd_idx], fmt = '.', color = 'red', label = 'McD')
        pl.errorbar(x[sso_idx] - 2450000, y[sso_idx], yerr = ye[sso_idx], fmt = '.', color = 'green', label = 'SSO')
        pl.errorbar(x[ctio_idx] - 2450000, y[ctio_idx], yerr = ye[ctio_idx], fmt = '.', color = 'blue', label = 'CTIO')
        pl.gca().invert_yaxis()
        pl.xlabel('HJD - 2450000', fontweight = 'bold')
        pl.ylabel('V Magnitude', fontweight = 'bold')
        pl.legend(loc = 'best')
        pl.grid()
        pl.show()

if __name__ == '__main__':
    # Load in data
    filenames = sys.argv[1:]

    # Unpack
    mags, mag_errs, hjd, observatories = make_equal(filenames, max_length = 904, assoc_idx = 3)

    # Separate target from comparison stars

    target_mags = mags[np.arange(len(mags)) == 4]   # target magnitude
    target_mag_errs = mag_errs[np.arange(len(mag_errs)) == 4]   # target magnitude errors
    comp_mags = mags[np.arange(len(mags)) != 4]     # comparison stars magnitudes
    comp_mag_errs = mag_errs[np.arange(len(mag_errs)) != 4]     # comparison stars magnitudes errors

    dm, dmerr = dphot(comp_mags, comp_mag_errs, frame_num = 0)

    check_variable_stars(dm, dmerr, ref_star_idx = 0)

    subtract_from_target(target_mags, target_mag_errs, dm, dmerr, hjd, observatories, ref_idx = 2)
