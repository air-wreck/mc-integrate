# a comparison of t and z distributions
# conclusion: for large n, the difference is irrelevant
#             for small n, t dominates
# this is pretty much what was expected, but I wanted to check

import numpy as np
import scipy.stats

def mc_int_t(f, xs, a, b, n=5000, alpha=0.05):
    ys = f(xs)
    res = np.average(ys) * (b - a)

    # compute margin of error and return interval
    t = scipy.stats.t.ppf(1.0 - alpha / 2.0, df=n-1)
    margin = t * np.std(ys, ddof=1) / np.sqrt(n)
    return res - margin, res + margin

def mc_int_z(f, xs, a=0, b=1, n=5000, alpha=0.05):
    ys = f(xs)
    res = np.average(ys) * (b - a)

    # get critical z-score and margin of error
    z = scipy.stats.norm.ppf(1.0 - alpha / 2.0)
    margin = z * np.std(ys, ddof=1) / np.sqrt(n)

    # we expect the true value of the integral to be within
    # res - margin and res + margin about 95% of the time
    # we'll return our guess res along with this confidence interval
    return res - margin, res + margin

N = 5000  # number of trials
true_val = 1 - np.cos(1)  # the true value of the integral

def add_if_true(arg):
    lo, hi = arg
    if lo <= true_val <= hi:
        return 1
    return 0

def test(n, alpha):
    ts = 0
    zs = 0
    for _ in range(N):
        xs = np.random.random(n)
        ts += add_if_true(mc_int_t(np.sin, xs, 0, 1, n=n, alpha=alpha))
        zs += add_if_true(mc_int_z(np.sin, xs, 0, 1, n=n, alpha=alpha))
    t = ts / N
    z = zs / N

    target = 1.0 - alpha / 2.0
    print('ts: %f' % (t - target))
    print('zs: %f' % (z - target))

test(5000, 0.05)

