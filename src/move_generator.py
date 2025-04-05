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
        board[0] = [
            Piece("rook", "black"), Piece("knight", "black"),
            Piece("bishop", "black"), Piece("queen", "black"),
            Piece("king", "black"), Piece("bishop", "black"),
            Piece("knight", "black"), Piece("rook", "black")
        ]
        # Hàng 1: 8 quân pawn đen
        board[1] = [Piece("pawn", "black") for _ in range(8)]
        
        # Hàng 2 đến 5: trống
        for i in range(2, 6):
            board[i] = [None for _ in range(8)]
        
        # Hàng 6: 8 quân pawn trắng
        board[6] = [Piece("pawn", "white") for _ in range(8)]
        
        # Hàng 7: quân trắng
        board[7] = [
            Piece("rook", "white"), Piece("knight", "white"),
            Piece("bishop", "white"), Piece("queen", "white"),
            Piece("king", "white"), Piece("bishop", "white"),
            Piece("knight", "white"), Piece("rook", "white")
        ]
        
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
        Trả về quân cờ tại vị trí được cho (row, col).
        Nếu vị trí ngoài bàn cờ, trả về None.
        """
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None
    
    def set_piece(self, position: tuple, piece: Piece):
        """
        Đặt quân cờ vào vị trí cho trước.
        """
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            self.grid[row][col] = piece
    
    def move_piece(self, start: tuple, end: tuple):
        """
        Di chuyển quân cờ từ vị trí start sang vị trí end.
        Nếu nước đi là en passant, xóa quân bị bắt.
        Nếu nước đi là phong cấp (pawn promotion), tự động nâng cấp thành queen.
        Sau khi di chuyển, cập nhật en passant và quyền nhập thành, rồi đổi lượt đi.
        """
        piece = self.get_piece(start)
        if piece is None:
            raise ValueError("Không có quân ở vị trí bắt đầu!")
        if piece != self.current_turn:
            raise ValueError("Không đúng lượt đi")
        
        # Kiểm tra xem nước đi có phải en passant không:
        is_en_passant = False
        if piece.type == "pawn" and end == self.en_passant_target:
            is_en_passant = True

        # Di chuyển quân
        self.set_piece(end, piece)
        self.set_piece(start, None)
        
        # Nếu en passant, xóa quân tốt bị bắt (nằm ngay sau ô mà tốt di chuyển qua)
        if is_en_passant:
            capture_row = end[0] + (1 if piece.color == "white" else -1)
            self.set_piece((capture_row, end[1]), None)
        
        # Xử lý phong cấp (Pawn Promotion)
        if piece.type == "pawn":
            # Với quân trắng, hàng đích là 0; với quân đen, hàng đích là 7
            if (piece.color == "white" and end[0] == 0) or (piece.color == "black" and end[0] == 7):
                self.promote_pawn(end, "queen")  # Tự động nâng cấp thành queen (có thể mở rộng cho lựa chọn khác)
        
        # Cập nhật en passant (chỉ áp dụng cho quân tốt)
        self.update_en_passant_target(start, end)
        
        # Cập nhật quyền nhập thành
        self.update_castling_rights(start, end)
        
        # Đổi lượt đi
        self.current_turn = "black" if self.current_turn == "white" else "white"
    
    def promote_pawn(self, position: tuple, new_type: str):
        """
        Nâng cấp quân tốt tại vị trí position thành loại new_type (mặc định "queen").
        """
        pawn = self.get_piece(position)
        if pawn and pawn.type == "pawn":
            self.set_piece(position, Piece(new_type, pawn.color))
    
    def update_castling_rights(self, start: tuple, end: tuple):
        """
        Cập nhật quyền nhập thành dựa trên nước đi vừa thực hiện.
        - Nếu quân vua di chuyển, mất cả hai quyền nhập thành.
        - Nếu quân xe di chuyển từ vị trí ban đầu, mất quyền nhập thành tương ứng.
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
                if start == (7, 7):
                    self.castling_rights["white"]["king_side"] = False
                elif start == (7, 0):
                    self.castling_rights["white"]["queen_side"] = False
            else:
                if start == (0, 7):
                    self.castling_rights["black"]["king_side"] = False
                elif start == (0, 0):
                    self.castling_rights["black"]["queen_side"] = False
    
    def update_en_passant_target(self, start: tuple, end: tuple):
        """
        Kiểm tra nếu quân tốt di chuyển 2 ô từ vị trí ban đầu.
        Nếu đúng, thiết lập en_passant_target là ô nằm giữa.
        Nếu không, đặt lại en_passant_target về None.
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
        Kiểm tra xem ô position có bị tấn công bởi quân của màu by_color không.
        Thực hiện bằng cách thay đổi lượt đi tạm thời và gọi generate_moves.
        Lưu ý: Đây không phải là giải pháp tối ưu, nhưng đủ cho mục đích kiểm tra.
        """
        saved_turn = self.current_turn
        self.current_turn = by_color
        from src.move_generator import generate_moves
        enemy_moves = generate_moves(self)
        self.current_turn = saved_turn
        for move in enemy_moves:
            if move[1] == position:
                return True
        return False

    def is_in_check(self, color: str) -> bool:
        """
        Kiểm tra xem vua của màu color có đang bị chiếu không.
        """
        # Tìm vị trí vua
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None and piece.type == "king" and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        if king_pos is None:
            # Nếu không tìm thấy vua, có thể báo lỗi hoặc trả về True
            return True
        # Kiểm tra xem ô vua có bị tấn công không
        enemy_color = "black" if color == "white" else "white"
        return self.is_square_attacked(king_pos, enemy_color)
    
    def is_move_legal(self, move: tuple) -> bool:
        """
        Kiểm tra tính hợp lệ của nước đi move dưới dạng ((row_from, col_from), (row_to, col_to)).
        Thực hiện bằng cách tạo bản sao bàn cờ, thực hiện nước đi và kiểm tra vua của bên đi có bị chiếu không.
        """
        board_copy = self.clone()
        start, end = move
        try:
            board_copy.move_piece(start, end)
        except Exception:
            return False
        # Nước đi hợp lệ nếu vua của bên di chuyển không bị chiếu.
        moving_color = self.get_piece(start).color if self.get_piece(start) else self.current_turn
        return not board_copy.is_in_check(moving_color)
    
    def clone(self):
        """
        Tạo bản sao sâu của đối tượng Board.
        Hữu ích cho việc mô phỏng các nước đi trong thuật toán tìm kiếm.
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

def generate_moves(board: Board) -> list:
    """
    Duyệt qua toàn bộ bàn cờ và gọi hàm sinh nước đi phù hợp cho từng quân
    thuộc lượt hiện tại.
    Trả về danh sách các nước đi dưới dạng tuple:
      - Với các nước đi thông thường: ((row_from, col_from), (row_to, col_to), promotion)
        (promotion là None nếu không phong cấp, hoặc giá trị như "queen")
    """
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.grid[row][col]
            if piece is not None and piece.color == board.current_turn:
                position = (row, col)
                if piece.type == "pawn":
                    moves.extend(generate_moves_for_pawn(board, position))
                elif piece.type == "knight":
                    moves.extend(generate_moves_for_knight(board, position))
                elif piece.type == "bishop":
                    moves.extend(generate_moves_for_bishop(board, position))
                elif piece.type == "rook":
                    moves.extend(generate_moves_for_rook(board, position))
                elif piece.type == "queen":
                    moves.extend(generate_moves_for_queen(board, position))
                elif piece.type == "king":
                    moves.extend(generate_moves_for_king(board, position))
    # Lọc bỏ các nước đi khiến vua bị chiếu
    legal_moves = [move for move in moves if is_move_legal(board, move)]
    return legal_moves


def generate_moves_for_pawn(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân tốt:
      - Di chuyển thẳng 1 ô nếu ô trống.
      - Nếu ở vị trí ban đầu, có thể đi 2 ô nếu cả hai ô đều trống.
      - Bắt quân theo đường chéo.
      - Xử lý en passant nếu board.en_passant_target được thiết lập.
      - Đánh dấu nước đi phong cấp nếu quân tốt di chuyển đến hàng đích.
    Trả về danh sách nước đi dưới dạng tuple: (start, end, promotion),
      với promotion là None nếu không phong cấp, hoặc (ví dụ) "queen" nếu cần phong cấp.
    """
    row, col = position
    moves = []
    direction = -1 if board.current_turn == "white" else 1
    next_row = row + direction

    # Nước đi 1 ô về phía trước nếu ô trống
    if 0 <= next_row < 8 and board.grid[next_row][col] is None:
        # Nếu nước đi đưa tốt đến hàng đích (promotion)
        if (board.current_turn == "white" and next_row == 0) or (board.current_turn == "black" and next_row == 7):
            moves.append((position, (next_row, col), "queen"))
        else:
            moves.append((position, (next_row, col), None))
        
        # Nếu tốt ở vị trí ban đầu, có thể đi 2 ô nếu cả hai ô trống
        if ((board.current_turn == "white" and row == 6) or 
            (board.current_turn == "black" and row == 1)):
            next_row2 = row + 2 * direction
            if board.grid[next_row2][col] is None:
                moves.append((position, (next_row2, col), None))
    
    # Nước đi bắt chéo (bắt quân thông thường hoặc phong cấp khi bắt quân)
    for delta_col in [-1, 1]:
        next_col = col + delta_col
        if 0 <= next_col < 8 and 0 <= next_row < 8:
            target = board.grid[next_row][next_col]
            if target is not None and target.color != board.current_turn:
                if (board.current_turn == "white" and next_row == 0) or (board.current_turn == "black" and next_row == 7):
                    moves.append((position, (next_row, next_col), "queen"))
                else:
                    moves.append((position, (next_row, next_col), None))
    
    # Xử lý en passant:
    if board.en_passant_target is not None:
        ep_row, ep_col = board.en_passant_target
        if ep_row == next_row and (ep_col == col - 1 or ep_col == col + 1):
            moves.append((position, board.en_passant_target, None))
    
    return moves


def generate_moves_for_knight(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân mã theo hình "L".
    """
    moves = []
    row, col = position
    knight_moves = [
        (row - 2, col - 1), (row - 2, col + 1),
        (row - 1, col - 2), (row - 1, col + 2),
        (row + 1, col - 2), (row + 1, col + 2),
        (row + 2, col - 1), (row + 2, col + 1)
    ]
    for new_row, new_col in knight_moves:
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            target = board.grid[new_row][new_col]
            if target is None or target.color != board.current_turn:
                moves.append((position, (new_row, new_col), None))
    return moves


def generate_moves_for_bishop(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân tượng di chuyển theo đường chéo cho đến khi bị cản.
    """
    moves = []
    row, col = position
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            target = board.grid[new_row][new_col]
            if target is None:
                moves.append((position, (new_row, new_col), None))
            elif target.color != board.current_turn:
                moves.append((position, (new_row, new_col), None))
                break
            else:
                break
            new_row += d_row
            new_col += d_col
    return moves


def generate_moves_for_rook(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân xe di chuyển theo đường ngang và dọc.
    """
    moves = []
    row, col = position
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            target = board.grid[new_row][new_col]
            if target is None:
                moves.append((position, (new_row, new_col), None))
            elif target.color != board.current_turn:
                moves.append((position, (new_row, new_col), None))
                break
            else:
                break
            new_row += d_row
            new_col += d_col
    return moves


def generate_moves_for_queen(board: Board, position: tuple) -> list:
    """
    Nước đi của quân hậu là sự kết hợp của nước đi của xe và tượng.
    """
    return generate_moves_for_rook(board, position) + generate_moves_for_bishop(board, position)


def generate_moves_for_king(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân vua di chuyển 1 ô theo mọi hướng.
    Bao gồm cả nước đi nhập thành nếu thỏa mãn các điều kiện (đầy đủ):
      - Vua không bị chiếu trước khi nhập thành.
      - Các ô mà vua đi qua và ô đích không bị tấn công.
    """
    moves = []
    row, col = position
    # Nước đi thông thường: di chuyển 1 ô theo mọi hướng
    for d_row in [-1, 0, 1]:
        for d_col in [-1, 0, 1]:
            if d_row == 0 and d_col == 0:
                continue
            new_row, new_col = row + d_row, col + d_col
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board.grid[new_row][new_col]
                if target is None or target.color != board.current_turn:
                    moves.append((position, (new_row, new_col), None))
    
    # Nhập thành (Castling)
    # Xét các điều kiện:
    # 1. Vua không ở trạng thái chiếu.
    # 2. Các ô mà vua đi qua (và ô đích) không bị tấn công.
    # 3. Các ô giữa vua và xe phải trống.
    enemy_color = "black" if board.current_turn == "white" else "white"
    if board.current_turn == "white" and position == (7, 4):
        if not board.is_in_check("white"):
            # Nhập thành bên vua (kingside)
            if board.castling_rights["white"]["king_side"]:
                if (board.grid[7][5] is None and board.grid[7][6] is None and
                    not board.is_square_attacked((7, 5), enemy_color) and
                    not board.is_square_attacked((7, 6), enemy_color)):
                    moves.append((position, (7, 6), None))
            # Nhập thành bên hậu (queenside)
            if board.castling_rights["white"]["queen_side"]:
                if (board.grid[7][1] is None and board.grid[7][2] is None and board.grid[7][3] is None and
                    not board.is_square_attacked((7, 3), enemy_color) and
                    not board.is_square_attacked((7, 2), enemy_color)):
                    moves.append((position, (7, 2), None))
    elif board.current_turn == "black" and position == (0, 4):
        if not board.is_in_check("black"):
            # Nhập thành bên vua (kingside)
            if board.castling_rights["black"]["king_side"]:
                if (board.grid[0][5] is None and board.grid[0][6] is None and
                    not board.is_square_attacked((0, 5), enemy_color) and
                    not board.is_square_attacked((0, 6), enemy_color)):
                    moves.append((position, (0, 6), None))
            # Nhập thành bên hậu (queenside)
            if board.castling_rights["black"]["queen_side"]:
                if (board.grid[0][1] is None and board.grid[0][2] is None and board.grid[0][3] is None and
                    not board.is_square_attacked((0, 3), enemy_color) and
                    not board.is_square_attacked((0, 2), enemy_color)):
                    moves.append((position, (0, 2), None))
    
    return moves
    
def is_move_legal(board: Board, move: tuple) -> bool:
    """
    Kiểm tra tính hợp lệ của nước đi move dưới dạng ((row_from, col_from), (row_to, col_to), promotion).
    Thực hiện bằng cách tạo bản sao bàn cờ, thực hiện nước đi và kiểm tra rằng vua bên đi không bị chiếu.
    """
    board_copy = board.clone()
    start, end, *promotion = move
    moving_color = board.current_turn
    try:
        board_copy.move_piece(start, end)
    except Exception:
        return False
    return not board_copy.is_in_check(moving_color)

