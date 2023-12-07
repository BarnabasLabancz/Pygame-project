"""
Game idea:
Game name:
The player spawns in a room along with a few monsters and a coin. This is level 1.
All monsters and the coin are placed randomly in the room.
The player must collect the coin while avoiding the monsters.
The monsters follow the player in a way similar to exercise 14 in part 13.

When the player collects the coin, a door appears on the right side of the room.
Going through the door, the player gets to level 2, which is a bit harder than level 1.
They new level is harder because there are more monsters, and maybe they are a bit faster as well.

The player starts with 3 lifes, losing 1 each time they touch a monster.
The number of lifes remaining is displayed in the corner of the screen.

There are 10 levels in total, the player completes the game if they successfully complete all levels.
The time of completion (shorter is better) and the number of remaining lifes gives a final score if the game is beaten.
This incentivizes competition.


If there is enough time, implement power-ups.
For example, a red circle could give an extra life, while a green circle increases the speed of the player temporarily.

Implement exit, pause, and help features.
"""

import pygame
import random
import math
from PIL import Image
import time


class InsertName():
    def __init__(self):
        pygame.init()
        # Fonts
        self.small_font = pygame.font.SysFont("Arial", 26)
        self.medium_font = pygame.font.SysFont("Arial", 32)
        self.large_font = pygame.font.SysFont("Arial", 40)
        self.huge_font = pygame.font.SysFont("Arial", 120)

        self.window_width = 1280
        self.window_height = 720
        self.top_bar_height = 50
        self.move_left, self.move_right, self.move_up, self.move_down = False, False, False, False
        self.lifes = 4
        self.moving_speed = 3
        self.monster_speed = 0.75
        self.safe_zone_width = 160

        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Insert Name")

        self.level = 0
        self.number_of_monsters = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
        self.coin_counter = 0
        self.player_alive = True
        self.win = False

        # Helper variable to only deduct 1 life point when hitting monster
        self.hit_monster_before = False

        self.clock = pygame.time.Clock()
        self.load_images()
        
        self.start_time=time.time()
        self.main_loop()

    def main_loop(self):
        self.next_level()

        while True:
            self.check_input()
            self.move()
            self.monster_move()
            self.draw_window()

            # Check if the player has hit anything
            if self.hit_monster():
                self.lose_life()
                self.hit_monster_before = True
            else:
                self.hit_monster_before = False

            if self.hit_coin() and self.coin_counter!=3:
                self.coin_counter += 1

            if self.coin_counter==3:
                self.spawn_door()

            if self.hit_door():
                if self.level < 10:
                    self.next_level()
                else:
                    self.win = True

    def load_images(self):
        self.robot = pygame.image.load("robot.png")
        self.monster = pygame.image.load("red_monster.png")
        self.coin = pygame.image.load("coin.png")
        self.door = pygame.image.load("door.png")

        self.robot_dimensions = (
            self.robot.get_width(), self.robot.get_height())
        self.monster_dimensions = (
            self.monster.get_width(), self.monster.get_height())
        self.coin_dimensions = (self.coin.get_width(), self.coin.get_height())
        self.door_dimensions = (self.door.get_width(), self.door.get_height())
    
    def new_monster_colour(self):
        r_new, g_new, b_new = 255, 20, 100

        im = Image.open("monster.png").convert('RGBA')
        
        pixels=list(im.getdata())
        new_pixels=[]

        for x in range(len(pixels)):
            r, g, b, a = pixels[x]
            if (r, g, b) == (0,0,0):
                new_pixels.append((r_new, g_new, b_new, a))
            else:
                new_pixels.append((r,g,b,a))
        
        new_im=Image.new(im.mode, im.size)
        new_im.putdata(new_pixels)
        new_im.save("red_monster.png")

    def next_level(self):
        self.level += 1

        self.robot_coordinates = [
            40, (self.window_height-self.top_bar_height)/2-self.robot_dimensions[1]/2]

        self.spawn_monsters()
        self.spawn_coin()
        self.coin_counter = 0

    def spawn_monsters(self):
        self.monsters=[]
        for i in range(self.number_of_monsters[self.level-1]):
            x_monster=random.randint(self.safe_zone_width, self.window_width-self.safe_zone_width-self.monster_dimensions[0])
            y_monster=random.randint(self.top_bar_height, self.window_height-self.monster_dimensions[1])
            wanderer=random.randint(1,10)<2
            wanderer_target=(random.randint(self.safe_zone_width + self.robot_dimensions[0]/2, self.window_width-self.safe_zone_width-self.monster_dimensions[0]/2),
             random.randint(self.top_bar_height + self.robot_dimensions[1]/2, self.window_height-self.monster_dimensions[1]/2))
            self.monsters.append([x_monster,y_monster, wanderer, wanderer_target])

    def spawn_coin(self):
        while True:
            # Generates random coordinates for coin until it is more than 500 pixels away from the player
            x_coin=random.randint(self.safe_zone_width, self.window_width-self.safe_zone_width-self.coin_dimensions[0])
            y_coin=random.randint(self.top_bar_height, (self.window_height)-self.coin_dimensions[1])
            if math.sqrt((x_coin-self.robot_coordinates[0])**2+(y_coin-self.robot_coordinates[1])**2)>500:
                break
        self.coin_coordinates=[x_coin,y_coin]

    def spawn_door(self):
        x_door=self.window_width-self.door_dimensions[0]-60
        y_door=(self.window_height+self.top_bar_height)/2-self.door_dimensions[1]/2
        self.door_coordinates = (x_door, y_door)

    def hit_monster(self):
        for monster in self.monsters:
            x_overlap = monster[0] <= self.robot_coordinates[0] <= monster[0] + \
                self.monster_dimensions[0] or self.robot_coordinates[0] <= monster[
                    0] <= self.robot_coordinates[0]+self.robot_dimensions[0]
            y_overlap = monster[1] <= self.robot_coordinates[1] < monster[1] + \
                self.monster_dimensions[1] or self.robot_coordinates[1] <= monster[
                    1] <= self.robot_coordinates[1]+self.robot_dimensions[1]
            if x_overlap and y_overlap:
                return True
        return False

    def hit_coin(self):
        x_overlap = self.coin_coordinates[0] <= self.robot_coordinates[0] <= self.coin_coordinates[0] + \
            self.coin_dimensions[0] or self.robot_coordinates[0] <= self.coin_coordinates[
                0] <= self.robot_coordinates[0]+self.robot_dimensions[0]
        y_overlap = self.coin_coordinates[1] <= self.robot_coordinates[1] < self.coin_coordinates[1] + \
            self.coin_dimensions[1] or self.robot_coordinates[1] <= self.coin_coordinates[
                1] <= self.robot_coordinates[1]+self.robot_dimensions[1]

        if x_overlap and y_overlap:
            # This bool is set to False here because of a small exploit I found
            # If you hit a monster and lose a life, you won't lose any more lifes if you stay in contact with the monster
            # (You can try this by commenting the self.hit_monster_before=False line out)
            # This is because of the way I implemented the monster-player collision
            # As the player still loses at least 1 life when using this method, it's not a viable method to complete the game
            # However, with this bool being set to False, the player now for sure loses a life if in contact with a monster when collecting a coin
            self.hit_monster_before=False
            self.spawn_coin()
            return True
        return False

    def hit_door(self):
        if self.coin_counter==3:
            x_overlap = self.door_coordinates[0] <= self.robot_coordinates[0] <= self.door_coordinates[0] + \
                self.door_dimensions[0] or self.robot_coordinates[0] <= self.door_coordinates[
                    0] <= self.robot_coordinates[0]+self.robot_dimensions[0]
            y_overlap = self.door_coordinates[1] <= self.robot_coordinates[1] < self.door_coordinates[1] + \
                self.door_dimensions[1] or self.robot_coordinates[1] <= self.door_coordinates[
                    1] <= self.robot_coordinates[1]+self.robot_dimensions[1]

            if x_overlap and y_overlap:
                return True

        return False

    def show_hearts(self):
        for i in range(self.lifes):
            # Don't try to understand the math I'm doing here, it's a result of trial and error
            # Two circles, one triangle and one rectangle arranged in the most heart-like shape I could get
            heart_padding = 50
            x_0 = 20
            y_0 = 25
            triangle_top_left = (x_0+heart_padding*i, y_0)
            triangle_top_right = (x_0+32+heart_padding*i, y_0)
            triangle_middle = (x_0+16+heart_padding*i, y_0+16)

            pygame.draw.polygon(
                self.window, (255, 0, 0), (triangle_top_left, triangle_top_right, triangle_middle))
            pygame.draw.rect(self.window, (255, 0, 0),
                             (triangle_top_left[0]+6, triangle_top_left[1]-9, 20, 10))
            pygame.draw.circle(
                self.window, (255, 0, 0), (triangle_top_left[0]+6, triangle_top_left[1]-7), 10)
            pygame.draw.circle(
                self.window, (255, 0, 0), (triangle_top_left[0]+26, triangle_top_left[1]-7), 10)
    
    def show_coins_collected(self):
        coin_text=self.small_font.render(f" x {self.coin_counter}", False, (200, 200, 200))
        group_width=self.coin_dimensions[0]+coin_text.get_width()

        x_coin=self.window_width/2-group_width/2
        y_coin=self.top_bar_height/2-self.coin_dimensions[1]/2
        x_text=x_coin+self.coin_dimensions[0]
        y_text=self.top_bar_height/2-coin_text.get_height()/2

        self.window.blit(self.coin, (x_coin, y_coin))
        self.window.blit(coin_text, (x_text, y_text))
    
    def show_time(self):
        minutes=int(round((time.time()-self.start_time)//60))
        seconds=(int(round(time.time()-self.start_time)%60))
        if minutes==0:
            game_time_str=f"00:{str(seconds).rjust(2, '0')}"
        elif minutes==1:
            game_time_str=f"01:{str(seconds).rjust(2, '0')}"
        else:
            game_time_str=f"{str(minutes).rjust(2, '0')}:{str(seconds).rjust(2, '0')}"
        
        time_text=self.medium_font.render(game_time_str, False, (200,200,200))
        time_text_width, time_text_height = time_text.get_width(), time_text.get_height()

        self.window.blit(time_text, (self.window_width-time_text_width-20,self.top_bar_height/2-time_text_height/2))

    def lose_life(self):
        if not self.hit_monster_before:
            self.lifes -= 1
        if self.lifes <= 0:
            self.player_alive = False

    def move(self):
        if self.robot_coordinates[0] >= self.moving_speed and self.move_left:
            self.robot_coordinates[0] -= self.moving_speed

        if self.robot_coordinates[0] <= self.window_width-self.robot_dimensions[0]-self.moving_speed and self.move_right:
            self.robot_coordinates[0] += self.moving_speed

        if self.robot_coordinates[1] >= self.moving_speed+self.top_bar_height and self.move_up:
            self.robot_coordinates[1] -= self.moving_speed

        if self.robot_coordinates[1] <= self.window_height-self.robot_dimensions[1]-self.moving_speed and self.move_down:
            self.robot_coordinates[1] += self.moving_speed

    def monster_move(self):
        for i in range(len(self.monsters)):
            if self.monsters[i][2]: # If robot is a random wanderer
                x_target_middle=self.monsters[i][3][0]
                y_target_middle=self.monsters[i][3][1]
                self.monsters[i][2] = random.randint(1,1000)>6
            else:
                x_target_middle = self.robot_coordinates[0] + self.robot_dimensions[0]/2
                y_target_middle = self.robot_coordinates[1] + self.robot_dimensions[1]/2
                self.monsters[i][2] = random.randint(1,1000)>990

                new_wanderer_target=(random.randint(self.safe_zone_width + self.robot_dimensions[0]/2, self.window_width-self.safe_zone_width-self.monster_dimensions[0]/2),
                    random.randint(self.top_bar_height + self.robot_dimensions[1]/2, self.window_height-self.monster_dimensions[1]/2))
                self.monsters[i][3]=new_wanderer_target

            x_monster_middle = self.monsters[i][0]+self.monster_dimensions[0]/2
            y_monster_middle = self.monsters[i][1]+self.monster_dimensions[1]/2

            left_border = self.safe_zone_width
            right_border = self.window_width - self.safe_zone_width-self.monster_dimensions[0]

            if self.monsters[i][0] < right_border-self.monster_speed and x_monster_middle < x_target_middle:
                self.monsters[i][0] += self.monster_speed
            elif self.monsters[i][0] > left_border+self.monster_speed and x_monster_middle > x_target_middle:
                self.monsters[i][0] -= self.monster_speed

            if y_monster_middle < y_target_middle:
                self.monsters[i][1] += self.monster_speed
            elif y_monster_middle > y_target_middle:
                self.monsters[i][1] -= self.monster_speed
        

    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key == pygame.K_LEFT:
                    self.move_left = True
                elif event.key == pygame.K_RIGHT:
                    self.move_right = True
                elif event.key == pygame.K_UP:
                    self.move_up = True
                elif event.key == pygame.K_DOWN:
                    self.move_down = True

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.move_left = False
                if event.key == pygame.K_RIGHT:
                    self.move_right = False
                if event.key == pygame.K_UP:
                    self.move_up = False
                if event.key == pygame.K_DOWN:
                    self.move_down = False

    def draw_window(self):
        if self.win:
            self.window.fill((0, 210, 0))

            win_text = self.large_font.render("You win!", False, (20, 20, 20))
            self.window.blit(win_text, (self.window_width/2-win_text.get_width() /
                             2, (self.window_height-self.top_bar_height)/2-win_text.get_height()/2))
        
        elif self.player_alive and not self.win:
            fill_colour=[(50,10,10),(10,10,50),(10,50,10)]
            side_bar_colour=[(180,60,60),(60,60,180),(60,180,60)]
            top_bar_colour=(10,10,10)

            self.window.fill(fill_colour[self.level%3])
            level_text=self.huge_font.render(f"{self.level}", False, side_bar_colour[self.level%3])
            x_level_text=self.window_width/2-level_text.get_width()/2
            y_level_text=300
            self.window.blit(level_text, (x_level_text, y_level_text))
            # Draws top bar
            pygame.draw.rect(self.window, top_bar_colour[self.level%3], (0,0,self.window_width,self.top_bar_height))
            # Draws sidebars
            pygame.draw.rect(self.window, side_bar_colour[self.level%3], (0, self.top_bar_height, self.safe_zone_width, self.window_height-self.top_bar_height))
            pygame.draw.rect(self.window, side_bar_colour[self.level%3], (self.window_width -
                             self.safe_zone_width, self.top_bar_height, self.safe_zone_width, self.window_height-self.top_bar_height))

            self.window.blit(self.robot, (self.robot_coordinates[0], self.robot_coordinates[1]))

            if self.coin_counter!=3:
                self.window.blit(self.coin, (self.coin_coordinates[0], self.coin_coordinates[1]))
            else:
                self.window.blit(self.door, self.door_coordinates)
                # Draws little rectangle to cover "ULOS" text above door
                pygame.draw.rect(self.window, side_bar_colour[self.level%3], (self.door_coordinates[0], self.door_coordinates[1], self.door_dimensions[0], 12))

            for monster in self.monsters:
                self.window.blit(self.monster, (monster[0], monster[1]))


            self.show_hearts()
            self.show_coins_collected()
            self.show_time()

        else:
            self.window.fill((210, 0, 0))

            death_text = self.large_font.render("You died!", False, (20, 20, 20))
            self.window.blit(death_text, (self.window_width/2-death_text.get_width()/2, (self.window_height-self.top_bar_height)/2-death_text.get_height()/2))


        pygame.display.flip()
        self.clock.tick(60)


InsertName()
