from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
from BuildManager import BuildManager

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class CompetitiveBot(BotAI):

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    async def on_step(self, iteration):
        self.BuildManager = await BuildManager.create(self)

    async def on_end(self):
        print("Game ended.")
        # Do things here after the game ends

def main():
    run_game(
        maps.get("BerlingradAIE"),
        [Bot(Race.Terran, CompetitiveBot()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()