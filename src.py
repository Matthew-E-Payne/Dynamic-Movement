#-=-=-=-=-=-=| Authors |-=-=-=-=-=-=-#
#            Matthew Payne           #
#             Will Cecil             #
#-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-#
# Contains most all of the math functions for the project to run

import numpy as np
import matplotlib.pyplot as plt


def magnitude(vector): # Return the magnitude of a vector
    return np.linalg.norm(vector)


def normalize(vector): # Return normalized vector
    vectorMagnitude = np.linalg.norm(vector)

    if vectorMagnitude:
        return vector / vectorMagnitude
    else:
        return np.array([0, 0], dtype=np.float64)


def dotProduct(vector1, vector2): # Return dot product of two vectors
    return np.dot(vector1, vector2)

def orientationToVector(orientation): # Return a radian orientation to vector
    return np.array([np.cos(orientation), np.sin(orientation)])


def distancePntToPnt(A, B): # Calculate distance between two 2D points
    return np.linalg.norm(np.subtract(B, A))

# Calculate the distance to a line in 2D
def distanceToLine(point, linePoint1, linePoint2):
    point, linePoint1, linePoint2 = np.array(point, dtype=np.float64), np.array(linePoint1, dtype=np.float64), np.array(linePoint2, dtype=np.float64)
    numerator = abs(((linePoint2[0] - linePoint1[0]) * (linePoint1[1] - point[1])) - 
                    ((linePoint1[0] - point[0]) * (linePoint2[1] - linePoint1[1])))
    denominator = np.linalg.norm(linePoint2 - linePoint1)
   
    return numerator / denominator

# Find point on line closest to point in 2D
def closestPointLine(Q, A, B): 
    Q, A, B = np.array(Q, dtype=np.float64), np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)
    T = np.dot(Q - A, B - A) / np.dot(B - A, B - A)
    return A + T * (B - A)

# Find point on segment closest to query point in 2D
def closestPointSegment(Q, A, B): 
    Q, A, B = np.array(Q, dtype=np.float64), np.array(A, dtype=np.float64), np.array(B, dtype=np.float64)
    T = np.dot(Q - A, B - A) / np.dot(B - A, B - A)
    
    if T < 0:
        return A
    elif T > 1:
        return B
    
    return A + T * (B - A)

def convertAngle(theta):
    theta = theta % (2 * np.pi)
    if np.abs(theta) > np.pi:
        theta = theta - (2 * np.pi * np.sign(theta))
    return theta


# Path functions

def createPath(pathID, path_x, path_y):
    path_x, path_y = np.array(path_x), np.array(path_y)
    
    path_segments = len(path_x) - 1
    
    pathDistance = np.zeros(path_segments + 1)
    for i in range(1, path_segments + 1):
        pathDistance[i] = pathDistance[i - 1] + distancePntToPnt([path_x[i - 1], path_y[i - 1]], [path_x[i], path_y[i]])
    
    path_param = np.zeros(path_segments + 1)
    for i in range(1, path_segments + 1):
        path_param[i] = pathDistance[i] / np.max(pathDistance)
    
    return {
        'id': pathID,
        'x': path_x,
        'y': path_y,
        'distance': pathDistance,
        'param': path_param,
        'segments': path_segments
    }

def getPathPosition(path, param):
    i = np.max(np.where(param > path['param'])[0])
    
    A = np.array([path['x'][i], path['y'][i]], dtype=np.float64)
    B = np.array([path['x'][i + 1], path['y'][i + 1]], dtype=np.float64)
    
    T = (param - path['param'][i]) / (path['param'][i + 1] - path['param'][i])
    P = A + (T * (B - A))
    
    return P

def getPathParam(path, position):
    closestDistance = np.inf
    position = np.array(position)
    
    for i in range(path['segments']):
        A = np.array([path['x'][i], path['y'][i]], dtype=np.float64)
        B = np.array([path['x'][i + 1], path['y'][i + 1]], dtype=np.float64)
        
        checkPoint = closestPointSegment(position, A, B)
        checkDistance = distancePntToPnt(position, checkPoint)
        
        if checkDistance < closestDistance:
            closest_point = checkPoint
            closestDistance = checkDistance
            closestSegment = i

    A = np.array([path['x'][closestSegment], path['y'][closestSegment]], dtype=np.float64)
    A_param = path['param'][closestSegment]
    B = np.array([path['x'][closestSegment + 1], path['y'][closestSegment + 1]], dtype=np.float64)
    B_param = path['param'][closestSegment + 1]
    C = closest_point
    T = magnitude(C - A) / magnitude(B - A)
    C_param = A_param + (T * (B_param - A_param))
    
    return C_param


# More movement functions
def closest_approach(A_position, A_velocity, B_position, B_velocity):
    A_position, A_velocity = np.array(A_position, dtype=np.float64), np.array(A_velocity, dtype=np.float64)
    B_position, B_velocity = np.array(B_position, dtype=np.float64), np.array(B_velocity, dtype=np.float64)
    
    d_p = B_position - A_position
    d_v = B_velocity - A_velocity
    
    if np.linalg.norm(d_v) != 0:
        closest_t = -dotProduct(d_p, d_v) / (magnitude(d_v) ** 2)
        closest_A = A_position + (A_velocity * closest_t)
        closest_B = B_position + (B_velocity * closest_t)
        closest_d = distancePntToPnt(closest_A, closest_B)
    else:
        closest_t = 0
        closest_A = A_position
        closest_B = B_position
        closest_d = distancePntToPnt(A_position, B_position)
    
    return closest_t, closest_d, closest_A, closest_B

def randomBinomial():
    return np.random.uniform(0, 1) - np.random.uniform(0, 1)

# Plotting Functions

def plotCircle(center=(0, 0), radius=1, sides=64, color="darkgray"):
    theta = np.linspace(0, 2 * np.pi, sides)
    sides_x = np.cos(theta) * radius + center[0]
    sides_y = np.sin(theta) * radius + center[1]
    plt.plot(sides_x, sides_y, linestyle='dashed', linewidth=0.75, color=color)

def textOut(msg, textfile, first=False):
    mode = 'w' if first else 'a'
    with open(textfile, mode) as f:
        f.write(msg + "\n")

def numWidth(x, left, right):
    format_spec = "{:." + str(right) + "f}"
    return format_spec.format(round(x, right)).rjust(left + right + (1 if right > 0 else 0))


# Test cases
def supportTest():
    results = []

    # Test case 1
    Q = np.array([-6, 3])
    A = np.array([-8, 5])
    B = np.array([-4, 5])
    Sl = np.array([-6, 5])
    Ss = np.array([-6, 5])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

 # Test case 2
    Q = np.array([3, 3])
    A = np.array([1, 2])
    B = np.array([1, 6])
    Sl = np.array([1, 3])
    Ss = np.array([1, 3])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    # Test case 3
    Q = np.array([6, 0])
    A = np.array([6, 2])
    B = np.array([9, 5])
    Sl = np.array([5, 1])
    Ss = np.array([6, 2])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    # Test case 4
    Q = np.array([-3, -1])
    A = np.array([-8, 1])
    B = np.array([-4, 0])
    Sl = np.array([-2.9, -0.3])
    Ss = np.array([-4, 0])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    # Test case 5
    Q = np.array([-8, -3])
    A = np.array([-7, -3])
    B = np.array([-5, -3])
    Sl = np.array([-8, -3])
    Ss = np.array([-7, -3])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    # Test case 6
    Q = np.array([3, -3])
    A = np.array([-1, -3])
    B = np.array([2, -3])
    Sl = np.array([3, -3])
    Ss = np.array([2, -3])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    # Test case 7
    Q = np.array([8, -3])
    A = np.array([9, -3])
    B = np.array([6, -3])
    Sl = np.array([8, -3])
    Ss = np.array([8, -3])
    results.append(np.array_equal(Sl, closestPointLine(Q, A, B)))
    results.append(np.array_equal(Ss, closestPointSegment(Q, A, B)))

    return results


if __name__ == "__main__":
    results = supportTest()
    for idx, result in enumerate(results):
        print(f"Test {idx+1} {'PASSED' if result else 'FAILED'}")