#Handles visual representation of the chess game using Pygame

import os
from turtle import pos 
import pygame
import chess
from typing import Optional, Tuple, List
from chess_game import ChessGame


class GameGUI:
    
    # Display constants
    WINDOW_SIZE = 800
    BOARD_SIZE = 640
    SQUARE_SIZE = BOARD_SIZE // 8
    BOARD_OFFSET = (WINDOW_SIZE - BOARD_SIZE) // 2
    
    # Colors
    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)
    HIGHLIGHT_COLOR = (186, 202, 68)
    LEGAL_MOVE_COLOR = (100, 100, 100, 100)
    
    def __init__(self, game: ChessGame):
        pygame.init()
        self.game = game
        self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
        pygame.display.set_caption("Chess AI Training")
        
        # Load piece images
        self.piece_images = {}
        self.load_piece_images()
        
        # Selection state
        self.selected_square = None
        self.legal_moves_for_selected = []
        
    
    def load_piece_images(self):
        pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
                 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    
        # FIX BUG #5: Check if assets folder exists
        assets_path = 'assets'
        if not os.path.exists(assets_path):
            print(f"WARNING: Assets folder not found at '{assets_path}'")
            print("Creating placeholder images...")
            self._create_placeholder_images(pieces)
            return
    
         # Try to load each piece image
        for piece in pieces:
           image_path = os.path.join(assets_path, f'{piece}.png')
           try:
              if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                image = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                self.piece_images[piece] = image
              else:
                 # FIX: Inform user which images are missing
                 print(f"WARNING: Image not found: {image_path}")
                 self._create_placeholder_for_piece(piece)
           except Exception as e:
                print(f"ERROR loading {image_path}: {e}")
                self._create_placeholder_for_piece(piece)
    
        # Verify all pieces loaded
        if len(self.piece_images) == 12:
           print("✓ All 12 piece images loaded successfully")
        else:
           print(f"⚠ Only {len(self.piece_images)}/12 images loaded, using placeholders")
    
    def draw_board(self):
        # Draw chess board squares
        for row in range(8):
            for col in range(8):
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                # Draw square
                x = self.BOARD_OFFSET + col * self.SQUARE_SIZE
                y = self.BOARD_OFFSET + row * self.SQUARE_SIZE
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Highlight selected square
                square = self.row_col_to_square(row, col)
                if square == self.selected_square:
                    pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR,
                                   (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
    
    def draw_pieces(self):
        # Draw chess pieces on the board
        for row in range(8):
            for col in range(8):
                square = self.row_col_to_square(row, col)
                piece = self.game.get_piece_at(square)
                
                if piece:
                    # Get piece image key
                    color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                    piece_type = chess.piece_name(piece.piece_type)[0]
                    image_key = color_prefix + piece_type
                    
                    # Draw piece
                    x = self.BOARD_OFFSET + col * self.SQUARE_SIZE
                    y = self.BOARD_OFFSET + row * self.SQUARE_SIZE
                    self.screen.blit(self.piece_images[image_key], (x, y))
    
    def draw_legal_moves(self):
        # Draw indicators for legal moves of selected piece
        for move_uci in self.legal_moves_for_selected:
            to_square = chess.Move.from_uci(move_uci).to_square
            row, col = self.square_to_row_col(to_square)
            
            x = self.BOARD_OFFSET + col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            y = self.BOARD_OFFSET + row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            
            # Draw circle for legal move
            pygame.draw.circle(self.screen, self.LEGAL_MOVE_COLOR, (x, y), 15)
    
    def draw(self):
        # Draw entire game state
        self.screen.fill((50, 50, 50))  # Dark background
        self.draw_board()
        self.draw_legal_moves()
        self.draw_pieces()
        pygame.display.flip()
    
    def square_to_row_col(self, square: int) -> Tuple[int, int]:
        # Convert chess square to row/col
        row = 7 - (square // 8)  # Flip because row 0 should be at top
        col = square % 8
        return row, col
    
    def row_col_to_square(self, row: int, col: int) -> int:
        # Convert row/col to chess square
        return (7 - row) * 8 + col
    
    def click_to_square(self, pos: Tuple[int, int]) -> Optional[int]:
    # Convert mouse click position to chess.square
        x, y = pos

    # Check if click is within board
        if (x < self.BOARD_OFFSET or x >= self.BOARD_OFFSET + self.BOARD_SIZE or
           y < self.BOARD_OFFSET or y >= self.BOARD_OFFSET + self.BOARD_SIZE):
           return None

    # FIXED BUG #6: Subtract BOARD_OFFSET before dividing by SQUARE_SIZE
        col = (x - self.BOARD_OFFSET) // self.SQUARE_SIZE
        row = (y - self.BOARD_OFFSET) // self.SQUARE_SIZE

        return self.row_col_to_square(row, col)

    
    def handle_click(self, pos: Tuple[int, int]):
        # Handle mouse click events
        square = self.click_to_square(pos)
        
        if square is None:
            return
        
        # If we have a piece selected and click is on legal move
        if self.selected_square is not None:
            move_uci = chess.square_name(self.selected_square) + chess.square_name(square)
            
            if move_uci in self.legal_moves_for_selected:
                # Make the move
                self.game.make_move(move_uci)
                self.selected_square = None
                self.legal_moves_for_selected = []
                return
        
        # Select a piece
        piece = self.game.get_piece_at(square)
        if piece and self.game.is_player_turn():
            # Check if piece belongs to player
            player_is_white = self.game.player_colour == "white"
            piece_is_white = piece.color == chess.WHITE
            
            if player_is_white == piece_is_white:
                self.selected_square = square
                self.legal_moves_for_selected = self.game.get_legal_moves_for_square(square)
            else:
                self.selected_square = None
                self.legal_moves_for_selected = []
        else:
            self.selected_square = None
            self.legal_moves_for_selected = []
    
    def run(self):
        # Main loop to run the GUI
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            self.draw()
        
        pygame.quit()