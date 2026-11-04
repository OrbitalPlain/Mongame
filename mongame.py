import pygame
import pymunk
import pymunk.pygame_util
import math
import sys
import random
import os

debug = True

SCREENWIDTH, SCREENHEIGHT = 800, 600
screenmult = SCREENWIDTH / 800
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
if debug:
	draw_options = pymunk.pygame_util.DrawOptions(screen)

# determines the collision types
player_collision = 1
wall_collision = 2
bush_collision = 3

current_game_state = {
	"player_name": "",
	"position": {"x": 0, "y": 0},
	"mons": [],
	"PC": [],
	"items": {"ball": 100}
}

space = pymunk.Space()
player_body = pymunk.Body(mass=1, moment=float("inf"))
player_body.position = (SCREENWIDTH // 2, SCREENHEIGHT // 2)
player_shape = pymunk.Circle(player_body, radius=30*screenmult)
space.gravity = (0, 0)
player_shape.elasticity, player_shape.friction, player_shape.collision_type = 0.0, 0.7, player_collision
space.add(player_body, player_shape)

pygame.init()
state = "OVERWORLD"
usedIDs = [0]
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24) # might make own font eventually

hisuian_zoroark = pygame.image.load("zoroark-hisuian.png").convert_alpha()
rattata = pygame.image.load("rattata.png").convert_alpha()

start_screen = pygame.image.load("start.png").convert()
start_screen = pygame.transform.scale(start_screen, (SCREENWIDTH, SCREENHEIGHT))
bush_image = pygame.image.load("bush.png").convert_alpha()
battlebackground_image = pygame.image.load("battlebackground.png").convert()
background_image = pygame.image.load("background.png").convert()
player_image = pygame.image.load("Player.png").convert_alpha()
player_diameter = int(player_shape.radius * 2)
player_image = pygame.transform.scale(player_image, (player_diameter, player_diameter))
battleui_image = pygame.image.load("ui.png").convert_alpha()
battleui_image = pygame.transform.scale(battleui_image, 600 * screenmult, 200 * screenmult)
button_image = pygame.image.load("button.png").convert_alpha()
button_image = pygame.transform.scale(button_image, 25 * screenmult, 50 * screenmult)

class creature: # general species
	def __init__(self, type, MHP, Atk, Def, SpA, SpD, Speed, frontsprite): # will add learnset, XP requirement, spawn position, ability, etc. later
		self.type = type
		self.mhp = MHP
		self.Atk = Atk
		self.Def = Def
		self.SpA = SpA
		self.SpD = SpD
		self.Speed = Speed
		self.front = frontsprite

class move: # general move // WILL ADD ANIMATION
	def __init__(self, type, BP, accuracy, targeting, category, priority=0):
		self.type = type
		self.bp = BP
		self.accuracy = accuracy
		self.targeting = targeting
		self.category = category
		self.priority = priority

species = { # will add more, currently just placeholders
	"Rattata": creature(["Normal"], 30, 56, 35, 25, 35, 72, rattata),
	"Hisuian Zoroark": creature(["Normal", "Ghost"], 55, 100, 60, 125, 60, 110, hisuian_zoroark)
}

moves = {
	"Tackle": move(["Normal"], 60, 100, "one", "Physical"),
	"Earthquake": move(["Ground"], 100, 100, "all", "Physical")
}

class mon: # specific instance of creature
	def __init__(self, species, name, level, current_type, stat_mods, CHP, moves): # will add EV, IV, condition, item, moves, etc. later
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


if debug: # makes sure the player has a mon before starter selection is complete
	current_game_state["mons"][0] = mon("Hissuian Zoroark", "Boo", 10, ["Normal", "Ghost"], [0,0,0,0,0], 55, ["Tackle", "Earthquake", "", ""])

walls = [ # numbers are (starting coord), (ending coord), thickness
	pymunk.Segment(space.static_body, (100, 100), (700, 100), 20 * screenmult)
]

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

class btn:
	def __init__(self,x,y,width,height,text,image_path=None):
		self.rect = pygame.Rect(x,y,width,height)
		self.text = text
		self.image_path = image_path
		if image_path != None:
			self.image = pygame.image.load(image_path).convert_alpha()
			self.image = pygame.transform.scale(self.image,(width,height))
		else:
			self.text_surface = font.render(self.text, True, (255,255,255))
			self.text_rect = self.text_surface.get_rect(center=self.rect.center)
	def draw(self,surface):
		if self.image_path != None:
			surface.blit(self.image, self.rect)
		else:
			pygame.draw.rect(surface,(0,0,0), self.rect)
			pygame.draw.rect(surface, (255,255,255), self.rect, 2)
			surface.blit(self.text_surface,self.text_rect)
	def is_clicked(self, mouse_pos):
		return self.rect.collidepoint(mouse_pos)


buttons = {
	"battle_attack": btn(10,400,75,75,"Attack"),
	"battle_bag": btn(115,400,75,75,"Bag"),
	"battle_mons": btn(10,505,75,75,"Mons"),
	"battle_run": btn(115,505,75,75,"Coward")
}

for wall in walls:
	wall.elasticity = 0.0
	wall.friction = 0.5
	wall.collision_type = wall_collision
	space.add(wall)

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

def on_player_enter_zone(arbiter, space, data):
	player_shape, hit_shape = arbiter.shapes
	zone_object = hit_shape.data
	return True
space.on_collision(player_collision, bush_collision, begin=on_player_enter_zone)

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
			case "Typeless":
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

def damagecalc(m, a, d, t): # move, attacker info, defender info, target count
	effect = chart(a.type, d.type)
	STAB = 1.0
	move = moves[m]
	t = 1.0
	if t > 1:
		T = 0.75
	if move.type in a.type:
		STAB = 1.5
	match move.category:
		case "Physical":
			Dmg = (math.floor((math.floor(2 * a.level / 5) * move.BP * a.Atk / a.Def) / 50) + 2) * STAB * effect * T
		case "Special":
			Dmg = (math.floor((math.floor(2 * a.level / 5) * move.BP * a.SpA / a.SpD) / 50) + 2) * STAB * effect * T
	return math.floor(Dmg)

def battle(enemy, type):
	global current_game_state, buttons
	enemyside = []
	playerside = []
	if type == "doubles":
		enemyside.append(enemy[1])
		for i in current_game_state["mons"]:
			if i.CHP > 0:
				playerside.append(i)
				break
	enemyside.append(enemy[0])
	for i in current_game_state["mons"]:
		if i.CHP > 0:
			if i not in playerside:
				playerside.append(i)
	while True:
		screen.blit(battlebackground_image, (0,0))
		if type == "doubles": # adds pokemon to area as needed
			screen.blit(pygame.transform.scale(species[enemyside[0].species].front,(170,170)),(400,50))
			screen.blit(pygame.transform.scale(species[enemyside[1].species].front,(170,170)),(520,100))
			screen.blit(pygame.transform.scale(species[playerside[0].species].front,(225,225)),(210,350))
			screen.blit(pygame.transform.scale(species[playerside[1].species].front,(225,225)),(330,400))
		else:
			screen.blit(species[playerside[0].species].front,(100,300))
			screen.blit(species[enemyside[0].species].front,(500,50))
		btnstate = "MAIN"
		mon = 0
		moves = [["",[0], 0, 0]] * len(playerside) # the keyword (switch, use, etc), target (enemy slot 1, enemy slot 2, both), move slot (if use), priority
		while True: # ^^ before turn, VV after turn, this is during turn select
			if mon == 2:
				break
			if btnstate not in ["BAG", "MONS"]:
				screen.blit(battleui_image,(0,0))
			match btnstate:
				case "MAIN":
					trect = pygame.Rect(10,10,180,350)
					tsurface = font.render(f"What will {playerside[mon].name} do?", True, (0,0,0))
					screen.blit(tsurface,trect)
					for b in ["battle_attack","battle_bag","battle_mons","battle_run"]:
						buttons[b].draw(screen)
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if buttons["battle_attack"].is_clicked(event.pos):
									btnstate = "ATTACK"
									break
								elif buttons["battle_bag"].is_clicked(event.pos):
									btnstate = "BAG"
									break
								elif buttons["battle_mons"].is_clicked(event.pos):
									btnstate = "MONS"
									break
								elif buttons["battle_run"].is_clicked(event.pos): # will make it more difficult to run from more difficult opponents later
									return "OVERWORLD"
				case "ATTACK":
					abtns = [
						btn(10, 10, 180, 120, playerside[mon].moves[0]),
						btn(10, 140, 180, 120, playerside[mon].moves[1]),
						btn(10, 270, 180, 120, playerside[mon].moves[2]),
						btn(10, 400, 180, 120, playerside[mon].moves[3]),
						btn(10, 540, 180, 60, "exit")
					]
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if abtns[0].is_clicked(event.pos):
									moves[mon] = ["use",[],1,playerside[mon].moves[0].priority]
									mon += 1
									break
								if abtns[1].is_clicked(event.pos):
									mon += 1
									break
								if abtns[2].is_clicked(event.pos):
									mon += 1
		any = False
		if len(enemyside) > 0:
			for mon in enemyside:
				if mon.CHP > 0:
					any = True
					break
		if any == False:
			return "OVERWORLD"
		any = False
		for mon in playerside:
			if mon.CHP > 0:
				any = True
				break
		if any == False:
			return "OVERWORLD"

def main():
	global state, current_game_state, usedIDs
	running = True
	encounter = []
	safe = safenumber()
	while running:
		if len(current_game_state["mons"]) != 6:
			current_game_state["mons"].append([""] * (6 - len(current_game_state["mons"])))
		screen.blit(background_image, (0,0))
		keys = pygame.key.get_pressed()
		events = pygame.event.get()
		for event in events: # single time things
			if event.type == pygame.QUIT:
				running = False
		if state == "OVERWORLD":
			player_screen_x, player_screen_y = SCREENWIDTH // 2, SCREENHEIGHT // 2
			player_rect = player_image.get_rect(center=(player_screen_x, player_screen_y))
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
				playerspeed = 250 * screenmult
			else:
				playerspeed = 150 * screenmult
			vx, vy = 0, 0
			if (keys[pygame.K_LEFT] != keys[pygame.K_RIGHT]) and (keys[pygame.K_UP] != keys[pygame.K_DOWN]):
				playerspeed /= math.sqrt(2)
			if keys[pygame.K_LEFT]:
				vx += -playerspeed
			if keys[pygame.K_RIGHT]:
				vx += playerspeed
			if keys[pygame.K_UP]:
				vy += -playerspeed
			if keys[pygame.K_DOWN]:
				vy += playerspeed
			player_body.velocity = (vx, vy)
			distance_moved = player_body.velocity.length
			camera_x, camera_y = (SCREENWIDTH // 2) - player_body.position.x, (SCREENHEIGHT // 2) - player_body.position.y
			collision_rects = []
			for bush in bushzones:
				bush_rect = pygame.Rect(bush.x + camera_x, bush.y + camera_y, bush.width, bush.height)
				collision_rects.append(bush_rect)
				screen.blit(bush_image, bush_rect)
			hit_index = player_rect.collidelist(collision_rects)
			if hit_index != -1 and distance_moved > 0:
				safe -= distance_moved
				if safe <= 0:
					current_bush = bushzones[hit_index]
					version = "singles"
					if random.random() < 0.750: # These movesets have not been defined
						enemy = random.choice(spawnzones[current_bush.pool][0])
						encounter.append(mon(species[enemy], enemy, random.randint(current_bush.pool[1], current_bush.pool[2]), species[enemy].type, [0,0,0,0,0], species[enemy].mhp, ["Tackle", "", "", ""]))
						version = "doubles"
					enemy = random.choice(spawnzones[current_bush.pool][0])
					encounter.append(mon(species[enemy], enemy, random.randint(current_bush.pool[1], current_bush.pool[2]), species[enemy].type, [0,0,0,0,0], species[enemy].mhp, ["Tackle", "", "", ""]))
					state = "BATTLE"
					safe = safenumber()
			space.step(1 / FPS)
			screen.blit(player_image, player_rect)
			if debug: # shows debug stuff
				for w in walls: # shows wall hitboxes
					p1 = wall.a
					p2 = wall.b
					screen_p1 = (p1.x + camera_x, p1.y + camera_y)
					screen_p2 = (p2.x + camera_x, p2.y + camera_y)
					pygame.draw.line(screen, (200, 0, 0), screen_p1, screen_p2, int(wall.radius * 2))
				draw_options.transform = pymunk.Transform.translation(camera_x, camera_y)
				space.debug_draw(draw_options) # shows player hitbox
		if state == "BATTLE":
			state = battle(encounter, version)
		if state == "START":
			screen.blit(start_screen, (0,0))
		pygame.display.flip()
		clock.tick(60)
	return
main()
pygame.quit()
sys.exit()
