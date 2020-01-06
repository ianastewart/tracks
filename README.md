# Train tracks solver
Solver for the train tracks puzzle as published in the London Times and other puzzle magazines or websites.

Train tracks is a puzzle where you have to draw train tracks on a grid to enable a train to pass from point A, somewhere on the left side, to point B, somewhere on the bottom.
Numbers across the top and down the right side indicate how many sections of track go in each row and column. There are only straight rails and rails that turn a corner. The track cannot cross itself. The start position, end position and a few (typically 2) other cells also contain tracks in the starting position..

The program draws the layout using Python turtle graphics. Set DEBUG=True to see the partially drawn track as the program searches for a solution, but note this will make the run time rather long.

The code uses a depth first recursive descent algorithm to solve the puzzle by brute force. A search is terminated and the next possible move is tried when the contraints on the number of pieces in a row or column are not met.

There is one optimisation to cut down the size of the search tree: the program checks for the case where a row or column is fully occupied, the current cell is on one side of this barrier and there are row or columns that need to have tracks in them that lie on the other side.
