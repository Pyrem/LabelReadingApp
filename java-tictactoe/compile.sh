#!/bin/bash

# Tic Tac Toe compile and run script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create output directory
mkdir -p out

# Compile Java files
echo "Compiling..."
javac -d out src/main/java/tictactoe/*.java

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    echo ""
    echo "Running Tic Tac Toe..."
    echo ""
    java -cp out tictactoe.TicTacToe
else
    echo "Compilation failed!"
    exit 1
fi
