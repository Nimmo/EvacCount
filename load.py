"""
EvacCount a plugin for EDMC
Copyright (C) 2019 Graeme Nimmo

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import Tkinter as tk
import myNotebook as nb
from config import config
import json
import sys
from functools import partial
from l10n import Locale

this = sys.modules[__name__]	# For holding module globals

this.VERSION = "0.1"
this.PADX = 5
this.WIDTH = 10

def resetTotalEvacuated():
    config.set("EvacCount_evacuated", 0)
    this.evacuatedTotal = 0

def plugin_prefs(parent, cmdr, is_beta):
   # Skeletony bits
   this.frame = nb.Frame(parent)

   frameTop = nb.Frame(this.frame)
   frameTop.grid(row=0, column=0, sticky=tk.W)
   frameBottom = nb.Frame(this.frame)
   frameBottom.grid(row=1, column=0, sticky=tk.SW)
   #End skeleton

   #headline
   this.evacCount = tk.IntVar(value=config.getint("EvacCountSetting"))	# Retrieve saved value from config
   frame = nb.Frame(parent)

   # total evac count
   evacuatedTotal = nb.Checkbutton(frameBottom, variable=evacuatedTotalOption, text="Calculate total number of evacuated civilians")
   evacuatedTotal.var = evacuatedTotalOption
   evacuatedTotal.grid(row=0, column=0, padx=this.PADX * 2, sticky=tk.W)
   resetButton = nb.Button(frameBottom, text="Reset", command=resetTotalEvacuated)
   resetButton.grid(row=1, column=0, padx=this.PADX * 4, pady=5, sticky=tk.W)

   evacuatedSession = nb.Checkbutton(frameBottom, variable=evacuatedSessionOption, text="Calculate evacuated civilians for current session")
   evacuatedSession.var = evacuatedSessionOption
   evacuatedSession.grid(row=2, column=0, padx=this.PADX * 2, sticky=tk.W)

   # radio button value: 1 = calculate for ED session; 0 = calculate for EDMC session
   evacuatedSessionEdmc = nb.Radiobutton(frameBottom, variable=evacuatedSessionSelected, value=0, text="EDMC session")
   evacuatedSessionEdmc.var = evacuatedSessionSelected
   evacuatedSessionEdmc.grid(row=3, column=0, padx=this.PADX * 4, sticky=tk.W)

   evacuatedSessionElite = nb.Radiobutton(frameBottom, variable=evacuatedSessionSelected, value=1, text="Elite session")
   evacuatedSessionElite.var = evacuatedSessionSelected
   evacuatedSessionElite.grid(row=4, column=0, padx=this.PADX * 4, sticky=tk.W)

   setStateRadioButtons(evacuatedSessionEdmc, evacuatedSessionElite)
   evacuatedSession.config(command=partial(setStateRadioButtons, evacuatedSessionEdmc, evacuatedSessionElite))
   nb.Label(frameBottom).grid(row=5)  # spacer
   nb.Label(frameBottom).grid(row=6)  # spacer
   nb.Label(frameBottom, text="Plugin version: {0}".format(this.VERSION)).grid(row=7, column=0, padx=this.PADX, sticky=tk.W)
   return this.frame

def setStateRadioButtons(evacuatedSessionEdmc, evacuatedSessionElite):
    if this.evacuatedSessionOption.get() == 1:
        evacuatedSessionEdmc["state"] = "normal"
        evacuatedSessionElite["state"] = "normal"
    else:
        evacuatedSessionEdmc["state"] = "disabled"
        evacuatedSessionElite["state"] = "disabled"


def prefs_changed():
   settings = [this.evacuatedTotalOption.get(), this.evacuatedSessionOption.get(), this.evacuatedSessionSelected.get()]
   config.set("EvacCount_options", json.dumps(settings))

   updateMainUi()

def updateMainUi():
    # labels for evacation EvacCountSetting
    settingTotal, settingSession, settingSessionOption = getSettingsEvacuated()
    row = 0
    for i in range(len(this.evacuatedLabels)):
        description, evacuated = this.evacuatedLabels[i]
        if (i == 0 and settingTotal) or (i == 1 and settingSession):
            description.grid(row=row, column=0, sticky=tk.W)
            description["text"] = "Evacuated ({0}):".format("total" if i == 0 else "session")
            evacuated.grid(row=row, column=1, sticky=tk.W)
            evacuated["text"] = "{0}".format(Locale.stringFromNumber(this.evacuatedTotal, 0) if i == 0 else Locale.stringFromNumber(this.evacuatedSession, 0))
            row += 1
        else:
            description.grid_remove()
            evacuated.grid_remove()

def plugin_app(parent):
    frame = tk.Frame(parent)
    this.emptyFrame = tk.Frame(frame)
    frame.columnconfigure(1, weight=1)

    this.status = tk.Label(parent, anchor=tk.W, text="")
    this.evacuatedLabels = list()
    for i in range(2):
        this.evacuatedLabels.append((tk.Label(frame), tk.Label(frame)))

    updateMainUi()

    return (frame)



def plugin_start():
   this.count = json.loads(config.get("EvacCount") or "[]")
   this.missions = json.loads(config.get("EvacCount_missions") or "{}")
   this.evacuatedTotal = config.getint("EvacCount_evacuated") or 0
   this.passengersOnBoard = config.getint("EvacCount_onBoard") or 0
   this.evacuatedSession = 0
   evacuatedTotalOption,evacuatedSessionOption,evacuatedSessionSelected = getSettingsEvacuated()
   this.evacuatedTotalOption = tk.IntVar(value=evacuatedTotalOption and 1)
   this.evacuatedSessionOption = tk.IntVar(value=evacuatedSessionOption and 1)
   this.evacuatedSessionSelected = tk.IntVar(value=evacuatedSessionSelected and 1)

   return "EvacCount"

def getSettingsEvacuated():
    settings = json.loads(config.get("EvacCount_options") or "[1,1,1]")
    settingTotal = settings[0] # calculate total passengers evacuated
    settingSession = settings[1] # Calculate for session only
    settingSettingOption = settings[2] # 1 = ED Session, 0 = EDMC Session
    return settingTotal, settingSession, settingSettingOption

def updateCounts():
    _, evacuated = this.evacuatedLabels[0]
    evacuated["text"] = "{0}".format(Locale.stringFromNumber(this.evacuatedTotal, 0))
    _, evacuated = this.evacuatedLabels[1]
    evacuated["text"] = "{0}".format(Locale.stringFromNumber(this.evacuatedSession, 0))

def journal_entry(cmdr, system, station, entry, state):
    if entry["event"] == "MissionAccepted" and entry["Name"] == "Mission_DS_PassengerBulk":
        #Figure out how we pick up passengers
        this.missions[entry["MissionID"]] = entry["PassengerCount"]
        config.set("EvacCount_missions", json.dumps(this.missions))
    elif entry["event"] == "SearchAndRescue" and (entry["Name"] == "occupiedcryopod" or entry["Name"] == "damagedescapepod"):
        this.evacuatedSession += entry["Count"] # Get correct ammount
        this.evacuatedTotal += entry["Count"] # Get correct ammount
        config.set("EvacCount_evacuated", int(this.evacuatedTotal))
        updateCounts()
    elif entry["event"] == "MissionCompleted" and entry["Name"] == "Mission_DS_PassengerBulk_name":
        this.evacuatedSession += this.missions[entry["MissionID"]] # Get correct ammount
        this.evacuatedTotal += this.missions[entry["MissionID"]] # Get correct ammount
        config.set("EvacCount_evacuated", int(this.evacuatedTotal))
        del this.missions[entry["MissionID"]]
        config.set("EvacCount_missions", json.dumps(this.missions))
        updateCounts()
    elif entry["event"] == "LoadGame" and this.evacuatedSessionOption.get() and this.evacuatedSessionSelected.get():
        this.evacuatedSession = 0
