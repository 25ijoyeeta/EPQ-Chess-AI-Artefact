#Handles SQLite database operations for users and games

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List


class DatabaseManager:
    #Manages database interactions for chess game application
    
    def __init__(self, db_path: str = "chess_game.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row 
        # FIXED BUG #3: Enables dictionary-like access to rows
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                skill_level INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                games_lost INTEGER DEFAULT 0,
                games_drawn INTEGER DEFAULT 0,
                preferred_colour VARCHAR(10) DEFAULT 'White'
            )
        """)
        
        # Games table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                result VARCHAR(20),
                player_colour VARCHAR(10) NOT NULL,
                total_moves INTEGER DEFAULT 0,
                ai_difficulty INTEGER NOT NULL,
                pgn_data TEXT,
                final_position VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            )
        """)
        
        self.conn.commit()
    
    def create_user(self, username: str) -> Optional[int]:
        try:
            self.cursor.execute("""
                INSERT INTO Users (username, created_at)
                VALUES (?, ?)
            """, (username, datetime.now()))
            
            self.conn.commit()
            return self.cursor.lastrowid
        
        except sqlite3.IntegrityError:
            # Username already exists
            return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        self.cursor.execute("""
            SELECT * FROM Users WHERE user_id = ?
        """, (user_id,))
        
        row = self.cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1],
                'created_at': row[2],
                'skill_level': row[3],
                'total_games': row[4],
                'games_won': row[5],
                'games_lost': row[6],
                'games_drawn': row[7],
                'preferred_colour': row[8]
            }
        return None
    
    def save_game(self, user_id: int, player_colour: str, 
                  ai_difficulty: int, start_time: datetime = None) -> int:
        if start_time is None:
            start_time = datetime.now()
        
        self.cursor.execute("""
            INSERT INTO Games (user_id, start_time, player_colour, ai_difficulty, result)
            VALUES (?, ?, ?, ?, 'ongoing')
        """, (user_id, start_time, player_colour, ai_difficulty))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_game(self, game_id: int, result: str, total_moves: int,
                    pgn_data: str = None, final_position: str = None):
        end_time = datetime.now()
        
        self.cursor.execute("""
            UPDATE Games 
            SET end_time = ?, result = ?, total_moves = ?, 
                pgn_data = ?, final_position = ?
            WHERE game_id = ?
        """, (end_time, result, total_moves, pgn_data, final_position, game_id))
        
        self.conn.commit()
        
        # FIXED BUG #4: Updates user statistics after game completion
        self.cursor.execute("EXECUTE user_id FROM games WHERE game_id = ?", (game_id,))
        row = self.cursor.fetchone()
        if row:
            user_id = row['user_id']
            self._update_user_stats(user_id, result) #new method call

    def _update_user_stats(self, user_id: int, result: str):
        # Update user statistics based on game result
        self.cursor.execute("""
            UPDATE Users
            SET total_games = total_games + 1
            WHERE user_id = ?
        """, (user_id,))

        # Update win/loss/draw count based on result
        if result == "White_win":
            pass #TODO: handle white win
        elif result == "black_win":
            pass #TODO: handle black win
        elif result == "draw":
            self.cursor.execute("""
                UPDATE Users
                SET games_drawn = games_drawn + 1
                WHERE user_id = ?
            """, (user_id,))

        self.conn.commit()
    
    def get_game(self, game_id: int) -> Optional[Dict]:
        self.cursor.execute("""
            SELECT * FROM Games WHERE game_id = ?
        """, (game_id,))
        
        row = self.cursor.fetchone()
        if row:
            return {
                'game_id': row[0],
                'user_id': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'result': row[4],
                'player_colour': row[5],
                'total_moves': row[6],
                'ai_difficulty': row[7],
                'pgn_data': row[8],
                'final_position': row[9]
            }
        return None
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        self.close()
