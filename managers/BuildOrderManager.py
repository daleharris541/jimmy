from typing import Set
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.game_data import Cost
from sc2.dicts.unit_trained_from import UNIT_TRAINED_FROM

import tools.logger_levels as l

next_build_steps = []           #this is our hopper that carries 5 orders and attempts to build ahead
completed_build_steps = []      #this is our original function meant to keep track of what's done
debug = True

def fill_build_queue(build_order: list, index, range):
    if len(next_build_steps) < range:
        if index < len(build_order):
            next_build_steps.append(build_order[index])
            index += 1
    return index

def build_queue(self: BotAI):
    """
    This function uses next_build_steps as the hopper of 5 orders
    step as the full order like ['BARRACKSTECHLAB', 'BUILD_TECHLAB_BARRACKS', 'addon', 27, Cost(50, 25)]
    """
    available = Cost(self.minerals, self.vespene)
    step_cost = Cost(0,0)
    for step in next_build_steps:
        cost: Cost = step[-1] 
        if (requirements_check(self, step)):
            if((available.minerals - step_cost.minerals) >= cost.minerals and (available.vespene - step_cost.vespene) >= cost.vespene):
                next_build_steps.remove(step)
                return step
            else:
                step_cost += cost
  
def requirements_check(self: BotAI, step):
    can_build = False
    if step[3] == 'structure' or step[3] == 'addon' or step[3] == 'commandcenter':
        if self.tech_requirement_progress(UnitTypeId[step[0]]) == 1:
            can_build = True
    elif step[3] == 'worker':
        if self.supply_left > 0:
            can_build = True
    elif step[3] == 'upgrade':
        if self.research(UpgradeId[step[2]]):
            can_build = True
    elif step[3] == 'unit':
        if self.structures(UnitTypeId[step[4]]).ready and self.supply_left >= self.calculate_supply_cost(UnitTypeId[step[0]]):
            can_build = True
    #train_structure_type: Set[UnitTypeId] = UNIT_TRAINED_FROM[step[0]]
    #TODO #25 Implement a proper lookup for unit type and validate all requirements met
    #/Users/dbh/Library/Python/3.9/lib/python/site-packages/sc2/dicts/unit_train_build_abilities.py
    return can_build

# def remove_from_hopper(unit: UnitTypeId):
#     """
#     This function receives an upgrade, building, or army unit that's been trained from the Bot
#     and removes it from the Hopper

#     Buildings are slow, but we are notified by BotAI when it's started
#     Upgrades are slow and notified only after completed, but we can also do a upgrade_check to see if it's being actively researched in another way
#     Units are fairly quick, and we are notified by BotAI when completed
#     Addons are not sent out as a "structure"being completed
#     Workers are tracked as Units

#     """
#     unit = unit.name
#     completed_build_steps.append(unit)
#     unit = str(unit)
#     for order in next_build_steps:
#         if order[0].find(unit.upper()) > -1:
#             if debug: l.g.log("CRITICAL",f"Hopper should work! Current Hopper Size: {len(next_build_steps)}")
#             next_build_steps.remove(order)
#             if debug: l.g.log("CRITICAL",f"After removing {order[0]}, New Hopper Size: {len(next_build_steps)}")
#             break