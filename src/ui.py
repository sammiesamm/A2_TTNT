import pygame as pg
from pygame.locals import *
from board import *
import sys
import threading
# Khởi tạo Pygame
class ChessUI:
   
    
    def __init__(self):
        class Player:
            def __init__(self,board):
                self.board=board
            def Act(self,turn,events=None): pass
        class Human(Player):
            def __init__(self, board):
                super().__init__(board)
                self.pickup=None
            def Act(self,turn,events):
                pos=None
                for event in events:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        pos=tuple(map(lambda x:x//(1280//8),pg.mouse.get_pos()))[::-1]
                        piece=self.board.getPieces(pos)
                        
                        if self.pickup is None:
                            if piece is None or turn==piece.getState():
                                self.pickup=piece
                        else:
                            if self.board.Update(self.pickup,pos):
                                self.pickup=None
                                return True
                            else: self.pickup = None
                return None
        class Bot(Player):
            def setmode(self,Mode):pass
        class RandomBot(Player):pass
        pg.init()
        self.clock = pg.time.Clock()
        
        self.WIDTH= 1280
        self.screen = pg.display.set_mode((self.WIDTH, self.WIDTH))
        pg.display.set_caption("Cờ Vua")
    
        self.square_size = self.WIDTH // 8
    
        self.pieces=['BR','BN','BB','BQ','BK','BP','WR','WN','WB','WQ','WK','WP']   
        self.pieces=dict(map(lambda x:(x,pg.transform.smoothscale(pg.image.load("chesspieces/"+x+".png"),(self.square_size,self.square_size))),self.pieces))
        self.font = pg.font.SysFont("arial", self.WIDTH//10)
        self.font1 = pg.font.SysFont("arial", self.WIDTH//20)
        self.mode=0
        self.rect=[Rect(self.WIDTH/3,self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,2*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,3*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,4*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,2*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14),
                   Rect(self.WIDTH/3,3*self.WIDTH/10+self.WIDTH/4,self.WIDTH/3,self.WIDTH/14)
                   ]
        self.board=Board()
        self.players=[Human(self.board),Bot(self.board),RandomBot(self.board)]
        self.player1=self.players[0]
        self.player2=self.players[0]
        self.turn=True

    def display(self):
        def draw_board():
            
            for row in range(8):
                for col in range(8):
                    color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                    rect = (col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                    pg.draw.rect(self.screen, color, rect)
            if self.players[0].pickup is not None:
                rect_surface = pg.Surface((self.WIDTH, self.WIDTH), pg.SRCALPHA) 
                rect_surface.set_alpha(128) 
                row,col=self.players[0].pickup.getPos()
                rect = (col * self.square_size, row * self.square_size, self.square_size, self.square_size)
                pg.draw.rect(rect_surface, (0,255,0), rect)
                # print(self.players[0].pickup.getValidPos())
                for row,col in self.players[0].pickup.getValidPos():
                    pg.draw.circle(rect_surface,(0,255,0),(col * self.square_size+self.square_size/2, row * self.square_size+self.square_size/2),self.square_size/4)
                self.screen.blit(rect_surface, (0, 0))  
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
                
        draw_board()
        draw_pieces()
        if self.mode!=0: menu()
        pg.display.flip()

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
                            self.mode=0
                            self.turn=True
                            self.board.reset()
                        elif self.rect[1].collidepoint(mouse_pos):
                            self.mode=0
                            self.turn=True
                            self.player1=self.players[0]
                            self.player2=self.players[0]
                            self.board.reset()
                        elif self.rect[2].collidepoint(mouse_pos):
                            self.player1=self.players[0]
                            self.player2=self.players[1]
                            self.mode=2
                        elif self.rect[3].collidepoint(mouse_pos):
                            self.player1=self.players[1]
                            self.player2=self.players[2]
                            self.mode=2
                    elif self.mode==2:
                        if self.rect[4].collidepoint(mouse_pos):
                            self.mode=0
                            self.turn=True
                            self.players[1].setmode(0)
                            self.board.reset()
                        elif self.rect[5].collidepoint(mouse_pos):
                            self.mode=0
                            self.turn=True
                            self.players[1].setmode(1)
                            self.board.reset()
                        elif self.rect[6].collidepoint(mouse_pos):
                            self.mode=0
                            self.turn=True
                            self.players[1].setmode(2)
                            self.board.reset()
            self.clock.tick(60)
            if keys[K_ESCAPE] and not pg.key.get_pressed()[K_ESCAPE]  :
                if self.mode==0: self.mode=1
                else: self.mode=0
            if self.turn: 
                if self.player1.Act(events=events,turn=1) is not None: self.turn=False
            else: 
                if self.player2.Act(events=events,turn=2) is not None: self.turn=True
            self.display()
            
            keys=pg.key.get_pressed()
            
            

class UI:
    def __init__(self):pass
    def run(self):
        ChessUI().run()
# class A:
#     def __init__(self):
#         self.a=0
#     def foo1(self):
#         for i in range(100000000):
#             self.a=i
    
if __name__=="__main__":
    interface=UI()
    interface.run()
    
    # b=A()
    # thread1=threading.Thread(target=b.foo1)
    # thread1.start()
    # while True:
        
    #     print(thread1.is_alive(),b.a)
    
