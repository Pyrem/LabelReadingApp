package tictactoe;

/**
 * Represents the Tic Tac Toe game board.
 */
public class Board {
    private char[][] grid;
    private static final int SIZE = 3;
    private static final char EMPTY = '-';

    public Board() {
        grid = new char[SIZE][SIZE];
        initialize();
    }

    /**
     * Initializes the board with empty cells.
     */
    public void initialize() {
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                grid[i][j] = EMPTY;
            }
        }
    }

    /**
     * Displays the current state of the board.
     */
    public void display() {
        System.out.println("\n  1 2 3");
        for (int i = 0; i < SIZE; i++) {
            System.out.print((i + 1) + " ");
            for (int j = 0; j < SIZE; j++) {
                System.out.print(grid[i][j] + " ");
            }
            System.out.println();
        }
        System.out.println();
    }

    /**
     * Places a mark on the board at the specified position.
     * @param row the row (0-indexed)
     * @param col the column (0-indexed)
     * @param mark the player's mark (X or O)
     * @return true if the move was successful, false otherwise
     */
    public boolean placeMark(int row, int col, char mark) {
        if (row < 0 || row >= SIZE || col < 0 || col >= SIZE) {
            return false;
        }
        if (grid[row][col] != EMPTY) {
            return false;
        }
        grid[row][col] = mark;
        return true;
    }

    /**
     * Checks if the specified player has won.
     * @param mark the player's mark to check
     * @return true if the player has won
     */
    public boolean checkWin(char mark) {
        // Check rows
        for (int i = 0; i < SIZE; i++) {
            if (grid[i][0] == mark && grid[i][1] == mark && grid[i][2] == mark) {
                return true;
            }
        }

        // Check columns
        for (int j = 0; j < SIZE; j++) {
            if (grid[0][j] == mark && grid[1][j] == mark && grid[2][j] == mark) {
                return true;
            }
        }

        // Check diagonals
        if (grid[0][0] == mark && grid[1][1] == mark && grid[2][2] == mark) {
            return true;
        }
        if (grid[0][2] == mark && grid[1][1] == mark && grid[2][0] == mark) {
            return true;
        }

        return false;
    }

    /**
     * Checks if the board is full.
     * @return true if all cells are filled
     */
    public boolean isFull() {
        for (int i = 0; i < SIZE; i++) {
            for (int j = 0; j < SIZE; j++) {
                if (grid[i][j] == EMPTY) {
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * Returns the grid size.
     */
    public int getSize() {
        return SIZE;
    }

    /**
     * Returns the cell value at the given position.
     */
    public char getCell(int row, int col) {
        if (row >= 0 && row < SIZE && col >= 0 && col < SIZE) {
            return grid[row][col];
        }
        return EMPTY;
    }
}
