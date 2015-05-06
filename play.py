#!/usr/bin/python3
from time import sleep
from calendar import timegm
from time import gmtime
import sys
RECLIMIT = 100 #sys.getrecursionlimit() - 1

def timenow():
    return timegm(gmtime())

class Camelot:
    def __init__(self, color, debug=False):
        self.hu_color = color
        self.co_color = 'B' if color == 'W' else 'W'
        #self.capmoves = {'W': list(), 'B': list()} #possible capture moves for each color
        self.p_set = {'B': list(), 'W': list()} #easier access
        
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
                self.p_set['W'].append((i,j))
                self.board[i+4][j] = 'BP'
                self.p_set['B'].append((i+4,j)) 
        for j in [2,5]: #initialize white pieces
            self.board[4][j] = 'WP'
            self.p_set['W'].append((4,j))
            self.board[9][j] = 'BP'
            self.p_set['B'].append((9,j))
        if debug: #testing only: add corner case scenarios here
            self.hu_color = 'W'
            self.board[4][2], self.board[7][2] = self.board[7][2], self.board[4][2]
            self.p_set['W'].remove((4,2))
            self.p_set['W'].append((7,2))
            self.board[4][3], self.board[12][4] = self.board[12][4], self.board[4][3]
            self.p_set['W'].remove((4,3))
            self.p_set['W'].append((12,4))

    def printboard(self, board=None):
        if board is None:
            board = self.board
        def horizrule(): #to print numbers for coordinates
            print('  ', end=' ')
            for i in range(8):
                print(' %i' % i, end=' ')
            print()
        horizrule()
        #from pprint import pprint
        for rownum, row in enumerate(board):
            if rownum < 10: #for neatness
                print(' %i' % rownum, end=' ')
            else:
                print('%i' % rownum, end=' ')
            for elem in row:
                print(elem, end=' ')
            print(rownum)
        horizrule()
        
    def isonboard(self, px, py): #check if a location is on the board or not. Static, doesn't depend on game state.
        if px >= 0 and px <= 13 and py >= 0 and py <= 7:
            return self.board[px][py] != '  '
        else:
            return False
        
    def get_moves(self, px, py, pcolor, board=None): #no p_set needed
        if board is None:
            board = self.board
        simplemoves = [(i,j) \
                 for i in range(px-1, px+2) \
                 for j in range(py-1, py+2) \
                 if (i != px or j != py) and \
                    self.isonboard(i,j) and \
                    (board[i][j] == '__' or board[i][j][1] == 'C') #empty or castle
                ]
        
        cantermoves = list()
        for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]:
            if self.isonboard(px+i, py+j):
                if board[px+i][py+j] == '__' and board[px+int(i/2)][py+int(j/2)] == pcolor + 'P':
                    cantermoves.append((px+i, py+j))

        return simplemoves + cantermoves
    
    def detect_win(self, board=None): #no p_set needed
        if board is None:
            board = self.board
        return 'B' if board[0][3] == 'BP' and board[0][4] == 'BP' else \
            'W' if board[13][3] == 'WP' and board[13][4] == 'WP' else \
                None

    def get_utility(self, pcolor, board, p_set):
        ocolor = 'B' if pcolor == 'W' else 'W'
        castley = 13 if ocolor == 'B' else 0
        if board[castley][3] == pcolor + 'P' and board[castley][4] == pcolor + 'P':
            castlescore = 1000 #if both castle positions are occupied by the player
        elif board[castley][3] == pcolor + 'P' or board[castley][4] == pcolor + 'P':
            castlescore = 500 #if one castle position is occupied by the player
        else:
            castlescore = 0
        #print('Castle score: %i' % castlescore)
        distancescore = sum([2*(abs(px - castley)) for px, py in p_set[pcolor]]) #distance from castle for each player piece
        #print('Distance score: %i' % distancescore)
        enemyscore = -5*len(p_set[ocolor]) #penalty for number of enemy pieces
        #print('Enemy piece score: %i' % enemyscore)
        return castlescore + distancescore + enemyscore

    def detect_captures(self, pcolor, board=None, p_set=None):
        if board is None or p_set is None:
            board = self.board
            p_set = self.p_set
        capmoves = list() #re-initialize so that old captures aren't recorded
        target  = 'B' if pcolor == 'W' else 'W'
        for (px, py) in p_set[pcolor]:
            for i,j in [(-2,2), (0,2), (2,2), (2,0), (2,-2), (0,-2), (-2,-2), (-2,0)]: #directions
                if self.isonboard(px+i, py+j):
                    if board[px+i][py+j] == '__' and board[px+int(i/2)][py+int(j/2)] == target + 'P': #if there's an empty spot to jump over an enemy piece to
                        capmoves.append((i,j, px, py))
        return capmoves

    def hu_makemove(self):
        capmoves = self.detect_captures(self.hu_color) #find if we can make any captures
        if len(capmoves) == 0: #no captures; play regular move
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
            moves = self.get_moves(px, py, self.hu_color)
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
            for idx, piece in enumerate(capmoves):
                print('*** %i: ' % idx, end='')
                print(piece)
            choice = -1
            while choice not in range(len(capmoves)):
                choice = input('Select the move: ')
                if not choice.isdigit():
                    print('Bad selection, try again.')
                else:
                    choice = int(choice)
                    if choice not in range(len(capmoves)):
                        print('Bad selection, try again.')
            i, j, px, py = capmoves[choice]
            capmoves.remove((i, j, px, py))
            fx, fy = px+i, py+j
            ex, ey = px+int(i/2), py+int(j/2)
            self.p_set[self.hu_color][self.p_set[self.hu_color].index((px, py))] = (fx, fy)
            self.board[fx][fy] = self.board[px][py]
            self.board[px][py] = '__'
            self.p_set[self.co_color].remove((ex, ey))
            self.board[ex][ey] = '__'

    def _enum_moves(self, board, p_set, pcolor): #returns a dictionary of actions ready for utility calculation
        moves = self.detect_captures(pcolor, board, p_set)
        if len(moves) == 0: #if no captures, look at regular moves
            moves = list()
            for px, py in p_set[pcolor]:
                fullmoves = self.get_moves(px, py, pcolor)
                moves += [(fx-px, fy-py, px, py) for fx, fy in fullmoves] #converting from destination,piece to offset,piece
        actions = {x:0 for x in moves} #converting to dictionary
        return actions
    
    def _alphabeta(self, pcolor, board, p_set, stupid=False):
        actions = self._enum_moves(board, p_set, self.co_color)
        if stupid: #stupid algorithm: pick a random move
            from random import choice
            return choice(list(actions.keys()))
        maxv = self._minmaxval(pcolor, board, p_set, actions, float('-inf'), float('inf'), timenow(), depth=0, ismax=True)
        for action, v in actions.items():
            if v == maxv:
                return action

    def _minmaxval(self, pcolor, board, p_set, actions, alpha, beta, starttime, depth, ismax):
        if (self.detect_win(board) is not None) or (timenow() - starttime >= 10) or (depth == RECLIMIT):
            return self.get_utility(pcolor, board, p_set)
        v = float('-inf') if ismax else float('inf')
        ocolor = 'B' if pcolor == 'W' else 'W'
        for i, move in enumerate(actions.keys()):
            print('Move to play: %i' % i, end='')
            print(move)
            print('Pieces in play: ', end='')
            print(p_set)
            board2 = board
            ix, iy, px, py = move
            if abs(ix) == 2 or abs(iy) == 2: #jumping over a piece
                ex, ey = px+int(ix/2), py+int(iy/2)
                if (ex, ey) in p_set[ocolor]: #board2[ex][ey] == ocolor + 'P': #capture
                    board2[ex][ey] = '__'
                    print('Enemy piece: %i, %i' % (ex, ey), file=sys.stderr)
                    print('Set of enemy pieces: ', end='', file=sys.stderr)
                    print(p_set[ocolor], file=sys.stderr)
                    p_set[ocolor].remove((ex,ey))
            board2[px+ix][py+iy], board2[px][py] = board2[px][py], board2[px+ix][py+iy]
            newactions = self._enum_moves(board2, p_set, ocolor)
            if ismax:
                v = max(v, self._minmaxval(ocolor, board2, p_set, newactions, alpha, beta, starttime, depth+1, ismax=False))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            else:
                v = min(v, self._minmaxval(ocolor, board2, p_set, newactions, alpha, beta, starttime, depth+1, ismax=True))
                if v >= alpha:
                    return v
                beta = min(beta, v)
        return v

    def co_makemove(self):
        move = self._alphabeta(self.co_color, self.board, self.p_set, stupid=False)
        print('Computer move: ', end='')
        print(move)
        ix, iy, px, py = move
        if move is None:
            print('Error: computer generated empty move.', file=sys.stderr)
            exit(1)
        if abs(ix) == 2 or abs(iy) == 2: #jumping over a piece
            ex, ey = px+int(ix/2), py+int(iy/2)
            if self.board[ex][ey] == self.hu_color + 'P': #capture
                self.board[ex][ey] = '__'
                self.p_set[self.hu_color].remove((ex,ey))
        self.board[px+ix][py+iy], self.board[px][py] = self.board[px][py], self.board[px+ix][py+iy]
        

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
