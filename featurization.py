import numpy as np
import scipy.interpolate
import matplotlib.pyplot as plt

def make_cosine_kernels(y=None,
                        y_resolution=500,
                        y_range=None, 
                        n_kernels=6, 
                        crop_first_and_last_kernels=True, 
                        warping_curve=None, 
                        plot_pref=1):
    '''
    Makes a set of cosines offset by pi/2.
    This function is useful for doing amplitude basis expansions.
    The outputs of this function can be used as a look up table
    for some one dimensional signal to effectively make its 
    representation nonlinear and high dimensional.

    This function works great up to ~100 kernels, then some
    rounding errors mess up the range slightly, but not badly.
    RH 2021

    Args:
        y (ndarray):
            1-D array. Used only to obtain the min and max for 
            setting 'y_range'. If 'y_range' is not None, then 
            this is unused.
        y_range (2 entry array):
            [min , max] of 'xAxis_of_curves'. Effectively defines
            the range of the look up table that will be applied.
        y_resolution (int):
            Sets the size (and therefore resolution) of the
            output array and xAxis_of_curves.
        n_kernels (int):
            Number of cosine kernels to be made. Increasing this
            also decreases the width of individual kernels.
        crop_first_and_last_kernels (bool):
            Preference of whether the first and last kernels
            should be cropped at their peak. Doing this
            maintains a constant sum over the entire range of
            kernels
        warping_curve (1-D array):
            A curve used for warping (via interpolation) the 
            shape of the cosine kernels. This allows for
            non-uniform widths of kernels. Make this array
            large (>=100000) values to keep interpolation smooth.
        plot_pref (bool):
            set to 1: show output curves
            set to 2: show intermediate provessing curves

    Returns:
        bases_interp (ndarray):
            The output cosine kernels
        xAxis_of_curves (1-D array):
            The look up table defined by 'y_range' or the
            min/max of 'y'. Use this axis to expand some signal
            'y' using the kernel bases functions
    '''

    if y is None:
        y = np.arange(0, 1, 0.1)

    if y_range is None:
        y_range = np.array([np.min(y) , np.max(y)])

    if warping_curve is None:
        warping_curve = np.arange(1000000)

    y_resolution_highRes = y_resolution * 10
    bases_highRes = np.zeros((y_resolution_highRes, n_kernels))

    cos_width_highRes = int((bases_highRes.shape[0] / (n_kernels+1))*2)
    cos_kernel_highRes = (np.cos(np.linspace(-np.pi, np.pi, cos_width_highRes)) + 1)/2

    for ii in range(n_kernels):
        bases_highRes[int(cos_width_highRes*(ii/2)) : int(cos_width_highRes*((ii/2)+1)) , ii] = cos_kernel_highRes

    if crop_first_and_last_kernels:
        bases_highRes_cropped = bases_highRes[int(cos_width_highRes/2):-int(cos_width_highRes/2)]
    else:
        bases_highRes_cropped = bases_highRes

    WC_norm = warping_curve - np.min(warping_curve)
    WC_norm = (WC_norm/np.max(WC_norm)) * (bases_highRes_cropped.shape[0]-1)

    f_interp = scipy.interpolate.interp1d(np.arange(bases_highRes_cropped.shape[0]),
                                          bases_highRes_cropped, axis=0)

    bases_interp = f_interp(WC_norm[np.uint64(np.round(np.linspace(0, len(WC_norm)-1, y_resolution)))])

    xAxis_of_curves = np.linspace(y_range[0] , y_range[1], y_resolution)

    if plot_pref==1:
        fig, axs = plt.subplots(1)
        axs.plot(xAxis_of_curves, bases_interp)
        axs.set_xlabel('y_range look up axis')
        axs.set_title('kernels_warped')
    if plot_pref>=2:
        fig, axs = plt.subplots(6, figsize=(5,15))
        axs[0].plot(bases_highRes)
        axs[0].set_title('kernels')
        axs[1].plot(bases_highRes_cropped)
        axs[1].set_title('kernels_cropped')
        axs[2].plot(warping_curve)
        axs[2].set_title('warping_curve')
        axs[3].plot(WC_norm)
        axs[3].set_title('warping_curve_normalized')
        axs[4].plot(xAxis_of_curves, bases_interp)
        axs[4].set_title('kernels_warped')
        axs[4].set_xlabel('y_range look up axis')
        axs[5].plot(np.sum(bases_interp, axis=1))
        axs[5].set_ylim([0,1.1])
        axs[5].set_title('sum of kernels')
        
    return bases_interp , xAxis_of_curves