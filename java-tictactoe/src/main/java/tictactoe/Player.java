package tictactoe;

/**
 * Represents a player in the Tic Tac Toe game.
 */
public class Player {
    private String name;
    private char mark;

    /**
     * Creates a new player with the given name and mark.
     * @param name the player's name
     * @param mark the player's mark (X or O)
     */
    public Player(String name, char mark) {
        this.name = name;
        this.mark = mark;
    }

    /**
     * Gets the player's name.
     */
    public String getName() {
        return name;
    }

    /**
     * Gets the player's mark.
     */
    public char getMark() {
        return mark;
    }

    @Override
    public String toString() {
        return name + " (" + mark + ")";
    }
}
