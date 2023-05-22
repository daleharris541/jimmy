from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units

async def research_upgrade(self: BotAI, unit_name):
        if self.research(UpgradeId[unit_name]):
            return True
        else:
            return False