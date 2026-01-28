#tests for cycle 1: Implementing core componenent--ChessGame, GameGUI, DatabaseManager, PositionEvaluator

import unittest
import os
import chess
from database_manager import DatabaseManager
from chess_game import ChessGame
from position_evaluator import PositionEvaluator
from game_gui import GameGUI

# Tests for DatabaseManager class
class TestDatabaseManager(unittest.TestCase):
    
    def setUp(self):
        self.test_db = "test_chess.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = DatabaseManager(self.test_db)
    
    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_UT17_create_new_user(self):
        #UT17: Create new user
        user_id = self.db.create_user("TestUser")
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)
        print(f"UT17 PASS: Created user with ID {user_id}")
    
    def test_UT21_handle_duplicate_username(self):
        #UT21: Handle duplicate username
        
        self.db.create_user("TestUser")
        duplicate_id = self.db.create_user("TestUser")
        self.assertIsNone(duplicate_id)
        print("UT21 PASS: Duplicate username rejected")
    
    def test_UT18_save_game(self):
        #UT18: Save game
        
        user_id = self.db.create_user("GameTester")
        game_id = self.db.save_game(user_id, "white", 5)
        self.assertIsNotNone(game_id)
        self.assertGreater(game_id, 0)
        
        # Try to retrieve the game
        game = self.db.get_game(game_id)
        self.assertIsNotNone(game)
        self.assertEqual(game['user_id'], user_id)
        print(f"UT18 PASS: Game saved with ID {game_id}")

# Tests for PositionEvaluator class
class TestPositionEvaluator(unittest.TestCase):
    
    def setUp(self):
        self.evaluator = PositionEvaluator()
    
    def test_UT08_evaluate_starting_position(self):
        #UT08: Evaluate starting position
        board = chess.Board()
        score = self.evaluator.evaluate_position(board)
        self.assertLess(abs(score), 50)
        print(f"UT08 PASS: Starting position score = {score}")
    
    def test_UT09_evaluate_material_advantage(self):
        #UT09: Evaluate material advantage (white up a queen)
        board = chess.Board()
        # Remove black queen
        board.remove_piece_at(chess.D8)
        score = self.evaluator.evaluate_position(board)
        self.assertGreater(score, 800)
        print(f"UT09 PASS: Material advantage score = {score}")
    
    def test_UT10_evaluate_checkmate(self):
        #UT10: Evaluate checkmate position
        # Fool's mate position
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        score = self.evaluator.evaluate_position(board)
        self.assertGreaterEqual(abs(score), 1000)
        print(f"UT10 PASS: Checkmate score = {score}")


class TestChessGame(unittest.TestCase):
    #Tests for ChessGame class
    
    def setUp(self):
        self.game = ChessGame("white")
    
    def test_UT01_validate_legal_move(self):
        #UT01: Validates legal move
        result = self.game.make_move("e2e4")
        self.assertTrue(result)
        self.assertIn("e2e4", self.game.get_board_fen())
        print("UT01 PASS: Legal move e2e4 accepted")
    
    def test_UT02_reject_illegal_move(self):
        #UT02: Reject illegal move
        result = self.game.make_move("e2e5")
        self.assertFalse(result)
        # Board should be unchanged
        self.assertEqual(self.game.get_board_fen(), chess.Board().fen())
        print("UT02 PASS: Illegal move e2e5 rejected")
    
    def test_UT03_detect_checkmate(self):
        #UT03: Detect checkmate
        # Set up fool's mate
        self.game.make_move("f2f3")
        self.game.make_move("e7e5")
        self.game.make_move("g2g4")
        self.game.make_move("d8h4")  # Checkmate
        
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_result(), "black_win")
        print("UT03 PASS: Checkmate detected")
    
    def test_UT04_detect_stalemate(self):
        #UT04: Detect stalemate
        # Set up stalemate position
        board_fen = "k7/8/1K6/8/8/8/8/1Q6 b - - 0 1"
        self.game.board = chess.Board(board_fen)
        self.game._check_game_over()
        
        self.assertTrue(self.game.is_game_over())
        self.assertEqual(self.game.get_result(), "draw")
        print("UT04 PASS: Stalemate detected")
    
    def test_UT05_handle_castling(self):
        #UT05: Handle castling
        # Set up position where white can castle kingside
        self.game.board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        result = self.game.make_move("e1g1")
        self.assertTrue(result)
        # Check that both king and rook moved
        self.assertIsNotNone(self.game.get_piece_at(chess.G1))  # King
        self.assertIsNotNone(self.game.get_piece_at(chess.F1))  # Rook
        print("UT05 PASS: Castling executed")
    
    def test_UT06_handle_en_passant(self):
        #UT06: Handle en passant
        # Set up en passant position
        self.game.board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
        self.game.make_move("d7d5")
        # Now white can capture en passant
        self.game.board.push(chess.Move.from_uci("e4d5"))
        
        # Check that pawn was captured
        self.assertIsNone(self.game.get_piece_at(chess.D5))
        print("UT06 PASS: En passant executed")
    
    def test_UT07_handle_promotion(self):
        #UT07: Handle promotion
        # Set up promotion position
        self.game.board = chess.Board("8/P7/8/8/8/8/8/4K2k w - - 0 1")
        result = self.game.make_move("a7a8q")  # Promote to queen
        self.assertTrue(result)
        piece = self.game.get_piece_at(chess.A8)
        self.assertEqual(piece.piece_type, chess.QUEEN)
        print("UT07 PASS: Promotion executed")


class TestGameGUI(unittest.TestCase):
    #Tests for GameGUI class
    
    def setUp(self):
        self.game = ChessGame("white")
        self.gui = GameGUI(self.game)
    
    def test_UT22_load_piece_images(self):
        #UT22: Load piece images
        # Check that all 12 pieces have images loaded
        expected_pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk',
                          'bp', 'bn', 'bb', 'br', 'bq', 'bk']
        
        for piece in expected_pieces:
            self.assertIn(piece, self.gui.piece_images)
        
        self.assertEqual(len(self.gui.piece_images), 12)
        print("UT22 PASS: All 12 piece images loaded")
    
    def test_UT23_convert_click_to_square(self):
        #UT23: Convert click to chess.square
        # Click at board offset + 2 squares right, 2 squares down
        x = self.gui.BOARD_OFFSET + 2 * self.gui.SQUARE_SIZE + self.gui.SQUARE_SIZE // 2
        y = self.gui.BOARD_OFFSET + 2 * self.gui.SQUARE_SIZE + self.gui.SQUARE_SIZE // 2
        
        square = self.gui.click_to_square((x, y))
        # Should be square c6 (chess coordinates)
        # Row 2 from top = rank 6, col 2 = file c
        expected_square = self.gui.row_col_to_square(2, 2)
        
        self.assertEqual(square, expected_square)
        print(f"UT23 PASS: Click converted to square {square}")


def run_all_tests():
    #Run all unit tests and print results
    print("=" * 70)
    print("CYCLE 1 UNIT TESTS")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPositionEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestChessGame))
    suite.addTests(loader.loadTestsFromTestCase(TestGameGUI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    run_all_tests()