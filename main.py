import itertools
import random
import sys
from typing import Union
from enum import Enum

# class syntax
class GameStateType(Enum):
    NotFinished = -1
    Draw = 0
    P1Win = 1
    P2Win = 2


CellState = int
GameState = tuple[CellState, CellState, CellState, CellState, CellState, CellState, CellState, CellState, CellState]


def check_won(state: GameState):
    winner = None
    # Check rows
    if state[0] == state[1] == state[2] != 0:
        winner = state[0]
    elif state[3] == state[4] == state[5] != 0:
        winner = state[3]
    elif state[6] == state[7] == state[8] != 0:
        winner = state[6]
    # Check cols
    elif state[0] == state[3] == state[6] != 0:
        winner = state[0]
    elif state[1] == state[4] == state[7] != 0:
        winner = state[1]
    elif state[2] == state[5] == state[8] != 0:
        winner = state[2]
    # Check diagonals
    elif state[0] == state[4] == state[8] != 0:
        winner = state[0]
    elif state[2] == state[4] == state[6] != 0:
        winner = state[2]
    return winner

def evaluateGameState(state: GameState) -> GameStateType:
    # check for 3 in a row for p1
    winner = check_won(state)
    if winner is not None:
        # someone won
        if winner == 1:
            return GameStateType.P1Win
        elif winner == 2:
            return GameStateType.P2Win
        else:
            raise Exception
    else:
        # check for draw
        if all(i != 0 for i in state):
            # drawed
            return GameStateType.Draw
    return GameStateType.NotFinished



def getPlayerTurn(gamestate:GameState):
    # popcnt
    nonzeros = sum(x != 0 for x in gamestate)
    if nonzeros % 2 == 0:
        return 1
    else:
        return 2

def printBoard(gamestate:GameState):
    mapchar = {
        0: ".",
        1: "X",
        2: "O"
    }
    for i in range(3):
        for j in range(3):
            print(mapchar[gamestate[i*3+j]], end="\n" if j == 2 else "")



class gameOutcome(Enum):
    Draw = 0
    P1Win = 1
    P2Win = 2


def getloss(player:int) -> gameOutcome:
    if player == 1:
        return gameOutcome.P2Win
    else:
        return gameOutcome.P1Win

def getwin(player:int) -> gameOutcome:
    if player == 1:
        return gameOutcome.P1Win
    else:
        return gameOutcome.P2Win

def gameStateTypeToGameOutcome(gamestateType:GameStateType) -> gameOutcome:
    if gamestateType == GameStateType.Draw:
        return gameOutcome.Draw
    elif gamestateType == GameStateType.P1Win:
        return gameOutcome.P1Win
    elif gamestateType == GameStateType.P2Win:
        return gameOutcome.P2Win
    else:
        raise Exception





perfectplay_outcome_map:dict[GameState, gameOutcome] = {}
def perfectplay_outcome(gamestate:GameState) -> gameOutcome:
    if gamestate in perfectplay_outcome_map:
        return perfectplay_outcome_map[gamestate]

    # Check if game ended
    evaluation = evaluateGameState(gamestate)
    if evaluation != GameStateType.NotFinished:
        perfectplay_outcome_map[gamestate] = gameStateTypeToGameOutcome(evaluation)
        return perfectplay_outcome_map[gamestate]

    curplayer = getPlayerTurn(gamestate)
    has_draw = False
    for cell in range(9):
        # try every possible move
        if gamestate[cell] == 0:
            newgamestate = list(gamestate)
            newgamestate[cell] = curplayer
            newgamestate: tuple[int,int,int,int,int,int,int,int,int] = tuple(newgamestate)
            outcome = perfectplay_outcome(newgamestate)
            if outcome == getwin(curplayer):
                perfectplay_outcome_map[gamestate] = outcome
                return perfectplay_outcome_map[gamestate]
            elif outcome == gameOutcome.Draw:
                has_draw = True
    if has_draw:
        perfectplay_outcome_map[gamestate] = gameOutcome.Draw
    else:
        perfectplay_outcome_map[gamestate] = getloss(curplayer)
    return perfectplay_outcome_map[gamestate]


def bestmove(gamestate:GameState) -> GameState:
    player = getPlayerTurn(gamestate)
    # go through moves in order
    first_draw_move = None
    candidates = []
    for i, x in enumerate(gamestate):
        if x == 0:
            newgamestate = list(gamestate)
            newgamestate[i] = player
            newgamestate = tuple(newgamestate)
            if perfectplay_outcome(newgamestate) == getwin(player):
                return newgamestate
            elif perfectplay_outcome(newgamestate) == gameOutcome.Draw:
                if first_draw_move is None:
                    first_draw_move = newgamestate
                candidates.append(newgamestate)

    # There is no guaranteed-win, so we pick the boardstate with the best score
    best_candidate = None
    best_candidate_score = -1
    for candidate in candidates:
        score = win_probability(candidate)
        if score > best_candidate_score:
            best_candidate_score = score
            best_candidate = candidate

    if first_draw_move is None:
        raise Exception("All moves lead to a loss. This should never happen in a real game.")
    if best_candidate is None:
        raise Exception("No candidates!?!?")
    return best_candidate


win_probability_map = {}
def win_probability(boardstate_enemyturn:GameState) -> float:
    if boardstate_enemyturn in win_probability_map:
        return win_probability_map[boardstate_enemyturn]

    # probability of winning if enemy plays randomly
    # Actually, I hacked it so that the center move is 3x more likely than the others
    # This is based on human experience
    def heuristic_append(probabilities, probability, cell):
        if cell == 4:
            probabilities.append(probability)
            probabilities.append(probability)
            probabilities.append(probability)
        else:
            probabilities.append(probability)

    probabilities = []
    enemyplayer = getPlayerTurn(boardstate_enemyturn)

    if perfectplay_outcome(boardstate_enemyturn) == getloss(enemyplayer):
        return 1

    evaluation = evaluateGameState(boardstate_enemyturn)
    if evaluation != GameStateType.NotFinished:
        # if it's finished, no moves left, then just return whether we won
        outcome = perfectplay_outcome(boardstate_enemyturn)
        if outcome == getloss(enemyplayer):
            return 1
        else:
            return 0

    for cell in range(9):
        if boardstate_enemyturn[cell] == 0:
            newgamestate = list(boardstate_enemyturn)
            newgamestate[cell] = enemyplayer
            newgamestate = tuple(newgamestate)
            outcome = perfectplay_outcome(newgamestate)
            if outcome == getloss(enemyplayer):
                heuristic_append(probabilities, 1, cell)
            elif outcome == gameOutcome.Draw:
                # check if there are any moves left
                # if there are no moves left then
                evaluation = evaluateGameState(newgamestate)
                if evaluation != GameStateType.NotFinished:
                    heuristic_append(probabilities, 0, cell)
                else:
                    prob = win_probability(bestmove(newgamestate))
                    heuristic_append(probabilities, prob, cell)
            else:
                raise Exception("Perfect play leads to loss. This shouldn't ever happen.")
    win_probability_map[boardstate_enemyturn] = sum(probabilities) / len(probabilities)
    if win_probability_map[boardstate_enemyturn] > 1:
        raise Exception("Something has gone wrong.")
    return win_probability_map[boardstate_enemyturn]





print(win_probability((1,0,0,0,0,0,0,0,0)))
print(win_probability((0,0,1,0,0,0,0,0,0)))
print(win_probability((0,1,0,0,0,0,0,0,0)))

print("center", win_probability((0,0,0,0,1,0,0,0,0)))


print(perfectplay_outcome((0,0,0,0,0,0,0,0,0)))

print(perfectplay_outcome((0,0,0,0,1,0,0,0,0)))

print(perfectplay_outcome((0,2,0,0,1,0,0,0,0)))

printBoard(bestmove((0,0,0,0,0,0,0,0,0)))

print(win_probability((1,0,0,0,0,0,0,0,0)))

print(win_probability((0,0,0,0,1,0,0,0,0)))

print(win_probability((2,0,0,0,1,0,0,0,0)))

print(win_probability((1,0,0,0,2,0,0,0,0)))

#print(win_probability((0,2,0,0,1,0,0,0,0)))

#print(perfectplay_outcome((0,2,0,0,1,0,0,0,0)))

printBoard(bestmove((0,2,0,
                2,1,1,
                0,1,2)))

def getGameOutcome(outcome:gameOutcome) -> str:
    if outcome == gameOutcome.Draw:
        return "Draw"
    elif outcome == gameOutcome.P1Win:
        return "Player 1 wins"
    else:
        return "Player 2 wins"

def checkGameIsOver(gamestate, playernum):
    evaluation = evaluateGameState(tuple(gamestate))
    if evaluation != GameStateType.NotFinished:
        printBoard(gamestate)
        if evaluation == GameStateType.Draw:
            print("It's a draw!")
        elif evaluation == GameStateType.P1Win and playernum == 1 or evaluation == GameStateType.P2Win and playernum == 2:
            print("You win!")
        else:
            print("You lose!")
        sys.exit()

# main loop
def main():
    player = input("Please enter whether you want to be player 1 (starts) or player 2 (enter 1 or 2):")
    playerstarts = False
    if player == "1":
        playerstarts = True
        playernum = 1
    else:
        playernum = 2

    gamestate = [0] * 9
    if not playerstarts:
        # Randomly choose a first move, with 70% chance of picking the center
        rand = random.randint(1, 100)
        if rand < 70:
            firstmove = 4
        else:
            firstmove = random.randint(0, 8)
        # play it
        gamestate[firstmove] = 1

    while True:
        printBoard(gamestate)
        move = input("It is your turn. Please enter your move:")
        try:
            move = int(move)
        except:
            print("Invalid input. Please enter a number from 0 to 8.")
            continue
        if move < 0 or move > 8:
            print("Invalid move. Please enter a number from 0 to 8.")
            continue
        if gamestate[move] != 0:
            print("You can't make that move. The tile is already occupied.")
            continue
        gamestate[move] = playernum
        checkGameIsOver(gamestate, playernum)
        outcome = perfectplay_outcome(tuple(gamestate))
        print("CPU thinks perfect play outcome is", getGameOutcome(outcome))

        cpumove = bestmove(tuple(gamestate))
        gamestate = list(cpumove)

        checkGameIsOver(gamestate, playernum)

if __name__ == "__main__":
    main()
