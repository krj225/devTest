# Maddie Judd, 7/2/24
# mixing demos from pygame.org and a lovely tutorial from nerdparadise.com
# this is a simple game loop that uses a scene manager to switch between them
# separates out the game loop from the scenes, and allows for easy scene switching
# what's implemented as the 'game' is just an interactive circle moving around a static screen
import pygame
# boilerplate scene code
class SceneBase:
    def __init__(self):
        self.next = self
        self.dt = 0
        self.player_pos = pygame.Vector2(640, 360) #hardcoded for now, i dont wanna pass screen everywhere atm
    
    def ProcessInput(self, events):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene


# runGame is a big function that handles the top level game loop
# filters events for any exit commands, sends events to the active scene, updates the active scene, and renders the active scene
# it also handles switching between scenes if necessary by reading the next attribute (changed by SwitchToScene)
# width/height control the screen size, fps for framerate, and start_scene is the first scene to run on boot
def runGame(width, height, fps, start_scene):
    pygame.init() # initializes pygame
    screen = pygame.display.set_mode((width, height)) # creates a window of width*height pixels
    clock = pygame.time.Clock() # used to limit the frame rate
    dt = 0 # delta time, time since last frame
    active_scene = start_scene

    while active_scene != None: #while we have a scene to go to--our end state is setting this to None
        keys = pygame.key.get_pressed() #each frame, check to see what keys are being pressed

        # here's where Event Filtering goes! (order of operations)
        filtered_events = []
        for event in pygame.event.get(): # what's happening? event checks things like mouse, keyboard, etc. 
            quit = False
            if event.type == pygame.QUIT: # X out the window
                quit = True
            elif event.type == pygame.KEYDOWN: # key pressed
                alt_pressed = keys[pygame.K_LALT] or keys[pygame.K_RALT] # left or right alt key (for alt-f4)
                if keys[pygame.K_ESCAPE]: # escape key
                    quit = True
                elif keys[pygame.K_F4] and alt_pressed: # alt-f4
                    quit = True
            if quit:
                active_scene.Terminate() # clean up the scene
            else:
                filtered_events.append(event) # send the event to the scene

        # general game loop consists of handling input, updating the game, and rendering the frame
        active_scene.ProcessInput(filtered_events, keys, screen, dt) # send filtered events and keys to the scene
        active_scene.Update() # logic
        active_scene.Render(screen) # draw

        active_scene = active_scene.next # switch to the next scene
        
        pygame.display.flip() # flip() the display to put your work on screen and begin work on next frame
        dt = clock.tick(60) / 1000 # limits FPS to set value, handy to have this as a variable so it can be altered
        # for debugging, show framerate in title
        pygame.display.set_caption(f"FPS: {clock.get_fps()}") # some handy formatting to combine the string with the clock output
# end of runGame function

# now we can define scenes!!

# on boot scene, will show some basic text for now. eventually, we can use pygui to spice it up
class TitleScene(SceneBase):
    def init(self):
        self.next = self
    
    def ProcessInput(self, events, pressed_keys, screen, dt):
        if pressed_keys[pygame.K_SPACE]:
            self.SwitchToScene(GameScene())
    
    def Update(self):
        pass # no updates needed, this scene either waits for input, switches, or exits.

    def Render(self, screen):
        screen.fill((255, 255, 255)) # fill the screen with white
        font = pygame.font.Font(None, 74) # set the font
        text = font.render("Welcome to Pygame!", True, (0, 0, 0)) # render the text
        text_rect = text.get_rect() # get the rectangle of the text
        text_x = screen.get_width() / 2 - text_rect.width / 2 # center the text
        text_y = screen.get_height() / 2 - text_rect.height / 2 
        screen.blit(text, [text_x, text_y]) # draw the text

        # do it again for the subtext
        font = pygame.font.Font(None, 24)
        text = font.render("Press Space to continue", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_x = screen.get_width() / 2 - text_rect.width / 2
        text_y = screen.get_height() / 2 - text_rect.height / 2 + 100 # offset the subtext
        screen.blit(text, [text_x, text_y])

    def Terminate(self):
        self.SwitchToScene(None) # switch to None to end the game
        
#gonna port the first test into a scene, so we have a little interactive demo
class GameScene(SceneBase):
    def init(self):
        SceneBase.init(self) # call the parent class's init (just set next to self!)
        # create variables for player position and dt
        self.player_pos = pygame.Vector2(640, 360) #hardcoded for now, i dont wanna pass screen everywhere atm
    
    def ProcessInput(self, events, pressed_keys, screen, dt):
        # don't worry about filtering, that's in the main loop
        # need to pass in screen to get bounds of the window--we'll find a better way to do this with time
        # here, we just want to check if the arrow/wasd keys are pressed
        # if they are, we'll move the player: all ifs so diagonal movement works
        if pressed_keys[pygame.K_w] or pressed_keys[pygame.K_UP]:
            #print("up" )
            self.player_pos.y -= 300 * dt
        if pressed_keys[pygame.K_s] or pressed_keys[pygame.K_DOWN]:
            #print("down")
            self.player_pos.y += 300 * dt
        if pressed_keys[pygame.K_a] or pressed_keys[pygame.K_LEFT]:
            #print("left")
            self.player_pos.x -= 300 * dt
        if pressed_keys[pygame.K_d] or pressed_keys[pygame.K_RIGHT]:
            #print("right")
            self.player_pos.x += 300 * dt
        
        # finally, lets bound the player to the screen--keep in mind the circle has a radius of 40
        self.player_pos.x = max(40, min(self.player_pos.x, screen.get_width() - 40))
        self.player_pos.y = max(40, min(self.player_pos.y, screen.get_height() - 40))

    def Update(self):
        pass

    def Render(self, screen):
        screen.fill((0, 0, 255)) # fill the screen with blue
        pygame.draw.circle(screen, (128, 0, 128), self.player_pos, 40) # draw a purple circle at the player's position
        

    def Terminate(self):
        self.SwitchToScene(None) # switch to None to end the game

# at the end, call runGame with wanted params
runGame(1280, 720, 60, TitleScene()) # 1280x720, 60fps, start with TitleScene