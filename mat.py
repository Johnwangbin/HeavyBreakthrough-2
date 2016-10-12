import numpy as np

def variance(x):
    xArray  = np.array(x)
    sum1    = xArray.sum()
    sum2    = (xArray*xArray).sum()
    N       = len(x)
    mean    = sum1 / N
    return sum2 / N - mean ** 2