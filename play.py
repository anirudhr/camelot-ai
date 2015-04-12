#!/usr/bin/python3


class board:
    def __init__(self):
        self.board = [['__']*8 for i in range(14)]
        for i in range(3):
            for j in range(3-i): #top-left
                self.board[i][j] = '  '
            for j in range(i+5, 8): #top-right
                self.board[i][j] = '  '
            for j in range(i+1): #bottom-left
                self.board[i+11][j] = '  '
            for j in range(2-i, 3): #bottom-right
                self.board[i+11][j+5] = '  '
        for j in [3,4]:
            self.board[0][j] = 'WC'
            self.board[13][j] = 'BC'
            for i in [4,5]:
                self.board[i][j] = 'WP'
                self.board[i+4][j] = 'BP'
        for j in [2,5]:
            self.board[4][j] = 'WP'
            self.board[9][j] = 'BP'
    def printboard(self):
        def horizrule():
            print('  ', end=' ')
            for i in range(8):
                print(' %i' % i, end=' ')
            print()
        horizrule()
        from pprint import pprint
        for rownum, row in enumerate(self.board):
            if rownum < 10:
                print(' %i' % rownum, end=' ')
            else:
                print('%i' % rownum, end=' ')
            for elem in row:
                print(elem, end=' ')
            print(rownum)
        horizrule()

game = board()
game.printboard()
