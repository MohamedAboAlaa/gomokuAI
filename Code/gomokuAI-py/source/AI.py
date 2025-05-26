import math
import sys
import source.utils as utils
from heapq import nlargest

sys.setrecursionlimit(1500)

N = 15  # board size 15x15


class GomokuAI():
    # Done
    def __init__(self, depth=4):
        self.depth = depth  # default depth set to 3
        self.boardMap = [[0 for j in range(N)] for i in range(N)]
        self.move_count = 0  # Add this line to track moves
        self.currentI = -1
        self.currentJ = -1
        self.ourScore = -1
        self.nextBound = {}  # to store possible moves to be checked (i,j)
        self.boardValue = 0

        self.turn = 0
        self.lastPlayed = 0
        self.emptyCells = N * N  # Used to detect when the board is full (draw condition)
        self.patternDict = utils.create_pattern_dict()
        self.zobristTable = utils.init_zobrist()
        self.rollingHash = 0
        self.TTable = {}

    # Draw board in string format
    def drawBoard(self):
        '''
            States:
            0 = empty (.)
            1 = AI (x)
            -1 = human (o)
        '''
        for i in range(N):
            for j in range(N):
                if self.boardMap[i][j] == 1:
                    state = 'x'
                if self.boardMap[i][j] == -1:
                    state = 'o'
                if self.boardMap[i][j] == 0:
                    state = '.'
                print('{}|'.format(state), end=" ")
            print()
        print()

    # Check whether a move is inside the board and whether it is empty
    def isValid(self, i, j, state=True):
        '''
            if state=True, check also whether the position is empty
            if state=False, only check whether the move is inside the board
        '''
        if i < 0 or i >= N or j < 0 or j >= N:
            return False
        if state:
            if self.boardMap[i][j] != 0:
                return False
            else:
                return True
        else:
            return True

    # Given a position, change the state and "play" the move
    def setState(self, i, j, state):
        '''
            States:
            0 = empty
            1 = AI
            -1 = human
        '''
        assert state in (-1, 0, 1), 'The state inserted is not -1, 0 or 1'
        self.boardMap[i][j] = state
        self.lastPlayed = state

    # isFive use it
    def countDirection(self, i, j, xdir, ydir, state):
        count = 0
        # look for 4 more steps on a certain direction
        for step in range(1, 5):
            if xdir != 0 and (j + xdir * step < 0 or j + xdir * step >= N):  # ensure move inside the board
                break
            if ydir != 0 and (i + ydir * step < 0 or i + ydir * step >= N):
                break
            if self.boardMap[i + ydir * step][j + xdir * step] == state:
                count += 1
            else:
                break
        return count

    # Check whether there are 5 pieces connected (in all 4 directions)
    def isFive(self, i, j, state):
        # 4 directions: horizontal, vertical, 2 diagonals
        directions = [[(-1, 0), (1, 0)],  # Horizontal axis
                      [(0, -1), (0, 1)],  # Vertical axis
                      [(-1, 1), (1, -1)],  # Diagonal (top-right to bottom-left)
                      [(-1, -1), (1, 1)]]  # Diagonal (top-left to bottom-right)
        for axis in directions:
            axis_count = 1
            for (xdir, ydir) in axis:
                axis_count += self.countDirection(i, j, xdir, ydir, state)
                if axis_count >= 5:
                    return True
        return False

    def childNodes(self, bound, k=5):  # Increased k to consider more moves
        """Select top moves by absolute score value"""
        # Get all empty positions with their absolute scores
        valid_moves = [(pos, abs(score)) for pos, score in bound.items()
                       if self.isPositionEmpty(*pos)]

        # Sort by score descending, then by position (for consistency)
        valid_moves.sort(key=lambda x: (-x[1], x[0]))

        # Yield top k moves
        for pos, _ in valid_moves[:k]:
            yield pos

    def updateBound(self, new_i, new_j, bound):
        # Step 1: Remove the played move
        played = (new_i, new_j)
        if played in bound:
            bound.pop(played)

        # Step 2: Add adjacent cells (8 directions)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1), (-1, -1), (1, 1)]
        for di, dj in directions:
            ni, nj = new_i + di, new_j + dj
            if self.isValid(ni, nj) and (ni, nj) not in bound:
                bound[(ni, nj)] = 0

        # Step 3: Strategic distant checks (optimized)
        if self.lastPlayed == -1:  # Only after human moves
            self._add_distant_human_moves(bound, directions)
        self.move_count += 1  # Increment move counter

    def _add_distant_human_moves(self, bound, directions):
        # Throttle checks to every 3 moves
        if hasattr(self, '_last_distant_check') and \
                self.move_count - self._last_distant_check < 3:
            return

        human_stones = [(i, j) for i in range(N) for j in range(N)
                        if self.boardMap[i][j] == -1]
        ai_stones = [(i, j) for i in range(N) for j in range(N)
                     if self.boardMap[i][j] == 1]

        distant_groups = []
        for hi, hj in human_stones:
            if all(abs(hi - ai) + abs(hj - aj) > 3 for ai, aj in ai_stones):
                distant_groups.append((hi, hj))

        # Only proceed if human has ≥2 stones in a distant zone
        if len(distant_groups) >= 2:
            for hi, hj in distant_groups[:2]:  # Track max 2 zones
                for di, dj in directions:
                    ni, nj = hi + di, hj + dj
                    if self.isValid(ni, nj) and (ni, nj) not in bound:
                        bound[(ni, nj)] = -100  # Low-priority but monitored

            self._last_distant_check = self.move_count  # Record last check

    def countPattern(self, i_0, j_0, pattern, score, bound, flag):
        """
            Optimized pattern counting with:
                - Cached direction calculations
                - Early termination conditions
                - Reduced boundary checks
                - Pre-allocated memory
        """
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1)]
        length = len(pattern)
        count = 0
        remember = []  # Pre-allocate memory

        for di, dj in directions:
            # Calculate bounds once per direction
            if di * dj == 0:
                max_steps = min(5, N - 1 - i_0 if di == 1 else i_0,
                                N - 1 - j_0 if dj == 1 else j_0)
            else:
                max_steps = min(5, N - 1 - i_0 if di == 1 else i_0,
                                N - 1 - j_0 if dj == 1 else j_0)

            # Check both forward and backward
            for step in range(-max_steps, max_steps - length + 2):
                match = True
                remember.clear()  # Reuse memory

                for idx in range(length):
                    ni = i_0 + di * (step + idx)
                    nj = j_0 + dj * (step + idx)

                    if not (0 <= ni < N and 0 <= nj < N):
                        match = False
                        break

                    if self.boardMap[ni][nj] != pattern[idx]:
                        match = False
                        break

                    if pattern[idx] == 0:  # Only remember empty spaces
                        remember.append((ni, nj))

                if match:
                    count += 1
                    for pos in remember:
                        bound[pos] = bound.get(pos, 0) + flag * score

                    # Skip ahead since we found a match
                    step += length - 1

        return count


    def evaluate(self, new_i, new_j, board_value, turn, bound):
        '''
            board_value = value of the board updated at each minimax and initialized as 0
            turn = [1, -1] AI or human turn
            bound = dict of empty playable cells with corresponding score
        '''
        value_before = 0
        value_after = 0

        # Check for every pattern in patternDict
        for pattern in self.patternDict:
            score = self.patternDict[pattern]
            # For every pattern, count have many there are for new_i and new_j
            # and multiply them by the corresponding score
            value_before += self.countPattern(new_i, new_j, pattern, abs(score), bound, -1) * score
            # Make the move then calculate value_after
            self.boardMap[new_i][new_j] = turn
            value_after += self.countPattern(new_i, new_j, pattern, abs(score), bound, 1) * score

            # Delete the move
            self.boardMap[new_i][new_j] = 0

        return board_value + value_after - value_before

    ### MiniMax algorithm with AlphaBeta Pruning ###
    def alphaBetaPruning(self, depth, board_value, bound, alpha, beta, maximizingPlayer):

        if depth <= 0 or (self.checkResult() != None):
            return board_value  # Static evaluation

        # Transposition table of the format {hash: [score, depth]}
        if self.rollingHash in self.TTable and self.TTable[self.rollingHash][1] >= depth:
            return self.TTable[self.rollingHash][0]  # return board value stored in TTable

        # AI is the maximizing player
        if maximizingPlayer:
            # Initializing max value
            max_val = -math.inf
            # Look through the all possible child nodes
            for child in self.childNodes(bound):
                i, j = child[0], child[1]
                # Create a new bound with updated values
                # and evaluate the position if making the move
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, 1, new_bound)

                # Make the move and update zobrist hash
                self.boardMap[i][j] = 1
                self.rollingHash ^= self.zobristTable[i][j][0]  # index 0 for AI moves

                # Update bound based on the new move (i,j)
                self.updateBound(i, j, new_bound)

                # Evaluate position going now at depth-1 and it's the opponent's turn
                eval = self.alphaBetaPruning(depth - 1, new_val, new_bound, alpha, beta, False)
                if eval > max_val:
                    max_val = eval
                    if depth == self.depth:
                        self.currentI = i
                        self.ourScore = bound[(i, j)]
                        self.currentJ = j
                        self.boardValue = eval
                        self.nextBound = new_bound
                alpha = max(alpha, eval)

                # Undo the move and update again zobrist hashing
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][0]

                del new_bound
                if beta <= alpha:  # prune
                    break

            # Update Transposition Table
            utils.update_TTable(self.TTable, self.rollingHash, max_val, depth)
            # print(max_val)
            return max_val

        else:
            # Initializing min value
            min_val = math.inf
            # Look through the all possible child nodes
            for child in self.childNodes(bound):
                i, j = child[0], child[1]
                # Create a new bound with updated values
                # and evaluate the position if making the move
                new_bound = dict(bound)
                new_val = self.evaluate(i, j, board_value, -1, new_bound)

                # Make the move and update zobrist hash
                self.boardMap[i][j] = -1
                self.rollingHash ^= self.zobristTable[i][j][1]  # index 1 for human moves

                # Update bound based on the new move (i,j)
                self.updateBound(i, j, new_bound)

                # Evaluate position going now at depth-1 and it's the opponent's turn
                eval = self.alphaBetaPruning(depth - 1, new_val, new_bound, alpha, beta, True)
                if eval < min_val:
                    min_val = eval
                    if depth == self.depth:
                        self.currentI = i
                        self.currentJ = j
                        self.ourScore = bound[(i, j)]
                        self.boardValue = eval
                        self.nextBound = new_bound
                beta = min(beta, eval)

                # Undo the move and update again zobrist hashing
                self.boardMap[i][j] = 0
                self.rollingHash ^= self.zobristTable[i][j][1]

                del new_bound
                if beta <= alpha:  # prune
                    break

            # Update Transposition Table
            utils.update_TTable(self.TTable, self.rollingHash, min_val, depth)

            return min_val

    def firstMove(self):
        self.currentI, self.currentJ = 7, 7
        self.setState(self.currentI, self.currentJ, 1)

    def checkResult(self):
        if self.isFive(self.currentI, self.currentJ, self.lastPlayed) \
                and self.lastPlayed in (-1, 1):
            return self.lastPlayed
        elif self.emptyCells <= 0:
            # tie
            return 0
        else:
            return None

    # Done
    def getWinner(self):
        if self.checkResult() == 1:
            return 'Gomoku AI! '
        if self.checkResult() == -1:
            return 'Human! '
        else:
            return 'None'

    def isPositionEmpty(self, i, j):
        """Check if position is empty and within bounds"""
        return 0 <= i < N and 0 <= j < N and self.boardMap[i][j] == 0   