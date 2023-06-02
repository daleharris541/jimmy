import json
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.game_data import Cost, UnitTypeData, AbilityData
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM
#from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM


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
    print(AbilityData.id_exists(16))

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
        builtfrom = None

        #upgrades game_data.py:280
        #
        #UnitTypeData.tech_requirement
        #UnitTypeData.techalias - this is for orbital command/planetary fortress
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
        elif type == 'unit':
            train_structure_type = UNIT_TRAINED_FROM[UnitTypeId[name]]
            builtfrom = str(train_structure_type).strip("{}").split(".")[1]

        if type != 'action':
            build_order.append([unit, ability, upgrade, type, builtfrom, supply]) #cost is always added to the end

    return build_order