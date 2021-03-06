NewEps - XBMC plugin
-----------------------

(Work in progress. Not an official release. Though the plugin works fine 
on my XBMC installation and used on a weekly basis)

* Goal: One of the steps to a complete torrent-based PVR experience. This plugin is meant to be used 
in conjunction with a torrent client (like utorrent) that's set up to use RSS downloading (more info below.)

Useful when automatic RSS downloading is set up in the torrent client for TV episodes, set
to save in a given directory.

Script checks the given directory for downloaded tv episodes, lists them, parses (scene release) names, 
loads episode info from TheTVDB. Search for episodes is recursive (subdirs are checked).
Playing an episode removes it from the list as watched (with an option to restore and others)

As the result, the plugin shows unwatched episodes + the new ones that were automatically
added by the torrent client.

=====================
INSTALLATION:
=====================

It's a plugin for XBMC, so XBMC has to be installed.
Go to %APPDATA%\XBMC\addons\
Create a new folder "neweps"
And copy all files from this repo into that folder.

It will appear in XBMC under Programs.



====================
ISSUES
====================

* Some constants in one of the source files (default.py) must be edited
to adapt the script to one's particular setup (just the directory name and etc)
* The interface is designed using outdated methods
* The interface doesn't scale properly on different resolutions
* Some context menu options are not yet implemented
* Though it works, at this point the script is highly personalized and not ready for a public release.


====================
On automatic rss torrent downloads and extraction
====================

The use of RSS downloader in a torrent client, coupled with an
automatic extraction tool (if needed**) brings you very close
to the complete torrent-based PVR experience.

When the new episode becomes available for download, the torrent client
gets notified via RSS and downloads the episode automatically.
On some good trackers, new episodes for popular shows are uploaded within
as little as 15-20 minutes after the show airs.
Torrent client then saves the downloaded video in a specified folder.

This plugin attempts to complete the situation, and provides
the means to view/track/manage those automatically downloaded episodes in XBMC.


** Automatic extraction tool is needed if downloading legit scene releases
from private trackers, where the files are broken down into multiple 
rars (r01, r02, ... ) as per scene standards. 
Excellent example of such utility is called SCRU.
