import unittest
from src.board import Board, Piece
from src.move_generator import generate_moves

class TestMoveGeneration(unittest.TestCase):
    def setUp(self):
        # Khởi tạo bàn cờ tiêu chuẩn cho các test không cần thay đổi đặc biệt.
        self.board = Board()

    def test_initial_pawn_moves(self):
        """
        Ở vị trí ban đầu, mỗi tốt có thể đi 1 ô hoặc 2 ô.
        Tổng số nước đi từ các tốt là 16.
        """
        moves = generate_moves(self.board)
        pawn_moves = [
            move for move in moves 
            if self.board.grid[move[0][0]][move[0][1]].type == "pawn"
        ]
        self.assertEqual(len(pawn_moves), 16, "Số nước đi của các tốt ban đầu phải là 16.")

    def test_knight_moves(self):
        """
        Kiểm tra rằng quân Mã (ví dụ: tại vị trí (7,1) cho trắng) có ít nhất 2 nước đi.
        """
        moves = generate_moves(self.board)
        knight_moves = [
            move for move in moves 
            if self.board.grid[7][1] is not None and self.board.grid[7][1].type == "knight"
        ]
        self.assertTrue(len(knight_moves) >= 2, "Quân Mã ở vị trí (7,1) phải có ít nhất 2 nước đi.")

    def test_king_castling_conditions(self):
        """
        Thiết lập bàn cờ đặc biệt cho phép nhập thành của bên trắng:
          - Xóa các quân ở giữa Vua và Xe.
          - Đảm bảo quyền nhập thành (castling rights) còn được đặt là True.
        Kiểm tra rằng nước đi nhập thành xuất hiện trong danh sách nước đi.
        """
        board = Board()
        board.current_turn = "white"
        # Loại bỏ quân giữa vua và xe cho nhập thành bên vua (kingside)
        board.grid[7][5] = None
        board.grid[7][6] = None
        board.castling_rights["white"]["king_side"] = True

        moves = generate_moves(board)
        castling_move_kingside = ((7, 4), (7, 6))
        self.assertIn(castling_move_kingside, moves,
                      "Nước đi nhập thành bên vua (kingside) không được sinh ra khi điều kiện thỏa mãn.")

        # Thiết lập cho nhập thành bên hậu (queenside)
        board = Board()
        board.current_turn = "white"
        board.grid[7][1] = None
        board.grid[7][2] = None
        board.grid[7][3] = None
        board.castling_rights["white"]["queen_side"] = True

        moves = generate_moves(board)
        castling_move_queenside = ((7, 4), (7, 2))
        self.assertIn(castling_move_queenside, moves,
                      "Nước đi nhập thành bên hậu (queenside) không được sinh ra khi điều kiện thỏa mãn.")

    def test_pawn_promotion(self):
        """
        Thiết lập bàn cờ sao cho một tốt trắng sắp đạt đến hàng cuối (hàng 0).
        Kiểm tra rằng nước đi từ vị trí của tốt sang hàng 0 được sinh ra.
        (Lưu ý: Chưa thêm logic phong cấp, nhưng nước đi di chuyển đến hàng cuối cũng cần được sinh ra.)
        """
        board = Board()
        board.current_turn = "white"
        # Xóa hàng 0 để đảm bảo ô đó trống
        for col in range(8):
            board.grid[0][col] = None
        # Đặt một quân tốt trắng tại vị trí (1,4) để có thể di chuyển lên hàng 0
        board.grid[1][4] = Piece("pawn", "white")
        moves = generate_moves(board)
        promotion_move = ((1, 4), (0, 4))
        self.assertIn(promotion_move, moves,
                      "Nước đi phong cấp của tốt (di chuyển từ (1,4) sang (0,4)) không được sinh ra.")

    def test_en_passant(self):
        """
        Thiết lập trường hợp en passant:
          - Giả lập quân tốt trắng tại (3,4).
          - Thiết lập board.en_passant_target là (2,5) (nước đi bắt en passant cho tốt trắng từ (3,4)).
        Kiểm tra rằng nước đi en passant được sinh ra.
        """
        board = Board()
        board.current_turn = "white"
        # Xóa bàn cờ để tạo môi trường test đơn giản
        for r in range(8):
            for c in range(8):
                board.grid[r][c] = None
        # Đặt quân tốt trắng tại (3,4)
        board.grid[3][4] = Piece("pawn", "white")
        # Giả sử quân đối phương vừa di chuyển và board.en_passant_target được đặt tại (2,5)
        board.en_passant_target = (2, 5)
        moves = generate_moves(board)
        en_passant_move = ((3, 4), (2, 5))
        self.assertIn(en_passant_move, moves,
                      "Nước đi en passant từ (3,4) sang (2,5) không được sinh ra khi điều kiện thỏa mãn.")

if __name__ == '__main__':
    unittest.main()
