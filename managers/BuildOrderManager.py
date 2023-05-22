from typing import Set
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.game_data import AbilityData, Cost
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM

next_build_steps = []
debug = True

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
        #if step[2] == 'action': next_build_steps.remove(step)
        cost: Cost = step[-1]
        if (requirements_check(self, step)):
            if((available.minerals - step_cost.minerals) >= cost.minerals and (available.vespene - step_cost.vespene) >= cost.vespene):
                if debug:
                    print(next_build_steps)
                    print(f"Sending {step[0]} to queue")
                next_build_steps.remove(step)
                return step
            else:
                step_cost += cost
  
def requirements_check(self: BotAI, step):
    can_build = False
    if step[2] == 'structure' or step[2] == 'addon' or step[2] == 'commandcenter':
        if self.tech_requirement_progress(UnitTypeId[step[0]]) == 1:
            can_build = True
    elif step[2] == 'worker':
        if self.supply_left > 0:
            can_build = True
    elif step[2] == 'upgrade':
        if self.research(UpgradeId[step[0]]):
            can_build = True
    elif step[2] == 'unit':
        train_structure_type = UNIT_TRAINED_FROM[UnitTypeId[step[0]]]
        building_name = str(train_structure_type).strip("{}").split(".")[1]
        if self.structures(UnitTypeId[building_name]).ready and self.supply_left >= self.calculate_supply_cost(UnitTypeId[step[0]]):
            can_build = True
    #train_structure_type: Set[UnitTypeId] = UNIT_TRAINED_FROM[step[0]]
    #TODO #25 Implement a proper lookup for unit type and validate all requirements met
    #/Users/dbh/Library/Python/3.9/lib/python/site-packages/sc2/dicts/unit_train_build_abilities.py
    return can_build