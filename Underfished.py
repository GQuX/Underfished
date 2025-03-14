#>- Settings -------------------------------------------------------------------------

UPDATE_TIME		 = 0.2 # Seconds
CENTER_THRESHOLD = 60 # Pixels
SCREENSHOT_RANGE = (915, 270,
					916, 824) # Pixel Range (X1, Y1, X2, Y2)

#>- Dependencies ---------------------------------------------------------------------

from desktopmagic.screengrab_win32 import getRectAsImage as Screenshot
from ahk._sync.window import Window
from ahk import AHK; ahk = AHK()
from time import sleep

#>- Constants ------------------------------------------------------------------------

RED		= (146,  71,  93, 255)
GREEN	= ( 72, 175, 106, 255)
BLUE	= ( 85, 132, 193, 255)
BLACK	= (  2,   2,   2, 255)

COLORS = [ RED, GREEN, BLUE, BLACK ]

#>- Functions ------------------------------------------------------------------------

def ColorMap(screenshot) -> dict:
	pixels = screenshot.load()
	color_map = {}
	
	for y in range(screenshot.height):
		if   sum((pixels[0, y][i] - BLUE[i] )**2 for i in range(3)) < 5000: color_map[y] = BLUE
		elif sum((pixels[0, y][i] - RED[i]  )**2 for i in range(3)) <  500: color_map[y] = RED
		elif sum((pixels[0, y][i] - GREEN[i])**2 for i in range(3)) <  500: color_map[y] = GREEN
		elif sum((pixels[0, y][i] - BLACK[i])**2 for i in range(3)) <  500: color_map[y] = BLACK
		else:																color_map[y] = BLUE
		pixels[0, y] = color_map[y]

	return color_map

#>- Classes --------------------------------------------------------------------------

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
			'X': int(dimensions.width  / 2),
			'Y': int(dimensions.height / 2) }
		
	def Fullscreen(self):
		fullscreen = self.window.get_position().y == 0
		if not fullscreen:
			self.window.activate()
			ahk.key_press('F11')

class Fisherman:
	def __init__(self):
		self.roblox = Roblox()
		self.iteration = 0
	
	def Locate(self) -> str | int:
		position = self.roblox.Dimensions()
		screenshot = Screenshot((position.x + SCREENSHOT_RANGE[0], position.y + SCREENSHOT_RANGE[1],
								 position.x + SCREENSHOT_RANGE[2], position.y + SCREENSHOT_RANGE[3]))
		color_map = ColorMap(screenshot)

		fish, fish_found = 0, False
		bar,  bar_found  = 0, False
		
		for y in color_map:
			if bar_found and fish_found: break
			elif not bar_found  and color_map[y] == RED:	bar  = y + 72; bar_found  = True
			elif not bar_found  and color_map[y] == GREEN:	bar  = y + 72; bar_found  = True
			elif not fish_found and color_map[y] == BLACK:  fish = y + 17; fish_found = True

		status = "No Bar"
		difference = fish - bar
		if not bar_found: return "No Bar", 0
		elif fish < bar - CENTER_THRESHOLD:	status = "Hold"
		elif fish > bar + CENTER_THRESHOLD:	status = "Release"
		else:								status = "Centered"
		
		return status, difference
	
	def Start(self):
		try:
			while True:
				status, difference = self.Locate()
				print(f"{self.iteration} | {status} ({difference}px)")
				self.iteration += 1

				if status == "No Bar":
					sleep(0.5)
				elif status == "Hold":
					ahk.key_down("LButton")
					sleep(UPDATE_TIME)
					ahk.key_release("LButton")
				elif status == "Release":
					sleep(UPDATE_TIME)
				elif status == "Centered":
					ahk.key_down("LButton")
					sleep(UPDATE_TIME/2)
					ahk.key_release("LButton")
					sleep(UPDATE_TIME/2)
		except KeyboardInterrupt:
			print("Keyboard Interruption, stopped fishing.")

#>- Initialize -----------------------------------------------------------------------

fisherman = Fisherman()
fisherman.Start()