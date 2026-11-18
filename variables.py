import pygame
import os
import random
pygame.font.init()

# general variables
debug = True
player_collision = 1
wall_collision = 2
bush_collision = 3
SCREENWIDTH, SCREENHEIGHT = 800, 600
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
screenmult = SCREENWIDTH / 800
state = "OVERWORLD"
FPS = 60
movespeed = 0.01
player_diameter = 60

# fonts
bigfont = pygame.font.SysFont("Arial", 48)
smolfont = pygame.font.SysFont("Arial", 20)

# mon images
hisuian_zoroark = pygame.image.load("zoroark-hisuian.png").convert_alpha()
rattata = pygame.image.load("rattata.png").convert_alpha()
chienpao = pygame.image.load("Chienpao.png").convert_alpha()

# general images
start_screen = pygame.image.load("start.png").convert()
start_screen = pygame.transform.scale(start_screen, (SCREENWIDTH, SCREENHEIGHT))
bush_image = pygame.image.load("bush.png").convert_alpha()
battlebackground_image = pygame.image.load("battlebackground.png").convert()
background_image = pygame.image.load("background.png").convert()
monbackground_image = pygame.image.load("battlebackground.png").convert()
player_image = pygame.image.load("Player.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (player_diameter, player_diameter))
battleui_image = pygame.image.load("ui.png").convert_alpha()
battleui_image = pygame.transform.scale(battleui_image, (220 * screenmult, 600 * screenmult))
button_image = pygame.image.load("button.png").convert_alpha()
button_image = pygame.transform.scale(button_image, (25 * screenmult, 50 * screenmult))

class bush:
	def __init__(self, x, y, width, height, pool):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.pool = pool
bushzones = [
	bush(100, 100, 100, 100, "route_1")
]
spawnzones = {
	"route_1": [["Rattata"], 1, 5]
}

class creature: # general species
	def __init__(self, type, MHP, Atk, Def, SpA, SpD, Speed, frontsprite=None): # will add learnset, XP requirement, ability, etc. later
		self.type = type
		self.mhp = MHP
		self.Atk = Atk
		self.Def = Def
		self.SpA = SpA
		self.SpD = SpD
		self.Speed = Speed
		self.front = frontsprite

class move: # general move // WILL ADD ANIMATION
	def __init__(self, type, BP, accuracy, targeting, category, secondaryeffects=None, priority=0):
		self.type = type
		self.bp = BP
		self.accuracy = accuracy
		self.targeting = targeting # one, all, both
		self.category = category
		self.priority = priority
		self.effects = secondaryeffects

species = { # will add more, currently just placeholders
	"Rattata": creature(["Normal"], 30, 56, 35, 25, 35, 72, rattata),
	"Hisuian Zoroark": creature(["Normal", "Ghost"], 55, 100, 60, 125, 60, 110, hisuian_zoroark),
	"Chienpao": creature(["Ice", "Dark"], 80, 120, 80, 90, 65, 135, chienpao)
}

moves = {
	"Tackle": move(["Normal"], 60, 100, "one", "Physical"),
	"Earthquake": move(["Ground"], 100, 100, "all", "Physical"),
	"Uturn": move(["Bug"],40,100,"one","PhysSwitch"),
	"Swordsdance": move(["Fighting"],0,"--","self","Status", [["Attack",2]])
}

class mon: # specific instance of creature
	def __init__(self, species, name, level, current_type, stat_mods, CHP, moves): # will add EV, IV, condition, item, etc. later
		self.species = species
		self.name = name
		self.level = level
		self.current_type = current_type
		self.stat_mods = stat_mods
		self.chp = CHP
		self.moves = moves
	def to_dict(self):
		return {"species": self.species, "name": self.name, "level": self.level, "CHP": self.chp, "ID": self.ID}
	def from_dict(cls, data):
		return cls(data["species"], data["name"], data["level"], species[data["species"]].type, [0,0,0,0,0], data["CHP"], data["ID"])

typechart = [ # currently set for pokemon, will change
        #non  nor  fir  wat  grs  rck  fly  ice  elc  fig  psn  grn  psy  bug  gst  dgn  drk  stl  fai
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], #typeless
        [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.5, 1.0], #normal
        [1.0, 1.0, 0.5, 0.5, 2.0, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0, 2.0, 1.0], #fire
        [1.0, 1.0, 2.0, 0.5, 0.5, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0], #water
        [1.0, 1.0, 0.5, 2.0, 0.5, 2.0, 0.5, 1.0, 1.0, 1.0, 0.5, 2.0, 1.0, 0.5, 1.0, 0.5, 1.0, 0.5, 1.0], #grass
        [1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 0.5, 1.0, 0.5, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 1.0], #rock
        [1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 0.5, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 0.5, 1.0], #flying
        [1.0, 1.0, 0.5, 0.5, 2.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 1.0], #ice
        [1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0], #electric
        [1.0, 2.0, 1.0, 1.0, 1.0, 2.0, 0.5, 2.0, 1.0, 1.0, 0.5, 1.0, 0.5, 0.5, 0.0, 1.0, 2.0, 2.0, 0.5], #fighting
        [1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 1.0, 1.0, 0.0, 2.0], #poison
        [1.0, 1.0, 2.0, 1.0, 0.5, 2.0, 0.0, 1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 2.0, 1.0], #ground
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 0.5, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0], #psychic
        [1.0, 1.0, 0.5, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0, 0.5, 0.5, 1.0, 2.0, 1.0, 0.5, 1.0, 2.0, 0.5, 0.5], #bug
        [1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 0.5, 1.0, 1.0], #ghost
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.5, 0.0], #dragon
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 0.5, 1.0, 0.5], #dark
        [1.0, 1.0, 0.5, 0.5, 1.0, 2.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 2.0], #steel
        [1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 0.5, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 0.5, 1.0] #fairy
]

class btn:
	def __init__(self,x,y,width,height,text,color=(0,0,0),image_path=None):
		self.rect = pygame.Rect(x,y,width,height)
		self.text = text
		self.image_path = image_path
		self.color = color
		if image_path != None:
			self.image = pygame.image.load(image_path).convert_alpha()
			self.image = pygame.transform.scale(self.image,(width,height))
		else:
			self.text_surface = smolfont.render(self.text, True, (255,255,255))
			self.text_rect = self.text_surface.get_rect(center=self.rect.center)
	def draw(self,surface):
		if self.image_path != None:
			surface.blit(self.image, self.rect)
		else:
			pygame.draw.rect(surface,self.color, self.rect)
			pygame.draw.rect(surface, (255,255,255), self.rect, 2)
			surface.blit(self.text_surface,self.text_rect)
	def is_clicked(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)

buttons = {
	"battle_attack": btn(20,400,75,75,"Attack"),
	"battle_bag": btn(125,400,75,75,"Bag"),
	"battle_mons": btn(20,505,75,75,"Mons"),
	"battle_run": btn(125,505,75,75,"Coward")
}

def save_game():
	global current_game_state
	json_data = {
		"player_name": current_game_state["player_name"],
		"position": current_game_state["position"],
		"mons": [item.to_dict() for item in current_game_state["mons"]],
		"PC": [item.to_dict() for item in current_game_state["PC"]],
		"items": current_game_state["items"]
	}
	try:
		with open("save1.json", "w") as file:
			json.dump(json_data, file, indent=4)
		print("Game saved successfully")
	except IOError:
		print("Error: could not write save file.")

def load_game(save):
	if not os.path.exists("save1.json"):
		print("No save file found. Starting a fresh game")
	try:
		with open("save1.json", "r") as file:
			data = json.load(file)
			print("game loaded successfully")
			return data
	except (IOError, json.JSONDecodeError):
		print("Error: Save file is corrupted or couldn't be read")
		return None

def safenumber():
	return random.randint(960, 3840)

def chart(a, d): # a, d are lists of the opposing types
	A = find(a)
	D = find(d)
	mult = 1
	for i in A:
		for j in D:
			match zip(i, j): # will be used later for special interactions
				case _:
					mult *= typechart[i][j]
	return mult

def find(f):
	m = []
	for i in f:
		match i:
			case "None":
				m.append(0)
			case "Normal":
				m.append(1)
			case "Fire":
				m.append(2)
			case "Water":
				m.append(3)
			case "Grass":
				m.append(4)
			case "Rock":
				m.append(5)
			case "Flying":
				m.append(6)
			case "Ice":
				m.append(7)
			case "Electric":
				m.append(8)
			case "Fighting":
				m.append(9)
			case "Poison":
				m.append(10)
			case "Ground":
				m.append(11)
			case "Psychic":
				m.append(12)
			case "Bug":
				m.append(13)
			case "Ghost":
				m.append(14)
			case "Dragon":
				m.append(15)
			case "Dark":
				m.append(16)
			case "Steel":
				m.append(17)
			case "Fairy":
				m.append(18)
	return m
