# Tic Tac Toe - Java Console Game

A simple two-player Tic Tac Toe game for the command line.

## Project Structure

```
java-tictactoe/
├── src/main/java/tictactoe/
│   ├── Board.java       # Game board logic
│   ├── Player.java      # Player representation
│   └── TicTacToe.java   # Main game class
├── compile.sh           # Build script
└── README.md
```

## How to Compile and Run

### Option 1: Using the compile script
```bash
./compile.sh
```

### Option 2: Manual compilation
```bash
# Compile
javac -d out src/main/java/tictactoe/*.java

# Run
java -cp out tictactoe.TicTacToe
```

## How to Play

1. Run the game
2. Enter player names (or press Enter for defaults)
3. Players take turns entering row (1-3) and column (1-3)
4. First player to get 3 in a row wins!
5. Choose to play again or exit

## Game Display

```
  1 2 3
1 - - -
2 - - -
3 - - -
```

- `-` represents an empty cell
- `X` is Player 1's mark
- `O` is Player 2's mark
