from sc2.bot_ai import BotAI

async def idle_workers(self: BotAI):
    if len(self.townhalls) > 0 and len(self.workers) > 0:
        workers = [worker for worker in self.workers if worker.is_idle]
        th = [townhall for townhall in self.townhalls if townhall.position in self.expansion_locations_list]
        for worker in workers:
            townhall = self.townhalls.ready.closest_to(worker)
            mineral = self.mineral_field.closest_to(townhall)
            worker.gather(mineral)