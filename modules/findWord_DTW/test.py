from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import numpy as np

def euclidean_dtw(X, Y):
    """Calculate Dynamic Time Warping distance with Euclidean distance as the element distance measure."""
    distance, path = fastdtw(X, Y, dist=euclidean)
    return distance

# Example usage:
X = np.random.rand(100, 3)  # Some 2-D Time series data
Y = np.random.rand(100, 3)  # Some other 2-D Time series data
print(X)

# print("MD-DTW Distance: ", md_dtw(X, Y))
print("Euclidean DTW Distance: ", euclidean_dtw(X, Y))
