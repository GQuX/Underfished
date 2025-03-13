from desktopmagic.screengrab_win32 import getRectAsImage as Screenshot
from ahk._sync.window import Window
from ahk import AHK; ahk = AHK()
from simple_pid import PID
from time import sleep
from PIL import Image
from os import path

######################################################################################

THRESHOLD = 10
RANGE = (915, 270,
		 916, 824)

######################################################################################

FOLDER_PATH = path.dirname(path.abspath(__file__))
SCREENSHOT_PATH = path.join(FOLDER_PATH, "Screenshots")

RED		= (146,  71,  93, 255)
GREEN	= ( 72, 175, 106, 255)
BLUE	= ( 85, 132, 193, 255)
BLACK	= (  2,   2,   2, 255)

COLORS = [ RED, GREEN, BLUE, BLACK ]

######################################################################################

class Roblox:
	def __init__(self):
		self.window: Window = self.GetWindow("Roblox")
		self.Fullscreen()

	def GetWindow(self, name: str) -> Window:
		if name == "Current":
			for window in ahk.windows():
				if window.active: return window
		else:
			window = ahk.win_get(title=name)
			if window: return window
		return None
	
	def Activate(self):
		self.window.activate()
	
	def Dimensions(self):
		return self.window.get_position()
	
	def Center(self):
		dimensions = self.dimensions()
		return {
			'x': int(dimensions.width  / 2),
			'y': int(dimensions.height / 2) }
		
	def Fullscreen(self):
		fullscreen = self.window.get_position().y == 0
		if not fullscreen:
			self.window.activate()
			ahk.key_press('F11')

def ColorMap(screenshot: Image) -> dict:
	pixels = screenshot.load()
	color_map = {}
	
	for y in range(screenshot.height):
		if   sum((pixels[0, y][i] - BLUE[i] )**2 for i in range(3)) < 5000: color_map[y] = BLUE
		elif sum((pixels[0, y][i] - RED[i]  )**2 for i in range(3)) <  500: color_map[y] = RED
		elif sum((pixels[0, y][i] - GREEN[i])**2 for i in range(3)) <  500: color_map[y] = GREEN
		elif sum((pixels[0, y][i] - BLACK[i])**2 for i in range(3)) <  500: color_map[y] = BLACK
		else:																color_map[y] = BLUE
		pixels[0, y] = color_map[y]

	#screenshot.save(path.join(SCREENSHOT_PATH, "Output - Rounded.png"), "png")
	return color_map

class Fisherman:
	def __init__(self):
		self.roblox = Roblox()
		self.iteration = 0
		self.pid = PID(
			Kp = 0.0015,
			Ki = 0.0015,
			Kd = 0.0001,
			setpoint = 0 )
	
	def Locate(self) -> str | int:
		position = self.roblox.Dimensions()
		screenshot = Screenshot((position.x + RANGE[0], position.y + RANGE[1],
								 position.x + RANGE[2], position.y + RANGE[3]))
		#screenshot.save(path.join(SCREENSHOT_PATH, "Output - Raw.png"), "png")
		color_map = ColorMap(screenshot)

		fish = 0
		fish_found = False
		bar = 0
		bar_found = False
		
		for y in color_map:
			if bar_found and fish_found: break
			elif not bar_found  and color_map[y] == RED:	bar  = y + 72; bar_found  = True
			elif not bar_found  and color_map[y] == GREEN:	bar  = y + 72; bar_found  = True
			elif not fish_found and color_map[y] == BLACK:  fish = y + 17; fish_found = True

		status = "?"
		difference = fish - bar
		if not bar_found:
			status = "No Bar"
			difference = 0
		elif fish < bar:										status = "Hold"
		elif fish > bar:										status = "Release"
		elif fish > bar - THRESHOLD and fish < bar + THRESHOLD:	status = "Centered"

		#if status == "No Bar":
		#	img_fullscreen = Screenshot((position.x,        position.y, 
		#								 position.x + 1920, position.y + 1080 ))
		#	img_fullscreen.save(path.join(SCREENSHOT_PATH, f"{self.iteration}_full.png"), "png")
		#	img.save(path.join(SCREENSHOT_PATH, f"{self.iteration}_{status}.png"), "png")

		return status, difference
	
	def Start(self):
		try:
			while True:
				status, difference = self.Locate()
				control = max(0.1, self.pid(difference))
				print(f"{self.iteration} | {status} | {difference}px ({control}s)")
				self.iteration += 1

				if status == "No Bar":
					sleep(0.5)
				else:
					if status == "Hold" or status == "Centered":
						ahk.key_down("LButton")
						sleep(control)
						ahk.key_release("LButton")
					elif status == "Release":
						sleep(control)
		except KeyboardInterrupt:
			print("Keyboard Interruption, stopped fishing.")

######################################################################################

fisherman = Fisherman()
fisherman.Start()