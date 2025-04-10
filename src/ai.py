import chess
import time
import math

from ChessEngine import GameState
from heuristic import AIEngine

# Định nghĩa giá trị của từng quân cờ
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

# -------- Piece-Square Tables (đánh giá vị trí) --------
pawn_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    0.1, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.1,
    0.05, 0.05, 0.1, 0.2, 0.2, 0.1, 0.05, 0.05,
    0, 0, 0, 0, 0, 0, 0, 0,
    -0.05,-0.05,-0.1,-0.2,-0.2,-0.1,-0.05,-0.05,
    -0.1,-0.1,-0.2,-0.3,-0.3,-0.2,-0.1,-0.1,
    0, 0, 0, 0, 0, 0, 0, 0
]

knight_table = [
    -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5,
    -0.4, -0.2,  0,    0,    0,    0,   -0.2, -0.4,
    -0.3,  0,    0.1,  0.15, 0.15, 0.1,   0,    -0.3,
    -0.3,  0.05, 0.15, 0.2,  0.2,  0.15,  0.05, -0.3,
    -0.3,  0,    0.15, 0.2,  0.2,  0.15,  0,    -0.3,
    -0.3,  0.05, 0.1,  0.15, 0.15, 0.1,   0.05, -0.3,
    -0.4, -0.2,  0,    0.05, 0.05, 0,   -0.2, -0.4,
    -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5
]

bishop_table = [
    -0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2,
    -0.1,  0,    0,    0,    0,    0,    0,   -0.1,
    -0.1,  0,    0.05, 0.1,  0.1,  0.05, 0,   -0.1,
    -0.1,  0.05, 0.1,  0.1,  0.1,  0.1,  0.05,-0.1,
    -0.1,  0,    0.1,  0.1,  0.1,  0.1,  0,   -0.1,
    -0.1,  0.05, 0.05, 0.1,  0.1,  0.05, 0.05,-0.1,
    -0.1,  0,    0,    0,    0,    0,    0,   -0.1,
    -0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2
]

rook_table = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05,
    -0.05, 0, 0, 0, 0, 0, 0, -0.05,
    -0.05, 0, 0, 0, 0, 0, 0, -0.05,
    -0.05, 0, 0, 0, 0, 0, 0, -0.05,
    -0.05, 0, 0, 0, 0, 0, 0, -0.05,
    -0.05, 0, 0, 0, 0, 0, 0, -0.05,
    0, 0, 0, 0.05, 0.05, 0, 0, 0
]

queen_table = [
    -0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2,
    -0.1,  0,    0,    0,     0,     0,    0,   -0.1,
    -0.1,  0,    0.05, 0.05,  0.05,  0.05, 0,   -0.1,
    -0.05, 0,    0.05, 0.05,  0.05,  0.05, 0,   -0.05,
    0,     0,    0.05, 0.05,  0.05,  0.05, 0,   -0.05,
    -0.1,  0.05, 0.05, 0.05,  0.05,  0.05, 0,   -0.1,
    -0.1,  0,    0.05, 0,     0,     0,    0,   -0.1,
    -0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2
]

king_table = [
    -0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3,
    -0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3,
    -0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3,
    -0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3,
    -0.2, -0.3, -0.3, -0.4, -0.4, -0.3, -0.3, -0.2,
    -0.1, -0.2, -0.2, -0.3, -0.3, -0.2, -0.2, -0.1,
    0.2,  0.2,  0,     0,    0,    0,    0.2,  0.2,
    0.2,  0.3,  0.3,   0,    0,    0,    0.3,  0.2
]

piece_square_tables = {
    chess.PAWN: pawn_table,
    chess.KNIGHT: knight_table,
    chess.BISHOP: bishop_table,
    chess.ROOK: rook_table,
    chess.QUEEN: queen_table,
    chess.KING: king_table
}

# Định nghĩa cấu trúc nút trong cây tìm kiếm
class TreeNode:
    def __init__(self, name, value=None, alpha=None, beta=None, pruned=False):
        self.name = name         # tên node: nước đi dạng UCI hoặc 'Root'
        self.value = value       # giá trị tạm thời (static evaluation hoặc từ minimax)
        self.alpha = alpha       # giá trị alpha tại node
        self.beta = beta         # giá trị beta tại node
        self.pruned = pruned     # đánh dấu nếu nhánh này đã bị cắt tỉa
        self.children = []       # danh sách các node con

    def add_child(self, child):
        self.children.append(child)
        
    # def print_tree(node, prefix=""):
    #     pruned_mark = " ✂" if node.pruned else ""
    #     line = f"{node.name}{pruned_mark} ({node.value}, {node.alpha}, {node.beta})"
    #     print(prefix + line)
        
    #     if node.children:
    #         child_count = len(node.children)
    #         for i, child in enumerate(node.children):
    #             child_prefix = prefix + "   \\- " if i == child_count - 1 else prefix + "   |- "
    #             print_tree(child, prefix=child_prefix)

class AI:
    def __init__(self, gs, turn):
        self.gs = gs
        self.engine = AIEngine(turn)
        
    # -------- Hàm đánh giá cải tiến --------
    # def improved_evaluation(self):
    #     """
    #     Kết hợp các yếu tố: vật chất, kiểm soát trung tâm, khả năng di chuyển, an toàn vua và bonus vị trí từ piece-square tables.
    #     """
    #     # Đầu tiên dùng hàm static_evaluation như cơ sở
    #     value = self.engine.evaluation(self.gs)
        
    #     # Bonus theo piece-square tables
    #     for square in chess.SQUARES:
    #         piece = board.piece_at(square)
    #         if piece:
    #             # Với quân trắng, lấy trực tiếp; với quân đen, dùng hàm square_mirror để lật bảng
    #             bonus = piece_square_tables[piece.piece_type][square] if piece.color == chess.WHITE else piece_square_tables[piece.piece_type][chess.square_mirror(square)]
    #             if piece.color == chess.WHITE:
    #                 value += bonus
    #             else:
    #                 value -= bonus
    #     return value

    # def static_evaluation(self):
    #     value = 0

    #     # 1. Material evaluation
    #     for piece_type in PIECE_VALUES:
    #         value += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
    #         value -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]

    #     # 2. Center control
    #     center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    #     center_bonus = 0.3
    #     for square in center_squares:
    #         piece = board.piece_at(square)
    #         if piece:
    #             if piece.color == chess.WHITE:
    #                 value += center_bonus
    #             else:
    #                 value -= center_bonus

    #     # 3. Mobility
    #     mobility_factor = 0.1
    #     # Số nước đi của bên đang đi
    #     current_moves = len(list(board.legal_moves))
    #     # Sử dụng null move để đếm nước đi của đối thủ
    #     board.push(chess.Move.null())
    #     opponent_moves = len(list(board.legal_moves))
    #     board.pop()
    #     value += mobility_factor * (current_moves - opponent_moves)

    #     # 4. King safety
    #     king_safety_penalty = 0.5
    #     white_king_square = board.king(chess.WHITE)
    #     black_king_square = board.king(chess.BLACK)
    #     if white_king_square and board.is_attacked_by(chess.BLACK, white_king_square):
    #         value -= king_safety_penalty
    #     if black_king_square and board.is_attacked_by(chess.WHITE, black_king_square):
    #         value += king_safety_penalty

    #     # 5. Checkmate (trường hợp chiếu hết)
    #     if board.is_checkmate():
    #         if board.turn == chess.WHITE:
    #             return -9999
    #         else:
    #             return 9999

    #     return value

    # -------- Quiescence Search --------
    # def quiescence_search(self, alpha, beta):
    #     """
    #     Mở rộng tìm kiếm ở các nước bắt quân nhằm loại bỏ các động thái biến động.
    #     """
    #     stand_pat = self.engine.evaluation(self.gs)
    #     if stand_pat >= beta:
    #         return beta, []
    #     if alpha < stand_pat:
    #         alpha = stand_pat

    #     best_move_seq = []
    #     for move in self.gs.getValidMoves():
    #         # Xét các nước bắt quân (có thể mở rộng thêm kiểm tra check, ...)
    #         if board.is_capture(move):
    #             board.push(move)
    #             score, move_seq = self.quiescence_search(self.gs.board, -beta, -alpha)
    #             score = -score
    #             board.pop()
    #             if score >= beta:
    #                 return beta, [move.uci()] + move_seq
    #             if score > alpha:
    #                 alpha = score
    #                 best_move_seq = [move.uci()] + move_seq
    #     return alpha, best_move_seq

    def move_to_coords(move):
        def pos_to_coord(pos):
            col = ord(pos[0]) - ord('a')       # chuyển 'a'-'h' thành 0-7
            row = 8 - int(pos[1])              # chuyển '1'-'8' thành 7-0
            return (row, col)

        from_pos = move[:2]
        to_pos = move[2:]
        return pos_to_coord(from_pos), pos_to_coord(to_pos)

    def minimax_ab_tree(self, depth, alpha, beta, is_maximizing, last_move=None):
        """
        Hàm minimax kết hợp alpha-beta pruning, xây dựng cây tìm kiếm.
        Trả về: (đánh giá, chuỗi nước đi từ node này, tree_node)
        """
        node_name = last_move.uci() if last_move else "Root"
        tree_node = TreeNode(name=node_name, alpha=alpha, beta=beta)

        if depth == 0 or self.gs.getValidMoves() == []:
            eval_val = self.engine.evaluation(self.gs)
            tree_node.value = eval_val
            move_seq = [last_move] if last_move is not None else []
            return eval_val, move_seq, tree_node

        best_moves = []

        if is_maximizing:
            max_eval = float('-inf')
            for move in self.gs.getValidMoves():
                if alpha >= beta:  # Nếu đã bị cắt tỉa, dừng ngay
                    tree_node.pruned = True
                    break

                self.gs.makeMove(move)
                child_eval, child_moves, child_node = self.minimax_ab_tree(depth - 1, alpha, beta, False, move)
                self.gs.undoMove()

                tree_node.add_child(child_node)
                if child_eval > max_eval:
                    max_eval = child_eval
                    best_moves = [move] + child_moves

                alpha = max(alpha, child_eval)
                tree_node.alpha = alpha

            tree_node.value = max_eval if max_eval != float('-inf') else alpha
            return tree_node.value, best_moves, tree_node

        else:
            min_eval = float('inf')
            for move in self.gs.getValidMoves():
                if beta <= alpha:  # Nếu đã bị cắt tỉa, dừng ngay
                    tree_node.pruned = True
                    break

                self.gs.makeMove(move)
                child_eval, child_moves, child_node = self.minimax_ab_tree(depth - 1, alpha, beta, True, move)
                self.gs.undoMove()

                tree_node.add_child(child_node)
                if child_eval < min_eval:
                    min_eval = child_eval
                    best_moves = [move] + child_moves

                beta = min(beta, child_eval)
                tree_node.beta = beta

            tree_node.value = min_eval if min_eval != float('inf') else beta
            return tree_node.value, best_moves, tree_node

    def iterative_deepening_tree(self, max_depth, time_limit):
        """
        Hàm iterative deepening kết hợp in cây tìm kiếm dạng cấu trúc.
        Sau mỗi độ sâu, chờ người dùng bấm Enter để hiển thị cây tìm kiếm.
        """
        start_time = time.time()
        best_move = None
        is_maximizing = True if self.gs.getTurn() == 'w' else False
        best_eval = float('-inf') if is_maximizing else float('inf')
        depth_reached = 0
        
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > time_limit:
                print(f"Dừng tìm kiếm vì hết thời gian. Độ sâu đạt được: {depth_reached}")
                break
            
            input(f"\nNhấn Enter để xem cây tìm kiếm ở độ sâu {depth}...")
            print(f"\n--- Đang tìm kiếm ở độ sâu {depth} ---")
            
            eval_val, moves, tree = self.minimax_ab_tree(depth, float('-inf'), float('inf'), is_maximizing)
            
            if moves:
                if (is_maximizing and eval_val > best_eval) or (not is_maximizing and eval_val < best_eval):
                    best_eval = eval_val
                    best_move = moves[0]
            
            depth_reached = depth
            print(f"\nĐộ sâu {depth}: Nước đi tốt nhất: {best_move}, Đánh giá: {best_eval}")
            # print("\nCây tìm kiếm:")
            # print_tree(tree)
            
            if not math.isinf(best_eval) and abs(best_eval) > 20000:
                print(f"Đã tìm thấy nước đi chiếu hết ở độ sâu {depth}")
                break
            
        elapsed_time = time.time() - start_time
        print(f"\nTổng thời gian tìm kiếm: {elapsed_time:.2f} giây")
        print(f"Độ sâu đạt được: {depth_reached}")
        best_move = self.move_to_coords(best_move)
        return best_move, best_eval, depth_reached

def get_user_move(board):
    """Hàm yêu cầu người dùng nhập nước đi và kiểm tra tính hợp lệ."""
    while True:
        user_input = input("Nhập nước đi của bạn: ").strip()
        try:
            move = chess.Move.from_uci(user_input)
            if move in board.legal_moves:
                return move
            else:
                print("Nước đi không hợp lệ. Vui lòng nhập lại.")
        except ValueError:
            print("Định dạng không đúng. Vui lòng nhập lại.")

def print_board_with_coords(board):
    """In bàn cờ với tọa độ hàng (1-8) và cột (a-h)."""
    ranks = "87654321"
    files = "abcdefgh"
    
    # Duyệt qua các hàng từ 8 xuống 1
    for rank in ranks:
        row_str = rank + "  "  # In số hàng ở đầu dòng
        for file in files:
            square = chess.parse_square(file + rank)
            piece = board.piece_at(square)
            row_str += (piece.symbol() if piece else ".") + " "
        print(row_str)
    
    # In dòng chữ cái dưới cùng
    print("\n   " + " ".join(files))

# if __name__ == "__main__":
#     board = chess.Board()
    
#     # print("=== Bắt đầu demo cây tìm kiếm của cờ vua ===")
    
#     # # Thiết lập thông số
#     # max_depth = 6
#     # time_limit = 300  # Giới hạn thời gian (giây)
    
#     # best_move, evaluation, depth_reached = iterative_deepening_tree(board, max_depth, time_limit)
    
#     # print("\n=== Kết quả tìm kiếm ===")
#     # print(f"Nước đi tốt nhất: {best_move}")
#     # print(f"Đánh giá: {evaluation}")
#     # print(f"Độ sâu đạt được: {depth_reached}")
    
#     # if best_move:
#     #     move = chess.Move.from_uci(best_move)
#     #     board.push(move)
#     #     print("\nBàn cờ sau khi thực hiện nước đi:")
#     #     print(board)
#     # else:
#     #     print("\nKhông tìm thấy nước đi hợp lệ.")
    
#     print("=== Mini Game Cờ Vua ===")
    
#     # Thiết lập thông số cho AI
#     max_depth = 4
#     time_limit = 300
    
#     # Bắt đầu trò chơi
#     while not board.is_game_over():
#         print("\nBàn cờ hiện tại:")
#         print_board_with_coords(board)
        
#         if board.turn == chess.WHITE:
#             print("\nLượt của người chơi: ")
#             user_move = get_user_move(board)
#             board.push(user_move)
#         else:
#             print("\nLượt của AI:")
#             best_move, evaluation, depth_reached = iterative_deepening_tree(board, max_depth, time_limit)
#             if best_move:
#                 move = chess.Move.from_uci(best_move)
#                 board.push(move)
#                 print(f"AI chọn nước đi: {best_move} với đánh giá: {evaluation}")
#             else:
#                 print("AI không tìm được nước đi hợp lệ.")
#                 break
    
#     print("\n=== Trò chơi kết thúc ===")
#     print(board)
#     result = board.result()
#     print("Kết quả:", result)