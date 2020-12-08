import string


class WrongCharacterError(Exception):
    def __init__(self):
        super().__init__('Неверный символ!')


class AlreadyDeclaredError(Exception):
    def __init__(self):
        super().__init__('Variable was declared again!')


class TypesMismatchError(Exception):
    def __init__(self):
        super().__init__('Types mismatch!')


class NotDeclaredError(Exception):
    def __init__(self):
        super().__init__('Variable was not declared!')


class Lexer(object):
    def __init__(self, input_file):
        self.ch = ''
        self.line = 1
        self.ch_pos = 0
        self.keywords = self.get_keywords()
        self.delims = self.get_delims()
        self.digits = dict()
        self.identifiers = dict()
        self.lexems = []
        self.input_file = input_file
        self.text = ''
        with open(input_file) as f:
            self.text = f.read()
        self.current_index = -1
        self.buffer = ''
        self.alphabet = set(string.ascii_letters)
        self.hexa_lets = set('ABCDEFabcdef0123456789')
        self.digits_chars = set(string.digits)

    def run(self):
        while True:
            try:
                self.ch = self._gc()
                if self.ch == ' ':
                    continue
                if self.ch in self.delims:
                    self._delims()
                if self.ch in self.alphabet:
                    self.buffer += self.ch
                    self.idents()
                if self.ch in self.keywords:
                    self.out(1, self.keywords[self.ch])
                if self.ch is '0' or self.ch is '1':
                    self.buffer += self.ch
                    self.binary()
                if ord('2') <= ord(self.ch) <= ord('7'):
                    self.buffer += self.ch
                    self.octal()
                if self.ch in self.digits_chars:
                    self.buffer += self.ch
                    self.decimal()
                if self.ch == '.':
                    self.buffer += self.ch
                    self.real()
                if not (self.ch in self.delims or self.ch is ' ' or self.ch is '\t' or self.ch in self.keywords):
                    raise WrongCharacterError
            except StopIteration:
                break
            except WrongCharacterError:
                print("Ошибка на {}:{}".format(self.line, self.ch_pos))
                break
        with open("3.txt", "w") as file:
            file.write('\n'.join('%s' % x for x in self.digits))
        with open("4.txt", "w") as file:
            file.write('\n'.join('%s' % x for x in self.identifiers))
        with open('lexems.txt', 'w') as file:
            file.write('\n'.join('%s %s' % x for x in self.lexems))

    def binary(self):
        while True:
            self.ch = self._gc()
            if not (self.ch == '0' or self.ch == '1'):
                break
            self.buffer += self.ch
        if ord('2') <= ord(self.ch) <= ord('7'):
            self.buffer += self.ch
            self.octal()
        elif self.ch == '8' or self.ch == '9':
            self.buffer += self.ch
            self.decimal()
        elif self.ch == '.':
            self.buffer += self.ch
            self.real()
        elif self.ch == 'E' or self.ch == 'e':
            self.buffer += self.ch
            self.exponential()
        elif self.ch == 'O' or self.ch == 'o':
            self.buffer += self.ch
            self.octal_end()
        elif self.ch == 'D' or self.ch == 'd':
            self.buffer += self.ch
            self.decimal_end()
        elif self.ch in set('ACFacf'):
            self.buffer += self.ch
            self.hexadecimal()
        elif self.ch == 'H' or self.ch == 'h':
            self.buffer += self.ch
            self.hexadecimal_end()
        elif self.ch == 'B' or self.ch == 'b':
            self.buffer += self.ch
            try:
                self.ch = self._gc()
            except StopIteration:
                raise WrongCharacterError
            if self.ch in self.hexa_lets:
                self.buffer += self.ch
                self.hexadecimal()
            elif self.ch == 'H' or self.ch == 'h':
                self.buffer += self.ch
                self.hexadecimal_end()
            elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
                self.check_end()
            else:
                raise WrongCharacterError
        elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def octal(self):
        while True:
            self.ch = self._gc()
            if not ord('0') <= ord(self.ch) <= ord('7'):
                break
            self.buffer += self.ch
        if self.ch == '8' or self.ch == '9':
            self.buffer += self.ch
            self.decimal()
        elif self.ch == '.':
            self.buffer += self.ch
            self.real()
        elif self.ch == 'E' or self.ch == 'e':
            self.buffer += self.ch
            self.exponential()
        elif self.ch in set('ABCFabcf'):
            self.buffer += self.ch
            self.hexadecimal()
        elif self.ch == 'H' or self.ch == 'h':
            self.buffer += self.ch
            self.hexadecimal_end()
        elif self.ch == 'D' or self.ch == 'd':
            self.buffer += self.ch
            self.decimal_end()
        elif self.ch == 'O' or self.ch == 'o':
            self.buffer += self.ch
            self.octal_end()
        elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def octal_end(self):
        try:
            self.ch = self._gc()
        except StopIteration:
            raise WrongCharacterError
        if self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def decimal(self):
        while True:
            self.ch = self._gc()
            if self.ch not in self.digits_chars:
                break
            self.buffer += self.ch
        if self.ch == '.':
            self.buffer += self.ch
            self.real()
        elif self.ch == 'E' or self.ch == 'e':
            self.buffer += self.ch
            self.exponential()
        elif self.ch in set('ABCFabcf'):
            self.buffer += self.ch
            self.hexadecimal()
        elif self.ch == 'H' or self.ch == 'h':
            self.buffer += self.ch
            self.hexadecimal_end()
        elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        elif self.ch == 'D' or self.ch == 'd':
            self.decimal_end()

    def decimal_end(self):
        try:
            self.ch = self._gc()
        except StopIteration:
            raise WrongCharacterError
        if self.ch in self.hexa_lets:
            self.buffer += self.ch
            self.hexadecimal()
        if self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def hexadecimal(self):
        while True:
            self.ch = self._gc()
            if self.ch not in self.hexa_lets:
                break
            self.buffer += self.ch
        if self.ch == 'H' or 'h':
            self.buffer += self.ch
            self.hexadecimal_end()

    def hexadecimal_end(self):
        try:
            self.ch = self._gc()
        except StopIteration:
            raise WrongCharacterError
        if self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def check_end(self):
        if self.buffer != '':
            if self.buffer not in self.digits:
                self.digits[self.buffer] = len(self.digits) + 1
                self.out(3, self.digits[self.buffer])
                self.buffer = ''
            else:
                self.out(3, self.digits[self.buffer])
                self.buffer = ''
            if self.ch in self.delims:
                self._delims()

    def real(self):
        while True:
            self.ch = self._gc()
            if self.ch not in self.digits_chars:
                break
            self.buffer += self.ch
        if self.ch == 'E' or self.ch == 'e':
            self.buffer += self.ch
            self.exponential()
        elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
            self.check_end()
        else:
            raise WrongCharacterError

    def exponential(self):
        self.ch = self._gc()
        if self.ch in set('ABCDEFabcdef'):
            self.buffer += self.ch
            self.hexadecimal()
        elif self.ch == 'H' or self.ch == 'h':
            self.hexadecimal_end()
        elif self.ch == '+' or self.ch == '-':
            self.buffer += self.ch
            while True:
                self.ch = self._gc()
                if self.ch not in self.digits_chars:
                    break
                self.buffer += self.ch
            if self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
                self.check_end()
            else:
                raise WrongCharacterError
        else:
            while True:
                self.ch = self._gc()
                if self.ch not in self.digits_chars:
                    break
                self.buffer += self.ch
            if self.ch in set('ABCDEFabcdef'):
                self.buffer += self.ch
                self.hexadecimal()
            elif self.ch == 'H' or self.ch == 'h':
                self.hexadecimal_end()
            elif self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
                self.check_end()
            else:
                raise WrongCharacterError

    def idents(self):
        while True:
            self.ch = self._gc()
            if self.ch not in self.digits_chars | self.alphabet:
                break
            self.buffer += self.ch
        if self.buffer in self.keywords:
            self.out(1, self.keywords[self.buffer])
            if self.ch in self.delims:
                self._delims()
        elif self.buffer in self.delims:
            self.out(2, self.delims[self.buffer])
            if self.ch in self.delims:
                self._delims()
        else:
            if self.ch == '\t' or self.ch == ' ' or self.ch in self.delims:
                if self.buffer not in self.identifiers:
                    self.identifiers[self.buffer] = len(self.identifiers) + 1
                    self.out(4, self.identifiers[self.buffer])
                    self.buffer = ''
                else:
                    self.out(4, self.identifiers[self.buffer])
                    self.buffer = ''
            if self.ch in self.delims:
                self._delims()

    def _delims(self):
        if self.ch == '/':
            cur = self._gc()
            if cur == '*':
                while True:
                    next = self._gc()
                    if next == '*':
                        prev = self._gc()
                    elif next == '\n':
                        self.ch_pos = 0
                        self.line += 1
                    elif next == '}':
                        raise WrongCharacterError
                    elif next == '/' and prev == '*':
                        break
            else:
                self.buffer += self.ch
                self.out(2, self.delims[self.buffer])
                self.ch = self.prev_char()
        elif self.ch == '<':
            self.buffer += self.ch
            cur = self._gc()
            if cur == '>':
                self.buffer += cur
                self.out(2, self.delims[self.buffer])
            elif cur == '=':
                self.buffer += cur
                self.out(2, self.delims[self.buffer])
            else:
                self.buffer += self.ch
                self.out(2, self.delims[self.buffer])
                self.ch = self.prev_char()
        elif self.ch == '>':
            self.buffer += self.ch
            cur = self._gc()
            if cur == '=':
                self.buffer += cur
                self.out(2, self.delims[self.buffer])
            else:
                self.out(2, self.delims[self.buffer])
                self.ch = self.prev_char()
        elif self.ch == '}':
            self.buffer += self.ch
            self.out(2, self.delims[self.buffer])
            raise StopIteration
        else:
            if self.ch == '\n':
                self.ch_pos = 0
                self.line += 1
            self.buffer += self.ch
            self.out(2, self.delims[self.buffer])

    def out(self, n, k):
        self.lexems.append((n, k))
        self.buffer = ''

    def get_keywords(self):
        filename = '1.txt'
        keywords = {}
        i = 1
        with open(filename) as f:
            for line in f.readlines():
                keywords[line.rstrip()] = i
                i += 1
        return keywords

    def get_delims(self):
        filename = '2.txt'
        delims = {}
        i = 1
        with open(filename) as f:
            for line in f.readlines():
                strip_line = line.rstrip()
                if strip_line != '':
                    delims[line.rstrip()] = i
                else:
                    delims['\n'] = i
                i += 1
        return delims

    def _gc(self):
        self.current_index += 1
        return self.text[self.current_index]

    def prev_char(self):
        self.current_index -= 1
        return self.text[self.current_index]


class Identifier(object):
    def __init__(self, value, _type=None):
        self.type = _type
        self.value = value

    def __repr__(self):
        return f'{self.type} {self.value}'

    def __eq__(self, other):
        return self.value == other.value


class Lexeme(object):
    def __init__(self, table, position):
        self.table = table
        self.position = position


class Parser(object):

    def __init__(self, lexer: Lexer):
        self.keywords = list(lexer.keywords.keys())
        self.delimiters = list(lexer.delims.keys())
        self.digits = list(lexer.digits.keys())
        self.identifiers = list(lexer.identifiers.keys())
        self.lexems = lexer.lexems
        self.tables = [list()] * 5
        self.tables[1] = self.keywords
        self.tables[2] = self.delimiters
        self.tables[3] = self.digits
        self.tables[4] = self.identifiers
        for table in self.tables:
            table.insert(0, None)
        self.lexems = lexer.lexems
        self.lexeme = None
        self.next = ''
        self.line = 1
        self.column = 0
        self.declared_idents = []
        self.expr_stack = []

    def run(self):
        try:
            if self.program():
                result = 'Ok'
            else:
                result = 'Syntax error at ' + str(self.line) + ':' + str(self.column)
        except RecursionError:
            result = 'Syntax error at ' + str(self.line) + ':' + str(self.column)
        except AlreadyDeclaredError:
            result = 'Variable \'' + self.next + '\' has already been declared at ' + str(self.line) + ':' + str(
                self.column)
        except TypesMismatchError:
            result = 'Types mismatch at ' + str(self.line) + ':' + str(
                self.column)
        except NotDeclaredError:
            result = 'Variable \'' + self.next + '\' has not been declared at ' + str(self.line) + ':' + str(
                self.column)
        print(result)

    def program(self):
        self.get_next()
        if self.next != '{':
            return False
        self.get_next()
        while True:
            if not (self.declaration() or self.complex_operator()):
                return False
            if not self.next == ';':
                return False
            self.get_next()
            if self.next == '}':
                break
        return True

    def get_next(self):
        lexeme = self.lexems.pop(0)
        self.lexeme = Lexeme(lexeme[0], lexeme[1])
        self.next = self.tables[lexeme[0]][lexeme[1]]
        self.column += 1

    def declaration(self):
        if not self.type():
            return False
        _type = self.next
        self.get_next()
        if self.lexeme.table != 4:
            return False
        id = Identifier(self.next, _type)
        if id in self.declared_idents:
            raise AlreadyDeclaredError
        self.declared_idents.append(id)
        self.get_next()
        while self.next == ',':
            self.get_next()
            if self.lexeme.table != 4:
                return False
            id = Identifier(self.next, _type)
            if id in self.declared_idents:
                raise AlreadyDeclaredError
            self.declared_idents.append(id)
            self.get_next()
        return True

    def complex_operator(self):
        if not self.operator():
            return False
        while self.next in ':\n':
            self.line += 1
            self.column = 0
            self.get_next()
            if not self.operator():
                return False
        return True

    def type(self):
        return self.next in '%!$'

    def operator(self):
        return self.assign() or self.condition() or self.for_loop() or self.while_loop() or \
               self.input() or self.output() or self.complex_operator()

    def assign(self):
        if not self.identifier():
            return False
        i = self.declared_idents.index(Identifier(self.next))
        _type = self.declared_idents[i].type
        self.get_next()
        if self.next != 'ass':
            return False
        self.get_next()
        if not self.expression():
            return False
        self.check_ass_type(_type, self.expr_stack.pop())
        return True

    def condition(self):
        if self.next != 'if':
            return False
        self.get_next()
        if not self.expression():
            return False
        if self.expr_stack.pop() != '$':
            raise TypesMismatchError
        if self.next != 'then':
            return False
        self.get_next()
        if not self.complex_operator():
            return False
        if self.next == 'else':
            self.get_next()
            return self.complex_operator()
        return True

    def for_loop(self):
        if self.next != 'for':
            return False
        self.get_next()
        if not self.assign():
            return False
        if self.next != 'to':
            return False
        self.get_next()
        if not self.expression():
            return False
        if self.expr_stack.pop() != '$':
            raise TypesMismatchError
        if self.next != 'do':
            return False
        self.get_next()
        return self.complex_operator()

    def while_loop(self):
        if self.next != 'while':
            return False
        self.get_next()
        if not self.expression():
            return False
        if self.expr_stack.pop() != '$':
            raise TypesMismatchError
        if self.next != 'do':
            return False
        self.get_next()
        return self.complex_operator()

    def input(self):
        if self.next != 'read':
            return False
        self.get_next()
        if self.next != '(':
            return False
        self.get_next()
        if not self.identifier():
            return False
        self.get_next()
        while self.next == ',':
            self.get_next()
            if not self.identifier():
                return False
            self.get_next()
        if self.next != ')':
            return False
        self.get_next()
        return True

    def output(self):
        if self.next != 'write':
            return False
        self.get_next()
        if self.next != '(':
            return False
        self.get_next()
        if not self.expression():
            return False
        while self.next == ',':
            self.get_next()
            if not self.expression():
                return False
            self.get_next()
        if self.next != ')':
            return False
        self.get_next()
        return True

    def identifier(self):
        if not self.lexeme.table == 4:
            return False
        if not Identifier(self.next) in self.declared_idents:
            raise NotDeclaredError
        self.push_id()
        return True

    def expression(self):
        self.expr_stack.clear()
        if not self.operand():
            return False
        while self.relation_operators():
            self.get_next()
            if not self.operand():
                return False
        self.check_types()
        return True

    def check_types(self):
        while len(self.expr_stack) > 1:
            op_2 = self.expr_stack.pop()
            operation = self.expr_stack.pop()
            if operation == 'not':
                self.check_unary(op_2)
            else:
                op_1 = self.expr_stack.pop()
                self.check_operation(op_2, operation, op_1)

    def check_operation(self, op_2, operation, op_1):
        if operation in '+-*':
            if op_1 == '$' or op_2 == '$':
                raise TypesMismatchError
            if op_1 == '%' or op_2 == '%':
                self.expr_stack.append('%')
            else:
                self.expr_stack.append('!')
        elif operation == '/':
            if op_1 == '$' or op_2 == '$':
                raise TypesMismatchError
            else:
                self.expr_stack.append('%')
        elif operation == 'or' or operation == 'and':
            if op_1 != '$' or op_2 != '$':
                raise TypesMismatchError
            self.expr_stack.append('$')
        else:
            if op_1 == '$' or op_2 == '$':
                raise TypesMismatchError
            self.expr_stack.append('$')

    def check_unary(self, operand):
        if operand == '$':
            self.expr_stack.append('$')
        else:
            raise TypesMismatchError

    def relation_operators(self):
        if self.next == '<>' or self.next == '=' or self.next == '<' or \
                self.next == '<=' or self.next == '>' or self.next == '>=':
            self.push_operation()
            return True
        else:
            return False

    def operand(self):
        if not self.term():
            return False
        while self.add_operation():
            self.get_next()
            if not self.term():
                return False
        return True

    def push_logical(self):
        self.expr_stack.append('$')

    def push_id(self):
        i = self.declared_idents.index(Identifier(self.next))
        _type = self.declared_idents[i].type
        self.expr_stack.append(_type)

    def push_operation(self):
        self.expr_stack.append(self.next)

    def push_number(self):
        number = self.next
        try:
            int(number)
            self.expr_stack.append('!')
        except ValueError:
            try:
                float(number)
                self.expr_stack.append('%')
            except ValueError:
                try:
                    int(number[:-1], 2)
                    self.expr_stack.append('!')
                except ValueError:
                    try:
                        int(number[:-1], 8)
                        self.expr_stack.append('!')
                    except ValueError:
                        int(number[:-1], 16)
                        self.expr_stack.append('!')

    def term(self):
        if not self.multiplier():
            return False
        self.get_next()
        while self.mult_operation():
            self.get_next()
            if not self.multiplier():
                return False
            self.get_next()
        return True

    def add_operation(self):
        if self.next == '+' or self.next == '-' or self.next == 'or':
            self.push_operation()
            return True
        else:
            return False

    def multiplier(self):
        if self.unary():
            self.get_next()
            return self.multiplier()
        elif self.next == '(':
            self.get_next()
            if not self.expression():
                return False
            return self.next == ')'
        elif self.identifier() or self.logical() or self.number():
            return True
        else:
            return False

    def mult_operation(self):
        if self.next == '*' or self.next == '/' or self.next == 'and':
            self.push_operation()
            return True
        else:
            return False

    def unary(self):
        if self.next == 'not':
            self.push_operation()
            return True
        else:
            return False

    def logical(self):
        if self.next == 'true' or self.next == 'false':
            self.push_logical()
            return True
        else:
            return False

    def number(self):
        if self.lexeme.table == 3:
            self.push_number()
            return True
        else:
            return False

    def check_ass_type(self, left, right):
        if left == '$' and not right == '$':
            raise TypesMismatchError
        if left == '!' and not right == '!':
            raise TypesMismatchError
        if left == '%' and not right == '%':
            raise TypesMismatchError


if __name__ == "__main__":
    lexer = Lexer('src.txt')
    lexer.run()
    parser = Parser(lexer)
    parser.run()