from random import randint
import time

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "\nВы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "\nВы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f'Dot({self.x},{self.y})'

class Ship:
    def __init__(self, start_dot, length, orientation):
        self.start_dot = start_dot
        self.length = length
        self.orientation = orientation
        self.lives = length
        
    @property
    def dots(self):
        dots_list = []
        for _ in range(self.length):
            if self.orientation == 0:
                dots_list.append(Dot(self.start_dot.x + _, self.start_dot.y))
            else:
                dots_list.append(Dot(self.start_dot.x, self.start_dot.y + _))
        return dots_list

class Board:
    def __init__(self, size, is_hidden = False):
        self.cells_list=[['○']*size for _ in range(size)]
        self.size = size
        self.busy = []
        self.ships = []
        self.is_hidden = is_hidden
        self.count = 0
        
    def __str__(self):
        beg_between = '┬───' * (self.size - 2)
        mid_between = '┼───' * (self.size - 2)
        end_between = '┴───' * (self.size - 2)
        beg = f'  ┌───{beg_between}┬───┐'
        mid = f'  ├───{mid_between}┼───┤'
        end = f'  └───{end_between}┴───┘'
        num = ''.join(map(str,list(range(1, self.size + 1))))
        board_text = '\n    ' + '   '.join(map(str,list(range(1, self.size + 1)))) + '  '
        board_text += '\n' + beg
        for i in range(self.size):
            board_text += f'\n{num[i]} │ '+' │ '.join(self.cells_list[i]) + ' │'
            if i<self.size - 1:
                board_text += '\n' + mid
        board_text += '\n' + end
        if self.is_hidden:
            board_text = board_text.replace('■','○')
        return board_text
    
    def out(self, dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))
    
    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.cells_list[dot.x][dot.y] = '■'
            self.busy.append(dot)
            
        self.ships.append(ship)
        self.contour(ship)            
            
        
    def contour(self, ship, verb = False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0 , 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots:
            for dotx, doty in near:
                cur = Dot(dot.x + dotx, dot.y + doty)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.cells_list[cur.x][cur.y] = "•"
                    self.busy.append(cur)
                    
    def shot(self, dot):
        
        if self.out(dot):
            raise BoardOutException()
        
        if dot in self.busy:
            raise BoardUsedException()        
        
        self.busy.append(dot)
        
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.cells_list[dot.x][dot.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("\nКорабль уничтожен!")
                    return True
                else:
                    print("\nКорабль ранен!")
                    return True
        
        self.cells_list[dot.x][dot.y] = 'T'
        print("\nМимо!")
        return False        
    
    def begin(self):
        self.busy = []                   

class Player:
    def __init__(self, board_self, board_enemy, board_size):
        self.board_self = board_self
        self.board_enemy = board_enemy
        self.board_size = board_size
        
    def ask():
        raise NotImplementedError()
    
    def move(self):
        while True:
            try:
                dot = self.ask()
                return self.board_enemy.shot(dot)
            except BoardException as e:
                print(e)       

class AI(Player):
    def ask(self):
        dot = Dot(randint(0, self.board_size - 1), randint(0, self.board_size - 1))
        print(f'\nХод компьютера: {dot.x + 1} {dot.y + 1}')
        return dot

class User(Player):
    def ask(self):
        num = ''.join(map(str,list(range(1, self.board_size + 1))))
        print('\nВаш ход...')
        while True:
            kord = input(f'\nЗадайте координаты поля в виде двух цифр в диапазоне 1...{self.board_size},\nпервая цифра - строка, вторая цифра - столбец   ... ')
            kord = kord.replace(' ','')
            if len(kord)!=2:
                print('\nЗадайте две координаты!')
                continue
            if not(kord[0] in num and kord[1] in num):
                print('\nКоординаты заданы некорректно, повторите ввод!')
                continue
            return Dot(int(kord[0])-1, int(kord[1])-1)


class Game:

    def create_board(self):
        counter = 0
        new_board = Board(self.size)
        for length in self.lens_ships:
            while True:
                counter += 1
                if counter >= 3000:
                    return None
                try:
                    new_board.add_ship(Ship(Dot(randint(0, self.size - 1), randint(0, self.size - 1)), length, randint(0, 1)))
                    break
                except BoardWrongShipException:
                    pass
        new_board.begin()
        return new_board    
        
    def gen_board(self):
        while True:
            new_board = self.create_board()
            if new_board is not None:
                break
        return new_board
    

    
    def __init__(self, size = 6, lens_ships = [3, 2, 2, 1, 1, 1, 1]):
        self.size = size
        self.lens_ships = lens_ships
        board_ai = self.gen_board()
        board_user = self.gen_board()
        board_ai.is_hidden = True
        
        self.ai = AI(board_ai, board_user, self.size)
        self.user = User(board_user, board_ai, self.size)           
    
    def greet(self):
        print("""
        =================================
        ** ИГРА "МОРСКОЙ БОЙ" **
        =================================
        Вы играете с компьютером.
        Для того, чтобы сделать ход,
        укажите координаты клетки,
        в которую хотите сделать выстрел,
        в формате "строка" "столбец",
        например: 1 2)
        =================================""")
        
    def loop(self):
        num = 0
        while True:
            us = str(self.user.board_self).split('\n')
            ai = str(self.ai.board_self).split('\n')        
            print('\n\n     Ваша доска                       Доска компьютера')
            for _ in range(len(us)):
                print(f'{us[_]}     {ai[_]}')
            if num % 2 == 0:
                repeat = self.user.move()
            else:
                print("Ходит компьютер!")
                time.sleep(1)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board_self.count == len(self.lens_ships):
                print("-"*20)
                print("Победа за Вами!")
                break

            if self.user.board_self.count == len(self.lens_ships):
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1            
            
            
    def start(self):
        self.greet()
        self.loop()              

g = Game()
g.start()
