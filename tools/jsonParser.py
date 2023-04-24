import json

def makeBuildOrder(filepath):
    build_order = []
    with open(filepath) as f:
        data = json.load(f)

    build = data['buildings']

    for key in build:
        unit = key['unit']
        action =  key['action']
        atSupply = key['atSupply']
        if 'targetQuantity' in key:
            targetQuantity = key['targetQuantity']
        else:
            targetQuantity = None
        
        build_order.append([unit, action, atSupply, targetQuantity])    
        #print(atSupply, type, unit, targetQuantity)
    return build_order