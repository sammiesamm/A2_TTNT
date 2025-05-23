import pygame as pg
from pygame.locals import *
from ai import  AI
from ChessEngine import GameState,Move
from random import randint
import threading
from copy import deepcopy
import os 
class ChessUI:
    def __init__(self):
        class Player:
            def __init__(self,gs:GameState):
                self.gs=gs
                self.last_move=None
                self.check=False
            def Act(self,turn,events=None): return 1
            def reset(self):
                self.last_move=None
                self.check=False
        class Human(Player):
            def __init__(self,gs,size):
                super().__init__(gs)
                self.pickup=None
                self.size=size
                self.promove=None
            def Act(self,turn,events):
                pos=None
                list_move =self.gs.getValidMoves()
                if len(list_move)==0: return 2
                for event in events:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        pos=tuple(map(lambda x:x//(self.size//8),pg.mouse.get_pos()))[::-1]
                        piece=self.gs.board[pos[0]][pos[1]]
                        if self.pickup is None:
                            if piece ==  '--':
                                self.pickup=None
                            elif turn==piece[0]:
                                self.pickup=pos
                        else: 
                            ppos=self.pickup
                            self.pickup=None
                            temp=Move(ppos,pos,self.gs.board)
                            for move in list_move:
                                if move == temp:
                                    if move.isPawnPromotion:
                                        self.promove=move
                                        self.last_move=move
                                        return 3
                                    self.last_move=move
                                    reval= self.gs.makeMove(move)
                                    _,self.check=self.gs._getPinAndCheckPieces()
                                    return reval
                                
                return None
            def reset(self):
                super().reset()
                self.pickup=None
        class Bot(Player):
            def __init__(self,gs,turn):
                super().__init__(gs)
                self.mode=1
                self.ai=AI(self.gs,turn)
                self.thread=None
            def setmode(self,Mode):
                self.mode=Mode
                self.reset()
            def _act(self):
                move,_,_=self.ai.iterative_deepening_tree(self.mode+1)
                self.last_move=move
            def Act(self,turn,events=None):
                if self.thread==None:
                    self.thread=threading.Thread(target=self._act)
                    self.thread.start()
                else:
                    if self.thread.is_alive(): return 0
                    self.thread=None
                    if self.gs.makeMove(self.last_move) ==0: reval= 2
                    else: reval= 1
                    _,self.check=self.gs._getPinAndCheckPieces()
                    return reval   
            def reset(self):
                super().reset()
                if self.thread != None:
                    while self.thread.is_alive(): self.ai.brk=True
                self.ai.brk=False
                self.thread=None   
        class RandomBot(Player):
            def __init__(self,gs):
                super().__init__(gs)
                self.thread=None
            def _act(self):
                pg.time.delay(500)
            def Act(self,turn,events=None):
                if self.thread==None:
                    self.thread=threading.Thread(target=self._act)
                    self.thread.start()
                else:
                    if self.thread.is_alive(): return 0
                    list_move =self.gs.getValidMoves()
                    self.thread=None
                    if len(list_move)==0: return 2
                    move=list_move[randint(0,len(list_move)-1)]
                    self.last_move=move
                    reval= self.gs.makeMove(move)
                    _,self.check=self.gs._getPinAndCheckPieces()
                    return reval
            def reset(self):
                super().reset()
                self.thread=None   
        pg.init()
        self.clock = pg.time.Clock()
        
        self.WIDTH=int(pg.display.get_desktop_sizes()[0][1]*0.9)
        self.screen = pg.display.set_mode((self.WIDTH, self.WIDTH))
        pg.display.set_caption("Chess")
    
        self.square_size = self.WIDTH // 8
    
        self.pieces=['BR','BN','BB','BQ','BK','BP','WR','WN','WB','WQ','WK','WP']   
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.pieces=dict(map(lambda x:(x,pg.transform.smoothscale(pg.image.load(BASE_DIR+ "/chesspieces/"+x+".png"),(self.square_size,self.square_size))),self.pieces))
        self.font = pg.font.SysFont("arial", self.WIDTH//10)
        self.font1 = pg.font.SysFont("arial", self.WIDTH//20)
        self.rect=[Rect(self.WIDTH*0.3,1*self.WIDTH/10+self.WIDTH/4,self.WIDTH*0.4,self.WIDTH/14),
                   Rect(self.WIDTH*0.3,2*self.WIDTH/10+self.WIDTH/4,self.WIDTH*0.4,self.WIDTH/14),
                   Rect(self.WIDTH*0.3,3*self.WIDTH/10+self.WIDTH/4,self.WIDTH*0.4,self.WIDTH/14),
                   Rect(self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(2*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(3*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(4*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   ]
        self.gs=GameState('W')
        self.board=deepcopy(self.gs.board)
        self.players=[Human(self.gs,self.WIDTH),Bot(self.gs,'W'),Bot(self.gs,'B'),RandomBot(self.gs)]
        self.player1=self.players[0]
        self.player2=self.players[0]
        self.turn=True
        self.mode=1
        self.lockmenu=True
    def display(self):
        def draw_board():
            
            for row in range(8):
                for col in range(8):
                    color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                    rect = (col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                    pg.draw.rect(self.screen, color, rect)
            def getKing(board,turn):
                for row in range(8):
                    for col in range(8):
                        if turn+'K'==board[row][col]:
                            return row,col
                return None,None
            player=self.player2 if self.turn else self.player1
            if player.last_move:
                up_scale=5
                rect_surface = pg.Surface((self.WIDTH*up_scale, self.WIDTH*up_scale), pg.SRCALPHA) 
                rect_surface.set_alpha(60) 
                if player.check:
                    row,col = getKing(self.board,'W') if self.turn else getKing(self.board,'B')
                    rect3 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    pg.draw.rect(rect_surface, (255,0,0), rect3)
                    for i in player.check:
                        row,col=i[0]
                        rect4 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                        pg.draw.rect(rect_surface, (255,0,0), rect4)
                else:
                    row,col=player.last_move.sqEnd
                    rect1 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    row,col=player.last_move.sqStart
                    rect2 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    pg.draw.rect(rect_surface, (150,180,0), rect1)
                    pg.draw.rect(rect_surface, (150,180,0), rect2)
                surf=pg.transform.smoothscale(rect_surface,(self.WIDTH,self.WIDTH))
                self.screen.blit(surf, (0, 0))  
            
            if self.players[0].pickup is not None:
                up_scale=5
                rect_surface = pg.Surface((self.WIDTH*up_scale, self.WIDTH*up_scale), pg.SRCALPHA) 
                rect_surface.set_alpha(86) 
                row,col=self.players[0].pickup
                rect = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                pg.draw.rect(rect_surface, (0,180,0), rect)
                validpos=list(filter(lambda x:self.players[0].pickup==x.sqStart,self.gs.getValidMoves()))
                for row,col in list(map(lambda x: x.sqEnd,validpos)):
                    if self.gs.board[row][col]!='--':
                        pg.draw.circle(rect_surface,(0,0,0),((col * self.square_size+self.square_size/2)*up_scale,( row * self.square_size+self.square_size/2)*up_scale),self.square_size/2*up_scale, self.square_size//12*up_scale)
                    else: pg.draw.circle(rect_surface,(0,0,0),((col * self.square_size+self.square_size/2)*up_scale,( row * self.square_size+self.square_size/2)*up_scale),self.square_size/4*up_scale)
                surf=pg.transform.smoothscale(rect_surface,(self.WIDTH,self.WIDTH))
                self.screen.blit(surf, (0, 0))  
        def draw_pieces():
            for row in range(8):
                for col in range(8):
                    piece=self.board[row][col]
                    if piece!="--": self.screen.blit(self.pieces[piece],tuple(map(lambda x:x*self.square_size,(row,col)))[::-1])
           
        def menu():
            rect_surface = pg.Surface((self.WIDTH, self.WIDTH))  # Kích thước (width, height)
            rect_surface.set_alpha(128) 
            self.screen.blit(rect_surface, (0, 0))
            if self.mode==1 :
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                [pg.draw.rect(self.screen,(255,255,255),self.rect[i],border_radius=self.WIDTH//40) for i in range(3)]
                text_surf= self.font.render("MENU",True,(255,255,255))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.25)))
                text_surf= self.font1.render("NEW GAME",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.39)))
                text_surf= self.font1.render("SELECT PLAYER 1",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.49)))
                text_surf= self.font1.render("SELECT PLAYER 2",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.59)))
            elif self.mode==2 or self.mode==3:
                
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                [pg.draw.rect(self.screen,(255,255,255),self.rect[i],border_radius=self.WIDTH//40) for i in range(3)]
                if self.mode==2:
                    if type(self.player1) is type(self.players[0]): idx=0
                    elif type(self.player1) is type(self.players[1]): idx = 1
                    else :idx =2
                else:
                    if type(self.player2) is type(self.players[0]): idx=0
                    elif type(self.player2) is type(self.players[2]): idx = 1
                    else :idx =2
                pg.draw.rect(self.screen,(120,180,0),self.rect[idx],border_radius=self.WIDTH//40,width=5)
                text_surf= self.font.render("SELECT PLAYER",True,(255,255,255))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.25)))
                text_surf= self.font1.render("HUMAN",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.39)))
                text_surf= self.font1.render("AI AGENT",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.49)))
                text_surf= self.font1.render("RANDOM BOT",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.59)))
            elif self.mode==4 or self.mode==5:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                [pg.draw.rect(self.screen,(255,255,255),self.rect[i],border_radius=self.WIDTH//40) for i in range(3)]
                if self.mode==4: idx=self.players[1].mode-1 
                else: idx=self.players[2].mode-1 
                pg.draw.rect(self.screen,(120,180,0),self.rect[idx],border_radius=self.WIDTH//40,width=5)
                text_surf= self.font.render("MODE",True,(255,255,255))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.25)))
                text_surf= self.font1.render("EASY",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.39)))
                text_surf= self.font1.render("MEDIUM",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.49)))
                text_surf= self.font1.render("HARD",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.59)))
            elif self.mode==7:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                if self.turn:
                    text_surf= self.font1.render("PLAYER 2 WON",True,(255,255,255))
                    self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.5)))
                else:
                    text_surf= self.font1.render("PLAYER 1 WON",True,(255,255,255))
                    self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.5)))
            elif self.mode==6:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH*0.1,self.WIDTH*0.4,self.WIDTH*0.8,self.WIDTH*0.2),border_radius=self.WIDTH//40)
                if self.turn: p='W'
                else: p='B'
                [pg.draw.rect(self.screen,(255,255,255),self.rect[i],border_radius=self.WIDTH//80) for i in range(3,7)]
                p1='RNBQ'
                [self.screen.blit(self.pieces[p+p1[i]],((i+1)*self.WIDTH*0.174,self.WIDTH*0.438)) for i in range(4)]
        
        draw_board()
        draw_pieces()
        if self.mode!=0 : menu()
        pg.display.flip()
    def reset(self):
        for i in self.players: i.reset()
        self.gs.reset()
        self.updateBoard()
        self.mode=0
        self.turn =True
    def updateBoard(self):
        self.board=deepcopy(self.gs.board)
    def run(self):
        keys=pg.key.get_pressed()
        while True:
            events= pg.event.get()
            for event in events:
                if event.type == QUIT:
                    for i in self.players: i.reset()
                    pg.quit()
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.mode==1:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[0].collidepoint(mouse_pos):
                            self.reset()
                            self.lockmenu=False
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.mode=2
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.mode=3
                    elif self.mode==2:
                        mouse_pos = pg.mouse.get_pos()
                        for i in range(3):
                            if self.rect[i].collidepoint(mouse_pos):
                                self.player1.reset()
                                self.player1=self.players[3] if i ==2 else self.players[i] 
                                self.mode=4 if i==1 else 1
                                break
                    elif self.mode==3:
                        mouse_pos = pg.mouse.get_pos()
                        for i in range(3):
                            if self.rect[i].collidepoint(mouse_pos):
                                self.player2.reset()
                                self.player2=self.players[0] if i ==0 else self.players[i+1] 
                                self.mode=5 if i==1 else 1
                                break
                    elif self.mode== 4 or self.mode== 5:
                        mouse_pos = pg.mouse.get_pos()
                        for i in range(3):
                            if self.rect[i].collidepoint(mouse_pos):
                                self.players[self.mode-3].setmode(i+1)
                                self.mode=1
                                break
                    elif self.mode==6:
                        mouse_pos = pg.mouse.get_pos()
                        p='RNBQ'
                        for i in range(3,7):
                            if self.rect[i].collidepoint(mouse_pos):
                                self.gs.makeMove(self.players[0].promove,p[i-3])
                                _,self.players[0].check=self.gs._getPinAndCheckPieces()
                                self.updateBoard()
                                self.mode=0
                                self.turn = not self.turn
            self.clock.tick(60)
            current_key=pg.key.get_pressed()
            if  keys[K_ESCAPE] and  not current_key[K_ESCAPE]  :
                if self.mode==0: self.mode=1
                elif self.mode ==1 and not self.lockmenu: self.mode=0
            if keys[K_LCTRL] and keys[K_z] and not current_key[K_z] :
                for i in self.players: i.reset()
                if self.turn: self.gs.undoMove()
                else: self.turn = not self.turn
                self.gs.undoMove()
                self.updateBoard()
            if self.mode==7:
                if any(keys):
                    self.mode=1
                    self.lockmenu=True
            if self.mode==0:
                match self.player1.Act(events=events,turn='W') if self.turn else self.player2.Act(events=events,turn='B'): 
                    case 1:
                        self.turn=not self.turn
                        self.updateBoard()
                    case 2:self.mode=7
                    case 3:self.mode=6
                    
            self.display()
            keys=pg.key.get_pressed()
            
class UI:
    def __init__(self):pass
    def run(self):
        ChessUI().run()
    
