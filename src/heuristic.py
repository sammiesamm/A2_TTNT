
piece_score = {"K": 20000, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}

pawn_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [50, 50, 50, 50, 50, 50, 50, 50],
               [10, 10, 20, 30, 30, 20, 10, 10],
               [5, 5, 10, 25, 25, 10, 5, 5],
               [0, 0, 0, 20, 20, 0, 0, 0],
               [5, -5,-10,  0,  0,-10, -5,  5],
               [5, 10, 10,-20,-20, 10, 10,  5],
               [0, 0, 0, 0, 0, 0, 0, 0]]

knight_scores = [[-50, -40, -30, -30, -30, -30, -40, -50],
                 [-40, -20, 0, 0, 0, 0, -20, -40],
                 [-30, 0, 10, 15, 15, 10, 0, -30],
                 [-30, 5, 15, 20, 20, 15, 5, -30],
                 [-30, 0, 15, 20, 20, 15, 0, -30],
                 [-30, 5, 10, 15, 15, 10, 5, -30],
                 [-40, -20, 0, 5, 5, 0, -20, -40],
                 [-50, -40, -30, -30, -30, -30, -40, -50]]

bishop_scores = [[-20, -10, -10, -10, -10, -10, -10, -20],
                 [-10, 0, 0, 0, 0, 0, 0, -10],
                 [-10, 0, 5, 10, 10, 5, 0, -10],
                 [-10, 5, 5, 10, 10, 5, 5, -10],
                 [-10, 0, 10, 10, 10, 10, 0, -10],
                 [-10, 10, 10, 10, 10, 10, 10, -10],
                 [-10, 5, 0, 0, 0, 0, 5, -10],
                 [-20, -10, -10, -10, -10, -10, -10, -20]]

rook_scores = [[0, 0, 0, 0, 0, 0, 0, 0],
               [5, 10, 10, 10, 10, 10, 10, 5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [-5, 0, 0, 0, 0, 0, 0, -5],
               [0, 0, 0, 5, 5, 0, 0, 0]]

queen_scores = [[-20, -10, -10, -5, -5, -10, -10, -20],
                [-10, 0, 0, 0, 0, 0, 0, -10],
                [-10, 0, 5, 5, 5, 5, 0, -10],
                [-5, 0, 5, 5, 5, 5, 0, -5],
                [0, 0, 5, 5, 5, 5, 0, -5],
                [-10, 5, 5, 5, 5, 5, 0, -10],
                [-10, 0, 5, 0, 0, 0, 0, -10],
                [-20, -10, -10, -5, -5, -10, -10, -20]]

king_middle_score = [[-30, -40, -40, -50, -50, -40, -40, -30],
                     [-30, -40, -40, -50, -50, -40, -40, -30],
                     [-30, -40, -40, -50, -50, -40, -40, -30],
                     [-30, -40, -40, -50, -50, -40, -40, -30],
                     [-20, -30, -30, -40, -40, -30, -30, -20],
                     [-10, -20, -20, -20, -20, -20, -20, -10],
                     [20, 20, 0, 0, 0, 0, 20, 20],
                     [20, 30, 10, 0, 0, 10, 30, 20]]

king_end_score = [[-50, -40, -30, -20, -20, -30, -40, -50],
                  [-30, -20, -10, 0, 0, -10, -20, -30],
                  [-30, -10, 20, 30, 30, 20, -10, -30],
                  [-30, -10, 30, 40, 40, 30, -10, -30],
                  [-30, -10, 30, 40, 40, 30, -10, -30],
                  [-30, -10, 20, 30, 30, 20, -10, -30],
                  [-30, -30, 0, 0, 0, 0, -30, -30],
                  [-50, -30, -30, -30, -30, -30, -30, -50]]

piece_position_scores = {"WN": knight_scores,
                         "BN": knight_scores[::-1],
                         "WB": bishop_scores,
                         "BB": bishop_scores[::-1],
                         "WQ": queen_scores,
                         "BQ": queen_scores[::-1],
                         "WR": rook_scores,
                         "BR": rook_scores[::-1],
                         "WP": pawn_scores,
                         "BP": pawn_scores[::-1],
                         "WK": king_middle_score,
                         'BK': king_middle_score[::-1]
                         }


class AIEngine:
    def __init__(self, aiTurn):
        self.aiTurn = aiTurn
        self.bestMove = None
        self.total_nodes = 0
        self.total_branch_cutoff = 0
        self.total_nodes_leaf = 0
        self.maxScore = 0
        self.executionTime = 0
        self.algoSearch = 'Alpha Beta'
        self.isEndGame = False
        self.timeGenerateMoves = 0
        
    def __checkEndGame(self,gs):
        if gs.piece_ingame['WQ'] == 0 and gs.piece_ingame['BQ'] == 0:
            return True
        if gs.piece_ingame['WQ'] == 1 and gs.piece_ingame['BQ'] == 1:
            white_minor_piece = 0
            black_minor_piece = 0
            for u, v in gs.piece_ingame.items():
                if u[1] == 'N' or u[1] == 'B':
                    if u[0] == 'W':
                        white_minor_piece += v
                    else:
                        black_minor_piece += v
            if white_minor_piece <= 1 and black_minor_piece <= 1:
                return True

        return False

    # Heuristic 1
    @staticmethod
    def getMaterialScore(gs):
        white_score = 0
        black_score = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                piece = gs.board[row][col]
                if piece != "--":
                    if piece[0] == "W":
                        white_score += piece_score[piece[1]]
                    else:
                        black_score += piece_score[piece[1]]
        return black_score - white_score

    # Heuristic 2
    def getPiecePositionScore(self, gs):
        score = 0
        if self.isEndGame:
            piece_position_scores['WK'] = king_end_score
            piece_position_scores['BK'] = king_end_score[::-1]
        else:
            piece_position_scores['WK'] = king_middle_score
            piece_position_scores['BK'] = king_middle_score[::-1]

        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                piece = gs.board[row][col]
                if piece != "--":
                    if piece[0] == "B":
                        score += piece_position_scores[piece][row][col]
                    else:
                        score -= piece_position_scores[piece][row][col]
        return score
    def evaluation(self, gs):
        self.__checkEndGame(gs)
        if self.aiTurn == 'B':
            score = self.getPiecePositionScore(gs) + AIEngine.getMaterialScore(gs)
        else:
            score = - self.getPiecePositionScore(gs) - AIEngine.getMaterialScore(gs)
        return score
