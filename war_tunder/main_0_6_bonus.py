from unittest import result
import pygame
from random import randint
pygame.init()
pygame.mixer.init()
import pygame_menu
pygame.init()
import math
WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 32

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Tank 2 player game")


start_sound = pygame.mixer.Sound("sounds/level_start.mp3")
lose_sound = pygame.mixer.Sound("sounds/level_finish.mp3")
shot_sound = pygame.mixer.Sound("sounds/shot.wav")
move_sound = pygame.mixer.Sound("sounds/move.wav")
engine_sound = pygame.mixer.Sound("sounds/engine.wav")


fontUI = pygame.font.Font(None, 30)

imgBrick = pygame.image.load('images/block_brick.png')
imgTanks = [
    pygame.image.load('images/tank1.png'),
    pygame.image.load('images/tank2.png'),
    pygame.image.load('images/tank3.png'),
    pygame.image.load('images/tank4.png'),
    pygame.image.load('images/tank5.png'),
    pygame.image.load('images/tank6.png'),
    pygame.image.load('images/tank7.png'),
    pygame.image.load('images/tank8.png'),
    ]
imgBangs = [
    pygame.image.load('images/bang1.png'),
    pygame.image.load('images/bang2.png'),
    pygame.image.load('images/bang3.png'),
    ]
imgBonuses = [
    pygame.image.load('images/bonus_star.png'),
    pygame.image.load('images/bonus_tank.png'),
    pygame.image.load('images/bonus_helmet.png'),
    ]

DIRECTS = [[0, -1], [1, 0], [0, 1], [-1, 0]]

MOVE_SPEED =    [1, 2, 2, 1, 2, 3, 3, 2]
BULLET_SPEED =  [4, 5, 6, 5, 5, 5, 6, 7]
BULLET_DAMAGE = [1, 1, 2, 3, 2, 2, 3, 4]
SHOT_DELAY =    [60, 50, 30, 40, 30, 25, 25, 30]

class UI:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        i = 0
        for obj in objects:
            if obj.type == 'tank':
                pygame.draw.rect(window, obj.color, (5 + i * 70, 5, 22, 22))

                text = fontUI.render(str(obj.rank), 1, 'black')
                rect = text.get_rect(center = (5 + i * 70 + 11, 5 + 11))
                window.blit(text, rect)

                text = fontUI.render(str(obj.hp), 1, obj.color)
                rect = text.get_rect(center = (5 + i * 70 + 32, 5 + 11))
                window.blit(text, rect)
                i += 1

class Tank:
    def __init__(self, color, px, py, direct, keyList):
        objects.append(self)
        self.move = False
        self.type = 'tank'
        self.color = color
        self.rect = pygame.Rect(px, py, TILE, TILE)
        self.direct = direct
        self.hp = 5
        self.shotTimer = 0

        self.moveSpeed = 2
        self.shotDelay = 60
        self.bulletSpeed = 5
        self.bulletDamage = 1

        self.keyLEFT = keyList[0]
        self.keyRIGHT = keyList[1]
        self.keyUP = keyList[2]
        self.keyDOWN = keyList[3]
        self.keySHOT = keyList[4]

        self.rank = 0
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.rect = self.image.get_rect(center = self.rect.center)
        for obj in objects:
            if obj != self and obj.type == 'block' and 'block2' and self.rect.colliderect(obj.rect):
                self.rect.right = obj.rect.left
    def update(self):
        self.image = pygame.transform.rotate(imgTanks[self.rank], -self.direct * 90)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() - 5, self.image.get_height() - 5))
        self.rect = self.image.get_rect(center = self.rect.center)

        self.moveSpeed = MOVE_SPEED[self.rank]
        self.shotDelay = SHOT_DELAY[self.rank]
        self.bulletSpeed = BULLET_SPEED[self.rank]
        self.bulletDamage = BULLET_DAMAGE[self.rank]
        
        oldX, oldY = self.rect.topleft
        if keys[self.keyLEFT] and self.rect.x > 0:
            self.rect.x -= self.moveSpeed
            self.direct = 3
            if move_sound.get_num_channels() == 0:
                move_sound.play()
        elif keys[self.keyRIGHT] and self.rect.x < WIDTH - TILE:
            self.rect.x += self.moveSpeed
            self.direct = 1
        elif keys[self.keyUP] and self.rect.y > 0:
            self.rect.y -= self.moveSpeed
            self.direct = 0
        elif keys[self.keyDOWN] and self.rect.y < HEIGHT - TILE:
            self.rect.y += self.moveSpeed
            self.direct = 2

        for obj in objects:
            if obj != self and obj.type == 'block' and 'block2' and self.rect.colliderect(obj.rect):
                self.rect.topleft = oldX, oldY

        if keys[self.keySHOT] and self.shotTimer == 0:
            shot_sound.play()
            dx = DIRECTS[self.direct][0] * self.bulletSpeed
            dy = DIRECTS[self.direct][1] * self.bulletSpeed
            Bullet(self, self.rect.centerx, self.rect.centery, dx, dy, self.bulletDamage)
            self.shotTimer = self.shotDelay

        if self.shotTimer > 0: self.shotTimer -= 1

    def draw(self):
        window.blit(self.image, self.rect)

    def damage(self, value):
        self.hp -= value

class Bullet:
    def __init__(self, parent, px, py, dx, dy, damage):
        bullets.append(self)
        self.parent = parent
        self.px, self.py = px, py
        self.dx, self.dy = dx, dy
        self.damage = damage

    def update(self):
        self.px += self.dx
        self.py += self.dy

        if self.px < 0 or self.px > WIDTH or self.py < 0 or self.py > HEIGHT:
            bullets.remove(self)
        else:
            for obj in objects:
                if obj != self.parent and obj.type != 'bang' and obj.type != 'bonus':
                    if obj.rect.collidepoint(self.px, self.py):
                        obj.damage(self.damage)
                        bullets.remove(self)
                        Bang(self.px, self.py)
                        break

    def draw(self):
        pygame.draw.circle(window, 'yellow', (self.px, self.py), 2)


class Bang:
    def __init__(self, px, py):
        objects.append(self)
        self.type = 'bang'

        self.px, self.py = px, py
        self.frame = 0

    def update(self):
        self.frame += 0.2
        if self.frame >= 3: objects.remove(self)

    def draw(self):
        image = imgBangs[int(self.frame)]
        rect = image.get_rect(center = (self.px, self.py))
        window.blit(image, rect)

class Block:
    def __init__(self, px, py, size):
        objects.append(self)
        self.type = 'block'

        self.rect = pygame.Rect(px, py, size, size)
        self.hp = 1

    def update(self):
        pass

    def draw(self):
        window.blit(imgBrick, self.rect)

    def damage(self, value):
        self.hp -= value
        if self.hp <= 0: objects.remove(self)

class Bonus:
    def __init__(self, px, py, bonusNum):
        objects.append(self)
        self.type = 'bonus'

        self.image = imgBonuses[bonusNum]
        self.rect = self.image.get_rect(center = (px, py))

        self.timer = 600
        self.bonusNum = bonusNum

    def update(self):
        if self.timer > 0: self.timer -= 1
        else: objects.remove(self)

        for obj in objects:
            if obj.type == 'tank' and self.rect.colliderect(obj.rect):
                if self.bonusNum == 0:
                    if obj.rank < len(imgTanks) - 1:
                        obj.rank += 1
                        objects.remove(self)
                        break
                elif self.bonusNum == 1:
                    obj.hp += 1
                    objects.remove(self)
                    break

    def draw(self):
        if self.timer % 30 < 15:
            window.blit(self.image, self.rect)
class Text():
    def __init__(self, text, x,y, font_name='verdana', font_size=20, color=(0,0,0)):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.color = color
        self.img = self.font.render(text, True, color)
        self.x = x
        self.y = y

    def draw(self):
        window.blit(self.img, (self.x, self.y))

    def set_text(self, new_text):
        self.img = self.font.render(new_text, True, self.color)

result_lb =  Text("", 200, 200, font_size= 50, color=(255, 255, 255))

bullets = []
objects = []
ui = UI()

def start_the_game():
    global run
    run = True
    menu.disable()
    Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    Tank('red', 650, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_l))
    start_sound.play()
    engine_sound.play()

def start_the_game1():
    global run
    run = True
    menu.disable()
    Tank('blue', 100, 275, 0, (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, pygame.K_SPACE))
    Tank('red', 660, 275, 0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_l))
    Tank('red', 650, 275, 0, (pygame.K_f, pygame.K_h, pygame.K_t, pygame.K_g, pygame.K_b))
    start_sound.play()
    engine_sound.play()

for _ in range(50):
    while True:
        x = randint(0, WIDTH // TILE - 1) * TILE
        y = randint(1, HEIGHT // TILE - 1) * TILE
        rect = pygame.Rect(x, y, TILE, TILE)
        fined = False
        for obj in objects:
            if rect.colliderect(obj.rect): fined = True

        if not fined: break

    Block(x, y, TILE)

bonusTimer = 180

myimage = pygame_menu.baseimage.BaseImage(
    image_path = 'images/block_brick.png',
    drawing_mode = pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
)

mytheme = pygame_menu.themes.THEME_DARK.copy()
mytheme.title_background_color = (255, 255, 255, 0)
mytheme.background_color = myimage
mytheme.font = pygame_menu.font.FONT_COMIC_NEUE


menu = pygame_menu.Menu('', 800, 600,
                       theme=mytheme)

menu.add.text_input('Name ', default='>_')
menu.add.button('Гра для 2', start_the_game)
menu.add.button('Гра для 3', start_the_game1)
menu.add.button('Створювачі', )
menu.add.button('Вийти', pygame_menu.events.EXIT)

menu.mainloop(window)

finish = False
while start_the_game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = False
            play = False
            start_the_game = False

    keys = pygame.key.get_pressed()

    if not finish:
        if bonusTimer > 0: bonusTimer -= 1
        else:
            Bonus(randint(50, WIDTH - 50), randint(50, HEIGHT - 50), randint(0, len(imgBonuses) - 1))
            bonusTimer = randint(120, 240)

        for bullet in bullets: bullet.update()
        for obj in objects:
            obj.update()
            if obj.type == "tank":
                if obj.hp <= 0:
                    finish = True
                    if obj.color == "red":
                        lose_sound.play()
                        result_lb.set_text("Переміг синій")
                    else:
                        lose_sound.play()
                        result_lb.set_text("Переміг червоний")

        ui.update()


    window.fill('black')
    for bullet in bullets: bullet.draw()
    for obj in objects: obj.draw()
    ui.draw()
    result_lb.draw()


    pygame.display.update()
    clock.tick(FPS)
#lose_sound.play()
pygame.quit()