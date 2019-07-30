import numpy as np
import scipy.stats
from functools import reduce

def mc_integrate_1d(f, lo, hi, n=5000, alpha=0.05):
    xs = np.random.random(n) * (hi - lo) + lo
    ys = f(xs)
    res = np.average(ys) * (hi - lo)

    # compute margin of error and return interval
    t = scipy.stats.t.ppf(1.0 - alpha / 2.0, df=n-1)
    margin = t * np.std(ys, ddof=1) / np.sqrt(n)
    return res
    # return res - margin, res + margin

def mc_integrate_nd(f, bounds, n=5000, alpha=0.05, coords=None):
    # we allow the user to input constants and functions in the bounds array
    # this prevents unsightly input like (lambda x,y,z: 0, lambda x,y,z: 1)
    # we then internally convert all bounds to functions for consistency
    # TODO: verify that closure doesn't mess things up
    def functionify(lo, hi):
        lower = lambda *_: lo
        if type(lo).__name__ == 'function':
            lower = lo
        upper = lambda *_: hi
        if type(hi).__name__ == 'function':
            upper = hi
        return lower, upper
    bounds = [functionify(lo, hi) for lo, hi in bounds]

    dim = len(bounds)
    if dim == 0:
        # if no bounds given, just evaluate the function
        # doesn't make much sense mathematically, but neat as a base case
        return f()
    if dim == 1:
        # TODO: check format of bounds array
        lo, hi = bounds[0]
        return mc_integrate_1d(f, lo(), hi(), n=n, alpha=alpha)

    # compute average value of the function over the given domain
    # we select 'n' uniform random samples in the given d-dimensional space
    # this provides a d-by-n matrix M that is used to estimate the average f
    # because nested bounds can be functions, we generate M layer-by-layer
    # TODO: consider changing this to generating an d-dimensional bounding box
    # and sampling uniformly from that box, filtering the bad ones?
    # this requires more points but reduces the calls to mc_volume_nd
    # this in turn cuts down on uncertainty
    res = 0.01
    samples = sample_point(bounds, n, resolution=res)
    M = np.array([samples])
    for i, _ in enumerate(bounds):
        if i == 0:
            continue
        newrow = []
        for j in range(n):
            fixed = fix_bounds(bounds, *M.T[j])
            point = sample_point(fixed[i:], 1, resolution=res)
            newrow += [point[0]]
        M = np.vstack([M, newrow])
    avg = np.average([f(*sample) for sample in M.T])

    # compute the volume by moving to a (d-1) dimensional space
    # then recursively integrate
    # TODO: adjust n, alpha for uncertainty
    vol = mc_volume_nd(bounds, n=n, alpha=alpha)
    return avg * vol

def mc_volume_nd(bounds, n, alpha):
    lo, hi = bounds[-1]
    if len(bounds) == 1:
        return hi() - lo()
    depth = lambda *x: hi(*x) - lo(*x)
    return mc_integrate_nd(depth, bounds[:-1], n=n, alpha=alpha)

# 1-norm of a vector v
# TODO: handle the zero vector appropriately
def normalize(v):
    return v / np.linalg.norm(v, ord=1)

# fix variable(s) in a bounds list
# e.g. fix [(x+y+z, x*y*z)] 0 3 => [(0+3+z, 0*3*z)]
# this is technically wrong, but it works
# I should have made everything take lists instead of varargs
def fix_bounds(bounds, *args):
    return list(map(lambda b: (lambda *y: b[0](*args, *y), lambda *y: b[1](*args, *y)), bounds))

def sample_point(region, n, resolution=0.01):
    lo, hi = region[0]
    assert hi() > lo()
    xs = np.linspace(lo(), hi(), num=np.ceil((hi() - lo())/resolution)+1)
    if len(region) == 1:
        return np.random.choice(xs, size=n)
    fixed = [fix_bounds(region[1:], x) for x in xs]
    weights = [mc_volume_nd(w, n=5000, alpha=0.05) for w in fixed]
    samples = np.random.choice(xs, size=n, p=normalize(weights))
    return samples

