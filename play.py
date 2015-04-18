#!/usr/bin/python3


class Camelot:
    def __init__(self, color):
        self.hu_color = color
        self.wp_set = list()
        self.bp_set = list()
        self.p_set = {'B': self.bp_set, 'W': self.wp_set}
        if self.hu_color == 'W':
            self.ai_color = 'B'
        else:
            self.ai_color = 'W'
        self.board = [['__']*8 for _ in range(14)]
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
                self.wp_set.append((i,j))
                self.board[i+4][j] = 'BP'
                self.bp_set.append((i+4,j)) 
        for j in [2,5]:
            self.board[4][j] = 'WP'
            self.wp_set.append((4,j))
            self.board[9][j] = 'BP'
            self.bp_set.append((9,j))

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
        
    def isonboard(self, px, py):
        if px >= 0 and px <= 13 and py >= 0 and py <= 7:
            return self.board[px][py] != '  '
        else:
            return False
        
    def getmoves(self, px, py, pcolor):
        simplemoves = [(i,j) \
                 for i in range(px-1, px+2) \
                 for j in range(py-1, py+2) \
                 if (i != px or j != py) and \
                    self.isonboard(i,j) and \
                    self.board[i][j] == '__'
                ]
        
        cantermoves = list()
        for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]:
            if self.isonboard(px+i, py+j):
                if self.board[px+i][py+j] == '__' and self.board[px+int(i/2)][py+int(j/2)] == pcolor + 'P':
                    cantermoves.append((px+i, py+j))

        return simplemoves + cantermoves

    def hu_makemove(self):
        for idx, elem in enumerate(self.p_set[self.hu_color]):
            print('*** %i: %s' % (idx, elem))
        choice1 = -1
        while choice1 not in range(6):
            choice1 = input('Select your piece from the above: ')
            if not choice1.isdigit():
                print('Bad choice, try again. ', end='')
            else:
                choice1 = int(choice1)
                if choice1 not in range(6):
                    print('Bad choice, try again. ', end='')
        px, py = self.p_set[self.hu_color][choice1]
        moves = self.getmoves(px, py, self.hu_color)
        for idx, elem in enumerate(moves):
            print('*** %i: %s' % (idx, elem))
        choice2 = -1
        while choice2 not in range(len(moves)):
            choice2 = input('Select your move from the above: ')
            if not choice2.isdigit():
                print('Bad choice, try again. ', end='')
            else:
                choice2 = int(choice2)
                if choice2 not in range(len(moves)):
                    print('Bad choice, try again. ', end='')
        fx, fy = moves[choice2]
        self.p_set[self.hu_color][choice1] = (fx, fy)
        self.board[fx][fy] = self.board[px][py]
        self.board[px][py] = '__'

if __name__ == '__main__':
    while True:
        color = input('Select your color (W/B): ')
        if color not in {'W', 'B'}:
            print('Bad input, try again.')
        else:
            break
    game = Camelot(color)
    game.printboard()
    game.hu_makemove()
    game.printboard()
#print(game.p_set['B'])
#print(game.p_set['W'])
