
class colours():
    BOLD_WHITE = '\033[1m\033[37m'
    FAINT_WHITE = '\033[2m\033[37m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    GREY = '\033[37m'
    RESET = '\033[0m'

    def no_colours(self):
        self.BOLD_WHITE=''
        self.FAINT_WHITE=''
        self.RED=''
        self.YELLOW=''
        self.GREEN=''
        self.GREY=''
        self.RESET=''

    def get_colours(self):
        return [self.BOLD_WHITE,
                self.FAINT_WHITE,
                self.RED,
                self.YELLOW,
                self.GREEN,
                self.GREY]

    def get_colour_code(self):
        for i in range(0,8):
            print('\033[3'+str(i)+'m', '033[3'+str(i)+'m')

clr=colours()

if __name__=='__main__':
    for c in clr.get_colours():
        print(c, '[clr]')

    clr.get_colour_code()
