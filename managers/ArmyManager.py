from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from loguru import logger

units_barracks = ['MARINE', 'REAPER', 'MARAUDER', 'GHOST']
units_factory = ['HELLION', 'WIDOWMINE', 'CYCLONE', 'SIEGETANK']
units_starport = ['VIKING', 'MEDIVAC', 'LIBERATOR', 'RAVEN', 'BANSHEE', 'BATTLECRUISER']

async def train_unit(self: BotAI, unit_name):
    if unit_name in units_barracks:
        for barracks in self.structures(UnitTypeId.BARRACKS).ready and self.structures(UnitTypeId.BARRACKS).idle:
            #print(f"ArmyManager: Barracks: Built {unit_name}")
            if (barracks.train(UnitTypeId[unit_name])):
                return True
    elif unit_name in units_factory:
        for factory in self.structures(UnitTypeId.FACTORY).ready:
            if (factory.train(UnitTypeId[unit_name])):
                return True
    elif unit_name in units_starport:
        for starport in self.structures(UnitTypeId.FACTORY).ready:
            if(starport.train(UnitTypeId[unit_name])):
                return True
    else:
        print(f'ArmyManager: (trainUnit) something went wrong - {unit_name}')
        return False