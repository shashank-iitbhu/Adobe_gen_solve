# -*- coding: utf-8 -*-
"""Adobe_genSolve.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LOiCNNzmYQL8WvHd7AlJBVLNBYDMOfGQ
"""

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

def read_csv(csv_path):
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    return path_XYs

def plot(paths_XYs):
    colours = ['red', 'green', 'blue', 'yellow', 'purple']
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    for i, XYs in enumerate(paths_XYs):
        c = colours[i % len(colours)]
        for XY in XYs:
            ax.plot(XY[:, 0], XY[:, 1], c=c, linewidth=2)
    ax.set_aspect('equal')
    plt.show()

# Function to fit a cubic Bézier curve to given points
def fit_bezier_curve(XY):
    def bezier_curve(t, P0, P1, P2, P3):
        return (1-t)**3 * P0 + 3*(1-t)**2 * t * P1 + 3*(1-t) * t**2 * P2 + t**3 * P3

    def error(params, X, Y):
        P0 = np.array([X[0], Y[0]])
        P3 = np.array([X[-1], Y[-1]])
        P1 = np.array([params[0], params[1]])
        P2 = np.array([params[2], params[3]])

        t = np.linspace(0, 1, len(X))
        curve_X = bezier_curve(t, P0[0], P1[0], P2[0], P3[0])
        curve_Y = bezier_curve(t, P0[1], P1[1], P2[1], P3[1])
        return np.sum((curve_X - X)**2 + (curve_Y - Y)**2)

    X = XY[:, 0]
    Y = XY[:, 1]

    # Initial guess for P1 and P2
    initial_guess = [X[len(X)//3], Y[len(Y)//3], X[2*len(X)//3], Y[2*len(Y)//3]]

    result = minimize(error, initial_guess, args=(X, Y))
    P0 = np.array([X[0], Y[0]])
    P3 = np.array([X[-1], Y[-1]])
    P1 = np.array([result.x[0], result.x[1]])
    P2 = np.array([result.x[2], result.x[3]])

    return np.array([P0, P1, P2, P3])

# Function to identify regular shapes
def identify_shape(bezier_curve):
    P0, P1, P2, P3 = bezier_curve

    # Check if it's a straight line
    if np.allclose(np.cross(P3 - P0, P1 - P0), 0) and np.allclose(np.cross(P3 - P0, P2 - P0), 0):
        return "Line"

    # Check if it's a circle or part of a circle
    if np.isclose(euclidean(P0, P3), euclidean(P1, P2)):
        return "Circle or Ellipse"

    # Check if it's a rectangle (more complex checks required)
    if np.isclose(np.dot(P1 - P0, P2 - P3), 0):
        return "Rectangle"

    return "Unknown Shape"

# Function to regularize identified shapes
def regularize_shape(bezier_curve, shape_type):
    P0, P1, P2, P3 = bezier_curve

    if shape_type == "Line":
        mid = (P0 + P3) / 2
        P1 = P2 = mid

    elif shape_type == "Circle or Ellipse":
        radius = (euclidean(P0, P3) + euclidean(P1, P2)) / 2
        mid = (P0 + P3) / 2
        P1 = P2 = mid + radius * (P1 - mid) / euclidean(P1, mid)

    elif shape_type == "Rectangle":
        mid = (P0 + P3) / 2
        P1 = mid + np.array([P1[1] - mid[1], mid[0] - P1[0]])
        P2 = mid + np.array([P2[1] - mid[1], mid[0] - P2[0]])

    return np.array([P0, P1, P2, P3])

# Process paths to identify and regularize shapes
def process_paths(paths_XYs):
    regular_shapes = []
    for XYs in paths_XYs:
        for XY in XYs:
            bezier_curve = fit_bezier_curve(np.array(XY))
            shape_type = identify_shape(bezier_curve)
            regular_curve = regularize_shape(bezier_curve, shape_type)
            regular_shapes.append((shape_type, regular_curve))
    return regular_shapes

# Example usage:
path_XYs = read_csv(csv_path='/content/frag2_sol.csv')
print(len(path_XYs))
plot(path_XYs)
regular_shapes = process_paths(path_XYs)

for shape in regular_shapes:
    print(f"Shape: {shape[0]}, Bézier Curve Control Points: {shape[1]}")