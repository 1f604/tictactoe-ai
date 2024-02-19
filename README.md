# tictactoe-ai

tictactoe game with unbeatable "smart" AI that uses a heuristic to beat imperfect human players.

# How does it work?

There are 2 core functions: `perfectplay_outcome` and `win_probability` (which is mutually recursive with `bestmove`).

`perfectplay_outcome` is the core functionality. It is standalone and it's the only thing you need to build an unbeatable AI that will never lose.

The `win_probability` is needed in order to implement a "smart" AI that will pick good moves against imperfect players.

The `perfectplay_outcome` function is actually really simple and took me only a few minutes to code up.

The hard part was coding up the `win_probability` and really making sure that it's correct.

Actually I thought it was wrong when it was right. Specifically, it was telling me that the corner first move was the best, even though I thought that the center move was the best. Actually it turns out that the corner move really IS the best if opponent plays randomly. But I thought it was obvious to pick the center. So I added a heuristic that basically said that the center move was more likely to picked than the other places, and that adjustment made it prefer the center move over the corner move.

# perfectplay_outcome

This is really the core part and it's standalone, you can use it by itself to build an unbeatable tictactoe AI, though it will play suboptimally against imperfect players - which is the whole reason I spent the time writing `win_probability` which is much more complicated.

To begin with I wanted to do some kind of bottom-up thing where I'd calculate the final states and then go up from the final state to the penultimate state but then I got kind of stuck on thinking how that was going to work.

Then I thought - fuck it, let's just do it in the simple, dumb, memoization way.

So I did it and it was fast and it worked.

Anyway, how it works is really simple. I begin by assuming that the function works. This is an incredibly powerful technique known as "Wishful Thinking" and is very useful for writing recursive programs. So, I begin by assuming that `perfectplay_outcome` already returns the `perfectplay_outcome`.

Then I define the base case: if the gamestate is already game over, then we just return that as the outcome.

On the other hand, if the gamestate is not game over, then we have to look at different moves available to us.

So, we first figure out which player we are. And then we look at which moves we can play. The algorithm is REALLY simple:

Is there a move that we can make in this gamestate that leads to a gamestate where the perfectplay outcome is our win? If so, then the perfectplay outcome of this gamestate is also our win.

If not, then is there a move that we can make in this gamestate that leads to a gamestate where the perfectplay outcome is draw? If so, then the perfectplay outcome of this gamestate is a draw.

Otherwise, it's our loss.

So the function signature is:

`perfectplay_outcome(gamestate) -> GameOutcome` where `GameOutcome` is either P1win, P2win, or Draw.

And `gamestate` in tictactoe is really simple - it's literally just a tuple of 9 integers. This is sufficient to describe the entire gamestate because it doesn't matter how you got there. History doesn't matter. The entire gamestate is just what's on the board.

So from just looking at the board, we can know what the perfect play game outcome is going to be.

And of course, you can memoize it to make it more efficient.

# bestmove

This function returns the "best move" for any gamestate. Now what does this mean specifically? It means that if you can make a move which gets into a state where the perfectplay outcome is your win, then that move is the best move.

Otherwise, you're in a game state where all moves lead to draws or worse. This is where the `win_probability` function comes in.

If you don't have `win_probability` then you have no way of scoring different draws - all draw states look the same to you but intuitively we know that they are not the same.

For example if you're in this gamestate (X turn to move):

```
O X .
X X O
. O .
```

There are 3 possible moves. The top right corner and bottom left corner both lead to win probability of 50% if enemy plays randomly, but if you go for the bottom right corner then you have a 0% probability of winning - it will draw no matter what the enemy does.

Of course it is better to be in a state where you can win if the enemy fucks up vs a state where you cannot possibly win no matter what the enemy does. That's the whole motivation behind the `win_probability` function.

The important insight here is that moves ARE board states. It is never useful to think of moves as moves, we always want the bestmove function to return a boardstate instead of just returning a move. That's because of how we want to use this function. The `bestmove` function is mutually recursive with `win_probability`, when we call it, we want a gamestate returned, not a move.

Another insight is that the gamestate includes whose turn it is. You can just tell by doing a popcount on the gamestate - count the number of empty squares. Since player 1 goes first and then player 2 and so on.

# win_probability

This is the hard part - relatively speaking. I mean, `perfectplay_outcome` took me only a few minutes to code up, this took me way longer just to conceptually think about it.

Okay, so here's how it works.

Since moves ARE board states, we score moves by scoring board states. They're literally the same. This is important, because you can get to a boardstate via multiple paths but it doesn't matter for the purpose of scoring the board state.

**The most important and crucial insight** is that we score board states by calculating the win probability if the enemy player plays randomly. (Actually, later on I modified this so that the enemy player is more likely to play in the center than in the other squares, but the idea is the same.)

This is very important, because probabilities are composable - you can add them up using the law of total probability. This is a really nice property. I came to realize this because I became stuck on trying to understand how to add up the scores. But if a score is just the probability of winning, then it's really obvious how to add them up. So conceptually this is really important for understanding what the score means.

The other thing that is necessary for understanding what this function does is to understand that it is called from `bestmove`. It is used to calculate the best move.

The `bestmove` function calculates the best move in any given gamestate. It does this by looking at each possible move and looking at the score associated with that move.

Now here is something really important. When we call `bestmove`, we are calling it from "our" perspective, i.e. we want to know the move that will lead to our win if it is our turn to play in the gamestate that we pass to `bestmove`. But when `bestmove` considers a move, it makes that move and that results in a gamestate where it is the enemy's turn to move.

So, `bestmove` considers the score for each move, and each move results in a gamestate where it is our opponent's turn to move.

Hence, the `win_probability` function takes in a gamestate where it is the **OPPONENT**'s turn to move. **This is really important.**

So how do we calculate the `win_probability`? Well, the input argument is a gamestate where it is the opponent's turn to move. The opponent could make any of up to 9 possible moves. So we have to consider every one of those moves in order to determine what our probability of winning is if the enemy decides to play randomly.

Intuitively we want to say that the probability of winning from a given gamestate S is the average of the probabilities of winning from each of the gamestates that can follow from moves made by the enemy in S.

For example, if in S the enemy has 2 moves, the first move gets the enemy into a gamestate where the perfect play outcome is our win, and the second move gets the enemy into a gamestate where we always draw no matter what happens, then the win probability is 0.5, because if the enemy makes the first move then we win, and if the enemy makes the second move then we draw, and since the probability of each move is equal, the total probability is (1+0)/2 = 0.5.

Now, here's the brain-melting part: When the enemy makes a move, that results in a gamestate where it is our turn to move. Hence we **CANNOT** run the `win_probability` function on *that* gamestate because it would calculate the wrong thing!

So this is where the `bestmove` function comes in, and that's why this is mutually recursive with it: when the enemy makes a move, that results in a gamestate where it is our turn to move. So what is the probability of us winning in that gamestate? Well, using the technique of wishful thinking, we assume that the `bestmove` function works and so we know what move we are going to make, which means we just apply the `bestmove` function to the gamestate where it is our turn to move, in order to get the gamestate that follows from that. And so the probability of us winning in gamestate_ourmove is exactly the same as the probability of us winning in `bestmove(gamestate_ourmove)`. This is because every time we are in `gamestate_ourmove`, we are going to make the best move, and thus arrive at the gamestate `bestmove(gamestate_ourmove)`. Therefore we can treat these gamestates as equivalent, because we will always make the same move to go from the former to the latter every time.

So that resolves the problem: we transform the gamestate where it is our turn to move into the gamestate that automatically follows that gamestate, thus obtaining a gamestate_enemysturn and we can pass that to `win_probability`.

So, given a gamestate, if perfect play from that state leads to our win, then the win probability of that state is 1.

Basically, the win probability function returns a number between 0 and 1 that reflects "how likely we are to win if the enemy plays randomly". If it's 1 then it means we will win no matter what the enemy plays. If it's 0 then it means we cannot win no matter what.

Pseudocode:

```
def bestmove(boardstate):
    return move with highest probability of winning

def probability_of_winning(boardstate):
    probabilities = []
    for each next_boardstate from this boardstate:
        probabilities.append(probability_of_winning(bestmove(next_boardstate)))
    return average(probabilities)
```



