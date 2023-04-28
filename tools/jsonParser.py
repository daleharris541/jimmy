import json

def makeBuildOrder(filepath):
    build_order = []
    with open(filepath) as f:
        build = json.load(f)
    #this would be somewhere we could import a ton of different strategies
    #and pick the build order randomly
    for key in build:
        unit = key['name']
        unit = unit.upper()
        unitId = key['id']
        unitType = key['type']
        atSupply = key['supply']
        time = key['time']
        frame = key['frame']

        build_order.append([unit, unitId, unitType, atSupply, time, frame])
        #print(atSupply, type, unit, targetQuantity)
    return build_order