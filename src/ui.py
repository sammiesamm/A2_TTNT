import pygame as pg
from pygame.locals import *
import pygame.gfxdraw
from board import *
import sys
import threading
# Khởi tạo Pygame
class ChessUI:
   
    
    def __init__(self):
        class Player:
            def __init__(self,board):
                self.board=board
            def Act(self,turn,events=None): return 1
            def reset(self):pass
        class Human(Player):
            def __init__(self, board,size):
                super().__init__(board)
                self.pickup=None
                self.size=size
            def Act(self,turn,events):
                pos=None
                for event in events:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        pos=tuple(map(lambda x:x//(self.size//8),pg.mouse.get_pos()))[::-1]
                        piece=self.board.getPieces(pos)
                        
                        if self.pickup is None:
                            if piece is None or turn==piece.getState():
                                self.pickup=piece
                        else: 
                            ppiece=self.pickup
                            self.pickup=None
                            return self.board.Update(ppiece,pos)
                            
                            
                return None
            def reset(self):self.pickup=None
        class Bot(Player):
            def setmode(self,Mode):pass
        class RandomBot(Player):pass
        pg.init()
        self.clock = pg.time.Clock()
        
        self.WIDTH=int(pg.display.get_desktop_sizes()[0][1]*0.9)
        self.screen = pg.display.set_mode((self.WIDTH, self.WIDTH))
        pg.display.set_caption("Cờ Vua")
    
        self.square_size = self.WIDTH // 8
    
        self.pieces=['BR','BN','BB','BQ','BK','BP','WR','WN','WB','WQ','WK','WP']   
        self.pieces=dict(map(lambda x:(x,pg.transform.smoothscale(pg.image.load("chesspieces/"+x+".png"),(self.square_size,self.square_size))),self.pieces))
        self.font = pg.font.SysFont("arial", self.WIDTH//10)
        self.font1 = pg.font.SysFont("arial", self.WIDTH//20)
        self.rect=[Rect(self.WIDTH/3,self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,2*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,3*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,4*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,2*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,3*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   
                   Rect(self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(2*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(3*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   Rect(4*self.WIDTH*0.174,self.WIDTH*0.438,self.WIDTH/8,self.WIDTH/8),
                   ]
        self.board=Board()
        self.players=[Human(self.board,self.WIDTH),Bot(self.board),RandomBot(self.board)]
        self.player1=self.players[0]
        self.player2=self.players[0]
        self.turn=True
        self.mode=0

    def display(self):
        def draw_board():
            
            for row in range(8):
                for col in range(8):
                    color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                    rect = (col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                    pg.draw.rect(self.screen, color, rect)
            if self.players[0].pickup is not None:
                up_scale=5
                rect_surface = pg.Surface((self.WIDTH*up_scale, self.WIDTH*up_scale), pg.SRCALPHA) 
                rect_surface.set_alpha(86) 
                row,col=self.players[0].pickup.getPos()
                rect = (col * self.square_size*up_scale, row * self.square_size*up_scale, self.square_size*up_scale, self.square_size*up_scale)
                pg.draw.rect(rect_surface, (0,180,0), rect)
                # print(self.players[0].pickup.getValidPos())
                for row,col in self.players[0].pickup.getValidPos():
                    if self.board.getPieces((row,col)) is not None:
                        pg.draw.circle(rect_surface,(0,0,0),((col * self.square_size+self.square_size/2)*up_scale,( row * self.square_size+self.square_size/2)*up_scale),self.square_size/2*up_scale, self.square_size//12*up_scale)
                    else: pg.draw.circle(rect_surface,(0,0,0),((col * self.square_size+self.square_size/2)*up_scale,( row * self.square_size+self.square_size/2)*up_scale),self.square_size/4*up_scale)
                surf=pg.transform.smoothscale(rect_surface,(self.WIDTH,self.WIDTH))
                self.screen.blit(surf, (0, 0))  
        def draw_pieces():
            for wpiece in self.board.getWhitePieces():
                if wpiece.getState()!=0: self.screen.blit(self.pieces[wpiece.getType()],tuple(map(lambda x:x*self.square_size,wpiece.getPos()))[::-1])
            for bpiece in self.board.getBlackPieces():
                if bpiece.getState()!=0: self.screen.blit(self.pieces[bpiece.getType()],tuple(map(lambda x:x*self.square_size,bpiece.getPos()))[::-1])
        def menu():
            rect_surface = pg.Surface((self.WIDTH, self.WIDTH))  # Kích thước (width, height)
            rect_surface.set_alpha(128) 
            self.screen.blit(rect_surface, (0, 0))
            if self.mode==1:
                
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[0],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[1],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[2],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[3],border_radius=self.WIDTH//40)
                
                text_surf= self.font.render("MENU",True,(255,255,255))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.25)))
                text_surf= self.font1.render("NEW GAME",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.39)))
                text_surf= self.font1.render("P v P",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.49)))
                text_surf= self.font1.render("P vs AI",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.59)))
                text_surf= self.font1.render("AI vs AI",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.69)))
            elif self.mode==2:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[4],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[5],border_radius=self.WIDTH//40)
                pg.draw.rect(self.screen,(255,255,255),self.rect[6],border_radius=self.WIDTH//40)
                text_surf= self.font.render("MODE",True,(255,255,255))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.25)))
                text_surf= self.font1.render("EASY",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.39)))
                text_surf= self.font1.render("MEDIUM",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.49)))
                text_surf= self.font1.render("HARD",True,(0,0,0))
                self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.59)))
            elif self.mode==3:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH/10,self.WIDTH/10,self.WIDTH*0.8,self.WIDTH*0.8),border_radius=self.WIDTH//40)
                if self.turn:
                    text_surf= self.font1.render("PLAYER 1 WON",True,(255,255,255))
                    self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.5)))
                else:
                    text_surf= self.font1.render("PLAYER 2 WON",True,(255,255,255))
                    self.screen.blit(text_surf,text_surf.get_rect(center=(self.WIDTH*0.5,self.WIDTH*0.5)))
            elif self.mode==4:
                pg.draw.rect(self.screen,(50,50,50),Rect(self.WIDTH*0.1,self.WIDTH*0.4,self.WIDTH*0.8,self.WIDTH*0.2),border_radius=self.WIDTH//40)
                if self.turn: p='W'
                else: p='B'
                pg.draw.rect(self.screen,(255,255,255),self.rect[7],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[8],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[9],border_radius=self.WIDTH//80)
                pg.draw.rect(self.screen,(255,255,255),self.rect[10],border_radius=self.WIDTH//80)
                self.screen.blit(self.pieces[p+"R"],(self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"N"],(2*self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"B"],(3*self.WIDTH*0.174,self.WIDTH*0.438))
                self.screen.blit(self.pieces[p+"Q"],(4*self.WIDTH*0.174,self.WIDTH*0.438))
        
                
        draw_board()
        draw_pieces()
        if self.mode!=0: menu()
        pg.display.flip()
    def reset(self):
        self.board.reset()
        self.mode=0
        self.turn =True
        for i in self.players: i.reset()
    def run(self):
        keys=pg.key.get_pressed()
        while True:
            events= pg.event.get()
            for event in events:
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.mode==1 :
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[0].collidepoint(mouse_pos):
                            self.reset()
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.player1=self.players[0]
                            self.player2=self.players[0]
                            self.reset()
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.player1=self.players[0]
                            self.player2=self.players[1]
                            self.mode=2
                        elif self.rect[3].collidepoint(mouse_pos):
                            self.player1=self.players[1]
                            self.player2=self.players[2]
                            self.mode=2
                    elif self.mode==2:
                        mouse_pos = pg.mouse.get_pos()
                        if self.rect[4].collidepoint(mouse_pos):
                            self.players[1].setmode(0)
                            self.reset()
                        elif self.rect[5].collidepoint(mouse_pos):
                            self.players[1].setmode(1)
                            self.reset()
                        elif self.rect[6].collidepoint(mouse_pos):
                            self.players[1].setmode(2)
                            self.reset()
                    elif self.mode==4:
                        mouse_pos = pg.mouse.get_pos()
                        if self.turn:
                            p='W'
                            for x in range(8):
                               piece=self.board.getPieces((0,x)) 
                               if piece.getType()[1]=="P":break
                        else:
                            p='B'
                            for x in range(8):
                               piece=self.board.getPieces((7,x)) 
                               if piece.getType()[1]=="P":break
                        if self.rect[7].collidepoint(mouse_pos):
                            piece.setType(p+'R')
                            piece.setRule(Rule.ROOK)
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[8].collidepoint(mouse_pos):
                            piece.setType(p+'N')
                            piece.setRule(Rule.KNIGH)
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[9].collidepoint(mouse_pos):
                            piece.setType(p+'B')
                            piece.setRule(Rule.BISHOP)
                            self.mode=0
                            self.turn = not self.turn
                        elif self.rect[10].collidepoint(mouse_pos):
                            piece.setType(p+'Q')
                            piece.setRule(Rule.QUEEN)
                            self.mode=0
                            self.turn = not self.turn
                    
            self.clock.tick(60)
            current_key=pg.key.get_pressed()
            if  keys[K_ESCAPE] and  not current_key[K_ESCAPE]  :
                if self.mode==0: self.mode=1
                elif self.mode ==1: self.mode=0
            if self.mode==3:
                if keys[K_RETURN] and  not current_key[K_RETURN]:
                    self.mode=0
                    self.board.reset()
            elif self.mode==0:
                if self.turn: 
                    match self.player1.Act(events=events,turn=1): 
                        case 1:self.turn=False
                        case 2:self.mode=3
                        case 3:self.mode=4
                else: 
                    match self.player2.Act(events=events,turn=2):
                        case 1:self.turn=True
                        case 2:self.mode=3
                        case 3:self.mode=4
            self.display()
            
            keys=pg.key.get_pressed()
            
            

class UI:
    def __init__(self):pass
    def run(self):
        ChessUI().run()
if __name__=="__main__":
    interface=UI()
    interface.run()
    
    
