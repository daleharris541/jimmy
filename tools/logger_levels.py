#Use this python file to import the custom logging levels for each python file/manager
from loguru import logger as g
import sys

g.level("JIMMY", no=100, color="<blue>")
g.level("ARMY", no=110, color="<green>")
g.level("UPGRADE", no=111, color="<green>")
g.level("BUILD", no=120, color="<yellow>")
g.level("CC",no=130, color="<blue>")
g.level("CONSTRUCTION", no=140, color="<yellow>")
g.level("MICROMANAGER", no=150, color="<red>")