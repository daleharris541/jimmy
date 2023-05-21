import json
from sc2.game_data import AbilityData, Cost

def make_build_order(filepath):
    build_order = []
    with open(filepath) as f:
        build = json.load(f)
    #consider name = unit structure to build
    #second field in build order should be AbilityID if applicable
    #normal build order
    #0 = name
    #1 = id
    #2 = supply
    #3 = time
    #4 = frame
    #proposed build order
    #0 = structure name or unit name
    #1 = abilityID if applicable
    #2 = supply?
    #3 = ?
    #4 = cost
    #tech_requirement_progress(self, structure_type: UnitTypeId) -> float:
    # Returns the tech requirement progress for a specific building
    # we only want structures being done this way
    for key in build:
        uppercase = key['name']
        name = uppercase.upper()
        id = key['id']
        type = key['type']
        supply = key['supply']
        time = key['time']
        cost = key['frame']
        
        if 'TECHLAB' in name:
            if name[:8] == 'BARRACKS':
                id = 'BUILD_TECHLAB_BARRACKS'
            elif name[:7] == 'FACTORY':
                id = "BUILD_TECHLAB_FACTORY"
            elif name[:8] == 'STARPORT':
                id = "BUILD_TECHLAB_STARPORT"
        
        elif 'REACTOR' in name:
            if name[:8] == 'BARRACKS':
                id = 'BUILD_REACTOR_BARRACKS'
            elif name[:7] == 'FACTORY':
                id = "BUILD_REACTOR_FACTORY"
            elif name[:8] == 'STARPORT':
                id = "BUILD_REACTOR_STARPORT"

        elif name == 'ORBITALCOMMND':
            name = 'UPGRADETOORBITAL_ORBITALCOMMAND'
            type = 'commandcenter' 

        elif name == 'PLANETARYFORTRESS':
            name = 'UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS'
            type = 'commandcenter' 
        
        elif name == 'REFINERY':
            type = 'commandcenter'
        build_order.append([name, id, type, supply])

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