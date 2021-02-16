from mapa import Map
import asyncio
from tree_search_boxes import *
from tree_search_boxes_helper import *


mapa = Map("levels/1.xsb")
'''
keeperDomain = KeeperDomain(mapa)
TestProblem = SearchProblemKeeper(keeperDomain, mapa.keeper, (mapa.keeper[0]-1,mapa.keeper[1]-2))
tree = SearchTreeKeeper(TestProblem)
keys = tree.search()
print(keys)
'''
async def do():
    Boxproblem = SearchProblemBoxes(Maze(mapa), mapa.boxes, mapa.filter_tiles([Tiles.GOAL]))
    Boxtree = SearchTreeBoxes(Boxproblem)
    keys = await Boxtree.search()
    print(keys)
loop = asyncio.get_event_loop()
loop.run_until_complete(do())