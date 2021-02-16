from tree_search_keeper import SearchDomainKeeper

class KeeperDomain(SearchDomainKeeper):
    def __init__(self,positions):
        self.blocked = positions
    # lista de accoes possiveis num estado
    def actions(self, state):
        
        moves = [] #actions
        x,y = state

        if not self.blocked.get((x+1,y)):
            #if the right isnt blocked and there is no box there
            moves+=[(x+1,y)] #its possible to move it right

        if not self.blocked.get((x-1,y)):
            moves+=[(x-1,y)] #its possible to move it left
        
        if not self.blocked.get((x,y+1)):
            moves+=[(x,y+1)] #its possible to move it down

        if not self.blocked.get((x,y-1)):
            moves+=[(x,y-1)] #its possible to move it up
        
        return moves

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        ##
        x1,y1 = state
        x2,y2 = goal
        return abs(x2-x1)+abs(y2-y1) #how close to the goal we are

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        #! problem solved
        return state == goal


