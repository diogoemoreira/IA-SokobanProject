from abc import ABC, abstractmethod
import bisect

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomainKeeper(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblemKeeper:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial #array with the initial position
        self.goal = goal #array with the positions of the goals
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNodeKeeper:
    def __init__(self,state,parent, cost=1, heuristic=0): 
        self.state = state #where the boxes are
        self.parent = parent #node parent
        self.cost = cost 
        self.heuristic=heuristic
        
    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + str(self.cost) + ")"
    def __repr__(self):
        return str(self)

    def __lt__(self, othernode):
        return ((self.heuristic+self.cost)<(othernode.heuristic+othernode.cost))

# Arvores de pesquisa
class SearchTreeKeeper:

    # construtor
    def __init__(self,problem): 
        ##
        self.problem = problem
        root = SearchNodeKeeper(problem.initial, None,0,
            problem.domain.heuristic(self.problem.initial,self.problem.goal))
        self.open_nodes = [root]
        self.movesmap = set([self.problem.initial])
        self.moveKeyMap= {(0,1):"s",(0,-1):"w",(1,0):"d",(-1,0):"a"}

    # path from the root to the node
    def get_moves(self,node):
        ##
        if node.parent==None:
            return ""
        changes = ((node.state[0] - node.parent.state[0]),(node.state[1] - node.parent.state[1]))

        #y grows as keeper goes down
        return self.get_moves(node.parent) + self.moveKeyMap.get(changes)

    def repeated_move(self,newstate):
        #confirms if the move was already made
        return newstate in self.movesmap

    # procurar a solucao
    def search(self):
        ##
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            
            if self.problem.goal_test(node.state): #se o node atual for a solucao ao problema
                return self.get_moves(node) #devolvemos o caminho da raiz ate ao node
            
            for action in self.problem.domain.actions(node.state):
                #criamos um novo node com o custo do anterior mais custo da nov transicao e com heuristica
                if not self.repeated_move(action):
                    self.movesmap.add(action)
                    newnode = SearchNodeKeeper(action, node, node.cost + 1, 
                        self.problem.domain.heuristic(action, self.problem.goal))
                    bisect.insort(self.open_nodes, newnode)
                
        return None