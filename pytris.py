import pygame
import random

FPS = 60
GAME_SPEED = 2

ELEMENT_SIZE = 48
BLOCKS_WIDTH = 10
BLOCKS_HEIGHT = 20
WIDTH = ELEMENT_SIZE * BLOCKS_WIDTH
HEIGHT = ELEMENT_SIZE * BLOCKS_HEIGHT

UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (111, 111, 111)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (80, 80, 255)
ORANGE = (255, 127, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)

BLANK = 0
SQUARE = 1
LINE = 2
REG_L = 3
INV_L = 4
REG_S = 5
INV_S = 6
T = 7

GAME_TICK = pygame.USEREVENT + 1
PIECEEVENT = pygame.USEREVENT + 2

class Game:
  def __init__(self):
    print("New game")
    pygame.init()

    self.clock = pygame.time.Clock()
    pygame.display.set_caption("PyTris Game")

    self.landed_pieces = Landed_Pieces()
    self.piece_list = [1,2,3,4,5,6,7]
    random.shuffle(self.piece_list)
    self.piece_counter = 0
    self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.time.set_timer(GAME_TICK, 1000 // FPS)
    pygame.time.set_timer(PIECEEVENT, 1000 // GAME_SPEED)

  def run(self):
    print("Running game")
    game_over = False

    piece = Piece(self.piece_list[self.piece_counter])
    self.piece_counter += 1

    while not game_over:
      self.clock.tick(FPS)

      for event in pygame.event.get():
        if event.type == GAME_TICK:
          # Draw Grid
          self.screen.fill(BLACK)
          for y in range(0, HEIGHT, ELEMENT_SIZE):
            pygame.draw.line(self.screen, GREY, [0, y], [WIDTH, y])
          for x in range(0, WIDTH, ELEMENT_SIZE):
            pygame.draw.line(self.screen, GREY, [x, 0], [x, HEIGHT])
          self.landed_pieces.draw(self.screen)
          piece.draw(self.screen)

          if piece.stop:
            self.landed_pieces.store(piece)

          pygame.display.update()
        if event.type == PIECEEVENT:
          if piece.stop:
              ## Check if we made any lines
            lines = self.landed_pieces.check_lines()
            if len(lines) > 0:
              self.landed_pieces.clear_lines(lines)

            if self.piece_counter == 7:
              random.shuffle(self.piece_list)
              self.piece_counter = 0
            piece = Piece(self.piece_list[self.piece_counter])
            self.piece_counter += 1
          else:
            piece.update(self.landed_pieces)
        if event.type == pygame.QUIT:
          game_over = True
        elif event.type == pygame.KEYDOWN:
          if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            piece.moveLeft(self.landed_pieces)
          if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            piece.moveRight(self.landed_pieces)
          if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            piece.moveDown(self.landed_pieces)
          if event.key == pygame.K_e:
            piece.rotateRight(self.landed_pieces)
          if event.key == pygame.K_q:
            piece.rotateLeft(self.landed_pieces)
          if event.key == pygame.K_ESCAPE:
            game_over = True

class Landed_Pieces:
  def __init__(self):
    print("We got the pieces")
    self.grid = [[0]*BLOCKS_WIDTH for i in range(BLOCKS_HEIGHT)]
  
  def check_lines(self):
    lines_to_clear = []
    for y in range(0, BLOCKS_HEIGHT):
      line_full = True
      for x in self.grid[y]:
        if x == 0:
          line_full = False
      if line_full:
        lines_to_clear.append(y)
    return lines_to_clear

  def clear_lines(self, lines):
    print("Clearing some lines")
    for line in lines:
      self.grid.pop(line)
      self.grid.insert(0, [0]*BLOCKS_WIDTH)

  def get_square(self, x, y):
    #print("Checking", y, BLOCKS_HEIGHT)
    if y < BLOCKS_HEIGHT:
      return self.grid[y][x]

  def store(self, piece):
    for element in piece.elements:
      x = piece.pos[0] + element[0]
      y = piece.pos[1] + element[1]
      self.grid[y][x] = piece.color

  def draw(self, screen):
    for x in range(0, BLOCKS_WIDTH):
      for y in range(0, BLOCKS_HEIGHT):
        if(self.grid[y][x] != 0):
          pygame.draw.rect(
            screen,
            self.grid[y][x],
            (x * ELEMENT_SIZE, y * ELEMENT_SIZE, ELEMENT_SIZE, ELEMENT_SIZE)
          )
          pygame.draw.rect(
            screen,
            BLACK,
            (x * ELEMENT_SIZE, y * ELEMENT_SIZE, ELEMENT_SIZE, ELEMENT_SIZE),
            1
          )
          

class Piece:
  def __init__(self, type):
    print("New piece")

    self.pos = (4, 0)
    self.stop = False
    self.rotationValue = 1
    match type:
      case 1:
        self.type = SQUARE
        self.color = YELLOW
        self.elements = [(0,0), (1,0), (0,1), (1,1)]
      case 2:
        self.type = LINE
        self.color = LIGHT_BLUE
        self.rotationMatrix = [
          [(1,3), (2,3), (3,3), (4,3)],
          [(2,1), (2,2), (2,3), (2,4)],
          [(0,3), (1,3), (2,3), (3,3)],
          [(2,0), (2,1), (2,2), (2,3)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]
      case 3:
        self.type = REG_L
        self.color = ORANGE
        self.rotationMatrix = [
          [(2,0), (0,1), (1,1), (2,1)],
          [(1,0), (1,1), (1,2), (2,2)],
          [(0,1), (1,1), (2,1), (0,2)],
          [(0,0), (1,0), (1,1), (1,2)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]
      case 4:
        self.type = INV_L
        self.color = BLUE
        self.rotationMatrix = [
          [(0,0), (0,1), (1,1), (2,1)],
          [(1,0), (2,0), (1,1), (1,2)],
          [(0,1), (1,1), (2,1), (2,2)],
          [(1,0), (1,1), (0,2), (1,2)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]
      case 5:
        self.type = REG_S
        self.color = GREEN
        self.rotationMatrix = [
          [(1,0), (2,0), (0,1), (1,1)],
          [(1,0), (1,1), (2,1), (2,2)],
          [(1,1), (2,1), (0,2), (1,2)],
          [(0,0), (0,1), (1,1), (1,2)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]
      case 6:
        self.type = INV_S
        self.color = RED
        self.rotationMatrix = [
          [(0,0), (1,0), (1,1), (2,1)],
          [(2,0), (1,1), (2,1), (1,2)],
          [(0,1), (1,1), (1,2), (2,2)],
          [(1,0), (0,1), (1,1), (0,2)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]
      case 7:
        self.type = T
        self.color = PURPLE
        self.rotationMatrix = [
          [(1,0), (0,1), (1,1), (2,1)],
          [(1,0), (1,1), (2,1), (1,2)],
          [(0,1), (1,1), (2,1), (1,2)],
          [(1,0), (0,1), (1,1), (1,2)]
        ]
        self.elements = self.rotationMatrix[self.rotationValue]

  def draw(self, screen):
    for element in self.elements:
      x = self.pos[0] + element[0] 
      y = self.pos[1] + element[1]
      pygame.draw.rect(screen, self.color, (
        x * ELEMENT_SIZE,
        y * ELEMENT_SIZE,
        ELEMENT_SIZE,
        ELEMENT_SIZE))
      
      pygame.draw.rect(screen, BLACK,(
        (x * ELEMENT_SIZE),
        (y * ELEMENT_SIZE),
        ELEMENT_SIZE,
        ELEMENT_SIZE),
        1
      )

  def update(self, landed_pieces):
    for element in self.elements:
      y = self.pos[1] + element[1] + 1
      x = self.pos[0] + element[0]
      if self.pos[1] + element[1] == BLOCKS_HEIGHT - 1:
        print("something below me!")
        self.stop = True
      elif landed_pieces.get_square(x, y) != 0:
        self.stop = True

    if not self.stop:
      self.pos = (self.pos[0], self.pos[1] + 1)
  
  def moveLeft(self, landed_pieces):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == 0:
        can_move = False
      elif landed_pieces.get_square(self.pos[0] + element[0] - 1, self.pos[1] + element[1]) != 0:
        can_move = False

    if can_move and not self.stop:
      self.pos = (self.pos[0] - 1, self.pos[1])

  def moveRight(self, landed_pieces):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == BLOCKS_WIDTH - 1:
        can_move = False
      elif landed_pieces.get_square(self.pos[0] + element[0] + 1, self.pos[1] + element[1]) != 0:
        can_move = False

    if can_move and not self.stop:
      self.pos = (self.pos[0] + 1, self.pos[1])

  def moveDown(self, landed_pieces):
    can_move = True

    for element in self.elements:
      if landed_pieces.get_square(self.pos[0] + element[0], self.pos[1] + element[1] + 1) != 0:
        can_move = False

    if can_move and not self.stop:
      self.pos = (self.pos[0], self.pos[1] + 1)

  def rotateRight(self, landed_pieces):
    if not self.stop:
      if not self.type == 1:
        #TODO: Check if we actually can perform the rotation
        if self.rotationValue == 3:
          self.rotationValue = 0
        else:
          self.rotationValue += 1
        self.elements = self.rotationMatrix[self.rotationValue]
  
  def rotateLeft(self, landed_pieces):
    if not self.stop:
      if not self.type == 1:
        #TODO: Check if we actually can perform the rotation
        if self.rotationValue == 0:
          self.rotationValue = 3
        else:
          self.rotationValue -= 1
        self.elements = self.rotationMatrix[self.rotationValue]

def main():
  game = Game()
  game.run()

if __name__ == '__main__':
  main()
