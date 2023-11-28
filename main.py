import pygame
import random

WIDTH = 400
HEIGHT = 600
BOUNDARY_Y_UPPER = HEIGHT * 0.6
BOUNDARY_Y_LOWER = HEIGHT
BOUNDARY_X_LEFT = 0
BOUNDARY_X_RIGHT = WIDTH

# Define gamepad button
START_BUTTON = 7
BACK_BUTTON = 6


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty):
        super().__init__()

        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()

        self.rect.center = [startx, starty]

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Player(Sprite):
    def __init__(self, startx, starty):
        super().__init__("aircraft.png", startx, starty)
        self.projectiles = pygame.sprite.Group()
        self.shoot_cooldown = 0 
        self.ultimate_cooldown = 0

    def update(self):
        #Left joystick
        x_speed = round(pygame.joystick.Joystick(0).get_axis(0))
        y_speed = round(pygame.joystick.Joystick(0).get_axis(1))

        #Right joystick
        x_speed += round(pygame.joystick.Joystick(0).get_axis(2))
        y_speed += round(pygame.joystick.Joystick(0).get_axis(3))

        #D-pad
        x_speed += round(pygame.joystick.Joystick(0).get_hat(0)[0])
        y_speed -= round(pygame.joystick.Joystick(0).get_hat(0)[1])

        #Back trigger
        right_boost = 1 + round(pygame.joystick.Joystick(0).get_axis(4))
        left_boost = 1 + round(pygame.joystick.Joystick(0).get_axis(5))

        # Set boundary
        if ((self.rect.top + y_speed*2) > BOUNDARY_Y_UPPER) and ((self.rect.bottom + y_speed*2) < BOUNDARY_Y_LOWER) and ((self.rect.left + (x_speed*2 - right_boost*2 + left_boost*2)) > BOUNDARY_X_LEFT) and ((self.rect.right + (x_speed*2 - right_boost*2 + left_boost*2)) < BOUNDARY_X_RIGHT): 
            self.move(x_speed*2 - right_boost*2 + left_boost*2, y_speed*2)

        # Shooting trigger
        if (pygame.joystick.Joystick(0).get_button(5) or pygame.joystick.Joystick(0).get_button(4)) and self.shoot_cooldown == 0:
            self.shoot()
            self.shoot_cooldown = 60

        # Ultimate trigger
        if (pygame.joystick.Joystick(0).get_button(8) or pygame.joystick.Joystick(0).get_button(9)) and self.ultimate_cooldown == 0:
            self.ultimate()
            self.ultimate_cooldown = 300

        # Update cooldown timer
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.ultimate_cooldown > 0:
            self.ultimate_cooldown -= 1

    def move(self, x, y):
        self.rect.move_ip([x, y])

    def shoot(self):
        new_projectile = Projectile(self.rect.centerx, self.rect.top)
        self.projectiles.add(new_projectile)

    def ultimate(self):
        new_projectile1 = Projectile(self.rect.centerx, self.rect.top)
        new_projectile2 = Projectile(self.rect.left, self.rect.top)
        new_projectile3 = Projectile(self.rect.right, self.rect.top)
        self.projectiles.add(new_projectile1)
        self.projectiles.add(new_projectile2)
        self.projectiles.add(new_projectile3)


class Box(Sprite):
    def __init__(self, startx, starty):
        super().__init__("enemy.png", startx, starty)

    def update(self):
        self.rect.y += 2

class Projectile(Sprite):
    def __init__(self, startx, starty):
        super().__init__("projectile.png", startx, starty)

    def update(self):
        self.rect.y -= 5  # Move the projectile upward
        if self.rect.bottom < 0:
            self.kill()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    player = Player(WIDTH*0.5, HEIGHT*0.8)
    boxes = pygame.sprite.Group()

    box_destroyed_count = 0
    
    spawn_box_timer = 0
    spawn_interval = 120

    in_menu = True
    game_over = False
    background_color = 0

    # Background image path
    BACKGROUND0 = pygame.image.load("summer1.png").convert()
    BACKGROUND1 = pygame.image.load("summer2.png").convert()
    BACKGROUND2 = pygame.image.load("summer3.png").convert()
    BACKGROUND3 = pygame.image.load("summer4.png").convert()

    while True:
        if in_menu:
            # Menu loop
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if pygame.joystick.Joystick(0).get_button(START_BUTTON):
                        in_menu = False
                        game_over = False
                        # Reinitialize game entities for a new game
                        player = Player(WIDTH*0.5, HEIGHT*0.8)
                        boxes = pygame.sprite.Group()
                        spawn_box_timer = 0

            # Menu screen
            screen.fill((255, 255, 255))
            font = pygame.font.Font(None, 36)
            text = font.render('Press Start to Play', True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)

            pygame.display.flip()
        else:
            # Main game loop
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if pygame.joystick.Joystick(0).get_button(BACK_BUTTON):
                        in_menu = True
                    if pygame.joystick.Joystick(0).get_button(0):
                        background_color = 0
                    elif pygame.joystick.Joystick(0).get_button(1):
                        background_color = 1
                    elif pygame.joystick.Joystick(0).get_button(2):
                        background_color = 2
                    elif pygame.joystick.Joystick(0).get_button(3):
                        background_color = 3 

            if game_over:
                in_menu = True
                continue

            pygame.event.pump()
            player.update()

            spawn_box_timer += 1
            if spawn_box_timer >= spawn_interval:
                spawn_box_timer = 0
                new_box_x = random.randint(BOUNDARY_X_LEFT, BOUNDARY_X_RIGHT - 50)
                boxes.add(Box(new_box_x, -50))

            for box in boxes:
                box.update()
                if box.rect.top > HEIGHT:
                    boxes.remove(box)

            # Collision detection
            if pygame.sprite.spritecollide(player, boxes, False):
                game_over = True
                print("Game Over!")

            # Update projectiles collision
            for projectile in player.projectiles:
                projectile.update()
                collided = pygame.sprite.spritecollide(projectile, boxes, True)
                if collided:
                    projectile.kill()
                    box_destroyed_count += 1

            # Changing background color
            if(background_color == 0):
                screen.blit(BACKGROUND0, (0, 0))
            elif(background_color == 1):
                screen.blit(BACKGROUND1, (0, 0))
            elif(background_color == 2):
                screen.blit(BACKGROUND2, (0, 0))
            elif(background_color == 3):
                screen.blit(BACKGROUND3, (0, 0))

            player.draw(screen)
            boxes.draw(screen)
            player.projectiles.draw(screen)

            # Display the box destroyed count
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Enemies Destroyed: {box_destroyed_count}', True, (255, 255, 255))
            screen.blit(score_text, (10, 10))

            pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    main()