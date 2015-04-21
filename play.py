#!/usr/bin/python3
from time import sleep

class Camelot:
    def __init__(self, color, debug=False):
        self.hu_color = color
        self.co_color = 'B' if color == 'W' else 'w'
        self.capmoves = {'W': False, 'B': False}
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
        if debug:
            self.hu_color = 'W'
            self.board[4][2], self.board[8][2] = self.board[8][2], self.board[4][2]
            self.wp_set.remove((4,2))
            self.wp_set.append((8,2))
            self.detect_capture('W', 'B', 8, 2)

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

    def detect_capture(self, player, target, px, py):
        for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]:
            if self.isonboard(px+i, py+j):
                if self.board[px+i][py+j] == '__' and self.board[px+int(i/2)][py+int(j/2)] == target + 'P':
                    self.capmoves[player] = (i,j, px, py)
                    return
        return False
            #return target + 'P' in [self.board[i][j] \
                                       #for i in range(fx-1,fx+2) for j in range(fy-1,fy+2) \
                                       #if self.isonboard(i,j) and (i!=fx or j!=fy)]

    def hu_makemove(self):
        if self.capmoves[self.hu_color] == False:
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
            #now we check for captures and set a flag for later use
            self.detect_capture(self.hu_color, self.co_color, fx, fy)
        else:
            print('Playing capture move.')
            sleep(1)
            i, j, px, py = self.capmoves[self.hu_color]
            self.capmoves[self.hu_color] = False
            fx, fy = px+i, py+j
            ex, ey = px+int(i/2), py+int(j/2)
            self.p_set[self.hu_color][self.p_set[self.hu_color].index((px, py))] = (fx, fy)
            self.board[fx][fy] = self.board[px][py]
            self.board[px][py] = '__'
            self.p_set[self.co_color].remove((ex, ey))
            self.board[ex][ey] = '__'
            self.detect_capture(self.hu_color, self.co_color, fx, fy)

    def co_makemove(self):
        piecemoves = dict()
        for px, py in self.p_set[self.co_color]:
            piecemoves[(px, py)] = self.getmoves(px, py, self.co_color)

if __name__ == '__main__':
    #while True:
    #    color = input('Select your color (W/B): ')
    #    if color not in {'W', 'B'}:
    #        print('Bad input, try again.')
    #    else:
    #        break
    color = 'W'
    game = Camelot(color, debug=True)
    if color == 'W':
        game.printboard()
        game.hu_makemove()
    while True:
        game.co_makemove()
        game.printboard()
        game.hu_makemove()
        game.printboard()
#print(game.p_set['B'])
#print(game.p_set['W'])
