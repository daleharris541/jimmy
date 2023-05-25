from sc2.bot_ai import BotAI
from sc2.ids.upgrade_id import UpgradeId


async def research_upgrade(self: BotAI, unit_name):
        if self.research(UpgradeId[unit_name]):
            return True
        else:
            return False