##http://sokobano.de/wiki/index.php?title=How_to_detect_deadlocks
import math
from tree_search_boxes import SearchDomainBoxes
from consts import Tiles

class Maze(SearchDomainBoxes):
    def __init__(self, map):
        #loops and ifs in the init dont cause much problems for performance
        #this is because it is only done once at the beginning
        self.map=map
        self.size=map.size
        (x0,y0) = map.size
        self.boxpos=[[False for y in range(y0)] for x in range(x0)] #[x][y] using positions of the boxes

        for x in range(0,x0):
            for y in range(0,y0):
                self.boxpos[x][y]=False

        self.walls = [[False for y in range(y0)] for x in range(x0)] #[x][y] using positions of the walls

        for (x,y) in map.filter_tiles([Tiles.WALL]):
            self.walls[x][y] = True
            
        self.goals = [[False for y in range(y0)] for x in range(x0)] #[x][y] using positions of the goals
        self.goalstate = []
        for (x,y) in map.filter_tiles([Tiles.GOAL,Tiles.BOX_ON_GOAL,Tiles.MAN_ON_GOAL]):
            self.goals[x][y] = True
            self.goalstate.append((x,y))

        self.simple_deadlock = [[False for y in range(y0)] for x in range(x0)]

        #confirms if there is a wall vertically and horizontally
        for x in range(1,x0-1):
            for y in range(1,y0-1):
                if not self.walls[x][y] and not self.goals[x][y]:
                    if ((self.walls[x+1][y] or self.walls[x-1][y]) and (self.walls[x][y+1] or self.walls[x][y-1])):
                        self.simple_deadlock[x][y]=True #its a deadlock
        
        self.blocked = [[False for y in range(y0)] for x in range(x0)] #[x][y] using positions of the goals

        self.frozenBox = [[False for y in range(y0)] for x in range(x0)] #used for freeze deadlock

        self.simpleTile = [[False for y in range(y0)] for x in range(x0)]

        for x in range(1,x0-1):
            for y in range(1,y0-1):
                if not self.walls[x][y] and not self.simple_deadlock[x][y]:
                    self.simpleTile[x][y] = True

        #If there is a simple deadlock square on both sides (left and right) of the box the box is blocked along this axis 
        for x in range(1,x0-1):
            for y in range(1,y0-1):
                if not self.walls[x][y] and not self.goals[x][y]:
                    if (((self.walls[x+1][y] or self.walls[x-1][y]) or (self.simple_deadlock[x+1][y] and self.simple_deadlock[x-1][y])) and 
                        ((self.walls[x][y+1] or self.walls[x][y-1]) or (self.simple_deadlock[x][y+1] and self.simple_deadlock[x][y-1]))):
                        self.blocked[x][y]=True
                    if self.blockingWall_deadlock(x,y,self.frozenBox, []):
                       self.blocked[x][y]=True #its a deadlock

    def blockingWall_deadlock(self,x,y,blockedPos, addedBlocked):
        #blocking wall is the positions touching a wall where placing a box causes a deadlock
              
        ###########
        #         # <- this is a blocking wall
              
        if self.goals[x][y]:
            #if there is a position that is a goal on that wall then that wall wont be considered as a blocking wall
            for (x1,y1) in addedBlocked:
                blockedPos[x1][y1] = False
            for (x1,y1) in addedBlocked:
                self.simpleTile[x1][y1] = True
            return False

        #blocked on y confirm if simple deadlock on the right and tile on the left
        if (( self.walls[x][y+1] or self.walls[x][y-1]) and
               ( (self.simple_deadlock[x+1][y] or blockedPos[x+1][y]) and self.simpleTile[x-1][y]) ):
            blockedPos[x][y] = True
            self.simpleTile[x][y]=False
            addedBlocked.append((x,y))
            return self.blockingWall_deadlock((x-1),y,blockedPos,addedBlocked)
        #blocked on y confirm if simple deadlock on the left and tile on the right
        if (( self.walls[x][y+1] or self.walls[x][y-1]) and
               ((self.simple_deadlock[x-1][y] or blockedPos[x-1][y]) and self.simpleTile[x+1][y]) ):
            blockedPos[x][y] = True
            self.simpleTile[x][y]=False
            addedBlocked.append((x,y))
            return self.blockingWall_deadlock((x+1),y,blockedPos,addedBlocked)
        #blocked on x confirm if simple deadlock on the top and tile on the bottom
        if (( self.walls[x+1][y]  or self.walls[x-1][y]) and
               ((self.simple_deadlock[x][y+1]  or blockedPos[x][y+1]) and self.simpleTile[x][y-1]) ):
            blockedPos[x][y] = True
            self.simpleTile[x][y]=False
            addedBlocked.append((x,y))
            return self.blockingWall_deadlock(x,(y-1),blockedPos,addedBlocked)
        #blocked on x confirm if simple deadlock on the bottom and tile on the top
        if (( self.walls[x+1][y]  or self.walls[x-1][y]) and
               ((self.simple_deadlock[x][y-1]  or blockedPos[x][y-1]) and self.simpleTile[x][y+1]) ):
            blockedPos[x][y] = True
            self.simpleTile[x][y]=False
            addedBlocked.append((x,y))
            return self.blockingWall_deadlock(x,(y+1),blockedPos,addedBlocked)

        if (((self.walls[x+1][y]or self.walls[x-1][y])) and 
                ( (self.simple_deadlock[x][y+1] or blockedPos[x][y+1]) and (self.simple_deadlock[x][y-1] or blockedPos[x][y-1]))):
            for (x1,y1) in addedBlocked:
                blockedPos[x1][y1] = False
            for (x1,y1) in addedBlocked:
                self.simpleTile[x1][y1] = True
            return True

        if (((self.walls[x][y+1]or self.walls[x][y-1])) and 
                ( (self.simple_deadlock[x+1][y] or blockedPos[x+1][y]) and (self.simple_deadlock[x-1][y] or blockedPos[x-1][y]))):
            for (x1,y1) in addedBlocked:
                blockedPos[x1][y1] = False
            for (x1,y1) in addedBlocked:
                self.simpleTile[x1][y1] = True
            return True
        

        for (x1,y1) in addedBlocked:
            blockedPos[x1][y1] = False
        for (x1,y1) in addedBlocked:
                self.simpleTile[x1][y1] = True
        return False

    # list of possible actions in a certain state
    def actions(self, state):
        #MAY BE POSSIBLE TO MAKE IT MORE EFFICIENT
        moves = [] #actions
        #state has the places of the boxes

        for (x0,y0) in state:
            self.boxpos[x0][y0]=True #update box positions

        for pos in state:
            (x,y) = pos
            otherboxes=[p for p in state if p != pos]
            if ((not self.walls[x+1][y]) and (not self.walls[x-1][y]) 
                    and not self.boxpos[x+1][y] and not self.boxpos[x-1][y]):
                #we need to confirm if he can go to x+1,y and 
                #if the player can push it from the positon x-1,y vice-versa
                if not (self.blocked[x-1][y]):
                    moves+=[(otherboxes+[(x-1,y)], (x+1,y), (x,y))] #its possible to move it left
                if not (self.blocked[x+1][y]):
                    moves+=[(otherboxes+[(x+1,y)], (x-1,y), (x,y))] #its possible to move it right

            if ((not self.walls[x][y+1]) and (not self.walls[x][y-1]) 
                    and not self.boxpos[x][y+1] and not self.boxpos[x][y-1]):
                #we need to confirm if he can go to x,y+1 and 
                #if the player can push it from the positon x,y-1 vice-versa
                if not (self.blocked[x][y-1]):
                    moves+=[(otherboxes+[(x,y-1)], (x,y+1), (x,y))] #its possible to move it up
                if not (self.blocked[x][y+1]):
                    moves+=[(otherboxes+[(x,y+1)], (x,y-1), (x,y))] #its possible to move it down

        for (x0,y0) in state:
            self.boxpos[x0][y0]=False #reset positions
        return moves

    # result of an action in a certain state
    def result(self, action):
        (finalboxpos, _, _) = action
        if not self.deadlock(finalboxpos):
            return finalboxpos

    def deadlock(self, boxpos):
        #If there is a wall on the left or on the right side of the box then the box is blocked along this axis
        #we need to confirm if the box is blocked on both axis
        for (x0,y0) in boxpos:
            self.boxpos[x0][y0]=True #update box positions

        for (x,y) in boxpos:
            if not self.goals[x][y]:
                if self.freeze_deadlock(boxpos, (x,y),self.frozenBox, (0,0), self.boxpos, []):
                    for (x0,y0) in boxpos:
                        self.boxpos[x0][y0]=False #reset positions
                    return True
        for (x0,y0) in boxpos:
            self.boxpos[x0][y0]=False
        return False
        
    def freeze_deadlock(self,boxpos,pos,frozenBox,newFrozen,otherboxes,addedFrozen):
        #confirms if the box enters a freeze deadlock with the other boxes
        #frozenBox is the location of the boxes we already discovered as blocked
        (x0,y0) = newFrozen
        otherboxes[x0][y0] = False  #otherboxes has the position of the other boxes while pos has the position for this box
        (x,y) = pos  #position of the box we want to check if its frozen

        #for box in otherboxes
        #blocked horizontally by walls/frozen boxes
        if (((self.walls[x+1][y] or frozenBox[x+1][y]) or (self.walls[x-1][y] or frozenBox[x-1][y]) or (self.simple_deadlock[x+1][y] and self.simple_deadlock[x-1][y])) and
                (otherboxes[x][y+1])):
            frozenBox[x][y]=True #our box is now frozen
            addedFrozen.append((x,y))
            return self.freeze_deadlock(boxpos,(x,y+1),frozenBox,pos,otherboxes,addedFrozen)
        if (((self.walls[x+1][y] or frozenBox[x+1][y]) or (self.walls[x-1][y] or frozenBox[x-1][y]) or (self.simple_deadlock[x+1][y] and self.simple_deadlock[x-1][y])) and
                (otherboxes[x][y-1])):
            frozenBox[x][y]=True
            addedFrozen.append((x,y))
            return self.freeze_deadlock(boxpos,(x,y-1),frozenBox,pos,otherboxes,addedFrozen)

        #blocked vertically by walls/frozen boxes
        if (((self.walls[x][y+1] or frozenBox[x][y+1]) or (self.walls[x][y-1] or frozenBox[x][y-1]) or (self.simple_deadlock[x][y+1] and self.simple_deadlock[x][y-1])) and
                (otherboxes[x+1][y] )):
            frozenBox[x][y]=True
            addedFrozen.append((x,y))
            return self.freeze_deadlock(boxpos,(x+1,y),frozenBox,pos,otherboxes,addedFrozen)
        if (((self.walls[x][y+1] or frozenBox[x][y+1]) or (self.walls[x][y-1] or frozenBox[x][y-1]) or (self.simple_deadlock[x][y+1] and self.simple_deadlock[x][y-1])) and
                (otherboxes[x-1][y] )):
            frozenBox[x][y]=True
            addedFrozen.append((x,y))
            return self.freeze_deadlock(boxpos,(x-1,y),frozenBox,pos,otherboxes,addedFrozen)

        if (((self.walls[x+1][y] or frozenBox[x+1][y]) or (self.walls[x-1][y] or frozenBox[x-1][y]) or (self.simple_deadlock[x+1][y] and self.simple_deadlock[x-1][y])) and
            ((self.walls[x][y+1] or frozenBox[x][y+1]) or (self.walls[x][y-1] or frozenBox[x][y-1]) or (self.simple_deadlock[x][y+1] and self.simple_deadlock[x][y-1]))):
            for (x,y) in addedFrozen:
                frozenBox[x][y]=False
            return True   
        for (x,y) in addedFrozen:
            frozenBox[x][y]=False
        return False


    #cost of action
    def cost(self, action,kGoal):
        #for the cost we see the distance between the ending
        #position of the keeper for last round and this round
        (_, kGo, _) = action
        #kGo is where he needs to go this round
        #kGoal is where he ended the last round
        (x1,y1)=kGo
        (x2,y2)=kGoal
        return abs(x2-x1)+abs(y2-y1)

    # predicted cost of an action
    def heuristic(self, state): 
        #this heuristic favours the states that has an higher number of boxes closer to the goal
        h = 0
        
        for (x1,y1) in state:
            if not self.goals[x1][y1]:
                for (x2,y2) in self.goalstate:
                    if (x2,y2) not in state:
                        h += abs(x2-x1)+abs(y2-y1)
        return h
        
    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state):

        for (x0,y0) in state:
            if not self.goals[x0][y0]:
                return False
        return True
