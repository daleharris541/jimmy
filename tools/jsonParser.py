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
    #2 = type
    #3 = supply
    #4 = cost (added on templateBot)
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
        
        if type == 'upgrade':
            if name == 'STIMPACK':
                id = 'BARRACKSTECHLABRESEARCH_STIMPACK'
        elif 'TECHLAB' in name:
            if name[:8] == 'BARRACKS':
                id = 'BUILD_TECHLAB_BARRACKS'
                type = 'addon'
            elif name[:7] == 'FACTORY':
                id = "BUILD_TECHLAB_FACTORY"
                type = 'addon'
            elif name[:8] == 'STARPORT':
                id = "BUILD_TECHLAB_STARPORT"
                type = 'addon'
        
        elif 'REACTOR' in name:
            if name[:8] == 'BARRACKS':
                id = 'BUILD_REACTOR_BARRACKS'
                type = 'addon'
            elif name[:7] == 'FACTORY':
                id = "BUILD_REACTOR_FACTORY"
                type = 'addon'
            elif name[:8] == 'STARPORT':
                id = "BUILD_REACTOR_STARPORT"
                type = 'addon'

        elif name == 'ORBITALCOMMND':
            name = 'UPGRADETOORBITAL_ORBITALCOMMAND'
            id = 'UPGRADETOORBITAL_ORBITALCOMMAND'
            type = 'commandcenter' 

        elif name == 'PLANETARYFORTRESS':
            name = 'UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS'
            id = 'UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS'
            type = 'commandcenter' 
        
        elif name == 'REFINERY':
            type = 'commandcenter'
            id = 'TERRANBUILD_REFINERY'
        if type != 'action':
            build_order.append([name, id, type, supply])

    return build_order