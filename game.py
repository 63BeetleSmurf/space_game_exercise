import pygame, random

FPS = 60

SCREEN_WIDTH  = 320
SCREEN_HEIGHT = 480
SCREEN_RECT   = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

BG_COLOR  = (  0,   0,   0)

ALIEN_ROWS      = 15
ALIEN_COLS      = 11
ALIEN_ROW_SPACE = 10
ALIEN_COL_SPACE = 10
ALIEN_WIDTH     = 10
ALIEN_HEIGHT    = 10
ALIEN_SWARM_X   = int((SCREEN_WIDTH / 2) - (((ALIEN_WIDTH * ALIEN_COLS) + (ALIEN_COL_SPACE * (ALIEN_COLS - 1))) / 2))
ALIEN_SWARM_Y   = 10
ALIEN_SPEED_X   = 1
ALIEN_SPEED_Y   = 1
ALIEN_HEALTH    = 50
ALIEN_EXPLODING = 10
ALIEN_MAX_BOMBS = 8
ALIEN_COLOR           = (  0, 128,   0)
ALIEN_EXPLOSION_COLOR = (255,   0,   0)
ALIEN_BOMB_SPEED_X = 2
ALIEN_BOMB_SPEED_Y = 2
ALIEN_BOMB_COLOR = (255,   0,   0)
ALIEN_BOMB_EXPLOSION_COLOR = (  0, 255,   0)

PLAYER_SHIP_WIDTH   = 40
PLAYER_SHIP_X       = int((SCREEN_WIDTH / 2) - (PLAYER_SHIP_WIDTH / 2))
PLAYER_SHIP_Y       = 400
PLAYER_SHIP_HEIGHT  = 15
PLAYER_SHIP_SPEED_X = 2
PLAYER_SHIP_COLOR   = (0, 0, 255)
PLAYER_SHIELDED_SHIP_COLOR = (0, 0, 128)

PLAYER_FIRE_RATE      = 4
PLAYER_BULLET_SPEED_Y = 2
PLAYER_BULLET_COLOR           = (128, 128, 128)
PLAYER_BULLET_EXPLOSION_COLOR = (255, 255,   0)

def ResetRect():
    return pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)

def ExpandRect(rect1, rect2):
    newRect = pygame.Rect(0, 0, 0, 0)
    newRect.x = min(rect1.x, rect2.x)
    newRect.y = min(rect1.y, rect2.y)
    newRect.width = max(rect1.width, rect2.right - newRect.x)
    newRect.height = max(rect1.height, rect2.bottom - newRect.y)
    return newRect

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Base():
    def ProcessInput(self, events, pressed_keys):
        print ("uh-oh, you didn't override this in the child class")

    def Update(self):
        print ("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print ("uh-oh, you didn't override this in the child class")

class ObjectBase(Base):
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.direction = Point(0, 0)
        self.speed = Point(0, 0)
        self.state = 0
        self.health = 0

class SceneBase(Base):
    def __init__(self):
        self.next = self

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)

class AlienSwarm(ObjectBase):

    def __init__(self, x, y):
        ObjectBase.__init__(self)
        self.alienRows = []
        xDirection = 1
        for i in range(ALIEN_ROWS):
            newRow = AlienRow(x, y + ((ALIEN_HEIGHT + ALIEN_ROW_SPACE) * i), xDirection)
            self.alienRows.append(newRow)
            xDirection *= -1
        self.state = 1

    def Update(self, explosions):
        self.state = 0
        self.rect = ResetRect()
        for row in self.alienRows:
            if row.state > 0:
                self.state = 1
                row.Update(explosions)
                self.rect = ExpandRect(self.rect, row.rect)

    def Render(self, surface):
        for row in self.alienRows:
            if row.state > 0:
                row.Render(surface)

class AlienRow(ObjectBase):
    def __init__(self, x, y, xDirection):
        self.alienShips = []
        ObjectBase.__init__(self)
        self.direction.x = xDirection
        self.rect = ResetRect()
        for i in range(ALIEN_COLS):
            newAlien = AlienShip(x + ((ALIEN_WIDTH + ALIEN_COL_SPACE) * i), y, self.direction.x)
            self.alienShips.append(newAlien)
            self.rect = ExpandRect(self.rect, newAlien.rect)
        self.state = 1

    def Update(self, explosions):
        self.direction.y = 0
        if self.rect.x < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction.x *= -1
            self.direction.y = 1

        self.state = 0
        self.rect = ResetRect()
        for alien in self.alienShips:
            if alien.state > 0:
                self.state = 1
                alien.Update(self.direction, explosions)
                self.rect = ExpandRect(self.rect, alien.rect)

    def Render(self, surface):
        for alien in self.alienShips:
            if alien.state > 0:
                alien.Render(surface)

class AlienShip(ObjectBase):

    def __init__(self, x, y, xDirection):
        ObjectBase.__init__(self)
        self.rect.x = x
        self.rect.y = y
        self.rect.width = ALIEN_WIDTH
        self.rect.height = ALIEN_HEIGHT
        self.speed.x = ALIEN_SPEED_X
        self.speed.y = ALIEN_SPEED_Y
        self.health = ALIEN_HEALTH
        self.state = 1

    def Update(self, direction, explosions):
        if self.state == 1 and self.health <= 0:
            self.state = 2
        elif self.state > 1 and self.state <= ALIEN_EXPLODING:
            explosions.append(Explosion(random.randint(self.rect.x, self.rect.right), random.randint(self.rect.y, self.rect.bottom), random.randint(0, 4), ALIEN_EXPLOSION_COLOR))
            self.state += 1
        elif self.state > ALIEN_EXPLODING:
            self.state = 0

        if self.state == 1:
            self.rect.x += self.speed.x * direction.x
            self.rect.y += self.speed.y * direction.y
        else:
            self.speed.x = 0

    def Render(self, surface):
        surface.fill(ALIEN_COLOR, self.rect)

class AlienBombs(Base):
    def __init__(self):
        self.bombs = []

    def Update(self, playerShip, alienSwarm, explosions):
        if len(self.bombs) < ALIEN_MAX_BOMBS:
            alien = alienSwarm.alienRows[random.randint(0, ALIEN_ROWS - 1)].alienShips[random.randint(0, ALIEN_COLS - 1)]
            if alien.state != 0:
                self.bombs.append(AlienBomb(alien.rect.x - int(alien.rect.width / 2), alien.rect.bottom))

        for bomb in self.bombs:
            if bomb.state == 0:
                self.bombs.remove(bomb)
            else:
                bomb.Update(playerShip, alienSwarm, self, explosions)

    def Render(self, surface):
        for bomb in self.bombs:
            bomb.Render(surface)

class AlienBomb(ObjectBase):
    def __init__(self, x, y):
        ObjectBase.__init__(self)
        self.rect.x = x
        self.rect.y = y
        self.rect.width = 3
        self.rect.height = 3
        self.speed.y = ALIEN_BOMB_SPEED_Y
        self.speed.x = ALIEN_BOMB_SPEED_X
        self.state = 1
        self.direction.y = 1
        self.direction.x = 0

    def Update(self, playerShip, alienSwarm, alienBombs, explosions):
        self.rect.y += self.speed.y * self.direction.y

        if self.direction.y == 1:
            if self.rect.y < SCREEN_HEIGHT:
                if self.rect.colliderect(playerShip.rect):
                    if playerShip.shields:
                        self.direction.y = -1
                        self.direction.x = playerShip.direction.x
                    else:
                        explosions.append(Explosion(self.rect.x, self.rect.y, 4, ALIEN_BOMB_EXPLOSION_COLOR))
                        self.state = 0
            else:
                self.state = 0
        else:
            if self.rect.y > 0:
                self.rect.x += self.speed.x * self.direction.x
                if self.rect.x <= 0 or self.rect.x >= SCREEN_WIDTH:
                    self.direction.x = self.direction.x * -1

                for alienBomb in alienBombs.bombs:
                    if alienBomb != self and alienBomb.state != 0 and self.rect.colliderect(alienBomb.rect):
                        alienBomb.state = 0
                        explosions.append(Explosion(self.rect.x, self.rect.y, 4, PLAYER_BULLET_EXPLOSION_COLOR))
                        self.state = 0
                        break

                if self.state != 0:
                    if alienSwarm.state != 0 and self.rect.colliderect(alienSwarm.rect):
                        for alienRow in alienSwarm.alienRows:
                            if alienRow.state != 0 and self.rect.colliderect(alienRow.rect):
                                for alien in alienRow.alienShips:
                                    if alien.state != 0 and self.rect.colliderect(alien.rect):
                                        alien.health = 0
                                        explosions.append(Explosion(self.rect.x, self.rect.y, 1, PLAYER_BULLET_EXPLOSION_COLOR))
                                        self.state = 0
                                        break
            else:
                self.state = 0

    def Render(self, surface):
        if self.state != 0:
            surface.fill(ALIEN_BOMB_COLOR, self.rect)

class PlayerShip(ObjectBase):

    def __init__(self, x, y):
        ObjectBase.__init__(self)
        self.rect.x = x
        self.rect.y = y
        self.rect.width = PLAYER_SHIP_WIDTH
        self.rect.height = PLAYER_SHIP_HEIGHT
        self.speed.x = PLAYER_SHIP_SPEED_X
        self.health = 100
        self.state = 1
        self.shields = False

    def ProcessInput(self, pressed_keys):
        if pressed_keys[pygame.K_LEFT]:
            self.direction.x = -1
        elif pressed_keys[pygame.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0
        if pressed_keys[pygame.K_LSHIFT]:
            self.shields = True
        else:
            self.shields = False

    def Update(self):
        newPosition = self.rect.x + (self.speed.x * self.direction.x)
        if newPosition > 0 and newPosition < SCREEN_WIDTH - self.rect.width:
            self.rect.x = newPosition

    def Render(self, surface):
        if self.shields:
            surface.fill(PLAYER_SHIELDED_SHIP_COLOR, self.rect)
        else:
            surface.fill(PLAYER_SHIP_COLOR, self.rect)

class PlayerBullets(Base):
    def __init__(self):
        self.fire = False
        self.bullets = []

    def ProcessInput(self, pressed_keys):
        self.fire = pressed_keys[pygame.K_SPACE]

    def Update(self, playerShip, alienSwarm, alienBombs, explosions):
        if self.fire and not playerShip.shields:
            for i in range(PLAYER_FIRE_RATE):
                self.bullets.append(PlayerBullet(random.randint(playerShip.rect.x + 2, playerShip.rect.right - 3), playerShip.rect.y))

        for bullet in self.bullets:
            if bullet.state == 0:
                self.bullets.remove(bullet)
            else:
                bullet.Update(alienSwarm, alienBombs, explosions)

    def Render(self, pixelArray):
        for bullet in self.bullets:
            bullet.Render(pixelArray)

class PlayerBullet(ObjectBase):
    def __init__(self, x, y):
        ObjectBase.__init__(self)
        self.rect.x = x
        self.rect.y = y
        self.rect.width = 1
        self.rect.height = 1
        self.speed.y = PLAYER_BULLET_SPEED_Y
        self.state = 1

    def Update(self, alienSwarm, alienBombs, explosions):
        if self.state == 1:
            explosions.append(Explosion(self.rect.x, self.rect.y, 0, PLAYER_BULLET_EXPLOSION_COLOR))
            self.state = 2
        elif self.state == 2:
            self.rect.y -= self.speed.y

            if self.rect.y > 0:
                if alienSwarm.state != 0 and self.rect.colliderect(alienSwarm.rect):
                    for alienRow in alienSwarm.alienRows:
                        if alienRow.state != 0 and self.rect.colliderect(alienRow.rect):
                            for alien in alienRow.alienShips:
                                if alien.state != 0 and self.rect.colliderect(alien.rect):
                                    alien.health -= 1
                                    explosions.append(Explosion(self.rect.x, self.rect.y, 1, PLAYER_BULLET_EXPLOSION_COLOR))
                                    self.state = 0
                                    break
                if self.state != 0:
                    for alienBomb in alienBombs.bombs:
                        if alienBomb.state != 0 and self.rect.colliderect(alienBomb.rect):
                            alienBomb.state = 0
                            explosions.append(Explosion(self.rect.x, self.rect.y, 4, PLAYER_BULLET_EXPLOSION_COLOR))
                            self.state = 0
                            break
            else:
                self.state = 0

    def Render(self, pixelArray):
        if self.state == 2 and pixelArray[self.rect.x][self.rect.y] != PLAYER_BULLET_EXPLOSION_COLOR:
            pixelArray[self.rect.x][self.rect.y] = PLAYER_BULLET_COLOR

class Explosion(ObjectBase):
    def __init__(self, x, y , maxSize, color):
        ObjectBase.__init__(self)
        self.state = 1
        self.rect.x = x
        self.rect.y = y
        self.maxSize = maxSize
        self.size = 0
        self.color = color
        self.explosion = {}

    def Update(self):
        del self.explosion
        x = self.rect.x
        y = self.rect.y
        color = self.color
        self.explosion = {x: {y: color}}
        if self.size >= 1:
            self.explosion[x    ][y - 1] = color
            self.explosion[x    ][y + 1] = color
            self.explosion[x - 1] = {y: color}
            self.explosion[x + 1] = {y: color}
            if self.size >= 2:
                self.explosion[x    ][y - 2] = color
                self.explosion[x    ][y + 2] = color
                self.explosion[x - 1][y - 1] = color
                self.explosion[x - 1][y + 1] = color
                self.explosion[x + 1][y - 1] = color
                self.explosion[x + 1][y + 1] = color
                self.explosion[x - 2] = {y: color}
                self.explosion[x + 2] = {y: color}
                if self.size == 3:
                    self.explosion[x    ][y - 3] = color
                    self.explosion[x    ][y + 3] = color
                    self.explosion[x - 1][y - 2] = color
                    self.explosion[x + 1][y - 2] = color
                    self.explosion[x - 1][y + 2] = color
                    self.explosion[x + 1][y + 2] = color
                    self.explosion[x - 2][y - 1] = color
                    self.explosion[x + 2][y - 1] = color
                    self.explosion[x - 2][y + 1] = color
                    self.explosion[x + 2][y + 1] = color
                    self.explosion[x - 3] = {y: color}
                    self.explosion[x + 3] = {y: color}
                    if self.size >= 4:
                        self.explosion[x    ][y - 4] = color
                        self.explosion[x    ][y + 4] = color
                        self.explosion[x - 1][y - 3] = color
                        self.explosion[x + 1][y - 3] = color
                        self.explosion[x - 1][y + 3] = color
                        self.explosion[x + 1][y + 3] = color
                        self.explosion[x - 3][y - 1] = color
                        self.explosion[x + 3][y - 1] = color
                        self.explosion[x - 3][y + 1] = color
                        self.explosion[x + 3][y + 1] = color
                        self.explosion[x - 2][y - 2] = color
                        self.explosion[x + 2][y - 2] = color
                        self.explosion[x - 2][y + 2] = color
                        self.explosion[x + 2][y + 2] = color
                        self.explosion[x - 4] = {y: color}
                        self.explosion[x + 4] = {y: color}
        if self.size == self.maxSize:
            self.state = 0
        else:
            self.size += 1

    def Render(self, pixelArray):
        for x in self.explosion.keys():
            if x >= 0 and x < SCREEN_WIDTH:
                for y in self.explosion[x].keys():
                    if y >= 0 and y < SCREEN_HEIGHT:
                        pixelArray[x][y] = self.explosion[x][y]

class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.Terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.SwitchToScene(GameScene())

    def Update(self):
        pass

    def Render(self, surface):
        surface.fill((255, 0, 0))

class GameScene(SceneBase):

    def __init__(self):
        SceneBase.__init__(self)
        self.alienSwarm = AlienSwarm(ALIEN_SWARM_X, ALIEN_SWARM_Y)
        self.alienBombs = AlienBombs()
        self.playerShip = PlayerShip(PLAYER_SHIP_X, PLAYER_SHIP_Y)
        self.playerBullets = PlayerBullets()
        self.explosions = []

    def ProcessInput(self, events, pressed_keys):
        self.playerShip.ProcessInput(pressed_keys)
        self.playerBullets.ProcessInput(pressed_keys)

    def Update(self):
        if self.alienSwarm.state == 0:
            self.SwitchToScene(TitleScene())
        self.alienSwarm.Update(self.explosions)
        self.alienBombs.Update(self.playerShip, self.alienSwarm, self.explosions)

        self.playerShip.Update()
        self.playerBullets.Update(self.playerShip, self.alienSwarm, self.alienBombs, self.explosions)

        for explosion in self.explosions:
            if explosion.state == 0:
                self.explosions.remove(explosion)
            else:
                explosion.Update()

    def Render(self, surface):
        surface.fill(BG_COLOR)
        self.alienSwarm.Render(surface)
        self.alienBombs.Render(surface)

        self.playerShip.Render(surface)

        pixelArray = pygame.PixelArray(surface)
        self.playerBullets.Render(pixelArray)
        for explosion in self.explosions:
            explosion.Render(pixelArray)
        del pixelArray

def run_game(width, height, fps, starting_scene):
    pygame.init()
    surface = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(surface)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)

def main(args):
    run_game(SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TitleScene())

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
