from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.game_data import AbilityData, Cost

next_build_steps = []

def fill_build_queue(build_order: list, step, range):
    if len(next_build_steps) < range:
        if step < len(build_order):
            next_build_steps.append(build_order[step])
            step += 1
    return step

def build_queue(self: BotAI):
    available = Cost(self.minerals, self.vespene)
    step_cost = Cost(0,0)

    for step in next_build_steps:
        cost: Cost = step[-1]
        if((available.minerals - step_cost.minerals) > cost.minerals):
            next_build_steps.remove(step)
            return step
        else:
            step_cost += cost