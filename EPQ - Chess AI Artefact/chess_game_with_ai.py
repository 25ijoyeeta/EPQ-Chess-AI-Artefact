#Cycle 1 contained core chess functionalities
#Cycle 2 adds AI integration and opponent modeling

from shutil import move
import chess
import chess.pgn
import time
from datetime import datetime
from typing import Optional, List, Tuple
from position_evaluator import PositionEvaluator
from ai_engine import AIEngine
from opponent_model import OpponentModel


class ChessGameWithAI:
    
    def __init__(self, player_colour: str = "white", ai_difficulty: int = 5,
                 db_manager=None, user_id: int = None):

        self.board = chess.Board()
        self.player_colour = player_colour.lower()
        self.evaluator = PositionEvaluator()
        self.ai_engine = AIEngine(difficulty=ai_difficulty)
        self.move_history = []
        self.move_times = []  # Track time per move
        self.game_over = False
        self.result = None
        self.db_manager = db_manager
        self.user_id = user_id
        self.game_id = None
        
        # Opponent modeling
        if db_manager and user_id:
            self.opponent_model = OpponentModel(db_manager)
        else:
            self.opponent_model = None
    
    def start_new_game(self):
        if self.db_manager and self.user_id:
            self.game_id = self.db_manager.save_game(
                self.user_id, 
                self.player_colour, 
                self.ai_engine.difficulty
            )
    
    def make_move(self, move_uci: str) -> bool:
        move = chess.Move.from_uci(move_uci)

        position_before = self.board.fen()

        #FIXED BUG #14: Evaluate BEFORE making the move
        eval_before = self.evaluator.evaluate_position(self.board)

        self.board.push(move)

        self.db_manager.save_move(
            game_id=self.game_id,
            move_number=self.board.fullmove_number,
            player_side="white" if self.board.turn == chess.BLACK else "black",
            move_uci=move_uci,
            move_san=self.board.san(move),
            position_before=position_before,
            position_after=self.board.fen(),
            evaluation_score=eval_before
        )

        return True

    
    def make_ai_move(self) -> Optional[str]:

        if self.game_over:
            return None
        
        # Get best move from AI
        best_move_uci, eval_score = self.ai_engine.get_best_move(self.board)
        
        # BUG #15: Not checking if AI move is actually legal
        # Assumes AI always returns legal move
        
        position_before = self.board.fen()
        move = chess.Move.from_uci(best_move_uci)
        
        self.board.push(move)
        self.move_history.append(best_move_uci)
        self.move_times.append(0.0)  # AI move time not tracked
        
        # Save AI move to database
        if self.db_manager and self.game_id:
            move_number = len(self.move_history)
            player_side = "black" if self.board.turn == chess.WHITE else "white"
            
            self.db_manager.save_move(
                self.game_id, move_number, player_side,
                best_move_uci, self.board.san(move), position_before,
                self.board.fen(), 0.0, eval_score
            )
        
        self._check_game_over()
        
        return best_move_uci
    
    def get_legal_moves(self) -> List[str]:
        return [move.uci() for move in self.board.legal_moves]
    
    def get_legal_moves_for_square(self, square: int) -> List[str]:
        legal_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                legal_moves.append(move.uci())
        return legal_moves
    
    def _check_game_over(self):
        if self.board.is_checkmate():
            self.game_over = True
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
        
        elif self.board.can_claim_threefold_repetition():
            self.game_over = True
            self.result = "draw"
        
        elif self.board.can_claim_fifty_moves():
            self.game_over = True
            self.result = "draw"
        
        # Save game result to database
        if self.game_over and self.db_manager and self.game_id:
            pgn = self.get_pgn()
            self.db_manager.update_game(
                self.game_id, self.result, len(self.move_history),
                pgn, self.board.fen()
            )
            
            # Analyze patterns after game
            if self.opponent_model and self.user_id:
                patterns = self.opponent_model.analyze_player_patterns(self.user_id)
                self.opponent_model.save_patterns(self.user_id, patterns)
    
    def is_game_over(self) -> bool:
        return self.game_over
    
    def get_result(self) -> Optional[str]:
        return self.result
    
    def get_board_fen(self) -> str:
        return self.board.fen()
    
    def get_pgn(self) -> str:
        game = chess.pgn.Game()
        
        game.headers["Event"] = "Chess AI Training"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Player" if self.player_colour == "white" else "AI"
        game.headers["Black"] = "AI" if self.player_colour == "white" else "Player"
        
        node = game
        temp_board = chess.Board()
        
        for move_uci in self.move_history:
            move = chess.Move.from_uci(move_uci)
            node = node.add_variation(move)
            temp_board.push(move)
        
        if self.game_over:
            if self.result == "white_win":
                game.headers["Result"] = "1-0"
            elif self.result == "black_win":
                game.headers["Result"] = "0-1"
            elif self.result == "draw":
                game.headers["Result"] = "1/2-1/2"
        else:
            game.headers["Result"] = "*"
        
        return str(game)
    
    def is_player_turn(self) -> bool:
        if self.player_colour == "white":
            return self.board.turn == chess.WHITE
        else:
            return self.board.turn == chess.BLACK
    
    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        return self.board.piece_at(square)
    
    def is_in_check(self) -> bool:
        return self.board.is_check()
    
    def get_turn(self) -> bool:
        return self.board.turn
    
    def get_ai_nodes_searched(self) -> int:
        return self.ai_engine.get_nodes_searched()
    
    def undo_move(self) -> bool:
        # BUG #16: Undo doesn't work properly with AI games
        try:
            if len(self.move_history) > 0:
                self.board.pop()
                self.move_history.pop()
                self.move_times.pop()
                self.game_over = False
                self.result = None
                return True
            return False
        except:
            return False
    
    def reset_game(self):
        self.board.reset()
        self.move_history = []
        self.move_times = []
        self.game_over = False
        self.result = None