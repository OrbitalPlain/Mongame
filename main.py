import pygame
pygame.init()
import pymunk
import pymunk.pygame_util
import math
import sys
import random
import os
from variables import *
if debug:
	draw_options = pymunk.pygame_util.DrawOptions(screen)

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

clock = pygame.time.Clock()

if debug: # makes sure the player has a mon before starter selection is complete
	current_game_state["mons"].append(mon("Hisuian Zoroark", "Boo", 10, ["Normal", "Ghost"], [0,0,0,0,0], 55, ["Tackle", "Earthquake", "", ""]))
	current_game_state["mons"].append(mon("Chienpao","Wiggles",10,["Ice", "Dark"],[0,0,0,0,0],80,["Earthquake", "Uturn", "Swordsdance", ""]))

walls = [ # numbers are (starting coord), (ending coord), thickness
	pymunk.Segment(space.static_body, (100, 100), (700, 100), 20 * screenmult)
]

for wall in walls:
	wall.elasticity = 0.0
	wall.friction = 0.5
	wall.collision_type = wall_collision
	space.add(wall)

def on_player_enter_zone(arbiter, space, data):
	player_shape, hit_shape = arbiter.shapes
	zone_object = hit_shape.data
	return True
space.on_collision(player_collision, bush_collision, begin=on_player_enter_zone)


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
			if i.chp > 0:
				playerside.append(i)
				break
	enemyside.append(enemy[0])
	for i in current_game_state["mons"]:
		if i.chp > 0:
			if i not in playerside:
				playerside.append(i)
		btnstate = "MAIN"
		monnumber = 0
		if type == "doubles":
			lim = 2
		else:
			lim = 1
	usedmoves = [["","", 0, 0]] * len(playerside) # the keyword (switch, use, etc), target (enemy slot 1, enemy slot 2, both, all), move (if use) or mon (if switch), user
	movenum = 0
	movenumber = math.floor(movenum)
	while True:
		screen.blit(battlebackground_image, (0,0))
		if type == "doubles": # adds pokemon to area as needed
			screen.blit(pygame.transform.scale(enemyside[0].species.front,(170,170)),(400,50))
			screen.blit(pygame.transform.scale(enemyside[1].species.front,(170,170)),(520,100))
			screen.blit(pygame.transform.scale(species[playerside[0].species].front,(225,225)),(210,350))
			screen.blit(pygame.transform.scale(species[playerside[1].species].front,(225,225)),(330,400))
		else:
			screen.blit(species[playerside[0].species].front,(100,300))
			screen.blit(enemyside[0].species.front,(500,50))
		if btnstate not in ["BAG", "MONS"]:
			screen.blit(battleui_image,(0,0))
		if monnumber < lim:
			match btnstate:
				case "MAIN":
					trect = pygame.Rect(10,10,180,350)
					tsurface = bigfont.render(f"What will {playerside[monnumber].name} do?", True, (0,0,0), None, 220)
					screen.blit(tsurface,trect)
					for b in ["battle_attack","battle_bag","battle_mons","battle_run"]:
						buttons[b].draw(screen)
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if buttons["battle_attack"].is_clicked(event.pos):
									btnstate = "ATTACK"
								#elif buttons["battle_bag"].is_clicked(event.pos):
									#btnstate = "BAG"
								elif buttons["battle_mons"].is_clicked(event.pos):
									btnstate = "MONS"
								#elif buttons["battle_run"].is_clicked(event.pos): # will make it more difficult to run from more difficult opponents later
									#return "OVERWORLD"
				case "ATTACK":
					move = ""
					abtns = [
						btn(20, 10, 180, 120, playerside[monnumber].moves[0]),
						btn(20, 140, 180, 120, playerside[monnumber].moves[1]),
						btn(20, 270, 180, 120, playerside[monnumber].moves[2]),
						btn(20, 400, 180, 120, playerside[monnumber].moves[3]),
						btn(20, 540, 180, 60, "exit")
					]
					for b in abtns:
						b.draw(screen)
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if abtns[0].is_clicked(event.pos):
									if playerside[monnumber].moves[0] != "":
										move = playerside[monnumber].moves[0]
								if abtns[1].is_clicked(event.pos):
									if playerside[monnumber].moves[1] != "":
										move = playerside[monnumber].moves[1]
								if abtns[2].is_clicked(event.pos):
									if playerside[monnumber].moves[2] != "":
										move = playerside[monnumber].moves[2]
								if abtns[3].is_clicked(event.pos):
									if playerside[monnumber].moves[3] != "":
										move = playerside[monnumber].moves[3]
								if abtns[4].is_clicked(event.pos):
									btnstate = "MAIN"
					if btnstate != "MAIN" and move != "":
						if moves[playerside[monnumber].moves[move]].targeting == "all":
							usedmoves[monnumber] = ["use","all",move,playerside[monnumber]]
							monnumber += 1
							btnstate = "MAIN"
						elif moves[playerside[monnumber].moves[move]].targeting == "both":
							usedmoves[monnumber] = ["use","both",move,playerside[monnumber]]
							monnumber += 1
							btnstate = "MAIN"
						elif type == "doubles":
							btnstate = "TARGET"
						else:
							usedmoves[monnumber] = ["use","both",move,playerside[monnumber]]
							monnumber += 1
							btnstate = "MAIN"
				case "TARGET":
					tarbtns = [
						btn(20,200,85,60,"enemy 1"),
						btn(115,200,85,60,"enemy 2"),
						btn(60,270,100,60, "ally"),
						btn(20,350,180,60,"back")
					]
					trect = pygame.Rect(10,10,180,180)
					tsurface = bigfont.render("Which mon is being targeted?", True, (0,0,0))
					screen.blit(tsurface,trect)
					for b in tarbtns:
						b.draw(screen)
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if tarbtns[3].is_clicked(event.pos):
									btnstate = "ATTACK"
								if tarbtns[0].is_clicked(event.pos):
									usedmoves[monnumber] = ["use","enemy 1",move,playerside[monnumber]]
								if tarbtns[1].is_clicked(event.pos):
									usedmoves[monnumber] = ["use","enemy 2",move,playerside[monnumber]]
								if tarbtns[2].is_clicked(event.pos):
									usedmoves[monnumber] = ["use","ally",move,playerside[monnumber]]
					if btnstate == "TARGET":
						monnumber += 1
						btnstate = "MAIN"
				case "MONS":
					monbtns = []
					for i in range(len(current_game_state["mons"])):
						if current_game_state["mons"][i] in playerside:
							monbtns.append(btn(50 + 350 * (i % 2), 50 + 180 * ((i + 1) % 2), 300, 150, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species, (0,141,191)))
						elif current_game_state["mons"][i].chp <= 0:
							monbtns.append(btn(50 + 350 * (i % 2), 50 + 180 * ((i + 1) % 2), 300, 150, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species, (255,0,0)))
						else:
							monbtns.append(btn(50 + 350 * (i % 2), 50 + 180 * ((i + 1) % 2), 300, 150, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species))
					for i in range(6 - len(monbtns)):
						monbtns.append(btn(50 + 350 * (i % 2), 50 + 100 * ((i + len(monbtns) + 1) % 2),300,150,""))
					for b in monbtns:
						b.draw(screen)
					for event in pygame.event.get():
						if event.type == pygame.MOUSEBUTTONDOWN:
							if event.button == 1:
								if monbtns[0].is_clicked(event.pos) and len(current_game_state["mons"]) > 0:
									if monbtns[0] not in playerside and current_game_state["mons"][0].chp > 0:
										playerside[monnumber] == current_game_state["mons"][0]
								elif monbtns[1].is_clicked(event.pos) and len(current_game_state["mons"]) > 1:
										if monbtns[1] not in playerside and current_game_state["mons"][1].chp > 0:
											playerside[monnumber] == current_game_state["mons"][1]
								elif monbtns[2].is_clicked(event.pos) and len(current_game_state["mons"]) > 2:
									if monbtns[2] not in playerside and current_game_state["mons"][2].chp > 0:
										playerside[monnumber] == current_game_state["mons"][2]
								elif monbtns[3].is_clicked(event.pos) and len(current_game_state["mons"]) > 3:
									if monbtns[3] not in playerside and current_game_state["mons"][3].chp > 0:
										playerside[monnumber] == current_game_state["mons"][3]
								elif monbtns[4].is_clicked(event.pos) and len(current_game_state["mons"]) > 4:
									if monbtns[4] not in playerside and current_game_state["mons"][4].chp > 0:
										playerside[monnumber] == current_game_state["mons"][4]
								elif monbtns[5].is_clicked(event.pos) and len(current_game_state["mons"]) > 5:
									if monbtns[5] not in playerside and current_game_state["mons"][5].chp > 0:
										playerside[monnumber] == current_game_state["mons"][5]
			movenumber += 0.01
		else:
			ecount = 0
			enemymoves = [["","",-1,0]] * len(enemyside) # the keyword (switch, use, etc), target (enemy slot 1, enemy slot 2, both, all), move (if use) or mon (if switch), user
			for e in enemyside:
				m = random.choice(e.moves)
				if type == "doubles" and moves[m].targeting == "one":
					if random.randint(1,2) == 1:
						t = "enemy 1"
					else:
						t = "enemy 2"
				else:
					if moves[m].targeting != "one":
						t = moves[m].targeting
					else:
						t = "both"
				enemymoves[ecount] = ["use",t,m,e]
			# will code enemy AI later
			movelist = []
			for m in enemymoves + usedmoves:
				if len(movelist) == 0:
					movelist.append(m)
				else:
					if m[0] == "switch":
						movelist.insert(0,m)
					for i in range(len(movelist)):
						if m[2].priority > movelist[i][2].priority:
							movelist.insert(i,m)
						elif m[2].priority == movelist[i][2].proiority:
							if m[3].speed > movelist[i][3].speed:
								movelist.insert(i,m)
							elif m[3].speed == movelist[i][3].speed:
								if random.randint(1,2) == 1:
									movelist.insert(i,m)
								else:
									movelist.insert(i + 1,m)
						else:
							if m[3].speed < movelist[i][3].speed:
								if i == len(movelist) - 1:
									movelist.append(m)
			mv = movelist[movenumber]
			movewait = False
			if not movewait:
				if mv[0] != "switch":
					if mv[3].accuracy == "--":
						miss = False
					else:
						miss = mv[3].accuracy > random.random() * 100
				playside = mv in usedmoves
				match mv[0]: # eventually add secondary effects
					case "switch":
						if playside:
							playerside[playerside.index(mv[3])] == mv[2]
						else:
							enemyside[enemyside.index(mv[3])] == mv[2]
					case "use":
						match mv[2].category:
							case "Physical" | "Special":
								if not miss:
									match mv[1]:
										case "both":
											if playerside:
												for m in enemyside:
													m.chp -= damagecalc(mv[2],mv[3],m,len(enemyside)) * movespeed
											else:
												for m in playerside:
													m.chp -= damagecalc(mv[2],mv[3],m,len(enemyside)) * movespeed
										case "all":
											all = enemyside + playerside
											all.pop(all.index(m[3]))
											for m in all:
												m.chp -= damagecalc(mv[2],mv[3],m,len(enemyside)) * movespeed
										case "ally":
											a = playerside
											a.pop(a.index(m[3]))
											for m in a:
												m.chp -= damagecalc(mv[2],mv[3],m,len(a)) * movespeed
										case "enemy 1":
											enemyside[0].chp -= damagecalc(mv[2],mv[3],enemyside[0],1) * movespeed
										case "enemy 2":
											enemyside[1].chp -= damagecalc(mv[2],mv[3],enemyside[1],1) * movespeed
							case "Status":
								if not miss:
									print("status not done")# status is coded later
							case "PhysSwitch":
								if not miss:
									match mv[1]:
										case "both":
											if playside:
												for m in enemyside:
													m.chp -= damagecalc(m[2][0],m[3],m,len(enemyside)) * movespeed
											else:
												for m in playerside:
													m.chp -= damagecalc(m[2][0],m[3],m,len(playerside)) * movespeed
										case "all":
											all = enemyside + playerside
											all.pop(all.index(m[3]))
											for m in all:
												m.chp -= damagecalc(mv[2][0],mv[3],m,len(enemyside)) * movespeed
										case "ally":
											a = playerside
											a.pop(a.index(m[3]))
											for m in a:
												m.chp -= damagecalc(mv[2][0],mv[3],m,len(a))
										case "enemy 1":
											enemyside[0].chp -= damagecalc(mv[2][0],mv[3],enemyside[0],1) * movespeed
										case "enemy 2":
											enemyside[1].chp -= damagecalc(mv[2][0],mv[3],enemyside[1],1) * movespeed
									if playside:
										movewait = True
									else:
										enemyside[enemyside.index(mv[3])] == random.choice([obj for obj in enemy if obj.chp > 0 and obj not in enemyside])
			else:
				monbtns = []
				for i in range(len(current_game_state["mons"])):
					if current_game_state["mons"][i] in playerside:
						monbtns.append(btn(20, 20 + 100 * i, 180, 80, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species, (0,141,191)))
					elif current_game_state["mons"][i].chp <= 0:
						monbtns.append(btn(20, 20 + 100 * i, 180, 80, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species, (255,0,0)))
					else:
						monbtns.append(btn(20, 20 + 100 * i, 180, 80, current_game_state["mons"][i].name + "," + current_game_state["mons"][i].species))
				for i in range(6 - len(monbtns)):
					monbtns.append(btn(20, 20 + 100 * (i + len(monbtns)),180,80,""))
				for b in monbtns:
					b.draw(screen)
				for event in pygame.event.get():
					if event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:
							if monbtns[0].is_clicked(event.pos):
								if monbtns[0] not in playerside and current_game_state["mons"][0].chp > 0:
									playerside[monnumber] == current_game_state["mons"][0]
							elif monbtns[1].is_clicked(event.pos):
									if monbtns[1] not in playerside and current_game_state["mons"][1].chp > 0:
										playerside[monnumber] == current_game_state["mons"][1]
							elif monbtns[2].is_clicked(event.pos):
								if monbtns[2] not in playerside and current_game_state["mons"][2].chp > 0:
									playerside[monnumber] == current_game_state["mons"][2]
							elif monbtns[3].is_clicked(event.pos):
								if monbtns[3] not in playerside and current_game_state["mons"][3].chp > 0:
									playerside[monnumber] == current_game_state["mons"][3]
							elif monbtns[4].is_clicked(event.pos):
								if monbtns[4] not in playerside and current_game_state["mons"][4].chp > 0:
									playerside[monnumber] == current_game_state["mons"][4]
							elif monbtns[5].is_clicked(event.pos):
								if monbtns[5] not in playerside and current_game_state["mons"][5].chp > 0:
									playerside[monnumber] == current_game_state["mons"][5]
				if movenumber >= lim * 2:
					movenumber = 0
					monnumber = 0
		fin = False
		if len(enemyside) > 0:
			for mon in enemyside:
				if mon.chp > 0:
					fin = True
					break
		if fin == False:
			return "OVERWORLD"
		fin = False
		for mon in playerside:
			if mon.chp > 0:
				fin = True
				break
		if fin == False:
			return "OVERWORLD"
		pygame.display.flip()
		clock.tick(60)

def main():
	global state, current_game_state
	running = True
	encounter = []
	safe = safenumber()
	while running:
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
					if random.random() < 0.750 and len(current_game_state["mons"]) > 1: # These movesets have not been defined
						enemy = random.choice(spawnzones[current_bush.pool][0])
						encounter.append(mon(species[enemy], enemy, random.randint(spawnzones[current_bush.pool][1], spawnzones[current_bush.pool][2]), species[enemy].type, [0,0,0,0,0], species[enemy].mhp, ["Tackle"]))
						version = "doubles"
					enemy = random.choice(spawnzones[current_bush.pool][0])
					encounter.append(mon(species[enemy], enemy, random.randint(spawnzones[current_bush.pool][1], spawnzones[current_bush.pool][2]), species[enemy].type, [0,0,0,0,0], species[enemy].mhp, ["Tackle"]))
					state = "BATTLE"
					safe = safenumber()
			space.step(1 / FPS)
			screen.blit(player_image, player_rect)
			if debug: # shows debug stuff
				for w in walls: # shows wall hitboxes
					p1 = w.a
					p2 = w.b
					screen_p1 = (p1.x + camera_x, p1.y + camera_y)
					screen_p2 = (p2.x + camera_x, p2.y + camera_y)
					pygame.draw.line(screen, (200, 0, 0), screen_p1, screen_p2, int(wall.radius * 2))
				draw_options.transform = pymunk.Transform.translation(camera_x, camera_y)
				space.debug_draw(draw_options) # shows player hitbox
		if state == "BATTLE":
			state = battle(encounter, version)
			print("done")
		if state == "START":
			screen.blit(start_screen, (0,0))
		pygame.display.flip()
		clock.tick(60)
	return
main()
pygame.quit()
sys.exit()
