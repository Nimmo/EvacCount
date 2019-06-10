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

this.VERSION = "0.3.1"
this.PADX = 5
this.WIDTH = 10

def resetTotalEvacuated():
    config.set("EvacCount_totals","[0,0,0,0,0,0,0,0]")
    config.set("EvacCount_missions",json.dumps({}))
    this.totals = [0,0,0,0,0,0,0,0]
    this.missions = {}
    updateCounts()

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
   evacuatedTotal = nb.Checkbutton(frameBottom, variable=evacuatedTotalOption, text="Calculate totals")
   evacuatedTotal.var = evacuatedTotalOption
   evacuatedTotal.grid(row=0, column=0, padx=this.PADX * 2, sticky=tk.W)
   resetButton = nb.Button(frameBottom, text="Reset Totals", command=resetTotalEvacuated)
   resetButton.grid(row=1, column=0, padx=this.PADX * 4, pady=5, sticky=tk.W)

   evacuatedSession = nb.Checkbutton(frameBottom, variable=evacuatedSessionOption, text="Calculate totals for current session")
   evacuatedSession.var = evacuatedSessionOption
   evacuatedSession.grid(row=2, column=0, padx=this.PADX * 2, sticky=tk.W)

   # radio button value: 1 = calculate for ED session; 0 = calculate for EDMC session
   evacuatedSessionEdmc = nb.Radiobutton(frameBottom, variable=evacuatedSessionSelected, value=0, text="EDMC session")
   evacuatedSessionEdmc.var = evacuatedSessionSelected
   evacuatedSessionEdmc.grid(row=3, column=0, padx=this.PADX * 4, sticky=tk.W)

   evacuatedSessionElite = nb.Radiobutton(frameBottom, variable=evacuatedSessionSelected, value=1, text="Elite session")
   evacuatedSessionElite.var = evacuatedSessionSelected
   evacuatedSessionElite.grid(row=4, column=0, padx=this.PADX * 4, sticky=tk.W)


   # Search and Rescue settings
   #'''# TODO: complete later
   nb.Label(frameBottom, text="Search and rescue options").grid(row=5, column=0, padx=this.PADX, sticky=tk.W)

   sarBlackBox = nb.Checkbutton(frameBottom, variable=blackBoxOption, text="Track black boxes")
   sarBlackBox.var = blackBoxOption
   sarBlackBox.grid(row=6, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarWreckage = nb.Checkbutton(frameBottom, variable=wreckageOption, text="Track wreckage")
   sarWreckage.var = wreckageOption
   sarWreckage.grid(row=7, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarEscapePod = nb.Checkbutton(frameBottom, variable=occupiedPodOption, text="Track occupied escape pods")
   sarEscapePod.var = occupiedPodOption
   sarEscapePod.grid(row=8, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarPersonalEffects = nb.Checkbutton(frameBottom, variable=personalEffectsOption, text="Track personal effects")
   sarPersonalEffects.var = personalEffectsOption
   sarPersonalEffects.grid(row=9, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarDamagedPod = nb.Checkbutton(frameBottom, variable=damagedPodOption, text="Track damaged pods")
   sarDamagedPod.var = damagedPodOption
   sarDamagedPod.grid(row=10, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarPrisoners = nb.Checkbutton(frameBottom, variable=prisonersOption, text="Track political prisoners")
   sarPrisoners.var = prisonersOption
   sarPrisoners.grid(row=11, column=0, padx=this.PADX * 2, sticky=tk.W)

   sarEncrypted = nb.Checkbutton(frameBottom, variable=correspondenceOption, text="Track encrypted correspondence")
   sarEncrypted.var = correspondenceOption
   sarEncrypted.grid(row=12, column=0, padx=this.PADX * 2, sticky=tk.W)
   #'''
   setStateRadioButtons(evacuatedSessionEdmc, evacuatedSessionElite)
   evacuatedSession.config(command=partial(setStateRadioButtons, evacuatedSessionEdmc, evacuatedSessionElite))
   nb.Label(frameBottom).grid(row=13)  # spacer
   nb.Label(frameBottom).grid(row=14)  # spacer
   nb.Label(frameBottom, text="Plugin version: {0}".format(this.VERSION)).grid(row=15, column=0, padx=this.PADX, sticky=tk.W)
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
   this.sarSettings =[blackBoxOption.get(),
                 wreckageOption.get(),
                 occupiedPodOption.get(),
                 personalEffectsOption.get(),
                 damagedPodOption.get(),
                 prisonersOption.get(),
                 correspondenceOption.get()]
   config.set("EvacCount_sarSettings",json.dumps(this.sarSettings))
   updateMainUi()

def updateMainUi():
    # labels for evacation EvacCountSetting
    settingTotal, settingSession, settingSessionOption = getSettingsEvacuated()
    sarSettings = getSarSettings
    print this.sarSettings
    skipped = 0
    count = 2
    for row in range(len(this.evacuatedLabels)):
        description, session, total = this.evacuatedLabels[row]
        if row == 0:
            description.grid(row=row, column=0, sticky=tk.W)
            description["text"] = "Item"
            session.grid(row=row, column=1, sticky=tk.W)
            session["text"] = "Session"
            if(settingTotal == 1):
                total.grid(row=row, column=2, sticky=tk.W)
                total["text"] = "Total"
            else:
                total.grid_remove()
        elif row == 1:
            description.grid(row=row, column=0, sticky=tk.W)
            description["text"] = this.labels[row-1]
            session.grid(row=row, column=1, sticky=tk.W)
            session["text"] = this.counts[row-1]
            if(settingTotal == 1):
                total.grid(row=row, column=2, sticky=tk.W)
                total["text"] = this.totals[row-1]
            else:
                total.grid_remove()
        else:
            if this.sarSettings[row - 2] == 1:
                description.grid(row=(count), column=0, sticky=tk.W)
                description["text"] = this.labels[row - 1]
                session.grid(row=(count), column=1, sticky=tk.W)
                session["text"] = this.counts[row - 1]

                print "printing:", this.labels[row - 1], "on line", str(count)
                if(settingTotal == 1):
                    total.grid(row=(count), column=2, sticky=tk.W)
                    total["text"] = this.totals[row - 1]
                else:
                    total.grid_remove()
                count += 1
            else:
                description.grid_remove()
                session.grid_remove()
                total.grid_remove()
                skipped += 1


def plugin_app(parent):
    frame = tk.Frame(parent)
    this.emptyFrame = tk.Frame(frame)
    frame.columnconfigure(1, weight=1)

    this.status = tk.Label(parent, anchor=tk.W, text="")
    this.evacuatedLabels = list()
    for i in range(9):
        this.evacuatedLabels.append((tk.Label(frame), tk.Label(frame), tk.Label(frame)))

    updateMainUi()

    return (frame)

def getSarSettings():
    sarSettings = json.loads(config.get("EvacCount_sarSettings") or "[1,1,1,1,1,1,1]")
    return sarSettings

def plugin_start():
   this.labels = ["Evacuees", "Black Boxes", "Wreckage", "Escape Pods", "Personal Effects", "Damaged Escape Pods", "Political Prisoners", "Encrypted Correspondence"]

   this.missions = json.loads(config.get("EvacCount_missions") or "{}")
   this.totals = json.loads(config.get("EvacCount_totals") or "[0,0,0,0,0,0,0,0]")
   this.counts = [0,0,0,0,0,0,0,0]

   evacuatedTotalOption,evacuatedSessionOption,evacuatedSessionSelected = getSettingsEvacuated()
   blackBoxOption, wreckageOption, occupiedPodOption, personalEffectsOption, damagedPodOption, prisonersOption, correspondenceOption = getSarSettings()
   this.evacuatedTotalOption = tk.IntVar(value=evacuatedTotalOption and 1)
   this.evacuatedSessionOption = tk.IntVar(value=evacuatedSessionOption and 1)
   this.evacuatedSessionSelected = tk.IntVar(value=evacuatedSessionSelected and 1)
   this.blackBoxOption = tk.IntVar(value=blackBoxOption and 1)
   this.wreckageOption = tk.IntVar(value=wreckageOption and 1)
   this.occupiedPodOption = tk.IntVar(value=occupiedPodOption and 1)
   this.personalEffectsOption = tk.IntVar(value=personalEffectsOption and 1)
   this.damagedPodOption = tk.IntVar(value=occupiedPodOption and 1)
   this.prisonersOption = tk.IntVar(value=prisonersOption and 1)
   this.correspondenceOption = tk.IntVar(value=correspondenceOption and 1)
   this.sarSettings =[this.blackBoxOption.get(),
                 this.wreckageOption.get(),
                 this.occupiedPodOption.get(),
                 this.personalEffectsOption.get(),
                 this.damagedPodOption.get(),
                 this.prisonersOption.get(),
                 this.correspondenceOption.get()]
   return "EvacCount"

def getSettingsEvacuated():
    settings = json.loads(config.get("EvacCount_options") or "[1,1,1]")
    settingTotal = settings[0] # calculate total passengers evacuated
    settingSession = settings[1] # Calculate for session only
    settingSettingOption = settings[2] # 1 = ED Session, 0 = EDMC Session
    return settingTotal, settingSession, settingSettingOption

def updateCounts():
    for i in range(1,len(this.evacuatedLabels)):
        item,session, total = this.evacuatedLabels[i]
        if i == 1:
            session["text"] = "{0}".format(Locale.stringFromNumber(counts[i-1],0))
            total["text"] = "{0}".format(Locale.stringFromNumber(totals[i-1],0))
        elif this.sarSettings[i-1] == 1:
            session["text"] = "{0}".format(Locale.stringFromNumber(counts[i-1],0))
            total["text"] = "{0}".format(Locale.stringFromNumber(totals[i-1],0))


def journal_entry(cmdr, system, station, entry, state):
    if entry["event"] == "MissionAccepted":
        if entry["Name"] == "Mission_DS_PassengerBulk":
            #Figure out how we pick up passengers
            this.missions[entry["MissionID"]] = entry["PassengerCount"]
            config.set("EvacCount_missions", json.dumps(this.missions))
            print "Picked up", str(entry["PassengerCount"]), "passengers."
    elif entry["event"] == "MissionCompleted":
        if entry["Name"] == "Mission_DS_PassengerBulk_name":
            try:
                print "Just got", str(this.missions[entry["MissionID"]]),"passengers."
                this.counts[0] += this.missions[entry["MissionID"]] # Get correct ammount
                this.totals[0] += this.missions[entry["MissionID"]] # Get correct ammount
                config.set("EvacCount_totals", json.dumps(this.totals))

                del this.missions[entry["MissionID"]]
            except KeyError:
                print "You appear to have tried to hand in a mission which this plugin didn't know about"
            config.set("EvacCount_missions", json.dumps(this.missions))
            updateCounts()
    elif entry["event"] == "SearchAndRescue" :
        if entry["Name"] == "usscargoblackbox":
            this.counts[1] += entry["Count"] # Get correct ammount
            this.totals[1] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"black boxes."
            updateCounts()
        elif entry["Name"] == "wreckagecomponents":
            this.counts[2] += entry["Count"] # Get correct ammount
            this.totals[2] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"wreckage components."
            updateCounts()
        elif entry["Name"] == "occupiedcryopod":
            this.counts[3] += entry["Count"] # Get correct ammount
            this.totals[3] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"escape pods."
            updateCounts()
        elif entry["Name"] == "personaleffects":
            this.counts[4] += entry["Count"] # Get correct ammount
            this.totals[4] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"personal effects."
            updateCounts()
        elif entry["Name"] == "damagedescapepod":
            this.counts[5] += entry["Count"] # Get correct ammount
            this.totals[5] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"damaged pods."
            updateCounts()
        elif entry["Name"] == "politicalprisoner":
            this.counts[6] += entry["Count"] # Get correct ammount
            this.totals[6] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"political prisoners."
            updateCounts()
    elif entry["event"] == "CollectCargo":
        if entry["Name"] == "encryptedcorrespondence":
            this.counts[6] += entry["Count"] # Get correct ammount
            this.totals[6] += entry["Count"] # Get correct ammount
            config.set("EvacCount_totals", json.dumps(this.totals))
            print "Just got", str(entry["Count"]),"encrupted correspondence."
            updateCounts()
