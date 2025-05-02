from heuristic import AIEngine

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
        

class AI:
    def __init__(self, gs, turn):
        self.brk=False
        self.gs = gs
        self.engine = AIEngine(turn)
        self.turn =turn

    def minimax_ab_tree(self, depth, alpha, beta, is_maximizing, last_move=None):
        """
        Hàm minimax kết hợp alpha-beta pruning, xây dựng cây tìm kiếm.
        Trả về: (đánh giá, chuỗi nước đi từ node này, tree_node)
        """
        if self.brk: return None,None,None
        node_name = last_move if last_move else "Root"
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
                if alpha >= beta: 
                    tree_node.pruned = True
                    break
                self.gs.makeMove(move)
                child_eval, child_moves, child_node = self.minimax_ab_tree(depth - 1, alpha, beta, False, move)
                self.gs.undoMove()
                if child_eval is None: return None,None,None
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
                if beta <= alpha:  
                    tree_node.pruned = True
                    break
                self.gs.makeMove(move)
                child_eval, child_moves, child_node = self.minimax_ab_tree(depth - 1, alpha, beta, True, move)
                self.gs.undoMove()
                if child_eval is None: return None,None,None
                tree_node.add_child(child_node)
                if child_eval < min_eval:
                    min_eval = child_eval
                    best_moves = [move] + child_moves

                beta = min(beta, child_eval)
                tree_node.beta = beta

            tree_node.value = min_eval if min_eval != float('inf') else beta
            return tree_node.value, best_moves, tree_node

    # def iterative_deepening_tree(self, max_depth):
    #     """
    #     Hàm iterative deepening kết hợp in cây tìm kiếm dạng cấu trúc.
    #     Sau mỗi độ sâu, chờ người dùng bấm Enter để hiển thị cây tìm kiếm.
    #     """
       
    #     best_move = None
    #     is_maximizing = True if self.gs.getTurn() == self.turn else False
    #     best_eval = float('-inf') if is_maximizing else float('inf')
    #     depth_reached = 0
    #     for depth in range(1, max_depth + 1):
    #         eval_val, moves, tree = self.minimax_ab_tree(depth, float('-inf'), float('inf'), is_maximizing)
    #         if eval_val is None: 
    #             return None,None,None
    #         if moves:
    #             if (is_maximizing and eval_val > best_eval) or (not is_maximizing and eval_val < best_eval):
    #                 best_eval = eval_val
    #                 best_move = moves[0]
    #         depth_reached = depth
    #     return best_move, best_eval, depth_reached
    
    def iterative_deepening_tree(self, max_depth):
        """
        Hàm iterative deepening kết hợp in cây tìm kiếm dạng cấu trúc.
        Sau mỗi độ sâu, chờ người dùng bấm Enter để hiển thị cây tìm kiếm.
        """
       
        best_move = None
        is_maximizing = True if self.gs.getTurn() == self.turn else False
        best_eval = float('-inf') if is_maximizing else float('inf')
        eval_val, moves, _ = self.minimax_ab_tree( max_depth, float('-inf'), float('inf'), is_maximizing)
        if eval_val is None: 
            return None,None,None
        if moves:
            if (is_maximizing and eval_val > best_eval) or (not is_maximizing and eval_val < best_eval):
                best_eval = eval_val
                best_move = moves[0]
        return best_move, best_eval, max_depth


