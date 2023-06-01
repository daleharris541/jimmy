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
    #Types are unit, structure, upgrade, worker, addon, cc

    for key in build:
        uppercase = key['name']
        name = uppercase.upper()
        id = key['id']
        type = key['type']
        supply = key['supply']
        time = key['time']
        frame = key['frame']
        
        unit = name
        ability = None
        upgrade = None

        if type == 'upgrade':
            if name == 'STIMPACK':
                unit = 'BARRACKSTECHLAB'
                ability = 'BARRACKSTECHLABRESEARCH_STIMPACK'
                upgrade = name

        elif 'TECHLAB' in name:
            if name[:8] == 'BARRACKS':
                unit = 'BARRACKS'
                ability = 'BUILD_TECHLAB_BARRACKS'
                type = 'addon'
            elif name[:7] == 'FACTORY':
                unit = 'FACTORY'
                ability = "BUILD_TECHLAB_FACTORY"
                type = 'addon'
            elif name[:8] == 'STARPORT':
                unit = 'STARPORT'
                ability = "BUILD_TECHLAB_STARPORT"
                type = 'addon'
        
        elif 'REACTOR' in name:
            if name[:8] == 'BARRACKS':
                unit = 'BARRACKS'
                ability = 'BUILD_REACTOR_BARRACKS'
                type = 'addon'
            elif name[:7] == 'FACTORY':
                unit = 'FACTORY'
                ability = "BUILD_REACTOR_FACTORY"
                type = 'addon'
            elif name[:8] == 'STARPORT':
                unit = 'STARPORT'
                ability = "BUILD_REACTOR_STARPORT"
                type = 'addon'

        elif name == 'ORBITALCOMMAND':
            ability = 'UPGRADETOORBITAL_ORBITALCOMMAND'
            type = 'commandcenter' 

        elif name == 'PLANETARYFORTRESS':
            ability = 'UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS'
            type = 'commandcenter' 

        if type != 'action':
            build_order.append([unit, ability, upgrade, type, supply])

    return build_order