import xbmc, xbmcgui, os, re, pickle
import constants
import thetvdbapi

# import rpdb2
# rpdb2.start_embedded_debugger('pw')

import thetvdbapi

ESCAPE_KEY = 61467
I_KEY = 61513
UP_KEY = 61478
DOWN_KEY = 61480

LIST_X = 80
LIST_Y = 240
LIST_W = 830
LIST_H = 450



TVDIR = "E:\\Video\\TV"
EPSFILE= "E:\\Video\\watched.txt"

TOREPL = ["hdtv","lol","asap","divx","p0w4","avi","mkv","xvid","-","fqm","dvdrip","reward","fever","2hd","aaf","pdtv","DVDSCR","","","","","","","","",""]

tv = thetvdbapi.TheTVDB("CAA0BFEC15F96EBE");


class MyClass(xbmcgui.Window):
	shiftv = 0
	shifth = 0
	
	allFiles = []				# path and filename
	allFilenames = []		# names only
	entries = []				# filenames read from the text file

	newEpsList = []		# populated by the make_diff function
	names = []				# converted file names, index wise matches newEpsList, which contain full file names.
	
	possibleChoices = ["Play", "Play & Keep","Paly Previous", "Restore Previous",  "Mark as Watched & Remove from List", "Refresh/Clear Cache for Selected", "Clear All Cache", "Exit"]
	#								0					1					2							3									4																			5								6					 7		
	
	def __init__(self):
	
		# window title
		self.topt = os.path.join(os.getcwd(),"images","top_title.png")
		self.addControl(xbmcgui.ControlImage(765,-28,400,100, self.topt))
		
		# main background rectangle
		self.bgImagePath = os.path.join(os.getcwd(),"images","backg.png")
		self.addControl(xbmcgui.ControlImage(50,50,1800,1020, self.bgImagePath))
	
		# banner-holding wide rectangle
		self.bannerBgImagePath = os.path.join(os.getcwd(),"images","banner_bg.png")
		self.addControl(xbmcgui.ControlImage(82,69,1736,160, self.bannerBgImagePath))	
		
		
		# file list background rectangle
		self.listBgImagePath = os.path.join(os.getcwd(),"images","list_bg.png")
		self.addControl(xbmcgui.ControlImage(LIST_X+32, LIST_Y, LIST_W, LIST_H, self.listBgImagePath))
		
		#description box, same rectangle as for the list
		self.infoboxBgPath = os.path.join(os.getcwd(),"images","infobox_bg.png")
		self.addControl(xbmcgui.ControlImage(LIST_X + 877, LIST_Y-4, LIST_W+5, LIST_H+7, self.infoboxBgPath))	

		# labels
		self.strShowName = xbmcgui.ControlLabel(990, 300, 900, 100, "", "font24", "#909090")
		self.addControl(self.strShowName)	
		
		self.strSeasonNumber = xbmcgui.ControlLabel(1400, 300, 900, 100, "", "font24", "#909090")
		self.addControl(self.strSeasonNumber)
		
		self.strEpisodeNumber = xbmcgui.ControlLabel(1585, 300, 900, 100, "", "font24", "#909090")
		self.addControl(self.strEpisodeNumber)
		
		self.strEpisodeName = xbmcgui.ControlLabel(990, 430, 900, 100, "Episoade name", "font14", "#909090")
		self.addControl(self.strEpisodeName)
		
		self.strOverview = xbmcgui.ControlTextBox(990, 550, 750, 460, font = "font14")
		self.addControl(self.strOverview)	
		
		
		self.strCountLabel = xbmcgui.ControlLabel(150, 120, 500, 100, "New episodes found: ", "font14", "#909090")
		self.addControl(self.strCountLabel)	
		#self.strCountLabel.setLabel("New episodes found: ")
		
		self.strCount = xbmcgui.ControlLabel(480, 120, 100, 100, "", "font14", "#909090")
		self.addControl(self.strCount)	
		
		self.make_list()
		
		# self.update_current_info()
		

# ------------------------------------------ onAction ------------------------------------------
	def onAction(self, action):
		if action.getButtonCode() == ESCAPE_KEY:
			self.close()
		
		if action.getButtonCode() == UP_KEY:
			self.update_current_info()

			
		if action.getButtonCode() == DOWN_KEY:	
			self.update_current_info()
			
		if action.getButtonCode() == I_KEY:
			self.lookup_episode_data()
			
# ------------------------------------------ onControl ------------------------------------------
	def onControl(self, control):
		if control == self.list:
			item = self.list.getSelectedItem()
			chooserResponse = self.action_selector()
			
			# play
			if chooserResponse == 0:
				self.play_action(item.getLabel(), "NORM")
				
			# play & keep
			if chooserResponse == 1:
				self.play_action(item.getLabel(), "KEEP")
				
			#restore previous	
			if chooserResponse == 3:
				self.restore_action()
				
			# mark as watched and remove
			if chooserResponse == 4:
				self.play_action(item.getLabel(), "REMOVE_ONLY")
			
			# clear cache for selected item
			if chooserResponse == 5:
				self.clear_cache("selected")
				
			# clear all cache
			if chooserResponse == 6:
				self.clear_cache("all")
				
			# exit action
			if chooserResponse == 7:
				self.close()
			

				
	def update_current_info(self):
		"""updates the show info labels, extracts episode name, season and episode numbers, assigns labels"""
		item = self.list.getSelectedItem()
		selected_text = item.getLabel()
		
		# returns list of tuples, groups are the tuple items
		matches = re.findall("(.*)S(\d*)E(\d*).*", selected_text)
		match = matches[0] # assumed there's only one match
		
		(name, season, episode) = match
		
		self.strShowName.setLabel(name)
		self.strSeasonNumber.setLabel("Season: " + season)
		self.strEpisodeNumber.setLabel("Episode: " + episode)
		
		self.lookup_episode_data()
		

	def lookup_episode_data(self):
		season = self.strSeasonNumber.getLabel().replace("Season:", "").strip()
		episode = self.strEpisodeNumber.getLabel().replace("Episode:", "").strip()
		name = self.strShowName.getLabel().strip()

		ep = self.findEp(name, season, episode)
				
		self.strEpisodeName.setLabel(ep[2])
		self.strOverview.setText(ep[3])
		
		
	
	def findEp(self, showName, seasonNum, episodeNum):
		""" searches for the show, grabs first found. Numbers are strings here! """
		cache = os.path.join(os.getcwd(),"cache", showName)
		result = None # default result
		
		if os.path.isfile(cache):
			f = open(cache, 'r')
			cache_data = f.readlines()
			f.close()
			
			foundInCache = False
			
			for entry in cache_data:
				split_data = entry.split("|||")
				if int(seasonNum) == int(split_data[0]) and int(episodeNum) == int(split_data[1]):
					foundInCache = True
					return split_data
				
			if foundInCache == False:
				self.strEpisodeName.setLabel("Not found in cache. Please update via menu.")

				
		else:
			print "---> no cache file found.. looking up and caching"
			self.strEpisodeName.setLabel("Updating... Please Wait.")
			self.strOverview.setText("")
			
			# showname substitutions. Used when a different name has to be sent to the server for lookup instead of the normal name, like "V (2009)" instead of "V"
			for show in constants.SHOWNAME_SUB:
				if showName == show[0]:
					showName = show[1]
					
			showId = tv.get_matching_shows(showName)[0][0]
			show = tv.get_show_and_episodes(showId)
			eps = show[1]
			
			# cache the entire show
			f = open(cache, 'w')
			for ep in eps:
				# unicode is converted into ascii to avoid file writing errors
				name = ep.name.strip().encode("ascii", "ignore")
				season = ep.season_number.strip().encode("ascii", "ignore")
				episode = ep.episode_number.strip().encode("ascii", "ignore")
				overview = ep.overview.strip().encode("ascii", "ignore").replace("\n", "")
				
				f.write(season + "|||" + episode + "|||" + name+ "|||" + overview + "\n")
				
				if int(season) == int(seasonNum) and int(episode) == int(episodeNum):
					result = (season, episode, name, overview)
					
			f.close()
			return result
				
	
	def clear_cache(self, what):
		if what == "selected":
			name = self.strShowName.getLabel().strip()
			cacheFilePath = os.path.join(os.getcwd(),"cache", name)
			if os.path.isfile(cacheFilePath):
				try:
					os.remove(cacheFilePath)
				except:
					self.message("Error occured!")
				# on success - offer to update cache.
				dialog = xbmcgui.Dialog()
				if dialog.yesno("Cache Cleared", "Old cache data for " + name + " has been cleared. \nWould you like to update cache?"):
					self.lookup_episode_data()
	

	def play_action(self, name, param):
		# get filename from text name(on the list). names and newEpsList have matcing indices.
		index = self.names.index(name)
		epFilename = self.newEpsList[index]
		
		# not that we have the filename, look up the full filename with path. allFiles and allFilenames have matcing indices.
		indexb = self.allFilenames.index(epFilename)
		fullname = self.allFiles[indexb]
		
		if param == "NORM" or param == "REMOVE_ONLY":
			#add the new entry to watched.txt then rebuild the list (the entry will disappear)
			f = open(EPSFILE, 'r+')
			skip = f.readlines()
			f.write(epFilename + "\n")
			f.close()
			
			
			# self.regenerate_list(index)
			
		if param == "NORM" or param == "KEEP":
				self.play(fullname)
				#self.debugstr(fullname)
				#self.debugstr(name)
		
		# rebuild the list, select previous item (index-1)	
		self.regenerate_list(index)
		
	
	def restore_action(self):
		tmp = self.entries.pop()
		
		f = open(EPSFILE, "w+")
		
		for line in self.entries:
			f.write(line+"\n")
		f.close()
		
		index = len(self.names) - 1
		self.regenerate_list(index)
		
		
			
	def make_list(self):
		ftexture = os.path.join(os.getcwd(),"images","sel_texture_w.png")
		#self.addControl(xbmcgui.ControlImage(82,69,1736,160, self.bannerBgImagePath))
		self.list = xbmcgui.ControlList(LIST_X+5+32, LIST_Y+5, LIST_W-10, LIST_H, "font12", "0xFFFFFFFF","",ftexture,"",10)
		self.list.setItemHeight(50)
		
		self.addControl(self.list)
		
		# build a list with unwatched shows, build a list of clean names
		self.make_diff() 
		self.make_name_list()
		
		for item in self.names:
			self.list.addItem(item)
		
		count = len(self.names)
		self.strCount.setLabel(str(count))
		self.setFocus(self.list)

		

	def make_filelist(self, dir):
		""" recursively walks through all subdirectories and builds a list of files 
			makes 2 lists - one with all filenames, another with all paths"""
		if os.path.isdir(dir) == True:
			listb = os.listdir(dir)
			for item in listb:
				self.make_filelist(os.path.join(dir,item))
		else:
			self.allFilenames.append(os.path.basename(dir))
			self.allFiles.append(dir)

	
	
	def make_entries_list(self):
		f = open(EPSFILE, 'r')
		self.entries = [line.strip() for line in f]
		f.close()
		
	def make_diff(self):
		self.newEpsList = []
		self.allFilenames = []
		self.entries = []
		self.names = []
		self.make_filelist(TVDIR)
		self.make_entries_list()
		self.newEpsList = [i for i in self.allFilenames if i not in self.entries]
		if len(self.entries) == 0:
				self.message(NO_WATHCED_SHOWS)

	def regenerate_list(self, itemToSelect):
		self.list.reset()
		self.make_diff()
		self.make_name_list()
		for item in self.names:
			self.list.addItem(item)
			
		# selecting previous item 
		if itemToSelect < 0:
			itemToSelect = 0
		if len(self.names) > 0:
			self.list.selectItem(itemToSelect)
		
		self.update_current_info()
	
# --------------------------------------------- handling the names ------------------------------------------------
	def make_name_list(self):
		""" makes a clean list of show names based on the newEpsList. Can only be called after make_diff """
		for line in self.newEpsList:
			# changing periods into spaces
			cleanLine = line.replace(".", " ")
			#lowercasing everything
			cleanLine = cleanLine.lower()
			
			# removing years 2004 - 2012 from names (they mess up episode count)
			year = 2004
			while year < 2013:
				cleanLine = cleanLine.replace(str(year),"")
				year += 1
			
			# removing stuff listed in TOREPL
			for entry in TOREPL:
				cleanLine = cleanLine.replace(entry,"")
			
			# episode name and number into sAAeBB format, 4 most common cases. Only one will match.
			# the resulting format is SaaEbb
			

				
			# SSEE format
			matches = re.findall("(.*)\s(\d\d)(\d\d)(.*)", cleanLine)
			if len(matches) == 1:
				match = matches[0]
				cleanLine = match[0] + " S" + match[1] + "E" + match[2] + match[3]

				
			# SEE format
			matches = re.findall("(.*)\s(\d)(\d\d)(.*)", cleanLine)
			if len(matches) == 1:
				match = matches[0]
				cleanLine = match[0] + " S0" + match[1] + "E" + match[2] + match[3]
				
			
			#SSxEE format
			matches = re.findall("(.*)\s(\d\d)x(\d\d)(.*)", cleanLine)
			if len(matches) == 1:
				match = matches[0]
				cleanLine = match[0] + " S" + match[1] + "E" + match[2] + match[3]
				
			#SxEE format
			matches = re.findall("(.*)\s(\d)x(\d\d)(.*)", cleanLine)
			if len(matches) == 1:
				match = matches[0]
				cleanLine = match[0] + " S0" + match[1] + "E" + match[2] + match[3]
			
			#uppercasing
			cleanLine = cleanLine.title()
			self.names.append(cleanLine)
# -----------------------------------------------------------------------------------------------------------------------		
	
	
	def play (self, fileToPlay):
		playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		playlist.clear()
		playlist.add(fileToPlay)
		xbmc.Player().play(playlist)
		
		
	
	def action_selector(self):
		dialog = xbmcgui.Dialog()
		choice = dialog.select("", self.possibleChoices)
		return choice
		
		
	def addlbl(self, text, x, y, font, color):
		self.strAction = xbmcgui.ControlLabel(x, y, 500, 500, str(text), font, color)
		self.addControl(self.strAction)	
		
		
	def message(self, messageText):
		dialog = xbmcgui.Dialog()
		dialog.ok("Message", messageText)
		
		
	def debugstr(self, text):
		self.strAction = xbmcgui.ControlLabel(30 + self.shifth, 20 + self.shiftv, 1000, 500, "", "font10", "0xFFFFFF00")
		self.addControl(self.strAction)
		self.strAction.setLabel(str(text))
		self.shiftv = self.shiftv + 25
		
		if self.shiftv > 950:
			self.shiftv = 0
			self.shifth = self.shifth + 300
		
		
# ------------------------------------- event loop starts ----------------------------------------------
mydisplay = MyClass()
mydisplay.doModal()
del mydisplay