from board import Board
from move_generator import generate_moves

def main():
    board = Board()
    board.display()
    # Ví dụ: in ra các nước đi hợp lệ từ vị trí ban đầu
    moves = generate_moves(board)
    print("Các nước đi hợp lệ từ vị trí hiện tại:", moves)

if __name__ == '__main__':
    main()
