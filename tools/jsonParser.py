import json

def makeBuildOrder(filepath):
    build_order = []
    with open(filepath) as f:
        data = json.load(f)
    #this would be somewhere we could import a ton of different strategies
    #and pick the build order randomly
    build = data['quickbuild']
    for key in build:
        unit = key['name']
        unitId = key['id']
        unitType = key['type']
        action =  key['action']
        atSupply = key['supply']
        time = key['time']
        frame = key['frame']
        if 'targetQuantity' in key:
            targetQuantity = key['targetQuantity']
        else:
            targetQuantity = None
        
        build_order.append([unit, unitId, unitType, action, targetQuantity, atSupply, time, frame])    
        #print(atSupply, type, unit, targetQuantity)
    return build_order