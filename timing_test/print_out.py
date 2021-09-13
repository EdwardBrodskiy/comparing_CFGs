class PrintOut:
    def __init__(self, depths=('|', '-', '.')):
        self.__depths = depths

    @staticmethod
    def start_up():
        print('starting')

    def depth(self, index):
        if index >= len(self.__depths):
            print(self.__depths[-1], end='')
        else:
            print(self.__depths[index], end='')
