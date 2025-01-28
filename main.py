CELL_WALL_H = '─' * 4

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
    return corners[0] + CELL_WALL_H + (corners[1] + CELL_WALL_H) * 7 + corners[2] + "\n"

def getPieceChessboardLine(*, isBlack:bool) -> str:
    return "│ " + "  │ ".join(list("♖♘♗♕♔♗♘♖" if isBlack else "♜♞♝♛♚♝♞♜")) + "  │\n" 

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

class Pos:
    def __init__(self, file:ChessFile, rank:int) -> None:
        self.file, self.rank = file, rank

    @staticmethod
    def createFromRaw(pos:str) -> "Pos":
        # Factory method
        return Pos(ChessFile[pos[0]], int(pos[1]))

    def isEqualTo(self, pos:tuple[int, int]) -> bool: return self.getCoords() == pos

    def getCoords(self) -> tuple[int, int]: return self.file.value, self.rank

class Piece:
    REPR = ""
    def __init__(self, pos:Pos, *, isBlack):
        self.pos, self.isBlack = pos, isBlack
    
    def __repr__(self) -> str: return self.REPR[self.isBlack]

class King(Piece):
    REPR = "♔♚"

class Bishop(Piece):
    pass

def buildChessboard(pieces:list[Piece]) -> str:
    top  = getHorizontalChessboardLine(Corner.Middle)
    cell = "│    " * 8 + "│\n"
    
    chessboard  = getHorizontalChessboardLine(Corner.Top)
    chessboard += getPieceChessboardLine(isBlack = True)
    chessboard += top + getPawnsChessboardLine(isBlack = True)

    for rank in range(4):
        chessboard += top
        for file in range(8):
            for piece in pieces:
                chessboard += "│ {:3s}".format(repr(piece) * (not piece.pos.isEqualTo((rank, file))))
        
        chessboard += '\n'

    chessboard += top
    chessboard += getPawnsChessboardLine(isBlack = False) + top
    chessboard += getPieceChessboardLine(isBlack = False)
    chessboard += getHorizontalChessboardLine(Corner.Bottom)

    return chessboard

def main() -> None:
    whiteKing = King(Pos.createFromRaw("e1"), isBlack = False)
    blackKing = King(Pos(ChessFile.e, 8), isBlack = True)

    print(buildChessboard([whiteKing, blackKing]))

if __name__ == '__main__':
    # p = Pos.createFromRaw("e5")
    # print(p.getCoords())
    main()