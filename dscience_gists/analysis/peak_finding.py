"""
Functions for identifying peaks in signals.
"""
from __future__ import division, print_function, absolute_import
import math
import numpy as np
from scipy._lib.six import xrange
from scipy.signal.wavelets import cwt, ricker
from scipy.stats import scoreatpercentile
from scipy.signal._peak_finding_utils import (_peak_prominences)


class PeakFinder:

    @classmethod
    def _boolrelextrema(cls, data, comparator, axis=0, order=1, mode='clip'):
        """
        Calculate the relative extrema of `data`.

        Relative extrema are calculated by finding locations where
        ``comparator(data[n], data[n+1:n+order+1])`` is True.

        Parameters
        ----------
        data : ndarray
            Array in which to find the relative extrema.
        comparator : callable
            Function to use to compare two data points.
            Should take two arrays as arguments.
        axis : int, optional
            Axis over which to select from `data`.  Default is 0.
        order : int, optional
            How many points on each side to use for the comparison
            to consider ``comparator(n,n+x)`` to be True.
        mode : str, optional
            How the edges of the vector are treated.  'wrap' (wrap around) or
            'clip' (treat overflow as the same as the last (or first) element).
            Default 'clip'.  See numpy.take

        Returns
        -------
        extrema : ndarray
            Boolean array of the same shape as `data` that is True at an extrema,
            False otherwise.

        See also
        --------
        argrelmax, argrelmin

        Examples
        --------
        >>> testdata = np.array([1,2,3,2,1])
        >>> PeakFinder._boolrelextrema(testdata, np.greater, axis=0)
        array([False, False,  True, False, False], dtype=bool)

        """
        if(int(order) != order) or (order < 1):
            raise ValueError('Order must be an int >= 1')

        datalen = data.shape[axis]
        locs = np.arange(0, datalen)

        results = np.ones(data.shape, dtype=bool)
        main = data.take(locs, axis=axis, mode=mode)
        for shift in xrange(1, order + 1):
            plus = data.take(locs + shift, axis=axis, mode=mode)
            minus = data.take(locs - shift, axis=axis, mode=mode)
            results &= comparator(main, plus)
            results &= comparator(main, minus)
            if~results.any():
                return results
        return results

    @classmethod
    def peak_prominences(cls, x, peaks, wlen=None):
        """
        Calculate the prominence of each peak in a signal.

        The prominence of a peak measures how much a peak stands out from the
        surrounding baseline of the signal and is defined as the vertical distance
        between the peak and its lowest contour line.

        Parameters
        ----------
        x : sequence
            A signal with peaks.
        peaks : sequence
            Indices of peaks in `x`.
        wlen : int or float, optional
            A window length in samples that optionally limits the evaluated area for
            each peak to a subset of `x`. The peak is always placed in the middle of
            the window therefore the given length is rounded up to the next odd
            integer. This parameter can speed up the calculation (see Notes).

        Returns
        -------
        prominences : ndarray
            The calculated prominences for each peak in `peaks`.
        left_bases, right_bases : ndarray
            The peaks' bases as indices in `x` to the left and right of each peak.
            The higher base of each pair is a peak's lowest contour line.

        Raises
        ------
        ValueError
            If an index in `peaks` does not point to a local maximum in `x`.

        See Also
        --------
        find_peaks
            Find peaks inside a signal based on peak properties.
        peak_widths
            Calculate the width of peaks.

        Notes
        -----
        Strategy to compute a peak's prominence:

        1. Extend a horizontal line from the current peak to the left and right
           until the line either reaches the window border (see `wlen`) or
           intersects the signal again at the slope of a higher peak. An
           intersection with a peak of the same height is ignored.
        2. On each side find the minimal signal value within the interval defined
           above. These points are the peak's bases.
        3. The higher one of the two bases marks the peak's lowest contour line. The
           prominence can then be calculated as the vertical difference between the
           peaks height itself and its lowest contour line.

        Searching for the peak's bases can be slow for large `x` with periodic
        behavior because large chunks or even the full signal need to be evaluated
        for the first algorithmic step. This evaluation area can be limited with the
        parameter `wlen` which restricts the algorithm to a window around the
        current peak and can shorten the calculation time if the window length is
        short in relation to `x`.
        However this may stop the algorithm from finding the true global contour
        line if the peak's true bases are outside this window. Instead a higher
        contour line is found within the restricted window leading to a smaller
        calculated prominence. In practice this is only relevant for the highest set
        of peaks in `x`. This behavior may even be used intentionally to calculate
        "local" prominences.

        .. warning::

           This function may return unexpected results for data containing NaNs. To
           avoid this, NaNs should either be removed or replaced.

        .. versionadded:: 1.1.0

        References
        ----------
        .. [1] Wikipedia Article for Topographic Prominence:
           https://en.wikipedia.org/wiki/Topographic_prominence

        Examples
        --------
        >>> from scipy.signal import find_peaks, peak_prominences
        >>> import matplotlib.pyplot as plt

        Create a test signal with two overlayed harmonics

        >>> x = np.linspace(0, 6 * np.pi, 1000)
        >>> x = np.sin(x) + 0.6 * np.sin(2.6 * x)

        Find all peaks and calculate prominences

        >>> peaks, _ = find_peaks(x)
        >>> prominences = peak_prominences(x, peaks)[0]
        >>> prominences
        array([1.24159486, 0.47840168, 0.28470524, 3.10716793, 0.284603  ,
               0.47822491, 2.48340261, 0.47822491])

        Calculate the height of each peak's contour line and plot the results

        >>> contour_heights = x[peaks] - prominences
        >>> plt.plot(x)
        >>> plt.plot(peaks, x[peaks], "x")
        >>> plt.vlines(x=peaks, ymin=contour_heights, ymax=x[peaks])
        >>> plt.show()

        Let's evaluate a second example that demonstrates several edge cases for
        one peak at index 5.

        >>> x = np.array([0, 1, 0, 3, 1, 3, 0, 4, 0])
        >>> peaks = np.array([5])
        >>> plt.plot(x)
        >>> plt.plot(peaks, x[peaks], "x")
        >>> plt.show()
        >>> peak_prominences(x, peaks)  # -> (prominences, left_bases, right_bases)
        (array([3.]), array([2]), array([6]))

        Note how the peak at index 3 of the same height is not considered as a
        border while searching for the left base. Instead two minima at 0 and 2
        are found in which case the one closer to the evaluated peak is always
        chosen. On the right side however the base must be placed at 6 because the
        higher peak represents the right border to the evaluated area.

        >>> peak_prominences(x, peaks, wlen=3.1)
        (array([2.]), array([4]), array([6]))

        Here we restricted the algorithm to a window from 3 to 7 (the length is 5
        samples because `wlen` was rounded up to the next odd integer). Thus the
        only two candidates in the evaluated area are the two neighbouring samples
        and a smaller prominence is calculated.
        """
        # Inner function expects `x` to be C-contiguous
        x = np.asarray(x, order='C', dtype=np.float64)
        if x.ndim != 1:
            raise ValueError('`x` must have exactly one dimension')

        peaks = np.asarray(peaks)
        if peaks.size == 0:
            # Empty arrays default to np.float64 but are valid input
            peaks = np.array([], dtype=np.intp)
        try:
            # Safely convert to C-contiguous array of type np.intp
            peaks = peaks.astype(np.intp, order='C', casting='safe',
                                 subok=False, copy=False)
        except TypeError:
            raise TypeError("Cannot safely cast `peaks` to dtype('intp')")
        if peaks.ndim != 1:
            raise ValueError('`peaks` must have exactly one dimension')

        if wlen is None:
            wlen = -1  # Inner function expects int -> None == -1
        elif 1 < wlen:
            # Round up to next positive integer; rounding up to next odd integer
            # happens implicitly inside the inner function
            wlen = int(math.ceil(wlen))
        else:
            # Give feedback if wlen has unexpected value
            raise ValueError('`wlen` must be at larger than 1, was ' + str(wlen))

        return _peak_prominences(x, peaks, wlen)

    @classmethod
    def _identify_ridge_lines(cls, matr, max_distances, gap_thresh):
        """
        Identify ridges in the 2-D matrix.

        Expect that the width of the wavelet feature increases with increasing row
        number.

        Parameters
        ----------
        matr : 2-D ndarray
            Matrix in which to identify ridge lines.
        max_distances : 1-D sequence
            At each row, a ridge line is only connected
            if the relative max at row[n] is within
            `max_distances`[n] from the relative max at row[n+1].
        gap_thresh : int
            If a relative maximum is not found within `max_distances`,
            there will be a gap. A ridge line is discontinued if
            there are more than `gap_thresh` points without connecting
            a new relative maximum.

        Returns
        -------
        ridge_lines : tuple
            Tuple of 2 1-D sequences. `ridge_lines`[ii][0] are the rows of the
            ii-th ridge-line, `ridge_lines`[ii][1] are the columns. Empty if none
            found.  Each ridge-line will be sorted by row (increasing), but the
            order of the ridge lines is not specified.

        References
        ----------
        Bioinformatics (2006) 22 (17): 2059-2065.
        :doi:`10.1093/bioinformatics/btl355`
        http://bioinformatics.oxfordjournals.org/content/22/17/2059.long

        Examples
        --------
        >>> data = np.random.rand(5,5)
        >>> ridge_lines = PeakFinder._identify_ridge_lines(data, 1, 1)

        Notes
        -----
        This function is intended to be used in conjunction with `cwt`
        as part of `find_peaks_cwt`.

        """
        if len(max_distances) < matr.shape[0]:
            raise ValueError('Max_distances must have at least as many rows '
                             'as matr')

        all_max_cols = PeakFinder._boolrelextrema(matr, np.greater, axis=1, order=1)
        # Highest row for which there are any relative maxima
        has_relmax = np.where(all_max_cols.any(axis=1))[0]
        if len(has_relmax) == 0:
            return []
        start_row = has_relmax[-1]
        # Each ridge line is a 3-tuple:
        # rows, cols,Gap number
        ridge_lines = [[[start_row],
                       [col],
                       0] for col in np.where(all_max_cols[start_row])[0]]
        final_lines = []
        rows = np.arange(start_row - 1, -1, -1)
        cols = np.arange(0, matr.shape[1])
        for row in rows:
            this_max_cols = cols[all_max_cols[row]]

            # Increment gap number of each line,
            # set it to zero later if appropriate
            for line in ridge_lines:
                line[2] += 1

            # XXX These should always be all_max_cols[row]
            # But the order might be different. Might be an efficiency gain
            # to make sure the order is the same and avoid this iteration
            prev_ridge_cols = np.array([line[1][-1] for line in ridge_lines])
            # Look through every relative maximum found at current row
            # Attempt to connect them with existing ridge lines.
            for ind, col in enumerate(this_max_cols):
                # If there is a previous ridge line within
                # the max_distance to connect to, do so.
                # Otherwise start a new one.
                line = None
                if len(prev_ridge_cols) > 0:
                    diffs = np.abs(col - prev_ridge_cols)
                    closest = np.argmin(diffs)
                    if diffs[closest] <= max_distances[row]:
                        line = ridge_lines[closest]
                if line is not None:
                    # Found a point close enough, extend current ridge line
                    line[1].append(col)
                    line[0].append(row)
                    line[2] = 0
                else:
                    new_line = [[row],
                                [col],
                                0]
                    ridge_lines.append(new_line)

            # Remove the ridge lines with gap_number too high
            # XXX Modifying a list while iterating over it.
            # Should be safe, since we iterate backwards, but
            # still tacky.
            for ind in xrange(len(ridge_lines) - 1, -1, -1):
                line = ridge_lines[ind]
                if line[2] > gap_thresh:
                    final_lines.append(line)
                    del ridge_lines[ind]

        out_lines = []
        for line in (final_lines + ridge_lines):
            sortargs = np.array(np.argsort(line[0]))
            rows, cols = np.zeros_like(sortargs), np.zeros_like(sortargs)
            rows[sortargs] = line[0]
            cols[sortargs] = line[1]
            out_lines.append([rows, cols])

        return out_lines

    @classmethod
    def _filter_ridge_lines(cls, cwt, ridge_lines, window_size=None, min_length=None, min_snr=1, noise_perc=10):
        """
        Filter ridge lines according to prescribed criteria. Intended
        to be used for finding relative maxima.

        Parameters
        ----------
        cwt : 2-D ndarray
            Continuous wavelet transform from which the `ridge_lines` were defined.
        ridge_lines : 1-D sequence
            Each element should contain 2 sequences, the rows and columns
            of the ridge line (respectively).
        window_size : int, optional
            Size of window to use to calculate noise floor.
            Default is ``cwt.shape[1] / 20``.
        min_length : int, optional
            Minimum length a ridge line needs to be acceptable.
            Default is ``cwt.shape[0] / 4``, ie 1/4-th the number of widths.
        min_snr : float, optional
            Minimum SNR ratio. Default 1. The signal is the value of
            the cwt matrix at the shortest length scale (``cwt[0, loc]``), the
            noise is the `noise_perc`th percentile of datapoints contained within a
            window of `window_size` around ``cwt[0, loc]``.
        noise_perc : float, optional
            When calculating the noise floor, percentile of data points
            examined below which to consider noise. Calculated using
            scipy.stats.scoreatpercentile.

        References
        ----------
        Bioinformatics (2006) 22 (17): 2059-2065. :doi:`10.1093/bioinformatics/btl355`
        http://bioinformatics.oxfordjournals.org/content/22/17/2059.long

        """
        num_points = cwt.shape[1]
        if min_length is None:
            min_length = np.ceil(cwt.shape[0] / 4)
        if window_size is None:
            window_size = np.ceil(num_points / 20)

        window_size = int(window_size)
        hf_window, odd = divmod(window_size, 2)

        # Filter based on SNR
        row_one = cwt[0, :]
        noises = np.zeros_like(row_one)
        for ind, val in enumerate(row_one):
            window_start = max(ind - hf_window, 0)
            window_end = min(ind + hf_window + odd, num_points)
            noises[ind] = scoreatpercentile(row_one[window_start:window_end], per=noise_perc)

        def filt_func(line):
            if len(line[0]) < min_length:
                return False
            snr = abs(cwt[line[0][0], line[1][0]] / noises[line[1][0]])
            if snr < min_snr:
                return False
            return True

        return list(filter(filt_func, ridge_lines))

    @classmethod
    def find_peaks_cwt(
            cls,
            vector, widths,
            wavelet=None, max_distances=None, gap_thresh=None, min_length=None, min_snr=1, noise_perc=10, noise_window_size=None
    ):
        """
        Find peaks in a 1-D array with wavelet transformation.

        The general approach is to smooth `vector` by convolving it with
        `wavelet(width)` for each width in `widths`. Relative maxima which
        appear at enough length scales, and with sufficiently high SNR, are
        accepted.

        Parameters
        ----------
        vector : ndarray
            1-D array in which to find the peaks.
        widths : sequence
            1-D array of widths to use for calculating the CWT matrix. In general,
            this range should cover the expected width of peaks of interest.
        wavelet : callable, optional
            Should take two parameters and return a 1-D array to convolve
            with `vector`. The first parameter determines the number of points
            of the returned wavelet array, the second parameter is the scale
            (`width`) of the wavelet. Should be normalized and symmetric.
            Default is the ricker wavelet.
        max_distances : ndarray, optional
            At each row, a ridge line is only connected if the relative max at
            row[n] is within ``max_distances[n]`` from the relative max at
            ``row[n+1]``.  Default value is ``widths/4``.
        gap_thresh : float, optional
            If a relative maximum is not found within `max_distances`,
            there will be a gap. A ridge line is discontinued if there are more
            than `gap_thresh` points without connecting a new relative maximum.
            Default is the first value of the widths array i.e. widths[0].
        min_length : int, optional
            Minimum length a ridge line needs to be acceptable.
            Default is ``cwt.shape[0] / 4``, ie 1/4-th the number of widths.
        min_snr : float, optional
            Minimum SNR ratio. Default 1. The signal is the value of
            the cwt matrix at the shortest length scale (``cwt[0, loc]``), the
            noise is the `noise_perc`th percentile of datapoints contained within a
            window of `window_size` around ``cwt[0, loc]``.
        noise_perc : float, optional
            When calculating the noise floor, percentile of data points
            examined below which to consider noise. Calculated using
            `stats.scoreatpercentile`.  Default is 10.

        Returns
        -------
        peaks_indices : ndarray
            Indices of the locations in the `vector` where peaks were found.
            The list is sorted.

        See Also
        --------
        cwt
            Continuous wavelet transform.
        find_peaks
            Find peaks inside a signal based on peak properties.

        Notes
        -----
        This approach was designed for finding sharp peaks among noisy data,
        however with proper parameter selection it should function well for
        different peak shapes.

        The algorithm is as follows:
         1. Perform a continuous wavelet transform on `vector`, for the supplied
            `widths`. This is a convolution of `vector` with `wavelet(width)` for
            each width in `widths`. See `cwt`
         2. Identify "ridge lines" in the cwt matrix. These are relative maxima
            at each row, connected across adjacent rows. See identify_ridge_lines
         3. Filter the ridge_lines using filter_ridge_lines.

        .. versionadded:: 0.11.0

        References
        ----------
        .. [1] Bioinformatics (2006) 22 (17): 2059-2065.
            :doi:`10.1093/bioinformatics/btl355`
            http://bioinformatics.oxfordjournals.org/content/22/17/2059.long

        Examples
        --------
        >>> from scipy import signal
        >>> xs = np.arange(0, np.pi, 0.05)
        >>> data = np.sin(xs)
        >>> peakind = signal.find_peaks_cwt(data, np.arange(1,10))
        >>> peakind, xs[peakind], data[peakind]
        ([32], array([ 1.6]), array([ 0.9995736]))

        """
        widths = np.asarray(widths)

        if gap_thresh is None:
            gap_thresh = np.ceil(widths[0])
        if max_distances is None:
            max_distances = widths / 4.0
        if wavelet is None:
            wavelet = ricker
        if noise_window_size is None:
            noise_window_size = np.ceil(len(vector) / 20)

        cwt_dat = cwt(vector, wavelet, widths)
        ridge_lines = PeakFinder._identify_ridge_lines(cwt_dat, max_distances, gap_thresh)
        filtered = PeakFinder._filter_ridge_lines(cwt_dat, ridge_lines, min_length=min_length,
                                       min_snr=min_snr, noise_perc=noise_perc, window_size=noise_window_size)
        max_locs = np.asarray([x[1][0] for x in filtered])
        max_locs.sort()

        return max_locs


__all__ = ['PeakFinder']

