# Gameplay

import pygame
import chess
import os
from typing import Optional, Tuple, List
from chess_game_with_ai import ChessGameWithAI
from database_manager import DatabaseManager 
from analysis_engine import AnalysisEngine
from feedback_generator import FeedbackGenerator


class FinalChessGame:
    
    # Display constants
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    BOARD_SIZE = 640
    SQUARE_SIZE = BOARD_SIZE // 8
    BOARD_OFFSET_X = 50
    BOARD_OFFSET_Y = 80
    PANEL_X = 750
    
    # Colors
    LIGHT_SQUARE = (240, 217, 181)
    DARK_SQUARE = (181, 136, 99)
    HIGHLIGHT_COLOR = (186, 202, 68, 180)
    LEGAL_MOVE_COLOR = (100, 100, 100, 128)
    BACKGROUND_COLOR = (40, 40, 40)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (70, 130, 180)
    BUTTON_HOVER = (100, 160, 210)
    BUTTON_SUCCESS = (50, 200, 50)
    PANEL_BG = (50, 50, 50)
    
    FPS = 60
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Chess AI Training - Complete System")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.db = DatabaseManager()
        self.analysis_engine = AnalysisEngine(self.db)
        self.feedback_generator = FeedbackGenerator(self.db)
        
        # User management
        self.current_user_id = None
        self.current_username = ""
        
        # Game state
        self.game = None
        self.selected_square = None
        self.legal_moves_for_selected = []
        self.ai_is_thinking = False
        
        # UI state
        self.screen_state = "login"  # login, menu, game, analysis
        self.difficulty = 3
        self.player_colour = "white"
        
        # Analysis data
        self.current_analysis = None
        self.current_feedback = []
        self.scroll_offset = 0
        
        # Load assets
        self.piece_images = {}
        self.load_piece_images()
        
        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_large = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 22)
        self.font_small = pygame.font.SysFont('Arial', 18)
        self.font_tiny = pygame.font.SysFont('Arial', 14)
        
        # Input field
        self.username_input = ""
        self.input_active = False
    
    def load_piece_images(self):
        pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
                  'bp', 'bn', 'bb', 'br', 'bq', 'bk']
        
        assets_path = 'assets'
        if not os.path.exists(assets_path):
            self._create_placeholder_images(pieces)
            return
        
        for piece in pieces:
            image_path = os.path.join(assets_path, f'{piece}.png')
            try:
                if os.path.exists(image_path):
                    image = pygame.image.load(image_path)
                    image = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
                    self.piece_images[piece] = image
                else:
                    self._create_placeholder_for_piece(piece)
            except:
                self._create_placeholder_for_piece(piece)
    
    def _create_placeholder_images(self, pieces: List[str]):
        for piece in pieces:
            self._create_placeholder_for_piece(piece)
    
    def _create_placeholder_for_piece(self, piece: str):
        surf = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
        
        color_map = {
            'p': (139, 69, 19), 'n': (70, 130, 180), 'b': (128, 0, 128),
            'r': (220, 20, 60), 'q': (255, 215, 0), 'k': (255, 255, 255)
        }
        
        is_white = piece[0] == 'w'
        piece_type = piece[1]
        base_color = color_map.get(piece_type, (200, 200, 200))
        
        if not is_white:
            base_color = tuple(c // 2 for c in base_color)
        
        center = self.SQUARE_SIZE // 2
        radius = self.SQUARE_SIZE // 3
        pygame.draw.circle(surf, base_color, (center, center), radius)
        
        font = pygame.font.SysFont('Arial', 32, bold=True)
        text_color = (255, 255, 255) if not is_white else (0, 0, 0)
        text = font.render(piece_type.upper(), True, text_color)
        text_rect = text.get_rect(center=(center, center))
        surf.blit(text, text_rect)
        
        self.piece_images[piece] = surf
    
    #LOGIN SCREEN
    
    def draw_login_screen(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Title
        title = self.font_title.render("Chess AI Training System", True, self.TEXT_COLOR)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_medium.render("Cycle 3 - Complete System", True, (180, 180, 180))
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Username input
        prompt = self.font_medium.render("Enter Username:", True, self.TEXT_COLOR)
        prompt_rect = prompt.get_rect(center=(self.WINDOW_WIDTH // 2, 250))
        self.screen.blit(prompt, prompt_rect)
        
        # Input box
        input_box = pygame.Rect(400, 300, 400, 50)
        color = self.BUTTON_HOVER if self.input_active else self.BUTTON_COLOR
        pygame.draw.rect(self.screen, color, input_box, border_radius=5)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, input_box, 2, border_radius=5)
        
        # Input text
        if self.username_input:
            input_text = self.font_medium.render(self.username_input, True, self.TEXT_COLOR)
        else:
            input_text = self.font_medium.render("Click to type...", True, (150, 150, 150))
        
        input_text_rect = input_text.get_rect(center=input_box.center)
        self.screen.blit(input_text, input_text_rect)
        
        # Login button
        self.draw_button("LOGIN / REGISTER", 450, 400, 300, 60)
        
        # Instructions
        instructions = [
            "New users: Enter any username to create account",
            "Existing users: Enter your username to continue",
            "",
            "Features:",
            "• Play against adaptive AI (10 difficulty levels)",
            "• Post-game analysis with mistake detection",
            "• Personalized feedback and improvement plans",
            "• Pattern recognition and counter-strategies"
        ]
        
        y = 500
        for instruction in instructions:
            text = self.font_small.render(instruction, True, (180, 180, 180))
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
    
    def handle_login_input(self, event):
        # Handle input for login screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_box = pygame.Rect(400, 300, 400, 50)
            if input_box.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
            
            # Check login button
            button_rect = pygame.Rect(450, 400, 300, 60)
            if button_rect.collidepoint(event.pos) and self.username_input:
                self.login_user(self.username_input)
        
        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN and self.username_input:
                self.login_user(self.username_input)
            elif event.key == pygame.K_BACKSPACE:
                self.username_input = self.username_input[:-1]
            elif len(self.username_input) < 20 and event.unicode.isalnum():
                self.username_input += event.unicode
    
    def login_user(self, username: str):
        #Login or create user
        # Try to create user
        user_id = self.db.create_user(username)
        
        if user_id is None:
            # User exists, find ID
            # Simple search - in production would have proper lookup
            user_id = 1  # Placeholder
        
        self.current_user_id = user_id
        self.current_username = username
        self.screen_state = "menu"
    
    #MAIN MENU
    
    def draw_menu_screen(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Welcome
        welcome = self.font_large.render(f"Welcome, {self.current_username}!", True, self.TEXT_COLOR)
        welcome_rect = welcome.get_rect(center=(self.WINDOW_WIDTH // 2, 80))
        self.screen.blit(welcome, welcome_rect)
        
        # Get user stats
        user_data = self.db.get_user(self.current_user_id)
        if user_data:
            stats_text = f"Games: {user_data['total_games']} | " \
                        f"Wins: {user_data['games_won']} | " \
                        f"Losses: {user_data['games_lost']} | " \
                        f"Draws: {user_data['games_drawn']}"
            stats = self.font_small.render(stats_text, True, (180, 180, 180))
            stats_rect = stats.get_rect(center=(self.WINDOW_WIDTH // 2, 120))
            self.screen.blit(stats, stats_rect)
        
        # Game settings
        diff_text = self.font_medium.render(f"Difficulty: {self.difficulty}/10", True, self.TEXT_COLOR)
        diff_rect = diff_text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(diff_text, diff_rect)
        
        # Difficulty buttons
        self.draw_button("Easy (1-3)", 200, 240, 150, 50, self.difficulty <= 3)
        self.draw_button("Medium (4-6)", 400, 240, 150, 50, 4 <= self.difficulty <= 6)
        self.draw_button("Hard (7-10)", 600, 240, 150, 50, self.difficulty >= 7)
        
        # Colour selection
        colour_text = self.font_medium.render(f"Play as: {self.player_colour.upper()}", True, self.TEXT_COLOR)
        colour_rect = colour_text.get_rect(center=(self.WINDOW_WIDTH // 2, 330))
        self.screen.blit(colour_text, colour_rect)
        
        self.draw_button("White", 400, 370, 150, 50, self.player_colour == "white")
        self.draw_button("Black", 600, 370, 150, 50, self.player_colour == "black")
        
        # Main buttons
        self.draw_button("START NEW GAME", 400, 480, 400, 70)
        self.draw_button("VIEW GAME HISTORY", 400, 570, 400, 60)
        self.draw_button("LOGOUT", 400, 650, 200, 50)
    
    def handle_menu_click(self, pos: Tuple[int, int]):
        # Handle clicks on menu options
        x, y = pos
        
        # Difficulty
        if 200 <= x <= 350 and 240 <= y <= 290:
            self.difficulty = 2
        elif 400 <= x <= 550 and 240 <= y <= 290:
            self.difficulty = 5
        elif 600 <= x <= 750 and 240 <= y <= 290:
            self.difficulty = 8
        
        # Colour
        elif 400 <= x <= 550 and 370 <= y <= 420:
            self.player_colour = "white"
        elif 600 <= x <= 750 and 370 <= y <= 420:
            self.player_colour = "black"
        
        # Start game
        elif 400 <= x <= 800 and 480 <= y <= 550:
            self.start_new_game()
        
        # View history (not implemented)
        elif 400 <= x <= 800 and 570 <= y <= 630:
            pass  # Would show game history
        
        # Logout
        elif 400 <= x <= 600 and 650 <= y <= 700:
            self.screen_state = "login"
            self.username_input = ""
            self.current_user_id = None
    
    #GAME SCREEN
    
    def start_new_game(self):
        # Start a new game with AI
        self.game = ChessGameWithAI(
            player_colour=self.player_colour,
            ai_difficulty=self.difficulty,
            db_manager=self.db,
            user_id=self.current_user_id
        )
        self.game.start_new_game()
        self.screen_state = "game"
        self.selected_square = None
        self.legal_moves_for_selected = []
        
        if self.player_colour == "black":
            self.ai_is_thinking = True
    
    def draw_game_screen(self):
        # Draw the main game screen
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Title
        title = self.font_large.render("Chess Game", True, self.TEXT_COLOR)
        self.screen.blit(title, (self.BOARD_OFFSET_X, 20))
        
        # Draw board and pieces
        self.draw_board()
        self.draw_legal_moves()
        self.draw_pieces()
        
        # Draw info panel
        self.draw_game_info_panel()
    
    def draw_board(self):
        # Draw chess board
        for row in range(8):
            for col in range(8):
                is_light = (row + col) % 2 == 0
                color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                
                x = self.BOARD_OFFSET_X + col * self.SQUARE_SIZE
                y = self.BOARD_OFFSET_Y + row * self.SQUARE_SIZE
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Highlight selected
                square = self.row_col_to_square(row, col)
                if square == self.selected_square:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    s.fill(self.HIGHLIGHT_COLOR)
                    self.screen.blit(s, (x, y))
    
    def draw_pieces(self):
        # Draw chess pieces on the board'
        for row in range(8):
            for col in range(8):
                square = self.row_col_to_square(row, col)
                piece = self.game.get_piece_at(square)
                
                if piece:
                    color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                    piece_type = chess.piece_name(piece.piece_type)[0]
                    image_key = color_prefix + piece_type
                    
                    x = self.BOARD_OFFSET_X + col * self.SQUARE_SIZE
                    y = self.BOARD_OFFSET_Y + row * self.SQUARE_SIZE
                    
                    if image_key in self.piece_images:
                        self.screen.blit(self.piece_images[image_key], (x, y))
    
    def draw_legal_moves(self):
        # Draw indicators for legal moves of selected piece
        for move_uci in self.legal_moves_for_selected:
            to_square = chess.Move.from_uci(move_uci).to_square
            row, col = self.square_to_row_col(to_square)
            
            x = self.BOARD_OFFSET_X + col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            y = self.BOARD_OFFSET_Y + row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            
            s = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(s, self.LEGAL_MOVE_COLOR, (15, 15), 15)
            self.screen.blit(s, (x - 15, y - 15))
    
    def draw_game_info_panel(self):
        # Draw side panel with game info and controls
        x = self.PANEL_X
        y = 100
        
        # Panel background
        panel = pygame.Rect(x - 10, y - 10, 430, 680)
        pygame.draw.rect(self.screen, self.PANEL_BG, panel, border_radius=10)
        
        # Game status
        if not self.game.is_game_over():
            turn = "White's turn" if self.game.get_turn() else "Black's turn"
            if self.game.is_in_check():
                turn += " - CHECK!"
            text = self.font_medium.render(turn, True, self.TEXT_COLOR)
            self.screen.blit(text, (x, y))
            y += 40
            
            if self.ai_is_thinking:
                thinking = self.font_small.render("AI thinking...", True, (255, 200, 0))
                self.screen.blit(thinking, (x, y))
                y += 30
        else:
            result = self.game.get_result()
            if result == "white_win":
                result_text = "White Wins!"
            elif result == "black_win":
                result_text = "Black Wins!"
            else:
                result_text = "Draw!"
            
            text = self.font_large.render(result_text, True, (255, 215, 0))
            self.screen.blit(text, (x, y))
            y += 60
            
            # Analysis button
            self.draw_button("VIEW ANALYSIS", x, y, 300, 50)
            y += 70
        
        # Stats
        moves = len(self.game.move_history)
        text = self.font_small.render(f"Moves: {moves}", True, self.TEXT_COLOR)
        self.screen.blit(text, (x, y))
        y += 30
        
        text = self.font_small.render(f"Difficulty: {self.difficulty}/10", True, self.TEXT_COLOR)
        self.screen.blit(text, (x, y))
        y += 50
        
        # Controls
        controls = [
            "Controls:",
            "U - Undo move",
            "R - Restart",
            "ESC - Menu"
        ]
        for control in controls:
            text = self.font_small.render(control, True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            y += 25
    
    def handle_game_click(self, pos: Tuple[int, int]):
        # Handle clicks on the game screen
        # Check analysis button if game over
        if self.game.is_game_over():
            x, y = pos
            if self.PANEL_X <= x <= self.PANEL_X + 300 and 200 <= y <= 250:
                self.show_analysis()
                return
        
        if self.game.is_game_over() or not self.game.is_player_turn():
            return
        
        square = self.click_to_square(pos)
        if square is None:
            return
        
        # Try to make move
        if self.selected_square is not None:
            move_uci = chess.square_name(self.selected_square) + chess.square_name(square)
            
            if move_uci in self.legal_moves_for_selected:
                success = self.game.make_move(move_uci)
                if success:
                    self.selected_square = None
                    self.legal_moves_for_selected = []
                    
                    if not self.game.is_game_over():
                        self.ai_is_thinking = True
                return
        
        # Select piece
        piece = self.game.get_piece_at(square)
        if piece and self.game.is_player_turn():
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
    
    #ANALYSIS SCREEN
    
    def show_analysis(self):
        # Show post-game analysis screen
        if not self.game or not self.game.game_id:
            return
        
        # Run analysis
        self.current_analysis = self.analysis_engine.analyze_game(self.game.game_id)
        
        if self.current_analysis:
            # Generate feedback
            self.current_feedback = self.feedback_generator.generate_game_feedback(
                self.game.game_id, 
                self.current_analysis
            )
        
        self.screen_state = "analysis"
        self.scroll_offset = 0
    
    def draw_analysis_screen(self):
        # Draw the analysis screen with feedback and suggestions
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Title
        title = self.font_large.render("Game Analysis", True, self.TEXT_COLOR)
        self.screen.blit(title, (50, 30))
        
        # Back button
        self.draw_button("BACK TO MENU", 900, 30, 250, 50)
        
        if not self.current_analysis:
            text = self.font_medium.render("No analysis available", True, self.TEXT_COLOR)
            self.screen.blit(text, (400, 300))
            return
        
        y = 100 - self.scroll_offset
        x = 50
        
        # Summary stats
        total_moves = self.current_analysis.get('total_moves', 0)
        accuracy = self.current_analysis.get('accuracy', 0)
        
        text = self.font_medium.render(f"Total Moves: {total_moves}", True, self.TEXT_COLOR)
        self.screen.blit(text, (x, y))
        y += 35
        
        acc_color = (50, 200, 50) if accuracy >= 80 else (255, 200, 0) if accuracy >= 60 else (255, 100, 100)
        text = self.font_medium.render(f"Accuracy: {accuracy}%", True, acc_color)
        self.screen.blit(text, (x, y))
        y += 50
        
        # Mistakes summary
        blunders = len(self.current_analysis.get('blunders', []))
        mistakes = len(self.current_analysis.get('mistakes', []))
        inaccuracies = len(self.current_analysis.get('inaccuracies', []))
        
        text = self.font_small.render(f"Blunders: {blunders} | Mistakes: {mistakes} | Inaccuracies: {inaccuracies}", 
                                     True, self.TEXT_COLOR)
        self.screen.blit(text, (x, y))
        y += 50
        
        # Feedback section
        text = self.font_medium.render("Feedback & Suggestions:", True, self.TEXT_COLOR)
        self.screen.blit(text, (x, y))
        y += 40
        
        for item in self.current_feedback:
            category = item['category']
            message = item['message']
            
            # Category header
            cat_text = self.font_small.render(f"• {category}", True, (100, 200, 255))
            self.screen.blit(cat_text, (x + 20, y))
            y += 25
            
            # Message (word wrap)
            words = message.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                if self.font_tiny.size(test_line)[0] < 1000:
                    line = test_line
                else:
                    text = self.font_tiny.render(line, True, (200, 200, 200))
                    self.screen.blit(text, (x + 40, y))
                    y += 20
                    line = word + " "
            
            if line:
                text = self.font_tiny.render(line, True, (200, 200, 200))
                self.screen.blit(text, (x + 40, y))
                y += 20
            
            y += 15
    
    def handle_analysis_input(self, event):
        # Handle input on analysis screen (scrolling and back button)
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # Back button
            if 900 <= x <= 1150 and 30 <= y <= 80:
                self.screen_state = "menu"
            
            # Scroll
            elif event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 30)
            elif event.button == 5:  # Scroll down
                self.scroll_offset += 30
    
    #UTILITY METHODS
    
    def draw_button(self, text: str, x: int, y: int, width: int, height: int, active: bool = False):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(x, y, width, height)
        
        is_hover = rect.collidepoint(mouse_pos)
        color = self.BUTTON_HOVER if is_hover else self.BUTTON_COLOR
        
        if active:
            color = self.BUTTON_SUCCESS
        
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, rect, 2, border_radius=5)
        
        text_surface = self.font_small.render(text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def square_to_row_col(self, square: int) -> Tuple[int, int]:
        # Convert square index to row/col
        row = 7 - (square // 8)
        col = square % 8
        return row, col
    
    def row_col_to_square(self, row: int, col: int) -> int:
        # Convert row/col to square index
        return (7 - row) * 8 + col
    
    def click_to_square(self, pos: Tuple[int, int]) -> Optional[int]:
        # Convert mouse click position to board square index
        x, y = pos
        
        if (x < self.BOARD_OFFSET_X or x >= self.BOARD_OFFSET_X + self.BOARD_SIZE or
            y < self.BOARD_OFFSET_Y or y >= self.BOARD_OFFSET_Y + self.BOARD_SIZE):
            return None
        
        col = (x - self.BOARD_OFFSET_X) // self.SQUARE_SIZE
        row = (y - self.BOARD_OFFSET_Y) // self.SQUARE_SIZE
        
        return self.row_col_to_square(row, col)
    
    def process_ai_move(self):
        if self.ai_is_thinking and not self.game.is_game_over():
            self.game.make_ai_move()
            self.ai_is_thinking = False
    
    def run(self):
        running = True
        
        while running:
            self.clock.tick(self.FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.screen_state == "login":
                        self.handle_login_input(event)
                    elif self.screen_state == "menu":
                        self.handle_menu_click(event.pos)
                    elif self.screen_state == "game":
                        self.handle_game_click(event.pos)
                    elif self.screen_state == "analysis":
                        self.handle_analysis_input(event)
                
                elif event.type == pygame.KEYDOWN:
                    if self.screen_state == "login":
                        self.handle_login_input(event)
                    
                    elif self.screen_state == "game":
                        if event.key == pygame.K_u:
                            self.game.undo_move()
                            self.selected_square = None
                            self.legal_moves_for_selected = []
                        elif event.key == pygame.K_r:
                            self.start_new_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.screen_state = "menu"
            
            # Process AI
            if self.screen_state == "game" and self.ai_is_thinking:
                self.process_ai_move()
            
            # Draw
            if self.screen_state == "login":
                self.draw_login_screen()
            elif self.screen_state == "menu":
                self.draw_menu_screen()
            elif self.screen_state == "game":
                self.draw_game_screen()
            elif self.screen_state == "analysis":
                self.draw_analysis_screen()
            
            pygame.display.flip()
        
        pygame.quit()
        self.db.close()


def main():
    print("=" * 70)
    print("CHESS AI TRAINING SYSTEM - CYCLE 3")
    print("=" * 70)
    print("\nComplete Features:")
    print("✓ Adaptive AI opponent (10 difficulty levels)")
    print("✓ Post-game analysis with mistake detection")
    print("✓ Personalized feedback system")
    print("✓ Pattern recognition and tracking")
    print("✓ User profiles and game history")
    print("✓ Complete GUI with multiple screens")
    print("\nNote: Contains intentional bugs for educational testing")
    print("=" * 70)
    
    game = FinalChessGame()
    game.run()


if __name__ == "__main__":
    main()