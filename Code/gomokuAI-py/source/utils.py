import random
import uuid

##### For managing the interface #####
SIZE = 540  # size of the board image
PIECE = 32  # size of the single pieces
N = 15
MARGIN = 23
GRID = (SIZE - 2 * MARGIN) / (N - 1)


# Not Important
def pixel_conversion(list_points, target):
    # point of the list from where start the search
    index = int((len(list_points) - 1) // 2)

    while True:
        if target < list_points[0]:
            index = 0
            break
        elif target >= list_points[-1]:
            index = len(list_points) - 2
            break

        elif list_points[index] > target:
            if list_points[index - 1] <= target:
                index -= 1
                break
            else:
                index -= 1

        elif list_points[index] <= target:
            if list_points[index + 1] > target:
                break
            else:
                index += 1

    return index


# Transform pygame pixel to boardMap coordinates
# Not Important
def pos_pixel2map(x, y):
    start = int(MARGIN - GRID // 2)
    end = int(SIZE - MARGIN + GRID // 2)
    list_points = [p for p in range(start, end + 1, int(GRID))]

    i = pixel_conversion(list_points, y)
    j = pixel_conversion(list_points, x)
    return (i, j)


# Transform boardMap to pygame pixel coordinates
def pos_map2pixel(i, j):
    return (MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2)


def create_mapping():
    pos_mapping = {}
    for i in range(N):
        for j in range(N):
            spacing = [r for r in range(MARGIN, SIZE - MARGIN + 1, int(GRID))]
            pos_mapping[(i, j)] = (spacing[j], spacing[i])

    return pos_mapping


#### Pattern scores ####
# Done
def create_pattern_dict():
    pattern_dict = {}

    # Scoring tiers (adjust multipliers for balance)
    WIN = 10_000_000
    CRITICAL = 1_000_000
    HIGH = 100_000
    MEDIUM = 10_000
    LOW = 1_000

    for player in [-1, 1]:  # -1=Human, 1=AI
        opponent = -player

        # ===== 1. WIN CONDITIONS =====
        pattern_dict[(player, player, player, player, player)] = WIN * player

        # ===== 2. IMMEDIATE THREATS =====
        # Open Four (Live Four)
        pattern_dict[(0, player, player, player, player, 0)] = CRITICAL * player
        pattern_dict[(player, player, player, player, 0)] = CRITICAL * player * 0.9
        pattern_dict[(0, player, player, player, player)] = CRITICAL * player * 0.9
        pattern_dict[(opponent, player, player, player, player, 0)] = CRITICAL * player * 0.9
        pattern_dict[(0, player, player, player, player, opponent)] = CRITICAL * player * 0.9

        # Gap Four (Single Space)
        pattern_dict[(player, 0, player, player, player)] = HIGH * 1.2 * player  # X_XXX
        pattern_dict[(player, player, 0, player, player)] = HIGH * 1.5 * player  # XX_XX (more dangerous)
        pattern_dict[(player, player, player, 0, player)] = HIGH * 1.2 * player  # XXX_X

        # ===== 3. FORCING PATTERNS =====
        # Double Fours (Unblockable)
        pattern_dict[(player, 0, player, 0, player, player)] = CRITICAL * player  # X_X_XX
        pattern_dict[(player, player, 0, player, 0, player)] = CRITICAL * player  # XX_X_X

        # Triple Threats
        pattern_dict[(player, 0, player, 0, player)] = HIGH * 1.8 * player  # X_X_X
        pattern_dict[(0, player, 0, player, 0)] = HIGH * 1.5 * player  # X_X

        # ===== 4. STRATEGIC PATTERNS =====
        # Open Three (Live Three)
        pattern_dict[(0, player, player, player, 0)] = HIGH * 2 * player  # XXX
        pattern_dict[(0, 0, player, player, player, 0)] = HIGH * 1.5 * player  # _XXX

        # Gap Three
        pattern_dict[(player, 0, player, player)] = MEDIUM * player  # X_XX
        pattern_dict[(player, player, 0, player)] = MEDIUM * player  # XX_X

        # ===== 5. DEFENSIVE PATTERNS =====
        # Block Opponent's Criticals (Negative Scoring)
        pattern_dict[(0, opponent, opponent, opponent, opponent, 0)] = -CRITICAL * 2.5 * player
        pattern_dict[(opponent, opponent, opponent, opponent, 0)] = -CRITICAL * 2.5 * player
        pattern_dict[(0, opponent, opponent, opponent, opponent)] = -CRITICAL * 2.5 * player
        pattern_dict[(player, opponent, opponent, opponent, opponent, 0)] = -CRITICAL * 2 * player
        pattern_dict[(0, opponent, opponent, opponent, opponent, player)] = -CRITICAL * 2 * player
        pattern_dict[(opponent, opponent, opponent, opponent, player)] = -CRITICAL * 2 * player
        pattern_dict[(player, opponent, opponent, opponent, opponent)] = -CRITICAL * 2 * player

        # Block Gap Fours
        pattern_dict[(opponent, 0, opponent, opponent, opponent)] = -WIN * 1.2 * player
        pattern_dict[(opponent, opponent, 0, opponent, opponent)] = -WIN * 1.5 * player
        pattern_dict[(0 , opponent, 0, opponent, opponent, opponent)] = -WIN * 1.2 * player
        pattern_dict[(0 , opponent, opponent, 0, opponent, opponent)] = -WIN * 1.5 * player
        pattern_dict[(0 , opponent, 0, opponent, opponent, opponent , 0)] = -WIN * 1.2 * player
        pattern_dict[(0 , opponent, opponent, 0, opponent, opponent , 0)] = -WIN * 1.5 * player
        pattern_dict[(opponent, 0, opponent, opponent, opponent , 0)] = -WIN * 1.2 * player
        pattern_dict[(opponent, opponent, 0, opponent, opponent , 0)] = -WIN * 1.5 * player

        # ===== 6. TRANSITIONAL PATTERNS =====
        # Two with Potential
        pattern_dict[(0, player, player, 0)] = LOW * player  # XX
        pattern_dict[(player, 0, 0, player)] = LOW * 0.8 * player  # X__X

        # ===== 7. EDGE/CORNER SPECIALS =====
        # Edge Threats
        edge_patterns = [
            (0, 0, player, player, -1),  # __XXO
            (-1, player, player, 0, 0),  # OXX__
            (0, player, -1, player, 0)  # XOX
        ]
        for p in edge_patterns:
            pattern_dict[p] = MEDIUM * 1.2 * player if p.count(player) > 1 else MEDIUM * player

        # Corner Sacrifices
        corner_sacrifice = [
            (player, -1, -1, 0, player),  # XOO_X
            (-1, player, player, 0, -1)  # OXX_O
        ]
        for p in corner_sacrifice:
            pattern_dict[p] = HIGH * 0.7 * player

    return pattern_dict


##### Zobrist Hashing #####
# Done
def init_zobrist():
    zTable = [[[uuid.uuid4().int for _ in range(2)] \
               for j in range(15)] for i in range(15)]  # changed to 32 from 64
    return zTable


# Done
def update_TTable(table, hash, score, depth):
    table[hash] = [score, depth]