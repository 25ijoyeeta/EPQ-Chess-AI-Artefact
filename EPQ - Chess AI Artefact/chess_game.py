#Handles the game logic and coordination between components

import chess
import chess.pgn
from datetime import datetime
from typing import Optional, List, Tuple
from position_evaluator import PositionEvaluator

#Main controller for chess game logic
class ChessGame:
    
    def __init__(self, player_colour: str = "white"):
        self.board = chess.Board()
        self.player_colour = player_colour.lower()
        self.evaluator = PositionEvaluator()
        self.move_history = []
        self.game_over = False
        self.result = None
        
    def make_move(self, move_uci: str) -> bool:
        try:
            move = chess.Move.from_uci(move_uci)
        
            # FIXED BUG #1: Validate move is legal BEFORE pushing to board
            if move not in self.board.legal_moves:
               return False
        
            self.board.push(move)
            self.move_history.append(move_uci)
        
            self._check_game_over()
            return True
        
        except (chess.InvalidMoveError, ValueError):
            return False
            
    
    def make_move_san(self, move_san: str) -> bool:
        try:
            move = self.board.parse_san(move_san)
            self.board.push(move)
            self.move_history.append(move.uci())
            
            self._check_game_over()
            
            return True
            
        except (chess.InvalidMoveError, chess.IllegalMoveError, ValueError):
            return False
    
    def get_legal_moves(self) -> List[str]:
        # FIXED BUG #7: Return legal moves in UCI format
        return [move.uci() for move in self.board.legal_moves]
    
    def get_legal_moves_for_square(self, square: int) -> List[str]:
        legal_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                legal_moves.append(move.uci())
        return legal_moves
    
    def _check_game_over(self):
        # Check for checkmate, stalemate, or insufficient material
        if self.board.is_checkmate():
            self.game_over = True
            # Winner is opposite of current turn (who got checkmated)
            if self.board.turn == chess.WHITE:
                self.result = "black_win"
            else:
                self.result = "white_win"
                
        elif self.board.is_stalemate():
            self.game_over = True
            self.result = "draw"
            
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.result = "draw"
    
    def is_game_over(self) -> bool:
        return self.game_over
    
    def get_result(self) -> Optional[str]:
        return self.result
    
    def get_board_fen(self) -> str:
        return self.board.fen()
    
    def get_pgn(self) -> str:
        game = chess.pgn.Game()
        
        # Set headers
        game.headers["Event"] = "Chess AI Training"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Player" if self.player_colour == "white" else "AI"
        game.headers["Black"] = "AI" if self.player_colour == "white" else "Player"
        
        # Currently just setting headers, moves not included
        
        return str(game)
    
    def undo_move(self) -> bool:
        try:
            if len(self.move_history) > 0:
                self.board.pop()
                self.move_history.pop()
                self.game_over = False
                self.result = None
                return True
            return False
        except:
            return False
    
    def reset_game(self):
        # Reset the game to initial state
        self.board.reset()
        self.move_history = []
        self.game_over = False
        self.result = None
    
    def evaluate_current_position(self) -> float:
        # Evaluate the current board position
        return self.evaluator.evaluate_position(self.board)
    
    def is_player_turn(self) -> bool:
        # Determine if it's the player's turn
        if self.player_colour == "white":
            return self.board.turn == chess.WHITE
        else:
            return self.board.turn == chess.BLACK
    
    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        #
        return self.board.piece_at(square)