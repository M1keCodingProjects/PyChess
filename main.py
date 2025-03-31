BOARD_VERT_SIZE     = 8
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
    class InvalidChessFileErr(Exception):
        def __init__(self, chessFile:str) -> None:
            super().__init__(f"{chessFile} is not a valid chess file, files go from {ChessFile._member_names_[0]} to {ChessFile._member_names_[-1]}.")

    a = next(iota)
    b = next(iota)
    c = next(iota)
    d = next(iota)
    e = next(iota)
    f = next(iota)
    g = next(iota)
    h = next(iota)

    @staticmethod
    def createFromRaw(chessfile:str) -> Self:
        try: return ChessFile[chessfile]
        except: raise ChessFile.InvalidChessFileErr(chessfile)

    def asLabel(self) -> str: return f"  {repr(self)}  "

    def __repr__(self) -> str: return self.name

class Pos:
    class RankOOBErr(Exception):
        def __init__(self, rank:int) -> None:
            super().__init__(f"{rank} is invalid, must be a positive integer lower than {BOARD_VERT_SIZE + 1}.")

    def __init__(self, file:ChessFile, rank:int) -> None:
        self.file, self.rank = file, rank

    @staticmethod
    def createFromRaw(pos:str) -> "Pos":
        # Factory method
        rank = int(pos[1])
        if rank <= 0 or rank > BOARD_VERT_SIZE: raise Pos.RankOOBErr(rank)

        return Pos(ChessFile.createFromRaw(pos[0]), rank)

    def isEqualTo(self, file:int, rank:int) -> bool: return self.getCoords() == (file, rank)

    def getCoords(self) -> tuple[int, int]: return self.file.value, self.rank

    def __repr__(self) -> str: return ", ".join(map(str, self.getCoords()))

    def copy(self) -> Self: return Pos(self.file, self.rank)

class Piece:
    REPR  = ""
    MOVES = []

    def __init__(self, pos:Pos, *, isBlack:bool) -> None:
        self.pos, self.isBlack = pos, isBlack
        self.isFirstMove = True
    
    def move(self, newPos:Pos) -> bool:
        if self._isLegalMove(newPos):
            self._changePiecePos(newPos)
            return True
        
        return False

    def _isLegalMove(self, newPos:Pos) -> bool:
        newFile, newRank = newPos.getCoords()
        file, rank = self.pos.getCoords()
        
        return (newFile - file, newRank - rank) in self.MOVES

    def _changePiecePos(self, newPos:Pos) -> None:
        self.pos = newPos
        if self.isFirstMove: self.isFirstMove = False

    def __repr__(self) -> str: return self.REPR[self.isBlack]

    @classmethod
    def copy(cls, piece:"Piece") -> Self:
        return cls(piece.pos.copy(), isBlack = piece.isBlack)

class King(Piece):
    REPR  = "♚♔"
    MOVES = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    FREE_FILES_SHORT = (ChessFile.f, ChessFile.g)
    FREE_FILES_LONG  = (ChessFile.b, ChessFile.c, ChessFile.d)

    def _isLegalMove(self, newPos:Pos) -> bool:
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
    MOVES = [(0, 1)]

    def __init__(self, pos:Pos, *, isBlack:bool) -> None:
        super().__init__(pos, isBlack = isBlack)
        if self.isBlack: self.MOVES   = [(0, -1)]
        self.canOpponentEnPassant     = False
        self.canPromote               = False

    def isValidForwardMove(self, newPos:Pos, nSquares = 1) -> bool:
        return newPos.rank - self.pos.rank == ((1 - 2 * self.isBlack) * nSquares)

    def _isLegalMove(self, newPos:Pos) -> bool:
        if super()._isLegalMove(newPos): return True

        # Diagonal motion: the file changes
        if newPos.file != self.pos.file:
            if abs(newPos.file.value - self.pos.file.value) != 1 or not self.isValidForwardMove(newPos): return False

            for piece in PIECES:
                if self.isBlack == piece.isBlack: continue

                if piece.pos.isEqualTo(newPos.file.value, newPos.rank): return True
                if isinstance(piece, Pawn) and piece.canOpponentEnPassant and piece.pos.rank == self.pos.rank: return True

            return False

        # First move can be 2 squares forward:
        if self.isValidForwardMove(newPos, 2) and self.isFirstMove:
            self.canOpponentEnPassant = True
            return True

    def _changePiecePos(self, newPos:Pos) -> None:
        super()._changePiecePos(newPos)

        if self.pos.rank == 8 - 7 * self.isBlack: self.canPromote = True

class Knight(Piece):
    REPR  = "♞♘"
    MOVES = [(2, 1), (2, -1), (-2, -1), (-2, 1), (1, 2), (1, -2), (-1, -2), (-1, 2)]

class Queen(Piece):
    REPR = "♛♕"

def buildChessboard(pieces:list[Piece]) -> str:
    LINE_SEPARATOR = getHorizontalChessboardLine(Corner.Middle)
    
    FILE_LABELS = "  " + "".join(map(ChessFile.asLabel, list(ChessFile.__members__.values()))) + '\n'
    chessboard  = FILE_LABELS + getHorizontalChessboardLine(Corner.Top)
    for rank in range(BOARD_VERT_SIZE, 0, -1):
        chessboard += LINE_SEPARATOR * (rank < BOARD_VERT_SIZE) + str(rank) + AFTER_LABEL_SPACING
        for file in range(1, len(ChessFile.__members__) + 1):
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
        rank = 1 + (BOARD_VERT_SIZE - 1) * i
        for j in (False, True):
            PIECES.append(Rook(  Pos(ChessFile(1 + 7 * j), rank), isBlack = i))
            PIECES.append(Knight(Pos(ChessFile(2 + 5 * j), rank), isBlack = i))
            PIECES.append(Bishop(Pos(ChessFile(3 + 3 * j), rank), isBlack = i))
    
        PIECES.append(Queen(Pos(ChessFile.d, rank), isBlack = i))
        PIECES.append(King(Pos(ChessFile.e, rank), isBlack = i))
        PIECES.extend([ Pawn(Pos(ChessFile(pos), 2 + 5 * i), isBlack = i) for pos in range(1, BOARD_VERT_SIZE + 1) ])

iota = iotaGen()
class GameCommand(Enum):
    quit = next(iota)

    @staticmethod
    def create(commandName:str) -> Self: return GameCommand[commandName]

def promotePawn(pawn:Pawn) -> None:
    while True:
        pieceName = input("Insert piece to promote to [K|Q|R|B]: ").upper()
        match pieceName:
            case 'K': PIECES.append(Knight.copy(pawn))
            case 'Q': PIECES.append(Queen.copy(pawn))
            case 'B': PIECES.append(Bishop.copy(pawn))
            case 'R': PIECES.append(Rook.copy(pawn))
            case other :
                print(f"\"{other}\" is not a valid promotion target. Try again.")
                continue
        
        break

    PIECES.remove(pawn)

def main() -> None:
    global turn
    setupPieces()

    pieceIRandomlyDecidedShouldMove = PIECES[9]
    print(pieceIRandomlyDecidedShouldMove.pos)
    while True:
        print('\n' * 5 * (turn > 0) + buildChessboard(PIECES))
        move = input(f"Turn: {turn}\nInsert your next move as {"black" if turn % 2 else "white"}: ")
        if move == GameCommand.quit.name: return
        
        pieceHasMoved = False
        print("\n")
        try:
            if pieceIRandomlyDecidedShouldMove.move(Pos.createFromRaw(move)):
                turn += 1
                pieceHasMoved = True
        
        except ChessFile.InvalidChessFileErr as err: print(err)
        except Pos.RankOOBErr as err: print(err)
        
        if not pieceHasMoved: print("Invalid move. Try again.")
        elif isinstance(pieceIRandomlyDecidedShouldMove, Pawn) and pieceIRandomlyDecidedShouldMove.canPromote:
            promotePawn(pieceIRandomlyDecidedShouldMove)
            pieceIRandomlyDecidedShouldMove = PIECES[-1]

if __name__ == '__main__':
    main()

#TODO: move timer