import pygame
import random
import os

pygame.init()
pygame.mixer.init()

shapes = [
    [[1, 5, 9, 13], [4, 5, 6, 7], [1, 5, 9, 13], [4, 5, 6, 7]],
    [[4, 5, 9, 10], [2, 6, 5, 9]],
    [[6, 7, 9, 10], [1, 5, 6, 10]],
    [[2, 1, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
    [[1, 2, 5, 6]],
]

shapeColors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), 
              (255, 165, 0), (0, 0, 255), (128, 0, 128)]

width = 700
height = 600
gameWidth = 200 
gameHeight = 400
blockSize = 20
fps = 60
initial_level = 4

topLeft_x = (width - gameWidth) // 2
topLeft_y = height - gameHeight - 50

class Block:
    def __init__(self, x, y, n):
        self.x = x
        self.y = y
        self.type = n
        self.color = n
        self.rotation = 0

    def image(self):
        return shapes[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(shapes[self.type])

class Tetris:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.state = "start"
        self.score = 0
        self.level = initial_level
        self.field = [[0] * self.width for _ in range(self.height)]
        self.block = None
        self.nextBlock = None
        self.game_over = False
        self.new_block()
        
        self.load_sounds()

    def load_sounds(self):
        try:
            pygame.mixer.music.load("secret_song_dont_play.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            print("Could not load music file")
        
        self.sounds = {
            'rotate': pygame.mixer.Sound('rotate.wav') if os.path.exists('rotate.wav') else None,
            'drop': pygame.mixer.Sound('drop.wav') if os.path.exists('drop.wav') else None,
            'line': pygame.mixer.Sound('line.wav') if os.path.exists('line.wav') else None,
            'gameover': pygame.mixer.Sound('gameover.wav') if os.path.exists('gameover.wav') else None
        }

    def play_sound(self, sound_name):
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def new_block(self):
        self.block = Block(3, 0, random.randint(0, len(shapes) - 1))
        if not self.nextBlock:
            self.nextBlock = Block(3, 0, random.randint(0, len(shapes) - 1))

    def new_next_block(self):
        self.nextBlock = Block(3, 0, random.randint(0, len(shapes) - 1))

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.block.image():
                    if (i + self.block.y >= self.height or
                        j + self.block.x < 0 or
                        j + self.block.x >= self.width or
                        self.field[i + self.block.y][j + self.block.x] > 0):
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(self.height -1, -1, -1):
            if all(self.field[i]):
                lines += 1
                del self.field[i]
                self.field.insert(0, [0] * self.width)
        
        if lines > 0:
            self.score += lines ** 2
            self.play_sound('line')
            
            self.level = initial_level + self.score // 1000

    def draw_next_block(self, screen):
        font = pygame.font.SysFont('Arial', 30, bold=True)
        label = font.render("Next Shape", True, (128, 128, 128))
        sx = topLeft_x + gameWidth + 50
        sy = topLeft_y + gameHeight//2 - 80
        screen.blit(label, (sx, sy - 30))
    
        if self.nextBlock:
            for i in range(4):
                for j in range(4):
                    if i *4 + j in self.nextBlock.image():
                        pygame.draw.rect(screen, shapeColors[self.nextBlock.color],
                                 (sx + j * blockSize, sy + i * blockSize, blockSize -1, blockSize -1))

    def go_down(self):
        self.block.y += 1
        if self.intersects():
            self.block.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.block.image():
                    self.field[i + self.block.y][j + self.block.x] = self.block.color
        
        self.play_sound('drop')
        self.break_lines()
        self.block = self.nextBlock
        self.new_next_block()
        
        if self.intersects():
            self.state = "gameover"
            self.play_sound('gameover')

    def moveHoriz(self, dx):
        self.block.x += dx
        if self.intersects():
            self.block.x -= dx

    def rotate(self):
        old_rotation = self.block.rotation
        self.block.rotate()
        if self.intersects():
            self.block.rotation = old_rotation
        else:
            self.play_sound('rotate')

    def moveBottom(self):
        while not self.intersects():
            self.block.y += 1
        self.block.y -= 1
        self.freeze()

    def reset_game(self):
        self.__init__(self.height, self.width)

def startGame():
    done = False
    clock = pygame.time.Clock()
    game = Tetris(20, 10)
    counter = 0
    pressing_down = False

    while not done:
        if game.block is None:
            game.new_block()
        
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // (game.level * 0.5)) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_DOWN:
                    pressing_down = True
                elif event.key == pygame.K_LEFT:
                    game.moveHoriz(-1)
                elif event.key == pygame.K_RIGHT:
                    game.moveHoriz(1)
                elif event.key == pygame.K_SPACE:
                    game.moveBottom()
                elif event.key == pygame.K_ESCAPE:
                    game.reset_game()
                elif event.key == pygame.K_m:  # Mute music
                    if pygame.mixer.music.get_volume() > 0:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(0.5)
            
            if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
                pressing_down = False

        screen.fill('#FFFFFF')

        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(screen, '#B2BEB5', 
                               (topLeft_x + j * blockSize, topLeft_y + i * blockSize,
                                blockSize, blockSize), 1)
                if game.field[i][j] > 0:
                    pygame.draw.rect(screen, shapeColors[game.field[i][j]],
                                   (topLeft_x + j * blockSize +1, topLeft_y + i * blockSize +1,
                                    blockSize -2, blockSize -2))

        if game.block:
            for i in range(4):
                for j in range(4):
                    if i * 4 + j in game.block.image():
                        pygame.draw.rect(screen, shapeColors[game.block.color],
                                       (topLeft_x + (j + game.block.x) * blockSize +1,
                                        topLeft_y + (i + game.block.y) * blockSize +1,
                                        blockSize -2, blockSize -2))

        game.draw_next_block(screen)
        font = pygame.font.SysFont('Arial', 40, bold=True)
        score_text = font.render(f'Score: {game.score}', True, (0, 0, 0))
        level_text = font.render(f'Level: {game.level}', True, (0, 0, 0))
        screen.blit(score_text, (topLeft_x + gameWidth + 50, topLeft_y))
        screen.blit(level_text, (topLeft_x + gameWidth + 50, topLeft_y + 50))

        if game.state == "gameover":
            over_font = pygame.font.SysFont('Arial', 60, bold=True)
            over_text = over_font.render('GAME OVER!', True, (255, 0, 0))
            restart_text = font.render('Press ESC to restart', True, (0, 0, 0))
            
            screen.blit(over_text, (width//2 - over_text.get_width()//2, 
                                  height//2 - over_text.get_height()//2 - 30))
            screen.blit(restart_text, (width//2 - restart_text.get_width()//2,
                                     height//2 + 30))

        pygame.display.flip()
        clock.tick(fps)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

running = True
while running:
    screen.fill((255,20,147))
    font = pygame.font.SysFont('Arial', 70, bold=True)
    label = font.render("PRESS ANY KEY", True, (255, 255, 255))
    subtitle = pygame.font.SysFont('Arial', 30).render("(M to toggle music)", True, (200, 200, 200))
    
    screen.blit(label, (width//2 - label.get_width()//2, height//2 - label.get_height()//2))
    screen.blit(subtitle, (width//2 - subtitle.get_width()//2, height//2 + 50))
    
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            startGame()
            running = False

pygame.quit()
