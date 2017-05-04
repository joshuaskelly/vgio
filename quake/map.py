"""Module for working with id Software style MAP files

Supported games:
    - QUAKE
"""

import re


__all__ = ['ParseError', 'Entity', 'Brush', 'Plane', 'loads', 'dumps']


class ParseError(Exception):
    pass


class Entity(object):
    def __init__(self):
        self.brushes = []


class Brush(object):
    def __init__(self):
        self.planes = []


class Plane(object):
    def __init__(self):
        self.coords = None
        self.texture_name = None
        self.offset = None
        self.rotation = None
        self.scale = None


def loads(s):
    """Deserializes string s into Python objects

    Args:
        s: A string containing a Map document.

    Returns:
        A list of Entity objects.
    """

    class StringLiteral(object):
        def __init__(self, id):
            self.id = id

    class NumericLiteral(object):
        def __init__(self, id):
            self.id = id

    class Symbol(object):
        def __init__(self, id):
            self.id = id

    class EndToken(object):
        pass

    separator_pattern = '\B([{}\(\)])\B'
    comment_pattern = '(\/\/.*)'
    quoted_literal_pattern = '(?:\"(.+?)\")'
    numeric_literal_pattern = '(-?\d+\.?\d*)'
    literal_pattern = '([\S\w\/\.]+)'
    white_space_pattern = '([\s\n])'
    rest_pattern = '(.)'

    pattern = '|'.join([separator_pattern,
                        comment_pattern,
                        quoted_literal_pattern,
                        numeric_literal_pattern,
                        literal_pattern,
                        white_space_pattern,
                        rest_pattern])

    pattern = re.compile(pattern)
    token = None
    line = 1
    column = 1

    def tokenize(program):
        nonlocal line, column
        fa = pattern.findall(program)

        for separator, comment, quoted_literal, numeric_literal, literal, white_space, rest in fa:
            if quoted_literal:
                literal = quoted_literal.strip()

            if literal:
                yield StringLiteral(literal)
                column += len(literal)

                if quoted_literal:
                    column += 2

            elif numeric_literal:
                yield NumericLiteral(float(numeric_literal))
                column += len(numeric_literal)

            elif separator:
                yield Symbol(separator)
                column += len(separator)

            elif comment:
                column += len(comment)

            elif white_space:
                if white_space == '\n':
                    line += 1
                    column = 1
                else:
                    column += len(white_space)

            elif rest:
                column += len(rest)

        yield EndToken()

    def advance(id_or_class=None):
        nonlocal token

        if id_or_class:
            expect(id_or_class)

        previous = token
        token = next()

        return previous

    def expect(id_or_class):
        nonlocal token

        if isinstance(id_or_class, str):
            if id_or_class and id_or_class != token.id:
                error('Expected "{0}" got "{1}"'.format(id_or_class, token.id))

        else:
            if id_or_class and not isinstance(token, id_or_class):
                error('Expected "{0}" got "{1}"'.format(id_or_class, token))

    def parse(program):
        nonlocal token
        entities = []

        while not isinstance(token, EndToken):
            entities.append(parse_entity())

        return entities

    def parse_entity():
        nonlocal token

        e = Entity()
        advance('{')

        while token.id != '}':
            if isinstance(token, StringLiteral):
                key, value = parse_property()
                setattr(e, key, value)

            elif token.id == '{':
                e.brushes.append(parse_brush())

            else:
                error('Unexpected symbol: "{0}"'.format(token.id))

        advance('}')

        return e

    def parse_property():
        nonlocal token
        key = advance(StringLiteral)

        if isinstance(token, StringLiteral) or isinstance(token, NumericLiteral):
            value = token

        else:
            raise

        token = next()

        return key.id, value.id

    def parse_brush():
        nonlocal token
        b = Brush()
        advance('{')

        while token.id != '}':
            p = Plane()

            advance('(')
            coord_0 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')
            advance('(')
            coord_1 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')
            advance('(')
            coord_2 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')

            p.coords = coord_0, coord_1, coord_2
            p.texture_name = advance(StringLiteral).id

            p.offset = advance(NumericLiteral).id, advance(NumericLiteral).id
            p.rotation = advance(NumericLiteral).id
            p.scale = advance(NumericLiteral).id, advance(NumericLiteral).id

            b.planes.append(p)

        advance('}')

        return b

    def error(message):
        nonlocal line, column

        location = ' line {0}, column {1}'.format(line, column)
        raise ParseError(message + location)

    next = tokenize(s).__next__
    token = next()

    return parse(s)


def dumps(entities):
    """Serialize Entity objects to a formatted string.

    Args:
        entities: A sequence of Entity objects.

    Returns:
        A formatted string containing a Map document.
    """

    result = ''

    for entity in entities:
        assert(isinstance(entity, Entity))

        result += '{\n'
        attrs = tuple(set(entity.__dict__.keys()) - {'brushes'})

        for attr in attrs:
            value = str(getattr(entity, attr))
            result += '"{0}" "{1}"\n'.format(attr, value)

        for brush in entity.brushes:
            assert(isinstance(brush, Brush))

            result += '{\n'

            for plane in brush.planes:
                assert(isinstance(plane, Plane))

                coords = plane.coords
                name = plane.texture_name
                offset = plane.offset
                rotation = plane.rotation
                scale = plane.scale

                plane_text = '( {0} {1} {2} ) ( {3} {4} {5} ) ( {6} {7} {8} ) {9} {10} {11} {12} {13} {14}\n'
                plane_text = plane_text.format(int(coords[0][0]),
                                               int(coords[0][1]),
                                               int(coords[0][2]),
                                               int(coords[1][0]),
                                               int(coords[1][1]),
                                               int(coords[1][2]),
                                               int(coords[2][0]),
                                               int(coords[2][1]),
                                               int(coords[2][2]),
                                               name,
                                               int(offset[0]),
                                               int(offset[1]),
                                               int(rotation),
                                               scale[0],
                                               scale[1])

                result += plane_text

            result += '}\n'

        result += '}\n'

    return result
