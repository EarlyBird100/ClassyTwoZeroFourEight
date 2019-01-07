##-------------------------------------------------------------------------------------
##  12/08/18 -  update print() statements to use str.format() for better formatting
##  12/12/18 -  remove padLeft() 
##              create GameArray methods for pack (1 play) and auto (multiple plays
##                  for a given strategy)
##-------------------------------------------------------------------------------------


try:
    import numpy as np
    import random
    from guizero import App, PushButton, Text, TextBox, Box
except ImportError:
    raise ImportError("NumPy, guizero and Random are required modules.")

class GameArray:

    # Initializer / Instance Attributes
    def __init__(self, size):
        self.size = size
        self.arr = np.zeros((size, size), dtype=int)
        self.seed(size)
        self._rounds = 0

    # Method
    def __pack(self, dir='l'):
        view = self.arr
        if dir=='u' or dir=='d':
            view=view.T
        if dir=='r' or dir=='d':
            view = np.fliplr(view)
        for row in view:
            self.__packRow(row)

    # Method (private)
    def __packRow(self, row):
        self.__trimRow(row)
        for i in range(len(row)-1):
            j=i+1
            if row[i]>0:
                if row[i]==row[j]:
                    row[i]+=row[j]
                    row[j]=0
                    i+=1
        self.__trimRow(row)

    # Method (private)
    def __trimRow(self, row):
        temp = np.array([row[i] for i in range(len(row)) if row[i]>0])
        for i in range(len(row)):
            if i < len(temp):
                row[i]=temp[i]
            else:
                row[i]=0

    # Property (private)
    def __empties():
        pass

    # Method
    def auto(self, strategy='l-r', plays=10):
        dir = strategy.split('-')

        k = len(dir)
        for i in range(plays):
            self.pack(dir[i%k])

    # Property
    def full(self):
        #check for any zeros in array
        match_z = not (np.count_nonzero(self.arr==0))
        #check for matching adjacent vertical values
        match_v = not (self.arr[1:] == self.arr[:-1]).any()
        #check for matching adjacent horitzonal values
        match_h = not (self.arr[:,1:] == self.arr[:,:-1]).any()
        return match_z and match_v and match_h

    # Method
    def pack(self, dir):
        if not self.full() and dir in ['l', 'r', 'u', 'd']:
            self.__pack(dir)
            self.seed()
            self._rounds += 1

    # Property
    def max(self):
        return self.arr.max()


    # Method
    def print(self, label='', indent=0):
        size = len(self.arr[0])
        template = '{0:>' + str(size) + '}'
        margin = ' ' * indent
        fmt_rows = []

        fmt_rows.append(label)
        sborder = margin + ':-' + '-:-'.join(['-'*size for col in range(size)]) + '-:'
        fmt_rows.append(sborder)
        for row in self.arr:
            srow = (margin + ': ' + ' : '.join([template.format(col) for col in row]) + ' :').replace(' 0 ', '   ')
            fmt_rows.append(srow)
            fmt_rows.append(sborder)

        print(*fmt_rows, sep='\n')
        print()

    # Property
    def rounds(self):
        return self._rounds

    # Property
    def score(self):
        return sum(sum(self.arr))

    # Method
    def seed(self, n = 1):
        empties = []
        size = len(self.arr[0])

        for i in range(self.arr.size):
            if self.arr[int(i/size)][i%size] == 0:
                empties.append(i)

        if len(empties) > 0:
            i = empties[random.choice(range(len(empties)))]
            self.arr[int(i/size)][i%size] = random.choice([2, 2, 2, 2, 4])

        if n > 1:
            self.seed(n-1)

    # Property
    def values(self):
        return [self.arr[i][j] for i in range(self.arr.shape[0]) for j in range(self.arr.shape[0])]


def main_gui():
    def set_colors():
        colors = {}
        colors[0] = (255, 255, 255)
        x = 1
        c_val = 255
        for i in range(1, 4):
            x *= 2
            c_val -= 20
            colors[x] = (c_val, c_val-10, c_val+10)
        c_val = 255
        for i in range(1, 4):
            x *= 2
            c_val -= 20
            colors[x] = (c_val-10, c_val, c_val+10)
        c_val = 255
        for i in range(1, 4):
            x *= 2
            c_val -= 20
            colors[x] = (c_val-10, c_val+10, c_val)
        return colors

    def update_buttons():
        i = 0
        for val in ga.values():
            grid_btns[i].text = str(val)
            if val == 0:
                grid_btns[i].text = ''
            if val in colors:
                grid_btns[i].bg = colors[val]
            i += 1
        counter.value = '{0:<8} {1:>8,}'.format('Rounds', ga.rounds() + 1)
        score.value =   '{0:<8} {1:>8,}'.format('Score', ga.score())

        if ga.full():
            spacer.value = 'No moves possible - GAME OVER!'
            spacer.text_color = 'red'
            spacer.bg = 'yellow'

    def auto_play(strategy):
        if key_in.value.isnumeric():
            plays = int(key_in.value)
        else:
            plays = 10

        ga.auto(strategy, plays)
        update_buttons()

    def make_play(dir):
        ga.pack(dir)
        update_buttons()


    def on_keyrelease(event_data):
        arrowkeys = {111: 'u', 116: 'd', 113: 'l', 114: 'r'}

        if event_data.key == 'q':
            app.destroy()
        else:
            key = event_data.tk_event.keycode
            if key in arrowkeys:
                dir = arrowkeys[key]
                make_play(dir)
                key_in.clear()

    N=8

    colors = set_colors()

    ga = GameArray(N)
    ROUNDS = 0

    app = App(title='Classy 2048', width=800, height=800, bg='white')
    wspace1 = Text(app, width=30, height=2)
    box1 = Box(app, layout='grid')
    grid_btns = [PushButton(box1, text=str(i), grid=[i%N, int(i/N)], width=6, height=3) for i in range(N*N)]

    wspace2 = Text(app, width=30, height=2)
    box2 = Box(app, layout='grid')

    counter = Text(box2, text='Rounds: ', grid=[0, 0], width=30, align='left')
    score = Text(box2, text='Score: ', grid=[1, 0], width=30, align='right')

    wspace3 = Text(app, width=30, height=2)
    box3 = Box(app, layout='grid')

    key_in = TextBox(box3, text='', grid=[0, 0], align = 'left', width=3)
    key_in.when_key_released = on_keyrelease
    key_in.focus()

    auto_b1 = PushButton(box3, text = 'L-R', command=auto_play, args=['l-r'], grid=[1, 0], width=5)
    auto_b1.bg = 'white'
    auto_b1.text_color = 'red'

    auto_b2 = PushButton(box3, text = 'U-D', command=auto_play, args=['u-d'], grid=[2, 0], width=5)
    auto_b2.bg = 'white'
    auto_b2.text_color = 'red'

    auto_b3 = PushButton(box3, text = 'CRNRS', command=auto_play, args=['l-u-r-d'], grid=[3, 0], width=5)
    auto_b3.bg = 'white'
    auto_b3.text_color = 'red'


    update_buttons()

    app.display



def main_txt():
    LOOP_SIZE = 3000

    ga = GameArray(5)

    plays = 1
    i = 0
    buffer = ''
    running = True
    while running:
        if ga.full():
            running = False

        if running:
            ga.print('Round {0:,}:'.format(ga.rounds()+1))
            if buffer:
                prompt = '<enter> to repeat last command (' + buffer + ')'
            else:
                prompt = 'Pack direction? (u, d, l, r)'
            prompt = prompt + ' -- q to quit: '
            raw_input = input(prompt)
            print('\n' * 2)
            if not raw_input:
                raw_input = buffer
            else:
                buffer = raw_input
            raw_input = buffer.split()
            direction = raw_input[0]
            if direction == 'q':
                running = False
            else:
                if len(raw_input) > 1:
                    plays = int(raw_input[1])

                if len(direction) == 1:
                    ga.pack(direction)
                else:
                    ga.auto(direction, plays)

    ga.print('Final in round {0:,}:'.format(ga.rounds() + 1))
    print(' '* 2 + '-' * 5, '{0} {1:>8,}'.format('Score', ga.score()), '-' * 5)
    print(' '* 2 + '-' * 5, '{0} {1:>8,}'.format('  Max', ga.max()), '-' * 5)
    print()



if __name__ =='__main__':
    main_txt()

