class CFG:
    def __init__(self, grammar):
        lines = grammar.split('\n')
        self.definitions = {}
        for line_num, line in enumerate(lines):
            line = line.strip()
            if len(line) == 0:
                continue
            key, = line.split(' ')
            if line_num == 0:
                self.start = key
            self.definitions[key] = line

    def define(self, key):
        if type(self.definitions[key]) != str:
            return self.definitions[key]

        functions = []

        _, to_define = self.definitions[key].split('->')

        to_define = map(lambda x: x.strip(), to_define.split(' | '))

        return tuple(map(self.decode, to_define))

    def decode(self, string):
        rules = string.split(' ')

        def function():
            return 'hi'

        return function
