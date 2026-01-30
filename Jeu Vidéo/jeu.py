import pygame
import random
import time

class Player:
    def __init__(self):
        self.image = pygame.image.load("pink_monster_jump.png")
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 500
        self.velocity = [0, 0]
        self.gravity = 1
        self.jump_force = -15
        self.run_speed = 5
        self.move_left = False
        self.move_right = False

    def update(self, platforms):
        self.velocity[1] += self.gravity

        if self.move_left and self.rect.left > 0:
            self.velocity[0] = -self.run_speed
        elif self.move_right and self.rect.right < 800:
            self.velocity[0] = self.run_speed
        else:
            self.velocity[0] = 0

        self.rect.move_ip(self.velocity)

        if self.rect.bottom >= 600:
            self.rect.bottom = 600
            self.velocity[1] = 0

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.rect.bottom == platform.rect.top:
                    self.velocity[1] = 0
                    self.rect.bottom = platform.rect.top
                elif self.rect.top == platform.rect.bottom:
                    self.rect.top = platform.rect.bottom

    def jump(self):
        self.velocity[1] = self.jump_force

    def render(self, screen):
        screen.blit(self.image, self.rect)

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)

class Level:
    def __init__(self):
        self.platforms = []
        self.score = 0
        self.sun = None

    def generate_platforms(self):
        for i in range(random.randint(8, 12)):
            x = random.randint(80, 800 - 140)
            y = random.randint(-200, -40)
            width = 100
            height = random.randint(20, 40)
            self.platforms.append(Platform(x, y, width, height))

    def check_sun(self, player):
        if player.rect.colliderect(self.sun.rect):
            self.reset_sun()
            self.score += 1
            self.platforms = []
            player.lives = 3

    def reset_sun(self):
        self.sun = None

    def render(self, screen):
        for platform in self.platforms:
            platform.render(screen)

        if self.sun:
            self.sun.render(screen)

    def is_complete(self):
        return len(self.platforms) == 0

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)

    def update(self, score, lives):
        self.score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
        self.lives_text = self.font.render(f"Lives: {lives}", True, (255, 255, 255))

    def render(self, screen):
        screen.blit(self.score_text, (10, 10))
        screen.blit(self.lives_text, (10, 40))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Platformer Game")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.level = Level()
        self.hud = HUD()
        self.mode_daltonien = False

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()