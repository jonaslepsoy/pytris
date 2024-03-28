import pygame
import random
import copy
import types

FPS = 60
GAME_SPEED = 4
MOVE_SPEED = 24
CLEARING_SPEED = 15

ELEMENT_SIZE = 40
BLOCKS_WIDTH = 10
BLOCKS_HEIGHT = 22
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
MOVEEVENT = pygame.USEREVENT + 3
CLEARINGEVENT = pygame.USEREVENT + 4

GAME_RUNNING = 1
CLEARING_LINES = 2

class Game:
  def __init__(self):
    print("New game")
    pygame.init()
    pygame.mixer.init()
    
    #Uncomment the following two lines and add a track for background music
    #pygame.mixer.music.load("music.mp3")
    #pygame.mixer.music.play(-1)

    self.sounds = types.SimpleNamespace()
    self.sounds.moveSound = pygame.mixer.Sound("se_game_move.wav")
    self.sounds.landingSound = pygame.mixer.Sound("se_game_landing.wav")
    self.sounds.match1Sound = pygame.mixer.Sound("se_game_count.wav")
    self.sounds.matchMoreSound = pygame.mixer.Sound("se_game_double.wav")
    self.sounds.matchTetrisSound = pygame.mixer.Sound("se_game_perfect.wav")
    self.sounds.rotateSound = pygame.mixer.Sound("se_game_rotate.wav")

    self.clock = pygame.time.Clock()
    pygame.display.set_caption("PyTris Game")

    self.landed_pieces = Landed_Pieces()
    self.piece_list = [1,2,3,4,5,6,7]
    random.shuffle(self.piece_list)
    self.lines_to_clear = []
    self.piece_counter = 0
    self.state = GAME_RUNNING
    self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
    pygame.time.set_timer(GAME_TICK, 1000 // FPS)
    pygame.time.set_timer(PIECEEVENT, 1000 // GAME_SPEED)
    pygame.time.set_timer(MOVEEVENT, 1000 // MOVE_SPEED)
    pygame.time.set_timer(CLEARINGEVENT, 1000 // CLEARING_SPEED)

  def run(self):
    print("Running game")
    game_over = False
    clearing_animation = []
    clearing_animation_frame = 5

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
          
          if self.state == GAME_RUNNING:
            piece.draw(self.screen)
          
          # Black top bar from line 21 and up
          # TODO: Replace with something nicer?
          pygame.draw.rect(
            self.screen,
            BLACK,
            (0, 0, BLOCKS_WIDTH * ELEMENT_SIZE, ELEMENT_SIZE * 2)
          )
          
          # Draw clearing animation
          for frame in clearing_animation:
            pygame.draw.rect(
              self.screen,
              WHITE,
              (frame[0] * ELEMENT_SIZE, frame[1] * ELEMENT_SIZE, ELEMENT_SIZE, ELEMENT_SIZE)
            )
            pygame.draw.rect(
              self.screen,
              BLACK,
              (frame[0] * ELEMENT_SIZE, frame[1] * ELEMENT_SIZE, ELEMENT_SIZE, ELEMENT_SIZE),
              1
            )

        if event.type == PIECEEVENT:
          if piece.stop:
            self.landed_pieces.store(piece, self.sounds)
              ## Check if we made any lines
            lines = self.landed_pieces.check_lines()
            if len(lines) > 0:
              #TODO: Indicate visually that a line is going to be cleared.
              if len(lines) >= 4:
                self.sounds.matchTetrisSound.play()
              elif len(lines) > 1:
                self.sounds.matchMoreSound.play()
              else:
                self.sounds.match1Sound.play()
              self.state = CLEARING_LINES
              self.lines_to_clear = lines

            if self.piece_counter == 7:
              random.shuffle(self.piece_list)
              self.piece_counter = 0
            piece = Piece(self.piece_list[self.piece_counter])
            if piece.collision(piece, self.landed_pieces):
              game_over = True
            self.piece_counter += 1
          elif self.state == GAME_RUNNING:
            piece.update(self.landed_pieces)
        if event.type == pygame.QUIT:
          game_over = True
        
        #Keypress events
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
            game_over = True
          if event.key == pygame.K_e:
            piece.rotateRight(self.landed_pieces, self.sounds)
          if event.key == pygame.K_q:
            piece.rotateLeft(self.landed_pieces, self.sounds)
          if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            #piece.move_left = True
            #piece.move_intention = LEFT
            piece.moveLeft(self.landed_pieces, self.sounds)
          if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            #piece.move_right = True
            #piece.move_intention = RIGHT
            piece.moveRight(self.landed_pieces, self.sounds)
          if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            piece.move_down = True
            piece.move_intention = DOWN
        if event.type == pygame.KEYUP:
          #if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            #piece.move_left = False
          #if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            #piece.move_right = False
          if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            piece.move_down = False

        if event.type == CLEARINGEVENT:
          if self.state == CLEARING_LINES:
            # If we cleared some lines, we'll have to prepare the animation here, but draw it on every frame
            if clearing_animation_frame >= 0: # 5 frames of animation
              for x in range(clearing_animation_frame, (BLOCKS_WIDTH // 2)): 
                for y in self.lines_to_clear:
                  clearing_animation.append((x,y))
              for x in range(BLOCKS_WIDTH // 2, BLOCKS_WIDTH - clearing_animation_frame):
                for y in self.lines_to_clear:
                  clearing_animation.append((x,y))
              clearing_animation_frame -= 1
            else:
              self.landed_pieces.clear_lines(self.lines_to_clear)
              self.lines_to_clear = []
              clearing_animation = []
              clearing_animation_frame = 5
              self.state = GAME_RUNNING

        # Move event logic
        if event.type == MOVEEVENT:
          if piece.move_down or piece.move_intention == DOWN:
            piece.moveDown(self.landed_pieces)
            piece.move_intention = None
          #if piece.move_left or piece.move_intention == LEFT:
          #  piece.moveLeft(self.landed_pieces, self.sounds)
          #  piece.move_intention = None
          #if piece.move_right or piece.move_intention == RIGHT:
          #  piece.moveRight(self.landed_pieces, self.sounds)
          #  piece.move_intention = None
      pygame.display.update()
    # Game over logic / animation
    print("Thank you for playing!")

          
class Landed_Pieces:
  def __init__(self):
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
    for line in lines:
      self.grid.pop(line)
      self.grid.insert(0, [0]*BLOCKS_WIDTH)

  def get_square(self, x, y):
    if y < BLOCKS_HEIGHT:
      return self.grid[y][x]

  def store(self, piece, sounds):
    for element in piece.elements:
      x = piece.pos[0] + element[0]
      y = piece.pos[1] + element[1]
      self.grid[y][x] = piece.color
    sounds.landingSound.play()

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
    self.pos = (4, 0)
    self.stop = False
    self.rotationValue = 1
    self.moved_this_cycle = False
    self.move_intention = None
    self.move_down = False
    self.move_left = False
    self.move_right = False

    match type:
      case 1:
        self.type = SQUARE
        self.color = YELLOW
        self.elements = [(0,0), (1,0), (0,1), (1,1)]
        self.rotationMatrix = [
          [(0,0), (1,0), (0,1), (1,1)],
          [(0,0), (1,0), (0,1), (1,1)],
          [(0,0), (1,0), (0,1), (1,1)],
          [(0,0), (1,0), (0,1), (1,1)]
        ]
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
    if self.moved_this_cycle:
      self.moved_this_cycle = False
      return

    for element in self.elements:
      y = self.pos[1] + element[1] + 1
      x = self.pos[0] + element[0]
      if self.pos[1] + element[1] == BLOCKS_HEIGHT - 1:
        #Something below
        self.stop = True
      elif landed_pieces.get_square(x, y) != 0:
        self.stop = True

    if not self.stop and not self.moved_this_cycle:
      self.pos = (self.pos[0], self.pos[1] + 1)

  def collision(self, virtual_piece, landed_pieces):
    virtual_piece.elements = virtual_piece.rotationMatrix[virtual_piece.rotationValue]
    for element in virtual_piece.elements:
      if virtual_piece.pos[0] + element[0] < 0:
        return True # Collision: Left wall
      if virtual_piece.pos[0] + element[0] >= BLOCKS_WIDTH:
        return True # Collision: Right wall
      elif virtual_piece.pos[1] + element[1] > BLOCKS_HEIGHT - 1:
        return True # Collision: Bottom
      elif landed_pieces.get_square(virtual_piece.pos[0] + element[0], virtual_piece.pos[1] + element[1]) != 0:
        return True # Collision: Landed piece below
    return False # No collision

  def moveLeft(self, landed_pieces, sounds):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == 0: # Prefer collision test?
        can_move = False
      elif landed_pieces.get_square(self.pos[0] + element[0] - 1, self.pos[1] + element[1]) != 0: # Prefer collision test?
        can_move = False

    if can_move and not self.stop:
      sounds.moveSound.play()
      self.pos = (self.pos[0] - 1, self.pos[1])

  def moveRight(self, landed_pieces, sounds):
    can_move = True
    for element in self.elements:
      if self.pos[0] + element[0] == BLOCKS_WIDTH - 1: # Prefer collision test?
        can_move = False
      elif landed_pieces.get_square(self.pos[0] + element[0] + 1, self.pos[1] + element[1]) != 0: # Prefer collision test?
        can_move = False

    if can_move and not self.stop:
      sounds.moveSound.play()
      self.pos = (self.pos[0] + 1, self.pos[1])

  def moveDown(self, landed_pieces):
    can_move = True
    piece_copy = copy.deepcopy(self)
    piece_copy.pos = (piece_copy.pos[0], piece_copy.pos[1] + 1)
    can_move = not self.collision(piece_copy, landed_pieces)

    if can_move and not self.stop:
      self.pos = (self.pos[0], self.pos[1] + 1)
      self.moved_this_cycle = True

  def rotateRight(self, landed_pieces, sounds):
    if not self.stop:
      if not self.type == 1: # We don't rotate squares
        # Check self.rotationMatrix[self.rotationValue] for any piece out of bounds.
        piece_copy = copy.deepcopy(self)
        if piece_copy.rotationValue == 3:
          piece_copy.rotationValue = 0
        else:
          piece_copy.rotationValue += 1
        
        if not self.collision(piece_copy, landed_pieces):
          if self.rotationValue == 3:
            self.rotationValue = 0
          else:
            self.rotationValue += 1
          sounds.rotateSound.play()
          self.elements = self.rotationMatrix[self.rotationValue]
  
  def rotateLeft(self, landed_pieces, sounds):
    if not self.stop:
      if not self.type == 1:
        # Check self.rotationMatrix[self.rotationValue] for any piece out of bounds.
        piece_copy = copy.deepcopy(self)
        if piece_copy.rotationValue == 0:
          piece_copy.rotationValue = 3
        else:
          piece_copy.rotationValue -= 1
        
        if not self.collision(piece_copy, landed_pieces):
          if self.rotationValue == 0:
            self.rotationValue = 3
          else:
            self.rotationValue -= 1
          sounds.rotateSound.play()
          self.elements = self.rotationMatrix[self.rotationValue]

def main():
  game = Game()
  game.run()

if __name__ == '__main__':
  main()
