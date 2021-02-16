import bisect
from abc import ABC, abstractmethod
from consts import Tiles
from tree_search_keeper_helper import KeeperDomain
from tree_search_keeper import *
import asyncio


# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomainBoxes(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblemBoxes:
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial #array with the initial positions of the boxes
    def goal_test(self, state):
        return self.domain.satisfies(state)

# Nos de uma arvore de pesquisa
class SearchNodeBoxes:
    def __init__(self, state,parent, cost=0, heuristic=0, keeperGo=None, keeperGoal=None, keys=""): 
        self.state = state #where the boxes are
        self.parent = parent #node parent
        self.cost = cost 
        self.heuristic=heuristic
        self.keeperGo = keeperGo #where the keeper needs to go
        self.keeperGoal = keeperGoal #where he needs to end
        self.keys = keys
        self.move = str([self.keeperGoal]+sorted(self.state))
        
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + str(self.cost) + ")"
    def __repr__(self):
        return str(self)

    def __lt__(self, othernode):
        return ((self.heuristic+self.cost)<(othernode.heuristic+othernode.cost))

# Arvores de pesquisa
class SearchTreeBoxes:

    # construtor
    def __init__(self,problem): 
        self.problem = problem
        root = SearchNodeBoxes(problem.initial, None,0, problem.domain.heuristic(self.problem.initial), self.problem.domain.map.keeper, self.problem.domain.map.keeper)
        self.open_nodes = [root]
        self.statesmap = set()
        self.moveKeyMap= {(0,1):"s",(0,-1):"w",(1,0):"d",(-1,0):"a"}

    def move_key(self, kGo,kGoal):
        ##
        #key needed to move it
        changes = ((kGoal[0] - kGo[0]),(kGoal[1]-kGo[1]))
        #y grows as it goes down
        return self.moveKeyMap.get(changes) #gets corresponding key

    def all_keys(self, node):
        if node.parent==None:
            return ""

        return self.all_keys(node.parent) + node.keys

    # procurar a solucao
    async def search(self):
        blocked = {}
        for tile in self.problem.domain.map.filter_tiles([Tiles.WALL]):
            blocked[tile] = True
        while self.open_nodes != []:
            await asyncio.sleep(0)  # this should be 0 in your code and this is REQUIRED
            node = self.open_nodes.pop(0)
            
            if node.parent!=None:
                for pos in node.parent.state:
                    blocked[pos] = True
                keeperproblem = SearchProblemKeeper(KeeperDomain(blocked),node.parent.keeperGoal, node.keeperGo)
                keepertree = SearchTreeKeeper(keeperproblem)
                keys = keepertree.search()
                for pos in node.parent.state:
                    blocked[pos] = False

                if keys == None:
                    continue

                node.keys = keys + self.move_key(node.keeperGo,node.keeperGoal)
            
            if self.problem.goal_test(node.state):
                print("done")
                return self.all_keys(node)

            self.statesmap.add(node.move)   #using set <- more efficient than dictionary/array

            for action in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(action)
                #criamos um novo node com o custo do anterior mais custo da nova transicao e com heuristica
                if newstate != None:
                    if not str([action[2]]+sorted(newstate)) in self.statesmap: #confirms if the move was already made
                        newnode = SearchNodeBoxes(newstate, node, node.cost + self.problem.domain.cost(action, node.keeperGoal), 
                            self.problem.domain.heuristic(newstate), action[1], action[2]) #a[1] its where the keeper needs to go to move the block, a[2] keeper goal
                        #this is a*
                        bisect.insort(self.open_nodes, newnode) #adicionamos o novo node na lista da pesquisa
        return None




