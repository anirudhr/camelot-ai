#!/usr/bin/python3
from time import sleep

class Camelot:
    def __init__(self, color, debug=False):
        self.hu_color = color
        self.co_color = 'B' if color == 'W' else 'W'
        self.capmoves = {'W': list(), 'B': list()} #possible capture moves for each color
        self.wp_set = list() #set of white pieces
        self.bp_set = list() #set of black pieces
        self.p_set = {'B': self.bp_set, 'W': self.wp_set} #easier access
        
        self.board = [['__']*8 for _ in range(14)] #Initialize the board with blank tiles
        for i in range(3):
            for j in range(3-i): #top-left
                self.board[i][j] = '  ' #not part of the board
            for j in range(i+5, 8): #top-right
                self.board[i][j] = '  '
            for j in range(i+1): #bottom-left
                self.board[i+11][j] = '  '
            for j in range(2-i, 3): #bottom-right
                self.board[i+11][j+5] = '  '
        for j in [3,4]: #initialize castles
            self.board[0][j] = 'WC'
            self.board[13][j] = 'BC'
            for i in [4,5]: #initialize black pieces
                self.board[i][j] = 'WP'
                self.wp_set.append((i,j))
                self.board[i+4][j] = 'BP'
                self.bp_set.append((i+4,j)) 
        for j in [2,5]: #initialize white pieces
            self.board[4][j] = 'WP'
            self.wp_set.append((4,j))
            self.board[9][j] = 'BP'
            self.bp_set.append((9,j))
        if debug: #testing only: add corner case scenarios here
            self.hu_color = 'W'
            self.board[4][2], self.board[12][3] = self.board[12][3], self.board[4][2]
            self.wp_set.remove((4,2))
            self.wp_set.append((12,3))
            self.board[4][3], self.board[12][4] = self.board[12][4], self.board[4][3]
            self.wp_set.remove((4,3))
            self.wp_set.append((12,4))
            #self.detect_captures('W')
            #self.detect_captures('B')

    def printboard(self):
        def horizrule(): #to print numbers for coordinates
            print('  ', end=' ')
            for i in range(8):
                print(' %i' % i, end=' ')
            print()
        horizrule()
        #from pprint import pprint
        for rownum, row in enumerate(self.board):
            if rownum < 10: #for neatness
                print(' %i' % rownum, end=' ')
            else:
                print('%i' % rownum, end=' ')
            for elem in row:
                print(elem, end=' ')
            print(rownum)
        horizrule()
        
    def isonboard(self, px, py): #check if a location is on the board or not
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
                    (self.board[i][j] == '__' or self.board[i][j][1] == 'C') #empty or castle
                ]
        
        cantermoves = list()
        for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]:
            if self.isonboard(px+i, py+j):
                if self.board[px+i][py+j] == '__' and self.board[px+int(i/2)][py+int(j/2)] == pcolor + 'P':
                    cantermoves.append((px+i, py+j))

        return simplemoves + cantermoves
    
    def detect_win(self):
        return 'B' if self.board[0][3] == 'BP' and  self.board[0][4] == 'BP' else \
            'W' if self.board[13][3] == 'WP' and  self.board[13][4] == 'WP' else \
                None
#        if self.board[0][3] == 'BP' and  self.board[0][4] == 'BP':
#            return 'B'
#        if self.board[13][3] == 'WP' and  self.board[13][4] == 'WP':
#            return 'W'
#        return None

    def get_utility(self, pcolor, board):
        ocolor = 'B' if pcolor == 'W' else 'W'
        util = 0
        castley = 13 if ocolor == 'B' else 0
        if board[castley][3] == pcolor + 'P' and board[castley][4] == pcolor + 'P':
            util = 1000 #if both castle positions are occupied by the player
        elif board[castley][3] == pcolor + 'P' or board[castley][4] == pcolor + 'P':
            util = 500 #if one castle position is occupied by the player
        util += sum([2*(14 - abs(py - castley)) for _, py in self.p_set[pcolor]]) #distance from castle for each player piece
        util -= 10*len(self.p_set[ocolor]) #penalty for number of enemy pieces

    def detect_captures(self, pcolor):
        self.capmoves[pcolor] = list() #re-initialize so that old captures aren't recorded
        target  = 'B' if pcolor == 'W' else 'W'
        for (px, py) in self.p_set[pcolor]:
            for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]: #directions
                if self.isonboard(px+i, py+j):
                    if self.board[px+i][py+j] == '__' and self.board[px+int(i/2)][py+int(j/2)] == target + 'P': #if there's an empty spot to jump over an enemy piece to
                        self.capmoves[pcolor].append((i,j, px, py))

    def hu_makemove(self):
        self.detect_captures(self.hu_color) #find if we can make any captures
        if len(self.capmoves[self.hu_color]) == 0: #no captures; play regular move
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
        else: #captures are obligatory
            print('Playing capture move.')
            print('Select a capture move (options are listed as X-offset, Y-offset, X-start, Y-start)')
            for idx, piece in enumerate(self.capmoves[self.hu_color]):
                print('*** %i: ' % idx, end='')
                print(piece)
            choice = -1
            while choice not in range(len(self.capmoves[self.hu_color])):
                choice = input('Select the move: ')
                if not choice.isdigit():
                    print('Bad selection, try again.')
                else:
                    choice = int(choice)
                    if choice not in range(len(self.capmoves[self.hu_color])):
                        print('Bad selection, try again.')
            i, j, px, py = self.capmoves[self.hu_color][choice]
            self.capmoves[self.hu_color].remove((i, j, px, py))
            fx, fy = px+i, py+j
            ex, ey = px+int(i/2), py+int(j/2)
            self.p_set[self.hu_color][self.p_set[self.hu_color].index((px, py))] = (fx, fy)
            self.board[fx][fy] = self.board[px][py]
            self.board[px][py] = '__'
            self.p_set[self.co_color].remove((ex, ey))
            self.board[ex][ey] = '__'

    def co_makemove(self):
        self.detect_captures(self.co_color)
        if len(self.capmoves[self.co_color]) == 0:
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
    while game.detect_win() is None:
        if game.detect_win() is None:
            game.co_makemove()
            game.printboard()
        if game.detect_win() is None:
            game.hu_makemove()
            game.printboard()
    if game.detect_win() == game.hu_color:
        print('You won!')
    else:
        print('Wow, you lost!')
    
#print(game.p_set['B'])
#print(game.p_set['W'])
