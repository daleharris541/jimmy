from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

units_barracks = ['MARINE', 'REAPER', 'MARAUDER', 'GHOST']
units_factory = ['HELLION ', 'WIDOWMINE', 'CYCLONE', 'SIEGETANK']
units_starport = ['VIKING', 'MEDICAC', 'LIBERATOR', 'RAVEN', 'BANSHEE', 'BATTLECRUISER']

async def research_upgrade(self: BotAI, unit_name):
    if unit_name == 'STIMPACK':
        if self.can_afford(AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK) and self.tech_requirement_progress(AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK) == 1:
            if self.structures(UnitTypeId.BARRACKSTECHLAB):
                for techlab in self.structures(UnitTypeId.BARRACKSTECHLAB).ready:
                    if techlab(AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK):
                        return True
    else:
        return True