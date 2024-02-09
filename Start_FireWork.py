# ---************************************************---
# @coding: utf-8
# @Time : 2023/1/21 0021 19:48
# @Author : Matrix
# @File : Start_FireWork.py
# @Software: PyCharm
# ---************************************************---
import pygame
from random import randint, uniform, choice
import math

# ===========首先设置全局变量====================
vector = pygame.math.Vector2
# 重力变量
gravity = vector(0, 0.3)
# 控制窗口的大小
# DISPLAY_WIDTH = 0
# DISPLAY_HEIGHT= 0

# 颜色选项
trail_colours = [(45, 45, 45), (60, 60, 60), (75, 75, 75), (125, 125, 125), (150, 150, 150)]
dynamic_offset = 1
static_offset = 3


# =======Firework : 整体部分；================
class Firework:
    def __init__(self,DISPLAY_WIDTH,DISPLAY_HEIGHT):
        # 随机颜色
        self.colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.colours = (
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            (randint(0, 255), randint(0, 255), randint(0, 255)),
            (randint(0, 255), randint(0, 255), randint(0, 255)))
        self.firework = Particle(randint(0, DISPLAY_WIDTH), DISPLAY_HEIGHT, True,
                                 self.colour)  # Creates the firework particle
        self.exploded = False
        self.particles = []
        self.min_max_particles = vector(100, 225)

    def update(self, win):  # 每帧调用
        if not self.exploded:
            self.firework.apply_force(gravity)
            self.firework.move()
            for tf in self.firework.trails:
                tf.show(win)

            self.show(win)

            if self.firework.vel.y >= 0:
                self.exploded = True
                self.explode()
        else:
            for particle in self.particles:
                particle.apply_force(vector(gravity.x + uniform(-1, 1) / 20, gravity.y / 2 + (randint(1, 8) / 100)))
                particle.move()
                for t in particle.trails:
                    t.show(win)
                particle.show(win)

    def explode(self):
        # amount 数量
        amount = randint(self.min_max_particles.x, self.min_max_particles.y)
        for i in range(amount):
            self.particles.append(Particle(self.firework.pos.x, self.firework.pos.y, False, self.colours))

    def show(self, win):
        pygame.draw.circle(win, self.colour, (int(self.firework.pos.x), int(self.firework.pos.y)), self.firework.size)

    def remove(self):
        if self.exploded:
            for p in self.particles:
                if p.remove is True:
                    self.particles.remove(p)

            if len(self.particles) == 0:
                return True
            else:
                return False


# ================Particle：烟花粒子（包含轨迹）======================
class Particle:
    def __init__(self, x, y, firework, colour):
        self.firework = firework
        self.pos = vector(x, y)
        self.origin = vector(x, y)
        self.radius = 20
        self.remove = False
        self.explosion_radius = randint(5, 18)
        self.life = 0
        self.acc = vector(0, 0)
        # trail variables
        self.trails = []  # stores the particles trail objects
        self.prev_posx = [-10] * 10  # stores the 10 last positions
        self.prev_posy = [-10] * 10  # stores the 10 last positions

        if self.firework:
            self.vel = vector(0, -randint(17, 20))
            self.size = 5
            self.colour = colour
            for i in range(5):
                self.trails.append(Trail(i, self.size, True))
        else:
            self.vel = vector(uniform(-1, 1), uniform(-1, 1))
            self.vel.x *= randint(7, self.explosion_radius + 2)
            self.vel.y *= randint(7, self.explosion_radius + 2)
            # 向量
            self.size = randint(2, 4)
            self.colour = choice(colour)
            # 5 个 tails总计
            for i in range(5):
                self.trails.append(Trail(i, self.size, False))

    def apply_force(self, force):
        self.acc += force

    def move(self):
        if not self.firework:
            self.vel.x *= 0.8
            self.vel.y *= 0.8
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        if self.life == 0 and not self.firework:  # 检查粒子的爆炸范围
            distance = math.sqrt((self.pos.x - self.origin.x) ** 2 + (self.pos.y - self.origin.y) ** 2)
            if distance > self.explosion_radius:
                self.remove = True

        self.decay()

        self.trail_update()

        self.life += 1

    def show(self, win):
        pygame.draw.circle(win, (self.colour[0], self.colour[1], self.colour[2], 0), (int(self.pos.x), int(self.pos.y)),
                           self.size)

    def decay(self):  # random decay of the particles
        if 50 > self.life > 10:  # early stage their is a small chance of decay
            ran = randint(0, 30)
            if ran == 0:
                self.remove = True
        elif self.life > 50:
            ran = randint(0, 5)
            if ran == 0:
                self.remove = True

    def trail_update(self):
        self.prev_posx.pop()
        self.prev_posx.insert(0, int(self.pos.x))
        self.prev_posy.pop()
        self.prev_posy.insert(0, int(self.pos.y))

        for n, t in enumerate(self.trails):
            if t.dynamic:
                t.get_pos(self.prev_posx[n + dynamic_offset], self.prev_posy[n + dynamic_offset])
            else:
                t.get_pos(self.prev_posx[n + static_offset], self.prev_posy[n + static_offset])


# =======Trail：烟花轨迹，本质上是一个点 。创建 Trail 类，定义 show 方法绘制轨迹 、get_pos  实时获取轨迹坐标====
class Trail:
    def __init__(self, n, size, dynamic):
        self.pos_in_line = n
        self.pos = vector(-10, -10)
        self.dynamic = dynamic

        if self.dynamic:
            self.colour = trail_colours[n]
            self.size = int(size - n / 2)
        else:
            self.colour = (255, 255, 200)
            self.size = size - 2
            if self.size < 0:
                self.size = 0

    def get_pos(self, x, y):
        self.pos = vector(x, y)

    def show(self, win):
        pygame.draw.circle(win, self.colour, (int(self.pos.x), int(self.pos.y)), self.size)


def update(win, fireworks):
    for fw in fireworks:
        fw.update(win)
        if fw.remove():
            fireworks.remove(fw)

    pygame.display.update()


def Draw():
    pygame.init()
    # 加载背景音乐
    pygame.mixer.music.load("./data/newyear.mp3")
    # 循环播放背景音乐
    pygame.mixer.music.play(-1)
    # 停止背景音乐
    # pygame.mixer.music.stop()
    # 加载音效
    boom_sound = pygame.mixer.Sound("./data/newyear.mp3")
    # 播放音效
    boom_sound.play()
    boom_sound.stop()
    pygame.display.set_caption("新年demo")  # 标题
    background = pygame.image.load("./data/1.png")  # 背景
    title_font = pygame.font.Font("./data/hanyijielongtaohuayuan.ttf", 30)
    author_font = pygame.font.Font("./data/hanyijielongtaohuayuan.ttf", 15)
    title = title_font.render("新年快乐", False, (0, 0, 0), (220, 20, 60))
    author = author_font.render("By 无名", False, (250, 59, 85))
    DISPLAY_WIDTH = background.get_width()
    DISPLAY_HEIGHT = background.get_height()
    # 计算文本居中位置
    title_rect = title.get_rect()  # 获取title的矩形区域
    title_center_x = DISPLAY_WIDTH // 2
    title_center_y = DISPLAY_HEIGHT // 2
    title_rect.center = (title_center_x, 50)  # 设置文本矩形的中心为屏幕中心
    author_rect=author.get_rect()
    author_rect.center = (title_center_x, 80)


    # pygame.image.load("")
    win = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    # win.blit(background)
    clock = pygame.time.Clock()

    fireworks = [Firework(DISPLAY_WIDTH,DISPLAY_HEIGHT) for i in range(2)]  # create the first fireworks
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # Change game speed with number keys
                if event.key == pygame.K_1:  # 按下 1
                    fireworks.append(Firework(DISPLAY_WIDTH,DISPLAY_HEIGHT))
                if event.key == pygame.K_2:  # 按下 2 加入10个烟花
                    for i in range(10):
                        fireworks.append(Firework(DISPLAY_WIDTH,DISPLAY_HEIGHT))
                if event.key == pygame.K_3:  # 按下 3 加入100个烟花
                    for i in range(100):
                        fireworks.append(Firework(DISPLAY_WIDTH,DISPLAY_HEIGHT))
        win.fill((20, 20, 30))  # 绘制背景
        win.blit(background, (0, 0))
        win.blit(title, title_rect)  # 用过位置绘制标题
        win.blit(author, author_rect)

        if randint(0, 20) == 1:  # 创建新的烟花
            fireworks.append(Firework(DISPLAY_WIDTH,DISPLAY_HEIGHT))
        update(win, fireworks)
    pygame.quit()
    quit()
    pass

# =======================主函数=======================
def main():
    pygame.init()
    pygame.font.init()
    # sound_wav = pygame.mixer.music.load("./newyear.mp3")
    # pygame.mixer.music.play()

Draw()
pass

if __name__ == 'main':
    main()