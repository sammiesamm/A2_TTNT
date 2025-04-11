<<<<<<< HEAD
from board import Board
from move_generator import generate_moves

def main():
    board = Board()
    board.display()
    moves = generate_moves(board)
    print("Các nước đi hợp lệ từ vị trí hiện tại:", moves)

if __name__ == '__main__':
    main()
=======
from ui import UI
if __name__=="__main__":
    UI().run()
>>>>>>> 2ff605b (update)
