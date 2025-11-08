import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
RED = (255, 50, 50)
CYAN = (0, 255, 255)
PURPLE = (200, 50, 255)
YELLOW = (255, 255, 0)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Particle class for explosions
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 4)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.2  # Gravity
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

# Player class
class Player:
    def __init__(self):
        self.width = 50
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 80
        self.speed = 5
        self.bullets = []
        self.shoot_cooldown = 0
    
    def move(self, direction):
        self.x += direction * self.speed
        self.x = max(0, min(WIDTH - self.width, self.x))
    
    def shoot(self):
        if self.shoot_cooldown == 0:
            self.bullets.append(Bullet(self.x + self.width // 2, self.y, -8, CYAN))
            self.shoot_cooldown = 15
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.bullets = [b for b in self.bullets if b.y > 0]
        for bullet in self.bullets:
            bullet.update()
    
    def draw(self, surface):
        # Draw spaceship with glow effect
        glow_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*CYAN, 30), (self.width // 2 + 10, self.height // 2 + 10), 30)
        surface.blit(glow_surface, (self.x - 10, self.y - 10))
        
        # Main body
        pygame.draw.polygon(surface, CYAN, [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ])
        # Cockpit
        pygame.draw.circle(surface, WHITE, (self.x + self.width // 2, self.y + 20), 8)
        
        for bullet in self.bullets:
            bullet.draw(surface)

# Enemy class
class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.width = 40
        self.height = 35
        self.x = x
        self.y = y
        self.type = enemy_type
        self.colors = [GREEN, PURPLE, YELLOW]
        self.color = self.colors[enemy_type]
        self.move_speed = 1
        self.anim_offset = random.uniform(0, math.pi * 2)
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def draw(self, surface):
        # Animated alien with pulsing effect
        pulse = math.sin(pygame.time.get_ticks() * 0.005 + self.anim_offset) * 3
        
        # Glow effect
        glow_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, 20), (self.width // 2 + 10, self.height // 2 + 10), 25)
        surface.blit(glow_surface, (self.x - 10, self.y - 10))
        
        # Body
        pygame.draw.rect(surface, self.color, (self.x + 5, self.y + 10, self.width - 10, self.height - 15))
        
        # Eyes
        eye_y = self.y + 15 + pulse
        pygame.draw.circle(surface, WHITE, (int(self.x + 12), int(eye_y)), 6)
        pygame.draw.circle(surface, WHITE, (int(self.x + self.width - 12), int(eye_y)), 6)
        pygame.draw.circle(surface, RED, (int(self.x + 12), int(eye_y)), 3)
        pygame.draw.circle(surface, RED, (int(self.x + self.width - 12), int(eye_y)), 3)
        
        # Antennae
        pygame.draw.line(surface, self.color, (self.x + 10, self.y + 10), (self.x + 5, self.y), 3)
        pygame.draw.line(surface, self.color, (self.x + self.width - 10, self.y + 10), (self.x + self.width - 5, self.y), 3)
        pygame.draw.circle(surface, self.color, (self.x + 5, self.y), 4)
        pygame.draw.circle(surface, self.color, (self.x + self.width - 5, self.y), 4)

# Bullet class
class Bullet:
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.width = 4
        self.height = 15
    
    def update(self):
        self.y += self.speed
    
    def draw(self, surface):
        # Draw bullet with trail effect
        for i in range(5):
            alpha = 255 - i * 50
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), (0, 0, self.width, self.height), border_radius=2)
            surface.blit(s, (self.x - self.width // 2, self.y + i * 3))

# Game class
class Game:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.enemy_bullets = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.enemy_direction = 1
        self.enemy_move_down = False
        self.game_over = False
        self.win = False
        self.spawn_enemies()
    
    def spawn_enemies(self):
        self.enemies = []
        rows = 3 + self.level // 2
        cols = 8
        for row in range(min(rows, 5)):
            for col in range(cols):
                enemy_type = row % 3
                x = 100 + col * 70
                y = 50 + row * 60
                self.enemies.append(Enemy(x, y, enemy_type))
    
    def update(self):
        if self.game_over or self.win:
            return
        
        # Update player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1)
        if keys[pygame.K_SPACE]:
            self.player.shoot()
        
        self.player.update()
        
        # Move enemies
        move_down = False
        for enemy in self.enemies:
            enemy.move(self.enemy_direction * 0.5, 0)
            if enemy.x <= 0 or enemy.x >= WIDTH - enemy.width:
                move_down = True
        
        if move_down:
            self.enemy_direction *= -1
            for enemy in self.enemies:
                enemy.move(0, 20)
        
        # Enemy shooting
        if random.random() < 0.02 and self.enemies:
            shooter = random.choice(self.enemies)
            self.enemy_bullets.append(Bullet(shooter.x + shooter.width // 2, shooter.y + shooter.height, 4, RED))
        
        # Update enemy bullets
        self.enemy_bullets = [b for b in self.enemy_bullets if b.y < HEIGHT]
        for bullet in self.enemy_bullets:
            bullet.update()
        
        # Check collisions - player bullets with enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (enemy.x < bullet.x < enemy.x + enemy.width and
                    enemy.y < bullet.y < enemy.y + enemy.height):
                    self.enemies.remove(enemy)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    self.score += 10
                    # Create explosion particles
                    for _ in range(15):
                        self.particles.append(Particle(enemy.x + enemy.width // 2, 
                                                      enemy.y + enemy.height // 2, 
                                                      enemy.color))
        
        # Check collisions - enemy bullets with player
        for bullet in self.enemy_bullets[:]:
            if (self.player.x < bullet.x < self.player.x + self.player.width and
                self.player.y < bullet.y < self.player.y + self.player.height):
                self.enemy_bullets.remove(bullet)
                self.lives -= 1
                # Create explosion particles
                for _ in range(20):
                    self.particles.append(Particle(self.player.x + self.player.width // 2, 
                                                  self.player.y + self.player.height // 2, 
                                                  CYAN))
                if self.lives <= 0:
                    self.game_over = True
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
        
        # Check if enemies reached bottom
        for enemy in self.enemies:
            if enemy.y + enemy.height >= self.player.y:
                self.game_over = True
        
        # Check win condition
        if not self.enemies:
            self.level += 1
            self.spawn_enemies()
    
    def draw(self):
        # Starfield background
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 123) % WIDTH
            y = (i * 456 + pygame.time.get_ticks() // 20) % HEIGHT
            size = (i % 3) + 1
            brightness = 150 + (i % 100)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        
        # Draw game objects
        self.player.draw(screen)
        
        for enemy in self.enemies:
            enemy.draw(screen)
        
        for bullet in self.enemy_bullets:
            bullet.draw(screen)
        
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        lives_text = font.render(f"Lives: {self.lives}", True, WHITE)
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 150, 10))
        screen.blit(level_text, (WIDTH // 2 - 50, 10))
        
        if self.game_over:
            font_big = pygame.font.Font(None, 72)
            game_over_text = font_big.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 20))

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.game_over:
                    game = Game()
        
        game.update()
        game.draw()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
