import numpy as np
import scipy.stats

def mc_integrate_1d(f, lo, hi, n=5000, alpha=0.05):
    xs = np.random.random(n) * (hi - lo) + lo
    ys = f(xs)
    res = np.average(ys) * (hi - lo)

    # compute margin of error and return interval
    t = scipy.stats.t.ppf(1.0 - alpha / 2.0, df=n-1)
    margin = t * np.std(ys, ddof=1) / np.sqrt(n)
    return res - margin, res + margin

def mc_integrate_nd(f, bounds, n=5000, alpha=0.05, coords=None):
    dim = len(bounds)
    if dim == 0:
        raise Exception('No bounds given')
    if dim == 1:
        # TODO: check format of bounds array
        lo, hi = bounds
        return mc_integrate_1d(f, lo, hi, n=n, alpha=alpha)

