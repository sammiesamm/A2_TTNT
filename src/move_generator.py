# src/move_generator.py

from .board import Board, Piece

def generate_pseudolegal_moves(board: Board) -> list:
    """
    Sinh tất cả các nước đi (pseudo-legal) dựa trên trạng thái bàn cờ và lượt đi hiện tại,
    KHÔNG loại bỏ nước đi làm vua bị chiếu.

    Trả về danh sách nước đi:
      (start, end, promotion)
    với promotion là None nếu không có phong cấp, hoặc "queen" nếu cần phong cấp.
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
    return moves


def generate_moves(board: Board) -> list:
    """
    Sinh nước đi HỢP LỆ bằng cách lọc các nước đi pseudo-legal qua hàm is_move_legal.
    
    Trả về danh sách nước đi (start, end, promotion).
    """
    pseudo_moves = generate_pseudolegal_moves(board)
    legal_moves = [move for move in pseudo_moves if is_move_legal(board, move)]
    return legal_moves


def generate_moves_for_pawn(board: Board, position: tuple) -> list:
    """
    Sinh nước đi cho quân tốt:
      - Đi thẳng 1 ô/2 ô nếu trống (nếu ở vị trí ban đầu).
      - Bắt chéo quân đối phương.
      - Xử lý en passant (nếu có board.en_passant_target).
      - Đánh dấu phong cấp với promotion='queen' nếu đến hàng cuối.
    
    Trả về [(start, end, promotion), ...]
    """
    row, col = position
    moves = []
    direction = -1 if board.current_turn == "white" else 1
    next_row = row + direction

    # Di chuyển 1 ô
    if 0 <= next_row < 8 and board.grid[next_row][col] is None:
        # Phong cấp khi đến hàng cuối
        if (board.current_turn == "white" and next_row == 0) or (board.current_turn == "black" and next_row == 7):
            moves.append((position, (next_row, col), "queen"))
        else:
            moves.append((position, (next_row, col), None))
        
        # Đi 2 ô nếu ở vị trí ban đầu
        if ((board.current_turn == "white" and row == 6) or 
            (board.current_turn == "black" and row == 1)):
            next_row2 = row + 2 * direction
            if board.grid[next_row2][col] is None:
                moves.append((position, (next_row2, col), None))
    
    # Bắt chéo
    for delta_col in [-1, 1]:
        next_col = col + delta_col
        if 0 <= next_col < 8 and 0 <= next_row < 8:
            target = board.grid[next_row][next_col]
            if target is not None and target.color != board.current_turn:
                if (board.current_turn == "white" and next_row == 0) or (board.current_turn == "black" and next_row == 7):
                    moves.append((position, (next_row, next_col), "queen"))
                else:
                    moves.append((position, (next_row, next_col), None))
    
    # En passant
    if board.en_passant_target is not None:
        ep_row, ep_col = board.en_passant_target
        if ep_row == next_row and abs(ep_col - col) == 1:
            moves.append((position, board.en_passant_target, None))
    
    return moves


def generate_moves_for_knight(board: Board, position: tuple) -> list:
    """
    Quân mã: di chuyển theo hình L.
    """
    moves = []
    row, col = position
    knight_steps = [
        (row - 2, col - 1), (row - 2, col + 1),
        (row - 1, col - 2), (row - 1, col + 2),
        (row + 1, col - 2), (row + 1, col + 2),
        (row + 2, col - 1), (row + 2, col + 1)
    ]
    for nr, nc in knight_steps:
        if 0 <= nr < 8 and 0 <= nc < 8:
            target = board.grid[nr][nc]
            if target is None or target.color != board.current_turn:
                moves.append((position, (nr, nc), None))
    return moves


def generate_moves_for_bishop(board: Board, position: tuple) -> list:
    """
    Quân tượng: di chuyển đường chéo đến khi bị cản.
    """
    moves = []
    row, col = position
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            target = board.grid[nr][nc]
            if target is None:
                moves.append((position, (nr, nc), None))
            elif target.color != board.current_turn:
                moves.append((position, (nr, nc), None))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def generate_moves_for_rook(board: Board, position: tuple) -> list:
    """
    Quân xe: di chuyển ngang dọc đến khi bị cản.
    """
    moves = []
    row, col = position
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            target = board.grid[nr][nc]
            if target is None:
                moves.append((position, (nr, nc), None))
            elif target.color != board.current_turn:
                moves.append((position, (nr, nc), None))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def generate_moves_for_queen(board: Board, position: tuple) -> list:
    """
    Quân hậu = kết hợp nước đi xe + tượng.
    """
    return generate_moves_for_rook(board, position) + generate_moves_for_bishop(board, position)


def generate_moves_for_king(board: Board, position: tuple) -> list:
    """
    Quân vua: di chuyển 1 ô mọi hướng, kiểm tra nhập thành.
    """
    moves = []
    row, col = position
    # Di chuyển 1 ô
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.grid[nr][nc]
                if target is None or target.color != board.current_turn:
                    moves.append((position, (nr, nc), None))
    
    # Nhập thành (castling)
    # Kiểm tra vua không bị chiếu, ô qua lại không bị tấn công, ô giữa vua và xe phải trống.
    enemy_color = "black" if board.current_turn == "white" else "white"
    if board.current_turn == "white" and position == (7, 4):
        # if not board.is_in_check("white"):
            # Castling kingside
            if board.castling_rights["white"]["king_side"]:
                if (board.grid[7][5] is None and board.grid[7][6] is None and
                    not board.is_square_attacked((7, 5), enemy_color) and
                    not board.is_square_attacked((7, 6), enemy_color)):
                    moves.append((position, (7, 6), None))
            # Castling queenside
            if board.castling_rights["white"]["queen_side"]:
                if (board.grid[7][1] is None and board.grid[7][2] is None and board.grid[7][3] is None and
                    not board.is_square_attacked((7, 3), enemy_color) and
                    not board.is_square_attacked((7, 2), enemy_color)):
                    moves.append((position, (7, 2), None))
    elif board.current_turn == "black" and position == (0, 4):
        # if not board.is_in_check("black"):
            # Castling kingside
            if board.castling_rights["black"]["king_side"]:
                if (board.grid[0][5] is None and board.grid[0][6] is None and
                    not board.is_square_attacked((0, 5), enemy_color) and
                    not board.is_square_attacked((0, 6), enemy_color)):
                    moves.append((position, (0, 6), None))
            # Castling queenside
            if board.castling_rights["black"]["queen_side"]:
                if (board.grid[0][1] is None and board.grid[0][2] is None and board.grid[0][3] is None and
                    not board.is_square_attacked((0, 3), enemy_color) and
                    not board.is_square_attacked((0, 2), enemy_color)):
                    moves.append((position, (0, 2), None))
    
    return moves


def is_move_legal(board: Board, move: tuple) -> bool:
    """
    Kiểm tra tính hợp lệ của nước đi move (start, end, promotion).
    Tạo clone bàn cờ, thực hiện move_piece, rồi kiểm tra vua của bên đi có bị chiếu không.
    """
    board_copy = board.clone()
    start, end, *promotion = move
    moving_color = board.current_turn

    # Thử di chuyển
    try:
        board_copy.move_piece(start, end)
    except Exception:
        return False
    
    # Vua của bên moving_color không bị chiếu
    return not board_copy.is_in_check(moving_color)
