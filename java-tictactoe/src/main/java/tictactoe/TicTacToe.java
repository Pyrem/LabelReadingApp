package tictactoe;

import java.util.Scanner;

/**
 * Main class for the Tic Tac Toe console game.
 */
public class TicTacToe {
    private Board board;
    private Player player1;
    private Player player2;
    private Player currentPlayer;
    private Scanner scanner;

    public TicTacToe() {
        board = new Board();
        scanner = new Scanner(System.in);
    }

    /**
     * Starts the game by getting player names and beginning the game loop.
     */
    public void start() {
        printWelcome();
        setupPlayers();
        gameLoop();
    }

    /**
     * Prints the welcome message.
     */
    private void printWelcome() {
        System.out.println("====================================");
        System.out.println("    Welcome to Tic Tac Toe!");
        System.out.println("====================================");
        System.out.println();
    }

    /**
     * Sets up the players by getting their names.
     */
    private void setupPlayers() {
        System.out.print("Enter Player 1 name (X): ");
        String name1 = scanner.nextLine().trim();
        if (name1.isEmpty()) {
            name1 = "Player 1";
        }
        player1 = new Player(name1, 'X');

        System.out.print("Enter Player 2 name (O): ");
        String name2 = scanner.nextLine().trim();
        if (name2.isEmpty()) {
            name2 = "Player 2";
        }
        player2 = new Player(name2, 'O');

        currentPlayer = player1;
        System.out.println("\n" + player1.getName() + " goes first!");
    }

    /**
     * Main game loop that continues until there's a winner or draw.
     */
    private void gameLoop() {
        boolean gameOver = false;

        while (!gameOver) {
            board.display();
            System.out.println(currentPlayer.getName() + "'s turn (" + currentPlayer.getMark() + ")");

            int[] move = getPlayerMove();
            board.placeMark(move[0], move[1], currentPlayer.getMark());

            if (board.checkWin(currentPlayer.getMark())) {
                board.display();
                System.out.println("====================================");
                System.out.println("  " + currentPlayer.getName() + " wins!");
                System.out.println("====================================");
                gameOver = true;
            } else if (board.isFull()) {
                board.display();
                System.out.println("====================================");
                System.out.println("  It's a draw!");
                System.out.println("====================================");
                gameOver = true;
            } else {
                switchPlayer();
            }
        }

        askPlayAgain();
    }

    /**
     * Gets the player's move with input validation.
     * @return an array with [row, col] (0-indexed)
     */
    private int[] getPlayerMove() {
        int row = -1;
        int col = -1;
        boolean validInput = false;

        while (!validInput) {
            try {
                System.out.print("Enter row (1-3): ");
                row = Integer.parseInt(scanner.nextLine().trim()) - 1;

                System.out.print("Enter column (1-3): ");
                col = Integer.parseInt(scanner.nextLine().trim()) - 1;

                if (row < 0 || row > 2 || col < 0 || col > 2) {
                    System.out.println("Invalid input! Please enter numbers between 1 and 3.");
                } else if (board.getCell(row, col) != '-') {
                    System.out.println("That cell is already taken! Try again.");
                } else {
                    validInput = true;
                }
            } catch (NumberFormatException e) {
                System.out.println("Invalid input! Please enter a number.");
            }
        }

        return new int[]{row, col};
    }

    /**
     * Switches the current player.
     */
    private void switchPlayer() {
        currentPlayer = (currentPlayer == player1) ? player2 : player1;
    }

    /**
     * Asks if the players want to play again.
     */
    private void askPlayAgain() {
        System.out.print("\nPlay again? (y/n): ");
        String response = scanner.nextLine().trim().toLowerCase();

        if (response.equals("y") || response.equals("yes")) {
            board.initialize();
            currentPlayer = player1;
            System.out.println("\nStarting new game...");
            gameLoop();
        } else {
            System.out.println("\nThanks for playing! Goodbye!");
            scanner.close();
        }
    }

    /**
     * Main entry point for the game.
     */
    public static void main(String[] args) {
        TicTacToe game = new TicTacToe();
        game.start();
    }
}
