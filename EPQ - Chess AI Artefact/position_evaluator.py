#Evaluate chess position 

import chess


class PositionEvaluator:    
    # Piece values in centipawns
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0
    }
    
    def __init__(self):
        pass
    
    def evaluate_position(self, board: chess.Board) -> float:
        # Check for terminal positions
        if board.is_checkmate():
            # FIXED BUG #2: Correct logic for who is checkmated
            if board.turn == chess.WHITE:
                return -10000  # White is checkmated, black wins
            else:
                return 10000   # Black is checkmated, white wins
        
        score = 0
        
        # Material balance
        score += self.count_material(board)        
        return score
    
    def count_material(self, board: chess.Board) -> int:
        white_material = 0
        black_material = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.PIECE_VALUES[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
        
        return white_material - black_material
    
    def evaluate_piece_squares(self, board: chess.Board) -> int:
        # Placeholder for future implementation
        return 0
    
    def evaluate_king_safety(self, board: chess.Board) -> int:
        return 0
    
    def evaluate_pawn_structure(self, board: chess.Board) -> int:
        return 0
    
    def evaluate_mobility(self, board: chess.Board) -> int:
        return 0
    
    def evaluate_center_control(self, board: chess.Board) -> int:
        return 0