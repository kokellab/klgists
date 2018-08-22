import numpy as np
import math
from scipy.special import gamma

def z_factor(pos_hist,neg_hist):
    nm = np.mean(neg_hist)
    nv = np.std(neg_hist)
    
    pm = np.mean(pos_hist)
    pv = np.std(pos_hist)
    
    z_fac = 1 - (3*(pv + nv)/np.abs(pm - nm))
    return z_fac

def bhatta(hist1, hist2):
    # calculate mean and std of hist1
    pm = np.mean(hist1)
    pv = np.var(hist1)

    # calculate mean and std of hist2
    qm = np.mean(hist2)
    qv = np.var(hist2)
    # calculate score
    score = 0.25 * np.log( 0.25*( 2 + (pv/qv) + (qv/pv) ) ) + 0.25*(((pm-qm)**2)/(pv+qv))

    return score

def permutation_test(case, control, n_resamples: int=1000):
    n, k = len(case), 0
    tobs = (np.mean(case) - np.mean(control))
    pooled = np.concatenate([case, control])
    for i in range(0,n_resamples):
        np.random.shuffle(pooled)
        k += tobs < (np.mean(pooled[:n]) - np.mean(pooled[n:]))
    if k == 0:
        #print('The estimated p-value was zero.\n \
        #Providing the upper bound of the 95% confidence interval of this result')
        p = (0,3/n_resamples)
        return 3/n_resamples # this actually becomes an interval, not sure how to handle
    else:
        p = k / n_resamples
        return p

# This will make a subsample of the controls equal to the number of samples in your case
def sample_then_split(df, fraction):
    sample = df.sample(frac=fraction, replace=False)
    return sample, df[~df.index.isin(sample.index)]

def ssmd(pos_hist, neg_hist):
    # calculate mean and std of positives
    pm = np.mean(pos_hist)
    pv = np.std(pos_hist)

    # calculate mean and std of negatives 
    nm = np.mean(neg_hist)
    nv = np.std(neg_hist)
    
    ssm = (pm-nm) / np.sqrt(pv**2 + nv**2)
    
    return ssm

def robust_ssmd(pos_hist, neg_hist):
    # calculate median and MAD of positives
    pm = np.median(pos_hist)
    pv = MAD(pos_hist)

    # calculate mean and std of negatives 
    nm = np.median(neg_hist)
    nv = MAD(neg_hist)
    
    ssm = (pm-nm) / (1.4826 * np.sqrt(pv**2 + nv**2))
    
    return ssm

def MAD(sample):
    return np.median([np.abs(x - np.median(sample)) for x in sample])


def ssmd_star_mad(case_value, neg_values):
    neg_median = np.median(neg_values)
    neg_sample_size = len(neg_values)
    k = neg_sample_size - 2.48
    mad = MAD(neg_values)
    final = (case_value - neg_median) / (1.4826 * mad * np.sqrt(2*(neg_sample_size - 1)/k))
    return final

def ssmd_star(case_value, neg_values):
    neg_mean = np.mean(neg_values)
    neg_std = np.std(neg_values)
    neg_sample_size = len(neg_values)
    k = neg_sample_size - 2.48
    final = (case_value - neg_mean) / (neg_std * np.sqrt(2*(neg_sample_size)/k))
    return final

def ssmd_multiple_sample(case_values, neg_values):
    neg_med = np.median(neg_values)
    dists = [(x - neg_med) for x in case_values]
    d = np.mean(dists)
    s = np.std(dists)
    n = len(case_values)
    coeff = (gamma((n-1)/2) / gamma((n-2)/2)) * np.sqrt(2/(n-1))
    return coeff * (d/s)