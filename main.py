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

    def copy(self) -> Self: return Pos(self.file, self.rank)

class Piece:
    REPR  = ""
    MOVES = []

    def __init__(self, pos:Pos, *, isBlack) -> None:
        self.pos, self.isBlack = pos, isBlack
        self.isFirstMove = True
    
    def move(self, newPos:Pos) -> None:
        if self._isLegalMove(newPos): self._changePiecePos(newPos)

    def _isLegalMove(self, newPos:Pos) -> bool:
        newFile, newRank = newPos.getCoords()
        file, rank = self.pos.getCoords()
        return (newFile - file, newRank - rank) in self.MOVES

    def _changePiecePos(self, newPos:Pos) -> None:
        self.pos = newPos
        if self.isFirstMove: self.isFirstMove = False

    def __repr__(self) -> str: return self.REPR[self.isBlack]

class King(Piece):
    REPR  = "♚♔"
    MOVES = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    FREE_FILES_SHORT = (ChessFile.f, ChessFile.g)
    FREE_FILES_LONG  = (ChessFile.b, ChessFile.c, ChessFile.d)

    def _isLegalMove(self, newPos):
        if super()._isLegalMove(newPos): return True
        if not self.isFirstMove or newPos.rank != self.pos.rank: return False
        # alternative black magic: newPos.rank != 1 + 7 * self.isBlack

        # if newPos.file == ChessFile.g: ...
        # elif newPos.file == ChessFile.c: ...
        # else: return False
        # ^^^ equivalent to vvv
        isShortCastle = False
        match newPos.file:
            case ChessFile.g: isShortCastle = True
            case ChessFile.c: isShortCastle = False
            case _: return False
        
        rook :Piece = PIECES[isShortCastle * 3 + 16 * self.isBlack]
        if not rook.isFirstMove: return False

        filesToCheck = King.FREE_FILES_SHORT if isShortCastle else King.FREE_FILES_LONG
        for piece in PIECES:
            if piece is self or piece is rook or isinstance(piece, Pawn) and piece.isBlack == self.isBlack: continue
            if piece.pos.rank == self.pos.rank and piece.pos.file in filesToCheck: return False
        
        rook._changePiecePos(Pos(ChessFile(newPos.file.value - 2 * isShortCastle + 1), newPos.rank))
        return True

class Bishop(Piece):
    REPR = "♝♗"

class Rook(Piece):
    REPR = "♜♖"

class Pawn(Piece):
    REPR  = "♟♙"
    MOVES = []

class Knight(Piece):
    REPR  = "♞♘"
    MOVES = []

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
PIECES :list[Piece] = []
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
        
        PIECES[23].move(Pos.createFromRaw(move))

        turn += 1

if __name__ == '__main__':
    main()

#TODO: move timer