
'''

    Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.

No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.

You are NOT allowed to change the defined interfaces.
In other words, you must fully adhere to the specifications of the 
functions, their arguments and returned values.
Changing the interfacce of a function will likely result in a fail 
for the test of your code. This is not negotiable! 

You have to make sure that your code works with the files provided 
(search.py and sokoban.py) as your code will be tested 
with the original copies of these files. 

Last modified by 2022-03-27  by f.maire@qut.edu.au
- clarifiy some comments, rename some functions
  (and hopefully didn't introduce any bug!)

'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search 
import sokoban


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [ (10891188, 'Asif Reza', 'Chowdhury') ]
    # raise NotImplementedError()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Variables

# cell definitions
mark = {
    "space": " ",
    "box": "$",
    "target":".",
    "wall":"#",
    "worker": "@",
    "worker_target":"!",
    "box_target":"*",
    "taboo":"X",
    "removed":['$','@'],
    "three_targets":['.','*','!']
}

#directions defined
direction= {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0)
}

# the final location in 2D area after a move
def moveIn2D(loc,delta):
    return (loc[0]+delta[0], loc[1] + delta[1])

# check walls in four sides
def checkWall (index, walls):
    return moveIn2D(index, direction["Up"]) in walls \
        or moveIn2D(index, direction["Down"]) in walls \
        or moveIn2D(index, direction["Left"]) in walls \
        or moveIn2D(index, direction["Right"]) in walls

# check corners
def checkCorner(index,walls):
    # Checking top and left cells for wall marks
    if moveIn2D(index, direction["Up"]) in walls \
        and moveIn2D(index, direction["Left"]) in walls:
        return True

    # Checking top and right cells for wall marks
    if moveIn2D(index, direction["Up"]) in walls \
        and moveIn2D(index, direction["Right"]) in walls:
        return True

    # Checking bottom and left cells for wall marks
    if moveIn2D(index, direction["Down"]) in walls \
        and moveIn2D(index, direction["Left"]) in walls:
        return True

    # Checking bottom and right cells for wall marks
    if moveIn2D(index, direction["Down"]) in walls \
        and moveIn2D(index, direction["Right"]) in walls:
        return True

    # for other cases being not a corner
    return False

#used manhattan distance for finding distance between two points
def mhDistance(loc1, loc2):
    return (abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]))

#cells which makes the puzzle not possible to solve
def restrictedCells(warehouse):
    def rule1st():
        # looping the rows
        for rowID in range(warehouse.nrows):
            outWall = True
            # looping the columns
            for colID in range(warehouse.ncols):
                matrixID = (colID, rowID)
                square = warehouse2D[rowID][colID]
                if outWall and square == mark["wall"]:
                    outWall = False

                elif not outWall:
                    if all([cell == mark["space"] for cell in warehouse2D[rowID][colID:]]):
                        break
                    if square == mark["space"] and checkCorner(matrixID, walls):
                        warehouse2D[rowID][colID] = mark["taboo"]
    
    def rule2nd():
        # looping the rows
        for rowID in range(warehouse.nrows):
            # looping the columns
            for colID in range(warehouse.ncols):
                matrixID = (colID, rowID)
                square = warehouse2D[rowID][colID]
                if square == mark["taboo"] and checkCorner(matrixID, walls):
                    remainingRow = warehouse2D[rowID][colID+1:]
                    remainingCol = [row[colID] for row in warehouse2D[rowID+1:]]

                    for idx, val in enumerate(remainingCol):
                        if val == mark["wall"] or val in mark["three_targets"]:
                            break
                        if val == mark["taboo"] and checkCorner((colID, rowID+idx+1), walls):
                            if all([checkWall((colID, loc), walls) for loc in range(rowID+1, rowID+idx+1)]):
                                for loc in range(rowID+1, rowID+idx+1):
                                    warehouse2D[loc][colID] = mark["taboo"]
                    
                    for idx, val in enumerate(remainingRow):
                        if val == mark["wall"] or val in mark["three_targets"]:
                            break
                        if val == mark["taboo"] and checkCorner((colID+idx+1, rowID), walls):
                            if all([checkWall((loc, rowID), walls) for loc in range(colID+1, colID+idx+1)]):
                                for loc in range(colID+1, colID+idx+1):
                                    warehouse2D[rowID][loc] = mark["taboo"]


    # location of all walls
    walls = warehouse.walls

    # converting warehouse to string
    warehouseStr = str(warehouse)

    # replacing the cell marks for box and player with space,
    for cell in mark["removed"]:
        warehouseStr = warehouseStr.replace(cell, " ")

    # splitting warehouse string into 2D matrix
    warehouse2D = [list(line) for line in warehouseStr.splitlines()]

    # aapplying the rules
    rule1st()
    rule2nd()

    #joining sokoban string list to full string
    warehouseStr = '\n'.join(["".join(row) for row in warehouse2D])

    # replacing the target marks
    for cell in mark["three_targets"]:
        warehouseStr = warehouseStr.replace(cell, " ")

    return warehouseStr

# - - - - - - - - - - - - - - - - - - - - - - - -
class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    '''
    
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.cache = {}
        self.initial = warehouse.worker, tuple(warehouse.boxes)
        self.taboo = [sokoban.find_2D_iterator(
            restrictedCells(self.warehouse).splitlines(), mark["taboo"])]
        self.weights = warehouse.weights
        self.boxes = warehouse.boxes
        self.walls = warehouse.walls
        self.goal = warehouse.targets

    def actions(self, state):
        """
        Return the list of legal actions that can be executed in the given state.
        
        """
        # state of worker and box
        workerState = state[0]
        boxState = list(state[1])
        # action list
        actions = []

        # looping for directions
        for key in direction.keys():
            nextWorkerState = moveIn2D(workerState, direction.get(key))
            if nextWorkerState in self.walls:
                continue
            # for pushing a box
            if nextWorkerState in boxState:
                nextBoxState = moveIn2D(nextWorkerState, direction.get(key))
                if nextBoxState not in self.walls and \
                    nextBoxState not in self.taboo and \
                        nextBoxState not in boxState:
                        actions.append(key)
            else:
                actions.append(key)
        return actions

    def result(self, state, action):
        workerState = state[0]
        boxState = list(state[1])
    
    
        # assuming the next worker state
        nextWorkerState = moveIn2D(workerState, direction.get(action))


        # checking the next worker state for a box
        if nextWorkerState in boxState:
            nextBoxState = moveIn2D(nextWorkerState, direction.get(action))
            box_index = boxState.index(nextWorkerState)
            boxState[box_index] = nextBoxState


        return nextWorkerState, tuple(boxState)


    def pathCost(self, k, state1, action, state2):
        if state1[1] != state2[1]:
            box_index = state1[1].index(state2[0])
            box_cost = self.weights[box_index]
            return box_cost + k + 1
        else:
            return k + 1


    def goalTest(self, state):
        return set(self.goal) == set(state[1])


    def h(self, n):
        boxes = list(n.state[1])
        worker = n.state[0]
        targets = self.goal
        heuristic = 0
        weights = self.weights
        for idx, box in enumerate(boxes):
                minDistance = float('inf')
                workerDistance = mhDistance(box, worker)
                for target in targets:
                    distance = mhDistance(box, target) * (weights[idx] + 1)
                    if minDistance > distance:
                        minDistance = distance
                heuristic += workerDistance
                heuristic += minDistance
        return heuristic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''
    #looping for actions
    for action in action_seq:
        currentLocation = warehouse.worker #worker location
        if action in list(direction.keys()):
            nextWorkerLocation = moveIn2D(currentLocation, direction.get(action)) #new location of worker
            if nextWorkerLocation in warehouse.walls:
                return "Impossible"
            elif nextWorkerLocation in warehouse.boxes:
                nextBoxLocation = moveIn2D(nextWorkerLocation, direction.get(action)) # box location after moving
                if nextBoxLocation in warehouse.walls or nextBoxLocation in warehouse.boxes:
                    return "Impossible"
                else:
                    boxIndex = warehouse.boxes.index(nextWorkerLocation)
                    warehouse.boxes[boxIndex] = nextBoxLocation
            else:
                warehouse.worker = nextWorkerLocation
    return warehouse.__str__()
    


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    '''
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.
    
    @param 
     warehouse: a valid Warehouse object

    @return
    
        If puzzle cannot be solved 
            return 'Impossible', None
        
        If a solution was found, 
            return S, C 
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C

    '''
    finalSokoban = SokobanPuzzle(warehouse)

    # Application of AstarGraphSearch for finding solution
    solution = search.astar_graph_search(finalSokoban)

    if solution is None:
        return 'Impossible', None
    else:
        # get one possible action sequence from class Node.solution()
        S = solution.solution()
        # get the total cost
        C = solution.pathCost

    return S, C


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

