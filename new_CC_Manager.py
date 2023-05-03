from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

"""
# Find all Command Centers
cc_list = self.units(UnitTypeId.COMMANDCENTER) | self.units(UnitTypeId.ORBITALCOMMAND) | self.units(UnitTypeId.PLANETARYFORTRESS)

# Create a new CC_Manager instance for each Command Center if it doesn't already exist
for cc in cc_list:
    if not any(cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers):
        cc_manager = CC_Manager(self, cc)
        self.cc_managers.append(cc_manager)

# Call the manage_cc function for each CC_Manager instance
for cc_manager in self.cc_managers:
    await cc_manager.manage_cc()
"""

class CC_Manager:

    def __init__(self, bot: BotAI, townhall: Unit):
        self.bot = bot
        self.townhall = townhall
        self.research_complete = False

    async def manage_cc(self):
        """The main function of the CC_Manager that manages the Command Center."""
        #await self.call_down_supply()
        await self.call_down_mule()

    async def upgrade_orbital_command(self):
        """This function upgrades the Command Center to an Orbital Command or Planetary Fortress."""
        if self.townhall.is_idle:
            if self.townhall.add_on_tag == 0 and self.bot.can_afford(UnitTypeId.ORBITALCOMMAND) and self.orbital:
                await self.bot.do(self.townhall(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND))

    async def upgrade_planetaryfortress(self):
        """This function upgrades the Command Center to an Orbital Command or Planetary Fortress."""
        if self.townhall.is_idle:
            if self.townhall.add_on_tag == 0 and self.bot.can_afford(UnitTypeId.PLANETARYFORTRESS) and not self.orbital:
                await self.bot.do(self.townhall(AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS))

    async def call_down_supply(self):
        """This function calls down a Supply Depot to the nearest buildable location."""
        if self.bot.supply_left < 5:
            if self.bot.can_afford(AbilityId.CALLDOWNMULE_CALLDOWNMULE):
                closest_buildable_location = await self.bot.get_next_expansion()
                if closest_buildable_location is not None:
                    await self.bot.do(self.townhall(AbilityId.SUPPLYDROP_SUPPLYDROP, closest_buildable_location))

    async def call_down_mule(self):
        """This function calls down a MULE to the nearest mineral field."""
        if self.bot.minerals > 300:
            closest_mineral_field = self.bot.state.mineral_field.closest_to(self.townhall)
            await self.bot.do(self.townhall(AbilityId.CALLDOWNMULE_CALLDOWNMULE, closest_mineral_field))
