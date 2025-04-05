


class Rule:
    def BPAWN(pos,board,state):
        lst=[]
        x,y=pos
        if y+1 < 8 and board[x+1][y+1] is not None:
            if  board[x+1][y+1].getState() != state: lst+=[(x+1,y+1)]
        if y+1 >=0 and board[x+1][y-1] is not None:
            if  board[x+1][y-1].getState() != state: lst+=[(x+1,y-1)]
        if  board[x+1][y] is None:
            lst+=[(x+1,y)]
            if board[x+2][y] is None and x==1: lst+=[(x+2,y)]
        return lst
    def WPAWN(pos,board,state):
        lst=[]
        x,y=pos
        if y+1 < 8 and board[x-1][y+1] is not None:
            if  board[x-1][y+1].getState() != state: lst+=[(x-1,y+1)]
        if  y+1 >= 0 and board[x-1][y-1] is not None:
            if  board[x-1][y-1].getState() != state: lst+=[(x-1,y-1)]
        if  board[x-1][y] is None:
            lst+=[(x-1,y)]
            if board[x-2][y] is None and x==6: lst+=[(x-2,y)]
        return lst
    def ROOK(pos,board,state):
        lst=[]
        x,y=pos
        for i in range(x+1,8):
            if board[i][y] is not None:
                stt=board[i][y].getState()
                if stt==state: break
                else:
                    lst+=[(i,y)]
                    break
            else: lst+=[(i,y)]
        for i in range(x-1,-1,-1):
            if board[i][y] is not None:
                stt=board[i][y].getState()
                if stt==state: break
                else:
                    lst+=[(i,y)]
                    break
            else: lst+=[(i,y)]   
        for i in range(y+1,8):
            if board[x][i] is not None:
                stt=board[x][i].getState()
                if stt==state: break
                else:
                    lst+=[(x,i)]
                    break
            else: lst+=[(x,i)]
        for i in range(y-1,-1,-1):
            if board[x][i] is not None:
                stt=board[x][i].getState()
                if stt==state: break
                else:
                    lst+=[(x,i)]
                    break
            else: lst+=[(x,i)] 
        return lst
    
    def KNIGH(pos,board,state):
        x,y=pos
        lst=[(x+2,y-1),(x-1,y-2),(x+2,y+1),(x-1,y+2),(x-2,y-1),(x+1,y-2),(x-2,y+1),(x+1,y+2)]
        def check(pos):
            x,y=pos
            if x<0 or y<0 or y>7 or x>7: return False
            piece=board[x][y]
            if piece is not None and piece.getState()==state: return False
            return True
        return list(filter(check,lst))
    def BISHOP(pos,board,state):
        x,y=pos
        lst=[]
        def check(x,y):
            if x<0 or y<0 or y>7 or x>7: return 0
            piece=board[x][y]
            if piece is not None:
                if piece.getState()==state: return 0
                else: return 1
            return 2
        for i in range(1,8):
            match check(x+i,y+i):
                case 0: break
                case 1:
                    lst+=[(x+i,y+i)]
                    break
                case 2:lst+=[(x+i,y+i)]
        for i in range(1,8):
            match check(x+i,y-i):
                case 0: break
                case 1:
                    lst+=[(x+i,y-i)]
                    break
                case 2:lst+=[(x+i,y-i)]
        for i in range(1,8):
            match check(x-i,y+i):
                case 0: break
                case 1:
                    lst+=[(x-i,y+i)]
                    break
                case 2:lst+=[(x-i,y+i)]
        for i in range(1,8):
            match check(x-i,y-i):
                case 0: break
                case 1:
                    lst+=[(x-i,y-i)]
                    break
                case 2:lst+=[(x-i,y-i)]
        return lst
    def QUEEN(pos,board,state):
        return Rule.BISHOP(pos,board,state)+Rule.ROOK(pos,board,state)
    def KING(pos,board,state):
        x,y=pos
        lst=[(x+1,y-1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x-1,y),(x+1,y),(x,y+1),(x,y-1)]
        def check(pos):
            x,y=pos
            if x<0 or y<0 or y>7 or x>7: return False
            piece=board[x][y]
            if piece is not None and piece.getState()==state: return False
            return True
        return list(filter(check,lst))
class Board:
    def __init__(self):
        
        self.B=[ ChessPiece("BR",(0,0),Rule.ROOK, 2),
                 ChessPiece("BN",(0,1),Rule.KNIGH, 2),
                 ChessPiece("BB",(0,2),Rule.BISHOP, 2),
                 ChessPiece("BQ",(0,3),Rule.QUEEN, 2),
                 ChessPiece("BK",(0,4),Rule.KING, 2),
                 ChessPiece("BB",(0,5),Rule.BISHOP, 2),
                 ChessPiece("BN",(0,6),Rule.KNIGH, 2),
                 ChessPiece("BR",(0,7),Rule.ROOK, 2),
                 ChessPiece("BP",(1,0),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,1),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,2),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,3),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,4),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,5),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,6),Rule.BPAWN, 2),
                 ChessPiece("BP",(1,7),Rule.BPAWN, 2)]
        self.W=[ChessPiece("WR",(7,0),Rule.ROOK, 1),
                 ChessPiece("WN",(7,1),Rule.KNIGH, 1),
                 ChessPiece("WB",(7,2),Rule.BISHOP, 1),
                 ChessPiece("WQ",(7,3),Rule.QUEEN, 1),
                 ChessPiece("WK",(7,4),Rule.KING, 1),
                 ChessPiece("WB",(7,5),Rule.BISHOP, 1),
                 ChessPiece("WN",(7,6),Rule.KNIGH, 1),
                 ChessPiece("WR",(7,7),Rule.ROOK, 1),
                 ChessPiece("WP",(6,0),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,1),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,2),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,3),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,4),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,5),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,6),Rule.WPAWN, 1),
                 ChessPiece("WP",(6,7),Rule.WPAWN, 1)]
        self.board=[[self.B[i] for i in range(8)],
                    [self.B[i] for i in range(8,16)],
                    [None for _ in range(8)],
                    [None for _ in range(8)],
                    [None for _ in range(8)],
                    [None for _ in range(8)],
                    [self.W[i] for i in range(8,16)],
                    [self.W[i] for i in range(8)]
                ]
        for i in self.W+self.B: i.setBoard(self.board)
    def Update(self,piece,pos):
        if piece is None: return False
        if pos in piece.getValidPos():
            x,y=pos
            if self.board[x][y] is not None:
                self.board[x][y].setState(0)
                typ=self.board[x][y].getType()
                self.board[x][y]=piece
                piece_x,piece_y=piece.getPos()
                self.board[piece_x][piece_y]=None
                if typ[1]=='K': 
                    piece.moveTo(pos)
                    return 2
                if piece.getType()[1]=='P' and (x == 0 or x == 7):
                    piece.moveTo(pos)
                    return 3
            else:
                piece_x,piece_y=piece.getPos()
                self.board[x][y],self.board[piece_x][piece_y]=self.board[piece_x][piece_y],self.board[x][y]
            piece.moveTo(pos)
            return 1
        return 0
    def getBlackPieces(self):
        return self.B
    def getWhitePieces(self):
        return self.W
    def getPieces(self,pos):
        x,y=pos
        return self.board[x][y]
    def reset(self):
        self.__init__()
        

class ChessPiece:
    def __init__(self,type,position,get_valid_pos,state):
        self.__type=type
        self.__pos=position
        self.__state=state
        self.__get_valid_pos=get_valid_pos
        self.__board=None
    def setBoard(self,board):
        self.__board=board
    def getPos(self):
        return self.__pos
    def getType(self):
        return self.__type
    def setType(self,type):
        self.__type =type
    def getState(self):
        return self.__state
    def setState(self,val):
        self.__state=val
    def setRule(self,rule):
        self.__get_valid_pos=rule
    def getValidPos(self):
        return self.__get_valid_pos(self.__pos,self.__board,self.__state)
    def moveTo(self,pos):
        self.__pos=pos
