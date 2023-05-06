from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

async def idle_workers(self: BotAI):
        workers = [worker for worker in self.workers if worker.is_idle]
        for worker in workers:
            townhall = self.townhalls.closest_to(worker)
            mineral = self.mineral_field.closest_to(townhall)
            worker.gather(mineral)