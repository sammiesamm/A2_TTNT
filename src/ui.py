import pygame as pg
from pygame.locals import *
import sys
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
            def Act(self,turn,events=None): return 1
            def reset(self):
                self.last_move=None
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
                                    return self.gs.makeMove(move)
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
                self.reval=None
            def setmode(self,Mode):
                self.mode=Mode
            def _act(self):
                move,_,_=self.ai.iterative_deepening_tree(self.mode+1)
                self.last_move=move
                if self.gs.makeMove(move) ==0: self.reval= 2
                else: self.reval= 1
            def Act(self,turn,events=None):
                if self.thread==None:
                    self.thread=threading.Thread(target=self._act)
                    self.thread.start()
                else:
                    if self.thread.is_alive(): return 0
                    self.thread=None
                    return self.reval      
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
                    return self.gs.makeMove(move)
        pg.init()
        self.clock = pg.time.Clock()
        
        self.WIDTH=int(pg.display.get_desktop_sizes()[0][1]*0.9)
        self.screen = pg.display.set_mode((self.WIDTH, self.WIDTH))
        pg.display.set_caption("Cờ Vua")
    
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
            if self.turn:
                if self.player2.last_move:
                    up_scale=5
                    rect_surface = pg.Surface((self.WIDTH*up_scale, self.WIDTH*up_scale), pg.SRCALPHA) 
                    rect_surface.set_alpha(60) 
                    row,col=self.player2.last_move.sqEnd
                    rect1 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    row,col=self.player2.last_move.sqStart
                    rect2 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    pg.draw.rect(rect_surface, (150,180,0), rect1)
                    pg.draw.rect(rect_surface, (150,180,0), rect2)
                    surf=pg.transform.smoothscale(rect_surface,(self.WIDTH,self.WIDTH))
                    self.screen.blit(surf, (0, 0))  
            else:
                if self.player1.last_move:
                    up_scale=5
                    rect_surface = pg.Surface((self.WIDTH*up_scale, self.WIDTH*up_scale), pg.SRCALPHA) 
                    rect_surface.set_alpha(60) 
                    row,col=self.player1.last_move.sqEnd
                    rect1 = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                    row,col=self.player1.last_move.sqStart
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
                pg.draw.rect(self.screen,(255,255,255),self.rect[0],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[1],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[2],border_radius=self.WIDTH//40)
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
                pg.draw.rect(self.screen,(255,255,255),self.rect[0],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[1],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[2],border_radius=self.WIDTH//40)
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
                pg.draw.rect(self.screen,(255,255,255),self.rect[0],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[1],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[2],border_radius=self.WIDTH//40)
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
                pg.draw.rect(self.screen,(255,255,255),self.rect[3],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[4],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[5],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[6],border_radius=self.WIDTH//80)
                self.screen.blit(self.pieces[p+"R"],(self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"N"],(2*self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"B"],(3*self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"Q"],(4*self.WIDTH*0.174,self.WIDTH*0.438))
        
        draw_board()
        draw_pieces()
        if self.mode!=0 : menu()
        pg.display.flip()
    def reset(self):
        self.gs.reset()
        self.updateBoard()
        self.mode=0
        self.turn =True
        for i in self.players: i.reset()
    def updateBoard(self):
        self.board=deepcopy(self.gs.board)
    def run(self):
        keys=pg.key.get_pressed()
        while True:
            events= pg.event.get()
            for event in events:
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
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
                        if self.rect[0].collidepoint(mouse_pos):
                            self.player1=self.players[0]
                            self.mode=1
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.player1=self.players[1]
                            self.mode=4
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.player1=self.players[3]
                            self.mode=1
                    elif self.mode==3:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[0].collidepoint(mouse_pos):
                            self.player2=self.players[0]
                            self.mode=1
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.player2=self.players[2]
                            self.mode=5
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.player2=self.players[3]
                            self.mode=1
                    elif self.mode== 4:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[0].collidepoint(mouse_pos):
                            self.players[1].setmode(1)
                            self.mode=1
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.players[1].setmode(2)
                            self.mode=1
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.players[1].setmode(3)
                            self.mode=1
                    elif self.mode== 5:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[0].collidepoint(mouse_pos):
                            self.players[2].setmode(1)
                            self.mode=1
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.players[2].setmode(2)
                            self.mode=1
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.players[2].setmode(3)
                            self.mode=1
                    elif self.mode==6:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[3].collidepoint(mouse_pos):
                            self.gs.makeMove(self.players[0].promove,'R')
                            self.updateBoard()
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[4].collidepoint(mouse_pos):
                            self.gs.makeMove(self.players[0].promove,'N')
                            self.updateBoard()
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[5].collidepoint(mouse_pos):
                            self.gs.makeMove(self.players[0].promove,'B')
                            self.updateBoard()
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[6].collidepoint(mouse_pos):
                            self.gs.makeMove(self.players[0].promove,'Q')
                            self.updateBoard()
                            self.mode=0
                            self.turn = not self.turn
            self.clock.tick(60)
            current_key=pg.key.get_pressed()
            if  keys[K_ESCAPE] and  not current_key[K_ESCAPE]  :
                if self.mode==0: self.mode=1
                elif self.mode ==1 and not self.lockmenu: self.mode=0
            if keys[K_LCTRL] and keys[K_z] and not current_key[K_z] :
                if self.turn: self.gs.undoMove()
                self.gs.undoMove()
                self.updateBoard()
            if self.mode==7:
                if any(keys):
                    self.mode=1
                    self.lockmenu=True
            elif self.mode==0:
                if self.turn: 
                    match self.player1.Act(events=events,turn='W'): 
                        case 1:
                            self.turn=False
                            self.updateBoard()
                        case 2:self.mode=7
                        case 3:self.mode=6
                else: 
                    match self.player2.Act(events=events,turn='B'):
                        case 1:
                            self.turn=True
                            self.updateBoard()
                        case 2:self.mode=7
                        case 3:self.mode=6
            self.display()
            
            keys=pg.key.get_pressed()
            
            

class UI:
    def __init__(self):pass
    def run(self):
        ChessUI().run()
    
