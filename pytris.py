import pygame
import random

FPS = 60
GAME_SPEED = 5

ELEMENT_SIZE = 16
BLOCKS_WIDTH = 10
BLOCKS_HEIGHT = 21
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

SQUARE = 0
LINE = 1

PIECEEVENT = pygame.USEREVENT + 1

class Game:
  def __init__(self):
    print("New game")
    pygame.init()

    self.clock = pygame.time.Clock()
    pygame.display.set_caption("PyTris Game")

    self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
    #pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)
    pygame.time.set_timer(PIECEEVENT, 1000)


  def run(self):
    print("Running game")
    game_over = False

    piece = Piece()

    while not game_over:
      self.clock.tick(FPS)
      self.screen.fill(GREY)
      # Draw Grid
      for y in range(0, HEIGHT, ELEMENT_SIZE):
        pygame.draw.line(self.screen, BLACK, [0, y], [WIDTH, y])
      for x in range(0, WIDTH, ELEMENT_SIZE):
        pygame.draw.line(self.screen, BLACK, [x, 0], [x, HEIGHT])

      for event in pygame.event.get():
          if event.type == PIECEEVENT:
            piece.update()
          if event.type == pygame.QUIT:
            game_over = True
          elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
              piece.moveLeft()
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
              piece.moveRight()
            if event.key == pygame.K_ESCAPE:
              game_over = True

      piece.draw(self.screen)

      pygame.display.update()

class Piece:
  def __init__(self):
    print("New piece")

    self.pos = (4, 0)
    type = random.randint(0,1)
    match type:
      case 0:
        self.type = SQUARE
        self.color = YELLOW
        self.elements = [(0,0), (1,0), (0,1), (1,1)]
      case 1:
        self.type = LINE
        self.color = RED
        self.elements = [(0,0), (1,0), (2,0), (3,0)]
        
    #
    #   ## The
    #   ## Square
    #
  
  def draw(self, screen):
    for element in self.elements:
      pygame.draw.rect(screen, self.color, (
        (self.pos[0] + element[0]) * ELEMENT_SIZE,
        (self.pos[1] + element[1]) * ELEMENT_SIZE, ELEMENT_SIZE, ELEMENT_SIZE))

  def update(self):
    self.pos = (self.pos[0], self.pos[1] + 1)
  
  def moveLeft(self):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == 0:
        can_move = False
    if can_move:
      self.pos = (self.pos[0] - 1, self.pos[1])

  def moveRight(self):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == BLOCKS_WIDTH - 1:
        can_move = False
    if can_move:
      self.pos = (self.pos[0] + 1, self.pos[1])

def main():
  game = Game()
  game.run()

if __name__ == '__main__':
  main()
