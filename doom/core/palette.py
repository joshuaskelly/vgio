class Color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return '<{0} r={1} g={2} b={3}>'.format(self.__class__.__name__, self.r, self.g, self.b)

class Palette(object):
    def __init__(self, colors, index):
        self.__colors = [Color(c.r, c.g, c.b) for c in colors[index * 256:(index + 1) * 256]]

        self.index = index

    def __getitem__(self, key):
        return self.__colors[key]

    def __len__(self):
        return 256

    def __repr__(self):
        return '<{0} index={1}>'.format(self.__class__.__name__, self.index)
