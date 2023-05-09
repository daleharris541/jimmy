from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from typing import List, Optional, FrozenSet, Set
from sc2.position import Point2, Point3

units_barracks = ['MARINE', 'REAPER', 'MARAUDER', 'GHOST']
units_factory = ['HELLION', 'WIDOWMINE', 'CYCLONE', 'SIEGETANK']
units_starport = ['VIKING', 'MEDIVAC', 'LIBERATOR', 'RAVEN', 'BANSHEE', 'BATTLECRUISER']

async def train_unit(self: BotAI, unit_name):
    if unit_name in units_barracks:
        for barracks in self.structures(UnitTypeId.BARRACKS).ready:
            if barracks.train(UnitTypeId[unit_name], True):
                return True
            else:
                return False
    elif unit_name in units_factory:
        for factory in self.structures(UnitTypeId.FACTORY).ready:
            factory.train(UnitTypeId[unit_name], True)
    elif unit_name in units_starport:
        for starport in self.structures(UnitTypeId.FACTORY).ready:
            starport.train(UnitTypeId[unit_name], True)
    else:
        print(f'ArmyManager: (trainUnit) something went wrong - {unit_name}')
        return False
    
async def scout_enemy_base(self : BotAI, Point2):
    # An ordered list of locations to scout. Current target
    # is first on the list, with descending priority, ie.
    # least important location is last.
    self.scout_locations: List[Point2] = []