class PrintOut:
    def __init__(self, depths=('|', '-', '.'), key=None):
        if key is None:
            key = dict()
        self.__depths = depths
        self.key = key

    def show_key(self):
        print('Key:')
        for key, value in self.key.items():
            print(f'  {key} : [{value}]')

    @staticmethod
    def start_up():
        print('starting')

    def depth(self, index):
        if index >= len(self.__depths):
            print(self.__depths[-1], end='')
        else:
            print(self.__depths[index], end='')
