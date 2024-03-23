#-=-=-=-=-=-=| Authors |-=-=-=-=-=-=-#
#            Matthew Payne           #
#             Will Cecil             #
#-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-#

import numpy as np
from Init import *

# Defining all movement behaviors

# Returns current linear and angular values of character
def DynamicGetSteeringContinue(mover):
    return {"linear": mover["linear"], "angular": mover["angular"]}

# Smoothly stops character by slowing said characters maximum acceleration value
def DynamicGetSteeringStop(mover):
    result = {"linear": np.array([0.0, 0.0], dtype=np.float64), "angular": 0.0}
    result["linear"] = - mover["velocity"]
    
    if magnitude(result["linear"]) > mover["max_linear"]:
        result["linear"] = normalize(result["linear"]) * mover["max_linear"]
    
    result["angular"] = - mover["rotation"]
    return result

# Align character with the orientation of target
def DynamicGetSteeringAlign(mover, target):
    result = {"linear": np.array([0.0, 0.0], dtype=np.float64), "angular": 0.0}
    rotation = target["orientation"] - mover["orientation"]
    rotation = convertAngle(rotation)
    
    if abs(rotation) < mover["align_radius"]:
        result["angular"] = -result["angular"]
    
    if abs(rotation) > mover["align_slow"]:
        align_rotation = mover["max_rotation"]
    else:
        align_rotation = mover["max_rotation"] * abs(rotation) / mover["align_slow"]
    
    align_rotation = align_rotation * np.sign(rotation)
    result["angular"] = (align_rotation - mover["rotation"]) / mover["align_time"]
    
    if abs(result["angular"]) > mover["max_angular"]:
        result["angular"] = mover["max_angular"] * np.sign(result["angular"])
    
    return result

# Moves straight toward target
def DynamicGetSteeringSeek(mover, target):
    result = {"linear": np.array([0.0, 0.0], dtype=np.float64), "angular": 0.0}
    direction = target['position'] - mover['position']
    result['linear'] = normalize(direction) * mover['max_linear']
    
    return result

# Moves straight away from target
def DynamicGetSteeringFlee(mover, target):
    result = {"linear": np.array([0.0, 0.0], dtype=np.float64), "angular": 0.0}
    direction = mover['position'] - target['position']
    result['linear'] = normalize(direction) * mover['max_linear']
   
    return result

# Slows charcter down to a stop as it approaches the target
def DynamicGetSteeringArrive(mover, target):
    result = {"linear": np.array([0.0, 0.0], dtype=np.float64), "angular": 0.0}
    direction = target['position'] - mover['position']
    distance = magnitude(direction)
    
    if distance < mover['arrive_radius']:
        arrive_speed = 0
    elif distance > mover['arrive_slow']:
        arrive_speed = mover['max_velocity']
    else:
        arrive_speed = mover['max_velocity'] * distance / mover['arrive_slow']
    
    arrive_velocity = normalize(direction) * arrive_speed
    result['linear'] = ((arrive_velocity - mover['velocity']) / mover['arrive_time'])

    if magnitude(result['linear']) > mover['max_linear']:
        result['linear'] = normalize(result['linear']) * mover['max_linear']
    
    return result

def DynamicGetSteeringFollowPath(mover, path):
    current_param = getPathParam(path, mover['position'])
    target_param = min(1, current_param + mover['path_offset'])
    target_position = getPathPosition(path, target_param)
    target = {'position': target_position}
    return DynamicGetSteeringSeek(mover, target)



# Constanly updating to simulate movement
def dynamicUpdate(mover, steering, deltaTime, physics, warnings=False, mode=None):
    mover['position'] = np.array(mover['position']).astype(np.float64)
    mover['velocity'] =  np.array(mover['velocity']).astype(np.float64)
    steering['linear'] = np.array(steering['linear']).astype(np.float64)

    if physics: 
        half_t_sq = 0.5 * deltaTime * deltaTime
        mover['position'] += mover['velocity'] * deltaTime + steering['linear'] * half_t_sq
        mover['orientation'] += mover['rotation'] * deltaTime + steering['angular'] * half_t_sq
    else: 
        mover['position'] += mover['velocity'] * deltaTime
        mover['orientation'] += mover['rotation'] * deltaTime

    mover['orientation'] = mover['orientation'] % (2 * np.pi)

    mover['velocity'] += steering['linear'] * deltaTime
    mover['rotation'] += steering['angular'] * deltaTime

    mover['linear'] = steering['linear']
    mover['angular'] = steering['angular']

    # Once velo gets low stop move -- attempt to reduce the jitter affect upon arrive
    if magnitude(mover['velocity']) < stop_velocity:
        mover['velocity'] = np.array([0, 0])

    if magnitude(mover['velocity']) > mover['max_velocity']:
        if warnings:
            print(f"character exceeded max velocity mode={mode} mover_id={mover['id']} max_velocity={mover['max_velocity']} velocity={mover['velocity']}")
        mover['velocity'] = mover['max_velocity'] * (mover['velocity'] / magnitude(mover['velocity']))

    if magnitude(mover['linear']) > mover['max_linear']:
        if warnings:
            print(f"character exceeded max linear mode={mode} mover_id={mover['id']} max_linear={mover['max_linear']} linear={mover['linear']}")
        mover['linear'] = mover['max_linear'] * (mover['linear'] / magnitude(mover['linear']))

    if abs(mover['rotation']) > mover['max_rotation']:
        if warnings:
            print(f"character exceeded max rotation mode={mode} mover_id={mover['id']} max_rotation={mover['max_rotation']} rotation={mover['rotation']}")
        mover['rotation'] = mover['max_rotation'] * np.sign(mover['rotation'])

    if abs(mover['angular']) > mover['max_angular']:
        if warnings:
            print(f"character exceeded max angular mode={mode} mover_id={mover['id']} max_angular={mover['max_angular']} angular={mover['angular']}")
        mover['angular'] = mover['max_angular'] * np.sign(mover['angular'])

    return mover

def writeTrajectory(character, time, trajectory_file):
    if np.isnan(character['position']).any():
        print("NaN detected in position:", character['position'])
    if np.isnan(character['velocity']).any():
        print("NaN detected in velocity:", character['velocity'])
    if np.isnan(character['linear']).any():
        print("NaN detected in linear:", character['linear'])
  
    char_out = f"{time},{character['id']},{character['position'][0]},{character['position'][1]},{character['velocity'][0]},{character['velocity'][1]},{character['linear'][0]},{character['linear'][1]},{character['orientation']},{character['steer']},{character['col_collided']}"
    with open(trajectory_file, 'a') as file:
        file.write(char_out + "\n")


for char in Character:
    writeTrajectory(char, Time, trajectory_file)

while Time < stopTime:
    Time += deltaTime
 
    for i in range(len(Character)):
        # Calling whichever behavior is needed
        if Character[i]['steer'] == CONTINUE:
            steering = DynamicGetSteeringContinue(Character[i])
        elif Character[i]['steer'] == STOP:
            steering = DynamicGetSteeringStop(Character[i])
        elif Character[i]['steer'] == SEEK:
            steering = DynamicGetSteeringSeek(Character[i], Character[i]['target'])
        elif Character[i]['steer'] == FLEE:
            steering = DynamicGetSteeringFlee(Character[i], Character[i]['target'])
        elif Character[i]['steer'] == ARRIVE:
            steering = DynamicGetSteeringArrive(Character[i], Character[i]['target'])
        elif Character[i]['steer'] == FOLLOW_PATH:
            pathToFollow = Character[i]['path_to_follow']
            steering = DynamicGetSteeringFollowPath(Character[i], Path[pathToFollow-1])

        Character[i] = dynamicUpdate(Character[i], steering, deltaTime, physics, warnings=False, mode=29)

    # Check for collisions -- stops both characters if a collision is found
    if checkCollisions:
        for i in range(len(Character) - 1):
            for j in range(i + 1, len(Character)):
                if not Character[i]['col_collided'] or not Character[j]['col_collided']:
                    col_distance = magnitude(Character[i]['position'] - Character[j]['position'])
                    col_radii = Character[i]['col_radius'] + Character[j]['col_radius']
                    if col_distance <= col_radii:
                        col_position = (Character[i]['position'] + Character[j]['position']) / 2
                        for k in [i, j]:
                            Character[k]['position'] = col_position
                            Character[k]['velocity'] = np.array([0, 0])
                            Character[k]['linear'] = np.array([0, 0])
                            Character[k]['rotation'] = 0
                            Character[k]['angular'] = 0
                            Character[k]['steer'] = STOP
                            Character[k]['col_collided'] = True

    # Write all updated positions to trajectory file
    for char in Character:
        writeTrajectory(char, Time, trajectory_file)
