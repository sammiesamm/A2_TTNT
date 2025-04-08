from copy import deepcopy

class Piece:
    """
    Đại diện cho một quân cờ.
    
    Attributes:
        type (str): "king", "queen", "rook", "knight", "bishop", "pawn".
        color (str): "white", "black".
        value (int): Giá trị cơ bản của quân, dùng cho hàm đánh giá.
    """
    def __init__(self, type, color):
        self.type = type      
        self.color = color 
        self.value = self.get_value()
    
    def get_value(self):
        """
        Trả về giá trị cơ bản của quân dựa trên loại quân.
        Các giá trị này thường được dùng cho hàm heuristic:
          - pawn: 1
          - knight/bishop: 3
          - rook: 5
          - queen: 9
          - king: 1000 (giá trị rất lớn, vì mất vua tức là thua cuộc)
        """
        values = {
            "pawn": 1,
            "knight": 3,
            "bishop": 3,
            "rook": 5,
            "queen": 9,
            "king": 1000
        }
        return values.get(self.type, 0)
    
    def __repr__(self):
        """
        Trả về biểu diễn dạng chuỗi của quân cờ (dùng cho debug).
        Ví dụ: "WK" cho Vua trắng, "BQ" cho Hậu đen.
        """
        color_symbol = self.color[0].upper()  # W hoặc B
        type_symbol = self.type[0].upper()
        return f"{color_symbol}{type_symbol}"


class Board:
    """
    Quản lý trạng thái của bàn cờ trong trò chơi Cờ vua.
    
    Attributes:
        grid (list): Mảng 2D 8x8 lưu trạng thái bàn cờ, mỗi phần tử là None hoặc một đối tượng Piece.
        current_turn (str): Lượt đi hiện tại, "white" hoặc "black".
        castling_rights (dict): Theo dõi quyền nhập thành cho mỗi bên.
        en_passant_target (tuple or None): Vị trí ô có khả năng bắt en passant (nếu có).
    """
    def __init__(self):
        self.grid = self.initialize_board()  # Khởi tạo bàn cờ theo vị trí tiêu chuẩn
        self.current_turn = "white"
        self.castling_rights = {
            "white": {"king_side": True, "queen_side": True},
            "black": {"king_side": True, "queen_side": True}
        }
        self.en_passant_target = None

    def initialize_board(self):
        """
        Khởi tạo bàn cờ theo vị trí tiêu chuẩn:
          - Hàng 0 (cho đen): [rook, knight, bishop, queen, king, bishop, knight, rook].
          - Hàng 1: 8 pawn đen.
          - Hàng 2-5: trống.
          - Hàng 6: 8 pawn trắng.
          - Hàng 7 (cho trắng): [rook, knight, bishop, queen, king, bishop, knight, rook].
        """
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Hàng 0: quân đen
        from_row_0 = [
            Piece("rook", "black"), Piece("knight", "black"),
            Piece("bishop", "black"), Piece("queen", "black"),
            Piece("king", "black"), Piece("bishop", "black"),
            Piece("knight", "black"), Piece("rook", "black")
        ]
        board[0] = from_row_0
        
        # Hàng 1: 8 pawn đen
        board[1] = [Piece("pawn", "black") for _ in range(8)]
        
        # Hàng 2 đến 5: trống
        for i in range(2, 6):
            board[i] = [None for _ in range(8)]
        
        # Hàng 6: 8 pawn trắng
        board[6] = [Piece("pawn", "white") for _ in range(8)]
        
        # Hàng 7: quân trắng
        from_row_7 = [
            Piece("rook", "white"), Piece("knight", "white"),
            Piece("bishop", "white"), Piece("queen", "white"),
            Piece("king", "white"), Piece("bishop", "white"),
            Piece("knight", "white"), Piece("rook", "white")
        ]
        board[7] = from_row_7
        
        return board
    
    def display(self):
        """
        Hiển thị bàn cờ ra console theo dạng ASCII art.
        Mỗi ô:
          - Nếu trống: in ". "
          - Nếu có quân: in ký hiệu của quân (chữ cái đầu của loại quân, in hoa).
        Cũng hiển thị lượt đi hiện tại.
        """
        print("Current turn:", self.current_turn)
        for row in self.grid:
            row_str = ""
            for cell in row:
                if cell is None:
                    row_str += ". "
                else:
                    symbol = cell.type[0].upper()
                    row_str += symbol + " "
            print(row_str)
        print("\n")
    
    def get_piece(self, position: tuple):
        """
        Trả về quân cờ tại vị trí (row, col). Nếu vị trí ngoài bàn cờ, trả về None.
        """
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def set_piece(self, position: tuple, piece: Piece):
        """
        Đặt quân cờ 'piece' vào vị trí (row, col) trên bàn cờ.
        """
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            self.grid[row][col] = piece
    
    def move_piece(self, start: tuple, end: tuple):
        """
        Di chuyển quân cờ từ vị trí start sang vị trí end.
        
        - Nếu nước đi là en passant, xóa quân bị bắt.
        - Nếu nước đi là phong cấp (pawn promotion), tự động nâng cấp thành queen.
        - Cập nhật en_passant_target và castling_rights.
        - Đổi lượt đi.
        """
        piece = self.get_piece(start)
        if piece is None:
            raise ValueError("Không có quân ở vị trí bắt đầu!")
        
        # Kiểm tra đúng lượt đi
        if piece.color != self.current_turn:
            raise ValueError("Không đúng lượt đi!")
        
        # Kiểm tra en passant
        is_en_passant = (piece.type == "pawn" and end == self.en_passant_target)
        
        # Di chuyển quân
        self.set_piece(end, piece)
        self.set_piece(start, None)
        
        # Nếu en passant, xóa quân tốt bị bắt (ở ngay sau ô mà tốt vừa đi qua)
        if is_en_passant:
            capture_row = end[0] + (1 if piece.color == "white" else -1)
            self.set_piece((capture_row, end[1]), None)
        
        # Phong cấp (nếu pawn đến hàng cuối)
        if piece.type == "pawn":
            if (piece.color == "white" and end[0] == 0) or (piece.color == "black" and end[0] == 7):
                self.promote_pawn(end, "queen")
        
        # Cập nhật en passant
        self.update_en_passant_target(start, end)
        
        # Cập nhật castling_rights
        self.update_castling_rights(start, end)
        
        # Đổi lượt
        self.current_turn = "black" if self.current_turn == "white" else "white"
    
    def promote_pawn(self, position: tuple, new_type: str):
        """
        Nâng cấp pawn tại vị trí 'position' thành new_type (mặc định: "queen").
        """
        p = self.get_piece(position)
        if p and p.type == "pawn":
            self.set_piece(position, Piece(new_type, p.color))
    
    def update_castling_rights(self, start: tuple, end: tuple):
        """
        Cập nhật quyền nhập thành nếu quân vua hoặc xe di chuyển từ vị trí ban đầu.
        """
        piece = self.get_piece(end)
        if piece and piece.type == "king":
            if piece.color == "white":
                self.castling_rights["white"]["king_side"] = False
                self.castling_rights["white"]["queen_side"] = False
            else:
                self.castling_rights["black"]["king_side"] = False
                self.castling_rights["black"]["queen_side"] = False
        
        if piece and piece.type == "rook":
            if piece.color == "white":
                if start == (7, 7):  # Rook ở góc h1
                    self.castling_rights["white"]["king_side"] = False
                elif start == (7, 0):  # Rook ở góc a1
                    self.castling_rights["white"]["queen_side"] = False
            else:
                if start == (0, 7):  # Rook ở góc h8
                    self.castling_rights["black"]["king_side"] = False
                elif start == (0, 0):  # Rook ở góc a8
                    self.castling_rights["black"]["queen_side"] = False
    
    def update_en_passant_target(self, start: tuple, end: tuple):
        """
        Nếu quân pawn vừa di chuyển 2 ô, đặt en_passant_target là ô ở giữa.
        Ngược lại, đặt en_passant_target = None.
        """
        piece = self.get_piece(end)
        if piece and piece.type == "pawn":
            start_row, start_col = start
            end_row, end_col = end
            if abs(end_row - start_row) == 2:
                mid_row = (start_row + end_row) // 2
                self.en_passant_target = (mid_row, start_col)
                return
        self.en_passant_target = None
    
    def is_square_attacked(self, position: tuple, by_color: str) -> bool:
        """
        Kiểm tra ô 'position' có bị tấn công bởi quân 'by_color' hay không.
        Tạo giả định rằng ta sẽ dùng generate_moves (hoặc pseudo-legal) trong board.py.
        """
        saved_turn = self.current_turn
        self.current_turn = by_color
        # Import hàm generate_moves Ở CUỐI file board.py để tránh vòng lặp.
        from src.move_generator import generate_pseudolegal_moves
        enemy_moves = generate_pseudolegal_moves(self)
        self.current_turn = saved_turn
        for move in enemy_moves:
            if move[1] == position:
                return True
        return False

    def is_in_check(self, color: str) -> bool:
        """
        Kiểm tra xem vua 'color' có bị chiếu không.
        """
        # Tìm vị trí vua
        king_pos = None
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece and piece.type == "king" and piece.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if king_pos is None:
            # Không tìm thấy vua => có thể xem như bị chiếu
            return True
        
        enemy_color = "black" if color == "white" else "white"
        return self.is_square_attacked(king_pos, enemy_color)
    
    def is_move_legal(self, move: tuple) -> bool:
        """
        Kiểm tra nước đi (start, end): 
          - Tạo bản sao board, move_piece => kiểm tra vua có bị chiếu không.
        """
        board_copy = self.clone()
        start, end = move
        try:
            board_copy.move_piece(start, end)
        except ValueError:
            # Nếu move_piece ném lỗi => nước đi không hợp lệ
            return False
        # Sau khi di chuyển, nếu vua của bên đi vẫn không bị chiếu => hợp lệ
        piece = self.get_piece(start)
        moving_color = self.current_turn if not piece else piece.color
        return not board_copy.is_in_check(moving_color)
    
    def clone(self):
        """
        Tạo bản sao sâu của bàn cờ, 
        bao gồm current_turn, castling_rights, en_passant_target, và grid.
        """
        new_board = Board()
        new_board.current_turn = self.current_turn
        new_board.castling_rights = {
            "white": self.castling_rights["white"].copy(),
            "black": self.castling_rights["black"].copy()
        }
        new_board.en_passant_target = self.en_passant_target
        new_board.grid = []
        for row in self.grid:
            new_row = []
            for cell in row:
                if cell is None:
                    new_row.append(None)
                else:
                    new_row.append(Piece(cell.type, cell.color))
            new_board.grid.append(new_row)
        return new_board
