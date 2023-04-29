import json

def makeBuildOrder(filepath):
    build_order = []
    with open(filepath) as f:
        build = json.load(f)
    #this would be somewhere we could import a ton of different strategies
    #and pick the build order randomly
    for key in build:
        uppercase = key['name']
        name = uppercase.upper()
        id = key['id']
        type = key['type']
        supply = key['supply']
        time = key['time']
        frame = key['frame']

        build_order.append([name, id, type, supply, time, frame])
    return build_order