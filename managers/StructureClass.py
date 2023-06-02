from tools import closest_point
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.position import Point2, Point3
from typing import Set

class Structure:

    def __init__(self, bot: BotAI, build_order, depot_positions: Set[Point2], building_positions: Set[Point2]):
        self.bot = bot
        self.build_order = build_order
        self.depot_positions = depot_positions
        self.building_positions = building_positions
        self.building_list = []
        self.building_command_received = []
        self.building_list_started = []
        self.building_list_completed = []
        self.failed_to_build = []
        self.debug = True