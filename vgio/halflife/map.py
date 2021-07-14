"""This module provides file I/O for Half-Life MAP map files.

Example:
    map_file = map.Map.open('example.map')
"""

import re


__all__ = ['ParseError', 'Entity', 'Brush', 'Plane', 'loads', 'dumps']


class ParseError(Exception):
    def __init__(self, message, location):
        super().__init__(message + ' line {0}, column {1}'.format(location[0], location[1]))
        self.location = location


class Entity:
    """Class for representing Map Entity data

    Note:
        Entity properties will be set as attributes.

    Attributes:
        brushes: A list of Brush objects.
    """
    def __init__(self, brushes):
        self.brushes = brushes


class Brush:
    """Class for representing Brush data

    Attributes:
        planes: A list of Plane objects
    """

    __slots__ = (
        'planes'
    )

    def __init__(self, planes):
        self.planes = planes


class Plane:
    """Class for representing planes(faces) of a Brush.

    Attributes:
        points: A triple of XYZ three-tuples representing three non-collinear
            points contained in the plane.

        texture_name: Name of the bsp.Miptexture

        s: An XYZ triple representing the s-vector of the texture plane in
            world space.

        s_offset: The offset along the s-vector.

        t: An XYZ triple representing the t-vector of the texture plane in
            world space.

        t_offset: The offset along the t-vector.

        rotation: The texture rotation angle in degrees.

        scale: The texture scale represented as an ST two-tuple.
    """

    __slots__ = (
        'points',
        'texture_name',
        's',
        's_offset',
        't',
        't_offset',
        'rotation',
        'scale'
    )

    def __init__(self,
                 points,
                 texture_name,
                 s,
                 s_offset,
                 t,
                 t_offset,
                 rotation,
                 scale):

        self.points = points
        self.texture_name = texture_name
        self.s = s
        self.s_offset = s_offset
        self.t = t
        self.t_offset = t_offset
        self.rotation = rotation
        self.scale = scale


def loads(s):
    """Deserializes string s into Entity objects

    Args:
        s: A string containing a Map document.

    Returns:
        A list of Entity objects.

    Raises:
        ParseError: If fails to parse given document
    """

    class StringLiteral:
        def __init__(self, id):
            self.id = id

    class NumericLiteral:
        def __init__(self, id):
            self.id = id

    class Symbol:
        def __init__(self, id):
            self.id = id

    class EndToken:
        pass

    separator_pattern = '\B([{}\(\)\[\]])\B'
    comment_pattern = '(\/\/.*)'
    quoted_literal_pattern = '(?:\"(.+?)\")'
    numeric_literal_pattern = '(-?\d+\.?\d*(?:e-\d+)?)\\b'
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
        """Transforms the given Map document into a sequence of tokens.

        Args:
            program: A string containing a Map document.

        Yields:
            The next token in the sequence. After all input has been processed
            the EndToken object will be yielded.
        """

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
        """Verifies the current token(if id_or_class is given) and proceeds
        to the next token.

        Args:
            id_or_class: A string, a class, or None. If not None, the current
                token will be compared against the given value.

        Returns:
            The previous token

        Raises:
            ParseError: If expected symbol is not found.
        """

        nonlocal token

        if id_or_class:
            expect(id_or_class)

        previous = token
        token = next()

        return previous

    def expect(id_or_class):
        """Verifies current token, raises if not equal to the given id_or_class

        Args:
            id_or_class: The string or class to compare against

        Raises:
            ParseError: If expected symbol is not found
        """

        nonlocal token
        error_message = 'Expected "{0}" got "{1}"'

        # Verify token value
        if isinstance(id_or_class, str):
            if id_or_class and id_or_class != token.id:
                error(error_message.format(id_or_class, token.id))

        # Verify token class
        else:
            if id_or_class and not isinstance(token, id_or_class):
                error(error_message.format(id_or_class, token))

    def parse():
        """Main point of entry for parsing Map documents. Creates a list of
        Entity objects from the token stream.

        Returns:
            A list of Entity objects
        """
        nonlocal token
        entities = []

        while not isinstance(token, EndToken):
            entities.append(parse_entity())

        return entities

    def parse_entity():
        """Creates an Entity object from the token stream.

        Returns:
            An Entity object
        """

        nonlocal token
        e = Entity([])
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
        """Creates a key-value pair from the token stream.

        Returns:
            A key-value pair tuple
        """

        nonlocal token
        key = advance(StringLiteral)

        if isinstance(token, StringLiteral) or isinstance(token, NumericLiteral):
            value = token

        else:
            error('Unexpected symbol: "{0}"'.format(token.id))

        token = next()

        return key.id, value.id

    def parse_brush():
        """Creates a Brush object from the token stream.

        Returns:
            A Brush object.
        """
        nonlocal token
        advance('{')

        # Parse planes
        planes = []
        while token.id != '}':
            # Parse points that define the plane
            advance('(')
            coord_0 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')
            advance('(')
            coord_1 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')
            advance('(')
            coord_2 = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            advance(')')

            points = coord_0, coord_1, coord_2

            # Parse texture name
            texture_name = advance(StringLiteral).id

            # Parse s-vector information
            advance('[')
            s = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            s_offset = advance(NumericLiteral).id
            advance(']')

            # Parse t-vector information
            advance('[')
            t = advance(NumericLiteral).id, advance(NumericLiteral).id, advance(NumericLiteral).id
            t_offset = advance(NumericLiteral).id
            advance(']')

            # Parse rotation and scale
            rotation = advance(NumericLiteral).id
            scale = advance(NumericLiteral).id, advance(NumericLiteral).id

            plane = Plane(
                points,
                texture_name,
                s,
                s_offset,
                t,
                t_offset,
                rotation,
                scale
            )
            planes.append(plane)

        advance('}')

        return Brush(planes)

    def error(message):
        """Raises an exception with the given message. Also provides the
        row and column information as to where the error occurred.

        Attributes:
            message: The exception message

        Raises:
            ParseError
        """

        nonlocal line, column
        location = line, column

        raise ParseError(message, location)

    next = tokenize(s).__next__
    token = next()

    return parse()


def dumps(entities):
    """Serialize Entity objects to a formatted string.

    Args:
        entities: A sequence of Entity objects.

    Returns:
        A formatted string containing a Map document.
    """

    result = ''

    def number(value):
        int_value = int(value)
        float_value = float(value)

        if int_value == float_value:
            return int_value

        return float_value

    def numbers(seq):
        return (number(s) for s in seq)

    def format(seq):
        return " ".join(map(str, numbers(seq)))

    for entity in entities:

        result += '{\n'
        attrs = tuple(set(entity.__dict__.keys()) - {'brushes'})

        for attr in attrs:
            value = str(getattr(entity, attr))
            result += '"{0}" "{1}"\n'.format(attr, value)

        for brush in entity.brushes:

            result += '{\n'

            for plane in brush.planes:

                x_coord, y_coord, z_coord = plane.points
                name = plane.texture_name
                s_info = plane.s + (plane.s_offset,)
                t_info = plane.t + (plane.t_offset,)
                translation_info = (plane.rotation,) + plane.scale

                plane_text = f'( {format(x_coord)} ) ' \
                             f'( {format(y_coord)} ) ' \
                             f'( {format(z_coord)} ) ' \
                             f'{name} ' \
                             f'[ {format(s_info)} ] ' \
                             f'[ {format(t_info)} ] ' \
                             f'{format(translation_info)}\n'

                result += plane_text

            result += '}\n'

        result += '}\n'

    return result
