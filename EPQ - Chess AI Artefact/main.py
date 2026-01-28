#Main entry point for the chess game application

from chess_game import ChessGame
from game_gui import GameGUI
from database_manager import DatabaseManager


def main():
    print("Chess AI Training - Cycle 1")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseManager()
    print("Database initialized")
    
    # Create a test user
    user_id = db.create_user("Player1")
    if user_id:
        print(f"User created with ID: {user_id}")
    else:
        print("User already exists, using existing user")
        user_id = 1
    
    # Initialize game
    game = ChessGame(player_colour="white")
    print("Game initialized")
    
    # Save game to database
    game_id = db.save_game(user_id, "white", ai_difficulty=5)
    print(f"Game saved with ID: {game_id}")
    
    # Initialize GUI
    print("Launching GUI...")
    gui = GameGUI(game)
    
    # Run the game
    gui.run()
    
    # Clean up
    db.close()
    print("Game ended")


if __name__ == "__main__":
    main()