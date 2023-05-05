from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

units_barracks = ['MARINE', 'REAPER', 'MARAUDER', 'GHOST']
units_factory = ['HELLION', 'WIDOWMINE', 'CYCLONE', 'SIEGETANK']
units_starport = ['VIKING', 'MEDICAC', 'LIBERATOR', 'RAVEN', 'BANSHEE', 'BATTLECRUISER']

async def train_unit(self: BotAI, unit_name):
    if unit_name in units_barracks:
        for barracks in self.structures(UnitTypeId.BARRACKS).ready.idle:
            barracks.train(UnitTypeId[unit_name])
    elif unit_name in units_factory:
        for factory in self.structures(UnitTypeId.FACTORY).ready.idle:
            factory.train(UnitTypeId[unit_name])
    elif unit_name in units_starport:
        for starport in self.structures(UnitTypeId.FACTORY).ready.idle:
            starport.train(UnitTypeId[unit_name])
    else:
        print(f'ArmyManager: (trainUnit) someting went wrong - {unit_name}')
        return False