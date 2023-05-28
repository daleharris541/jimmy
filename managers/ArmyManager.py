from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId

import tools.logger_levels as l

debug = False

units_barracks = ['MARINE', 'REAPER', 'MARAUDER', 'GHOST']
units_factory = ['HELLION', 'WIDOWMINE', 'CYCLONE', 'SIEGETANK']
units_starport = ['VIKING', 'MEDIVAC', 'LIBERATOR', 'RAVEN', 'BANSHEE', 'BATTLECRUISER']

async def train_unit(self: BotAI, unit_name):
    """
    This function checks for ready/idle structures to train.

    :param unit:
    """
    if unit_name in units_barracks:
        for barracks in self.structures(UnitTypeId.BARRACKS).ready and self.structures(UnitTypeId.BARRACKS).idle:
            #print(f"ArmyManager: Barracks: Built {unit_name}")
            if (barracks.train(UnitTypeId[unit_name])):
                return True
    elif unit_name in units_factory:
        for factory in self.structures(UnitTypeId.FACTORY).ready and self.structures(UnitTypeId.FACTORY).idle:
            if (factory.train(UnitTypeId[unit_name])):
                return True
    elif unit_name in units_starport:
        for starport in self.structures(UnitTypeId.STARPORT).ready and self.structures(UnitTypeId.STARPORT).idle:
            if(starport.train(UnitTypeId[unit_name])):
                return True
    else:
        l.g.log("ARMY", f'ArmyManager: (trainUnit) something went wrong - {unit_name}')
        return False