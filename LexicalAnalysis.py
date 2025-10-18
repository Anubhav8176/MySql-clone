from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


# A function for Lexical Analysis
class TokenType(Enum):

    # Keywords
    SELECT = "SELECT"
    DELETE = "DELETE"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    TABLE = "TABLE"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT = "INSERT"
    INTO = "INTO"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    #Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "NULL"

    IDENTIFIER = "IDENTIFIER"

    # Operators
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUALS = "<="
    GREATER_EQUALS = ">="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"

    # Symbols
    LPAREN = "("
    RPAREN = ")"
    COMMA = ","
    SEMICOLON = ";"
    DOT = "."

    # Special
    EOF = "EOF"


@dataclass
class Token:
    type: TokenType
    value: any
    position: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"



class LexicalAnalysis:

    def __init__(self, text: str):

        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None

        self.keywords = {
            'SELECT': TokenType.SELECT,
            'DELETE': TokenType.DELETE,
            'CREATE': TokenType.CREATE,
            'UPDATE': TokenType.UPDATE,
            'TABLE': TokenType.TABLE,
            'FROM': TokenType.FROM,
            'WHERE': TokenType.WHERE,
            'INSERT': TokenType.INSERT,
            'INTO': TokenType.INTO,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
        }

    # Displaying the error
    def error(self, message: str):
        raise Exception(f"Lexer encountered and error at position {self.position}: {message}")

    # Moving to the next character in the input string.
    def move_forward(self):
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    # Skipping the whitespaces from the input text.
    def skip_whitespaces(self):
        while self.current_char is not None and self.current_char.isspace() :
            self.move_forward()


    # Skipping the comments added in the input text.
    def skip_comments(self):
        while self.current_char is not None and self.current_char != "\n":
            self.move_forward()
        self.move_forward()


    # Look at the next element.
    def observe_next_ele(self, offset: int = 1) -> Optional[str]:
        observe_position = self.position + offset
        if observe_position >= len(self.text):
            return None
        else:
            return self.text[observe_position]


    # Reading the number present in the input string
    def read_number(self) -> Token:

        start_pos = self.position
        number_string = ''

        while self.current_char is not None and self.current_char.isdigit():
            number_string += self.current_char
            self.move_forward()

        if self.current_char == "." and self.observe_next_ele() and self.observe_next_ele().isdigit():
            number_string += self.current_char
            self.move_forward()

            while self.current_char is not None and self.current_char.isdigit():
                number_string += self.current_char
                self.move_forward()

            return Token(
                type = TokenType.NUMBER,
                position = start_pos,
                value = float(number_string)
            )

        return Token(
            type = TokenType.NUMBER,
            position = start_pos,
            value = int(number_string)
        )

    # Reading the string in the input text
    def read_string(self, quote_char: str) -> Token:
        start_position  = self.position
        final_string = ''
        self.move_forward()

        while self.current_char is not None and self.current_char!=quote_char:

            if self.current_char == "\\":
                self.move_forward()
                if self.current_char == "n":
                    final_string += "\n"
                elif self.current_char == "t":
                    final_string += "\t"
                elif self.current_char == "\\":
                    final_string += "\\"
                elif self.current_char == quote_char:
                    final_string += quote_char
                else:
                    final_string += self.current_char
                self.move_forward()

            else:
                final_string += self.current_char
                self.move_forward()

        if self.current_char == quote_char:
            self.error(f"Unterminated string at position {start_position}")

        self.move_forward()
        return Token(
            type=TokenType.STRING,
            value=final_string,
            position=start_position
        )


    # Getting the identifiers and keywords from the input string
    def read_identifiers_and_keywords(self) -> Token:
        start_position = self.position

        result_string = ''
        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            result_string += self.current_char
            self.move_forward()

        upper_temp_string = result_string.upper()

        if upper_temp_string in self.keywords:
            token_type = self.keywords[upper_temp_string]
            return Token(
                type=token_type,
                value=upper_temp_string,
                position=start_position
            )

        return Token(
            type=TokenType.IDENTIFIER,
            value=result_string,
            position=start_position
        )


    # Getting the converted token from the input string
    def get_token(self) -> Token:
        while self.current_char is not None:

            # Skipping the spaces
            if self.current_char.isspace():
                self.skip_whitespaces()
                continue

            # Skipping the comments
            if self.current_char=="-" and self.observe_next_ele()=="-":
                self.skip_comments()
                continue

            # Numbers
            if self.current_char.isdigit():
                return self.read_number()

            # Strings
            if self.current_char in ("'", '"'):
                return self.read_string(self.current_char)

            # Identifiers and Keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifiers_and_keywords()

            # Two-char operators
            if self.current_char == "=" and self.observe_next_ele(1) == "=":
                token = Token(
                    type=TokenType.EQUALS,
                    value="==",
                    position=self.position
                )
                self.move_forward()
                self.move_forward()
                return token

            elif self.current_char == "!" and self.observe_next_ele(1)=="=":
                token = Token(
                    type=TokenType.NOT_EQUALS,
                    value="!=",
                    position=self.position
                )
                self.move_forward()
                self.move_forward()
                return token

            elif self.current_char == "<" and self.observe_next_ele(1)=="=":
                token = Token(
                    type=TokenType.LESS_EQUALS,
                    value="<=",
                    position=self.position
                )
                self.move_forward()
                self.move_forward()
                return token

            elif self.current_char == ">" and self.observe_next_ele(1)=="=":
                token = Token(
                    type=TokenType.GREATER_EQUALS,
                    value=">=",
                    position=self.position
                )
                self.move_forward()
                self.move_forward()
                return token

            # Single-char operators
            single_char_tokens = {
                '=': TokenType.EQUALS,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '.': TokenType.DOT,
            }

            if self.current_char in single_char_tokens:
                token_type = single_char_tokens[self.current_char]
                token = Token(
                    type=token_type,
                    value=self.current_char,
                    position=self.position
                )
                self.move_forward()
                return token

            self.error(f"Unexpected character: {self.current_char!r}")

        return Token(TokenType.EOF, None, self.position)


    def tokenise(self) -> List[Token]:
        tokens = []
        while True:
            token = self.get_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break

        return tokens


sql_command = "SELECT * FROM user WHERE age > 20"
lexical = LexicalAnalysis(sql_command)
result_tokens = lexical.tokenise()

print(f"The command after lexical analysis => {result_tokens}")
