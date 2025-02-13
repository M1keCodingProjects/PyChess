CELL_WALL_H         = '─' * 4
LABEL_SPACING_AMT   = 2
LABEL_SPACING       = ' ' * LABEL_SPACING_AMT
AFTER_LABEL_SPACING = ' ' * (LABEL_SPACING_AMT - 1)

from enum import Enum, StrEnum
from typing import Self
class Corner(StrEnum):
    Top    = "┌┬┐"
    Middle = "├┼┤"
    Bottom = "└┴┘"

    def __str__(self):
        return self.name + ":" + self.value

def getHorizontalChessboardLine(pos:Corner) -> str:
    corners = pos.value
    return LABEL_SPACING + corners[0] + CELL_WALL_H + (corners[1] + CELL_WALL_H) * 7 + corners[2] + "\n"

@DeprecationWarning
def getPieceChessboardLine(*, isBlack:bool) -> str:
    return "│ " + "  │ ".join(list("♖♘♗♕♔♗♘♖" if isBlack else "♜♞♝♛♚♝♞♜")) + "  │\n" 

@DeprecationWarning
def getPawnsChessboardLine(*, isBlack:bool) -> str:
    return "│" + f" {'♙' if isBlack else '♟' }  │" * 8 + "\n"

def iotaGen(start = 0):
    while True:
        start += 1
        yield start

iota = iotaGen()

class ChessFile(Enum):
    a = next(iota)
    b = next(iota)
    c = next(iota)
    d = next(iota)
    e = next(iota)
    f = next(iota)
    g = next(iota)
    h = next(iota)

    def asLabel(self) -> str: return f"  {repr(self)}  "

    def __repr__(self) -> str: return self.name

class Pos:
    def __init__(self, file:ChessFile, rank:int) -> None:
        self.file, self.rank = file, rank

    @staticmethod
    def createFromRaw(pos:str) -> "Pos":
        # Factory method
        return Pos(ChessFile[pos[0]], int(pos[1]))

    def isEqualTo(self, file:int, rank:int) -> bool: return self.getCoords() == (file, rank)

    def getCoords(self) -> tuple[int, int]: return self.file.value, self.rank

    def __repr__(self) -> str: return ", ".join(map(str, self.getCoords()))

class Piece:
    REPR = ""
    def __init__(self, pos:Pos, *, isBlack):
        self.pos, self.isBlack = pos, isBlack
    
    def __repr__(self) -> str: return self.REPR[self.isBlack]

class King(Piece):
    REPR = "♚♔"

class Bishop(Piece):
    REPR = "♝♗"

class Rook(Piece):
    REPR = "♜♖"

class Pawn(Piece):
    REPR = "♟♙"

class Knight(Piece):
    REPR = "♞♘"

class Queen(Piece):
    REPR = "♛♕"

def buildChessboard(pieces:list[Piece]) -> str:
    LINE_SEPARATOR = getHorizontalChessboardLine(Corner.Middle)
    
    FILE_LABELS = "  " + "".join(map(ChessFile.asLabel, map(ChessFile, range(1, 9)))) + '\n'
    chessboard  = FILE_LABELS + getHorizontalChessboardLine(Corner.Top)
    for rank in range(8, 0, -1):
        chessboard += LINE_SEPARATOR * (rank < 8) + str(rank) + AFTER_LABEL_SPACING
        for file in range(1, 9):
            for piece in pieces:
                if piece.pos.isEqualTo(file, rank):
                    chessboard += f"│ {piece}  "
                    break
            else:
                chessboard += "│    "
        
        chessboard += f"│{AFTER_LABEL_SPACING + str(rank)}\n"

    chessboard += getHorizontalChessboardLine(Corner.Bottom) + FILE_LABELS
    return chessboard

turn   = 0
PIECES = []
def setupPieces() -> None:
    global PIECES
    PIECES = []
    for i in (False, True):
        rank = 1 + 7 * i
        for j in (False, True):
            PIECES.append(Rook(  Pos(ChessFile(1 + 7 * j), rank), isBlack = i))
            PIECES.append(Knight(Pos(ChessFile(2 + 5 * j), rank), isBlack = i))
            PIECES.append(Bishop(Pos(ChessFile(3 + 3 * j), rank), isBlack = i))
    
        PIECES.append(Queen(Pos(ChessFile.d, rank), isBlack = i))
        PIECES.append(King(Pos(ChessFile.e, rank), isBlack = i))
        PIECES.extend([ Pawn(Pos(ChessFile(pos), 2 + 5 * i), isBlack = i) for pos in range(1, 9) ])

iota = iotaGen()
class GameCommand(Enum):
    quit = next(iota)

    @staticmethod
    def create(commandName:str) -> Self: return GameCommand[commandName]

def main() -> None:
    global turn
    setupPieces()
    while True:
        print('\n' * 5 * (turn > 0) + buildChessboard(PIECES))
        move = input(f"Turn: {turn}\nInsert your next move as {"black" if turn % 2 else "white"}: ")
        if move == GameCommand.quit.name: return
        
        turn += 1

if __name__ == '__main__':
    main()

#TODO: move timer