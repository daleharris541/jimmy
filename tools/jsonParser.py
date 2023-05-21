import json

def make_build_order(filepath):
    build_order = []
    with open(filepath) as f:
        build = json.load(f)

    for key in build:
        uppercase = key['name']
        name = uppercase.upper()
        id = key['id']
        type = key['type']
        supply = key['supply']
        time = key['time']
        frame = key['frame']
        build_order.append([name, type, supply])

    for order in build_order:
        if order[1] == 'action':
            build_order.remove[order]

    return build_order

def order_change(build_order):
    for order in build_order:

        if 'TECHLAB' in order[0]:
            if order[0][:8] == 'BARRACKS':
                order[0] = 'BUILD_TECHLAB_BARRACKS'
            elif order[0][:7] == 'FACTORY':
                order[0] = "BUILD_TECHLAB_FACTORY"
            elif order[0][:8] == 'STARPORT':
                order[0] = "BUILD_TECHLAB_STARPORT"
        
        elif 'REACTOR' in order[0]:
            if order[0][:8] == 'BARRACKS':
                order[0] = 'BUILD_REACTOR_BARRACKS'
            elif order[0][:7] == 'FACTORY':
                order[0] = "BUILD_REACTOR_FACTORY"
            elif order[0][:8] == 'STARPORT':
                order[0] = "BUILD_REACTOR_STARPORT"

        elif order[0] == 'ORBITALCOMMND':
            order[0] = 'UPGRADETOORBITAL_ORBITALCOMMAND'
            order[1] = 'commandcenter' 

        elif order[0] == 'PLANETARYFORTRESS':
            order[0] = 'UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS'
            order[1] = 'commandcenter' 
        
        elif order[0] == 'REFINERY':
            order[1] = 'commandcenter'