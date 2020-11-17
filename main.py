#TMB - Tibia Mac Bot

#library imports
import os
import subprocess
import re
import math
import importlib
import json
import threading
from datetime import *
from random import *
from javax.swing import JFrame, JButton, JLabel, JScrollPane, JTextArea, JPanel, JButton
from java.awt.BorderLayout import *
from java.awt import Robot, Color
from sikuli import *

#basic sikuli configurations
Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0

############################################################
 ######   #######  ##    ## ######## ####  ######    ######  
##    ## ##     ## ###   ## ##        ##  ##    ##  ##    ## 
##       ##     ## ####  ## ##        ##  ##        ##       
##       ##     ## ## ## ## ######    ##  ##   ####  ######  
##       ##     ## ##  #### ##        ##  ##    ##        ## 
##    ## ##     ## ##   ### ##        ##  ##    ##  ##    ## 
 ######   #######  ##    ## ##       ####  ######    ######  
############################################################

#in case ping latency is too high, increase the waiting time (use only integer values)
global walk_lag_delay 
walk_lag_delay = 2

#center of screen
global screen_center_x
global screen_center_y
screen_center_x = 640
screen_center_y = 280

#hotkey presets

#tools
htk_food         = Key.F12
htk_rope         = "o"
htk_shovel       = "p"
htk_ring         = "l"

#spells
htk_poison_spell = Key.F10
htk_utura        = "5"

#############################################################
########  ########  ######   ####  #######  ##    ##  ######  
##     ## ##       ##    ##   ##  ##     ## ###   ## ##    ## 
##     ## ##       ##         ##  ##     ## ####  ## ##       
########  ######   ##   ####  ##  ##     ## ## ## ##  ######  
##   ##   ##       ##    ##   ##  ##     ## ##  ####       ## 
##    ##  ##       ##    ##   ##  ##     ## ##   ### ##    ## 
##     ## ########  ######   ####  #######  ##    ##  ######  
#############################################################

#watchable regions
statusbar_region  = Region(1111,451,110,15)
battlelist_region = Region(1104,469,30,120)
warning_region    = Region(658,440,34,14)
game_region       = Region(401,105,478,350)
valuable_region   = Region(360,732,546,41)
ammo_region       = Region(1184,394,37,36)
ring_region       = Region(1111,394,34,34)

##########################################################################
########  ########  #### ##    ## ########    ##        #######   ######   
##     ## ##     ##  ##  ###   ##    ##       ##       ##     ## ##    ##  
##     ## ##     ##  ##  ####  ##    ##       ##       ##     ## ##        
########  ########   ##  ## ## ##    ##       ##       ##     ## ##   #### 
##        ##   ##    ##  ##  ####    ##       ##       ##     ## ##    ##  
##        ##    ##   ##  ##   ###    ##       ##       ##     ## ##    ##  
##        ##     ## #### ##    ##    ##       ########  #######   ######     
##########################################################################

#receives a message and print it onto jframe
def log(message):
    textArea.append(str(datetime.now().strftime("%H:%M:%S.%f - "))+str(message)+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())

#############################################################################################
########  #### ##     ## ######## ##           ######   #######  ##        #######  ########  
##     ##  ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##     ## 
##     ##  ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##     ## 
########   ##     ###    ######   ##          ##       ##     ## ##       ##     ## ########  
##         ##    ## ##   ##       ##          ##       ##     ## ##       ##     ## ##   ##   
##         ##   ##   ##  ##       ##          ##    ## ##     ## ##       ##     ## ##    ##  
##        #### ##     ## ######## ########     ######   #######  ########  #######  ##     ##
#############################################################################################

#returns the color (HEX) of one exact pixel on the screen
def get_pixel_color(posX,posY):   
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    return color

#to be used exclusively by the healer thread
def get_healer_color(posX,posY):
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    #print "Color at",posX,posY,":",color
    return color

###########################################################
##        #######   ######       #######  ######## ######## 
##       ##     ## ##    ##     ##     ## ##       ##       
##       ##     ## ##           ##     ## ##       ##       
##       ##     ## ##   ####    ##     ## ######   ######   
##       ##     ## ##    ##     ##     ## ##       ##       
##       ##     ## ##    ##     ##     ## ##       ##       
########  #######   ######       #######  ##       ##       
###########################################################

def logoff_function():
    
    if statusbar_region.exists("battleon.png"):
        log("Battle icon on - Waiting 30 secs")
        wait(30)
        log("Trying to logoff again...")
        logoff_function()
        
    else:
        log("Printing Screen")
        type("3", KeyModifier.CMD + KeyModifier.SHIFT)
        type("l", KeyModifier.CMD)
        log("[END OF EXECUTION]")
        stop_threads = 1
        type("c", KeyModifier.CMD + KeyModifier.SHIFT)

###########################################################################################
##      ##    ###    ##    ## ########   #######  #### ##    ## ######## ######## ########  
##  ##  ##   ## ##    ##  ##  ##     ## ##     ##  ##  ###   ##    ##    ##       ##     ## 
##  ##  ##  ##   ##    ####   ##     ## ##     ##  ##  ####  ##    ##    ##       ##     ## 
##  ##  ## ##     ##    ##    ########  ##     ##  ##  ## ## ##    ##    ######   ########  
##  ##  ## #########    ##    ##        ##     ##  ##  ##  ####    ##    ##       ##   ##   
##  ##  ## ##     ##    ##    ##        ##     ##  ##  ##   ###    ##    ##       ##    ##  
 ###  ###  ##     ##    ##    ##         #######  #### ##    ##    ##    ######## ##     ## 
###########################################################################################

#function to walk to next waypoint
def waypointer(label,wp):
    log("Walking to "+label+" waypoint "+str(wp)) 
    if label == "go_hunt":
        wp_action = imported_script.label_go_hunt(wp)
    
    if label == "hunt":
        wp_action = imported_script.label_hunt(wp)
        
    if label == "leave":
        wp_action = imported_script.label_leave(wp)

    #moves mouse back to center of screen 
    hover(Location(screen_center_x,screen_center_y))

    #checks if the Char has stopped or continues walking
    walking_check(0,wp_action,label,wp)
    
    return wp_action
 
def walking_check(time_stopped,wp_action,label,wp):
    while time_stopped != walk_lag_delay:
        minimap_region    = Region(1109,161,115,119)
        minimap_region.onChange(1,changeHandler)
        minimap_region.somethingChanged = False
        minimap_region.observe(1)
        
        #if enters here, means char is still walking
        if minimap_region.somethingChanged:
            
            time_stopped = 0
            
            #verifies if it should engage combat while walking
            if label == "hunt" and lure_mode == 0: 
                battleList = get_pixel_color(1117,495)
                if battleList != "323232":
                    type(Key.ESC)
                    wait(0.5)
                    attack_function()
                    waypointer(label,wp)
                else: pass
                
            #in case shouldn't engane combat
            else: pass
        
        #if nothing changes on the screen for some time, add 1 to stopped timer
        if not minimap_region.somethingChanged:
            time_stopped+=1

        continue
    else: return

#sikuli default function to verify if something is changing on screen
def changeHandler(event):
    event.region.somethingChanged = True
    event.region.stopObserver()
    
####################################################################################
##      ## ########        ###     ######  ######## ####  #######  ##    ##  ######  
##  ##  ## ##     ##      ## ##   ##    ##    ##     ##  ##     ## ###   ## ##    ## 
##  ##  ## ##     ##     ##   ##  ##          ##     ##  ##     ## ####  ## ##       
##  ##  ## ########     ##     ## ##          ##     ##  ##     ## ## ## ##  ######  
##  ##  ## ##           ######### ##          ##     ##  ##     ## ##  ####       ## 
##  ##  ## ##           ##     ## ##    ##    ##     ##  ##     ## ##   ### ##    ## 
 ###  ###  ##           ##     ##  ######     ##    ####  #######  ##    ##  ######  
####################################################################################

#wp_action list:
        #0: indicates its a normal waypoint
        #1: use rope
        #2: use ladder
        #3: use shovel

def waypoint_action(wp_action): 
    if wp_action == 1:
        type(htk_rope)
        click(Location(screen_center_x,screen_center_y))
        log("Using rope")
        
    if wp_action == 2:
        click(Location(screen_center_x,screen_center_y))
        log("Using ladder")
        
    if wp_action == 3:
        type(htk_shovel)
        click(Location(screen_center_x,screen_center_y))
        log("Using shovel")    
        
    wait(1)
    return

########################################################    
##     ## ########    ###    ##       ######## ########  
##     ## ##         ## ##   ##       ##       ##     ## 
##     ## ##        ##   ##  ##       ##       ##     ## 
######### ######   ##     ## ##       ######   ########  
##     ## ##       ######### ##       ##       ##   ##   
##     ## ##       ##     ## ##       ##       ##    ##  
##     ## ######## ##     ## ######## ######## ##     ##
########################################################

bad_color = ("1b2953","1b2853")

def healer_function(arg):
    while stop_threads == 0:

        if vocation == 0:
            life40 = get_healer_color(1175,281)
            if life40 in bad_color:
                log("[HEALER] Using small health potion")
                type(Key.F1)
            wait(1)
            continue
            
        else:

            exhaustedPot  = 0
            exhustedSpell = 0

            life40 = get_healer_color(1155,281)
            if life40 in bad_color:
                log("[HEALER] Using life potion")
                type(Key.F3)
                exhaustedPot = 1

            mana50 = get_healer_color(1175,294)
            if mana50 in bad_color:
                if exhaustedPot == 1: wait(1)
                log("[HEALER] using mana potion")
                type("3")
                exhaustedPot = 1

            life80 = get_healer_color(1190,281)
            if life80 in bad_color:
                log("[HEALER] using intense heal spell")
                type(Key.F1)
                exhaustedSpell = 1

            wait(1)
            continue
        
    else: print "Ending healer thread"
   
def startHealerThread():
    healer_thread = threading.Thread(target=healer_function, args = (0,))
    if healer_thread.isAlive() == False:
        print "Starting healer thread"
        healer_thread.start()
    else: 
        print "Healer thread already running"

stop_threads = 0

########################################################
########    ###    ########   ######   ######## ######## 
   ##      ## ##   ##     ## ##    ##  ##          ##    
   ##     ##   ##  ##     ## ##        ##          ##    
   ##    ##     ## ########  ##   #### ######      ##    
   ##    ######### ##   ##   ##    ##  ##          ##    
   ##    ##     ## ##    ##  ##    ##  ##          ##    
   ##    ##     ## ##     ##  ######   ########    ##   
########################################################

def attack_function():
    log("Monster detected on Battle List")
    type(Key.SPACE)
    attacking()
    #checks for new mob on screen
    battleList = get_pixel_color(1117,495)
    if battleList != "323232": attack_function()
    else:
        log("Battle list clear")
        return
    
def attacking(): 
    battlelist_region.waitVanish("atk_small.png",30) #waits for 30 seconds before switching mob
    if loot_type == 1: 
        melee_looter()
        if valuable_region.exists("valuable_loot.png",0): melee_looter()
    elif loot_type == 2 and valuable_region.exists("valuable_loot.png",0):
        melee_looter();melee_looter()
    else: return

#checks for targets around character
def near_targets(mode):

    #1 2 3
    #4 c 5
    #6 7 8

    pos1 = get_pixel_color(595,228)
    pos2 = get_pixel_color(627,228)
    pos3 = get_pixel_color(659,228)
    pos4 = get_pixel_color(595,260)    
    pos5 = get_pixel_color(659,260)
    pos6 = get_pixel_color(595,292)
    pos7 = get_pixel_color(627,292)
    pos8 = get_pixel_color(659,292)

    if mode == "box":
        
        targets_around = 0
      
        if pos1 == "000000": targets_around += 1   
        if pos2 == "000000": targets_around += 1
        if pos3 == "000000": targets_around += 1
        if pos4 == "000000": targets_around += 1
        if pos5 == "000000": targets_around += 1                
        if pos6 == "000000": targets_around += 1        
        if pos7 == "000000": targets_around += 1       
        if pos8 == "000000": targets_around += 1
        
        if targets_around >= 4: 
            log("[TARGETING] Casting box spell")
            type("f")
            wait(2)
            return

    if mode == "front":
        
        if (pos1 == "000000" and pos2 == "000000" and pos3 == "000000"):
            type(Key.UP, KeyModifier.CMD)
            log("[TARGETING] Casting front spell (Up)")
            type("g")
            wait(2)
            return
        
        elif (pos1 == "000000" and pos4 == "000000" and pos6 == "000000"): 
            type(Key.LEFT, KeyModifier.CMD)
            log("[TARGETING] Casting front spell (Left)")
            type("g")
            wait(2)
            return
        
        elif (pos6 == "000000" and pos7 == "000000" and pos8 == "000000"):
            type(Key.DOWN, KeyModifier.CMD)
            log("[TARGETING] Casting front spell (Down)")
            type("g")
            wait(2)
            return
        
        elif (pos3 == "000000" and pos5 == "000000" and pos8 == "000000"):
            type(Key.RIGHT, KeyModifier.CMD)
            log("[TARGETING] Casting front spell (Right)")
            wait(2)
            type("g")
            
        else: return

    if mode == "diagonal":
        
        if (pos2 == "000000" or pos7 == "000000"): 
            walk = randint(1,2)
            if walk == 1: type(Key.LEFT)
            if walk == 2: type(Key.RIGHT)
            return
        elif (pos4 == "000000" or pos5 == "000000"): 
            walk = randint(1,2)
            if walk == 1: type(Key.UP)
            if walk == 2: type(Key.DOWN)
            return
        else: return
    
    if mode == "distance":
        
        #mob on top
        if (pos1 == "000000" or pos2 == "000000" or pos3 == "000000"): 
            type(Key.DOWN)
            walk = randint(1,2)
            if walk == 1: type(Key.LEFT)
            if walk == 2: type(Key.RIGHT)
            return
        
        #mob on the left
        elif (pos1 == "000000" or pos4 == "000000" or pos6 == "000000"): 
            type(Key.RIGHT)
            walk = randint(1,2)
            if walk == 1: type(Key.UP)
            if walk == 2: type(Key.DOWN)
            return
            
        #mob on the right
        elif (pos3 == "000000" or pos5 == "000000" or pos8 == "000000"): 
            type(Key.LEFT)
            walk = randint(1,2)
            if walk == 1: type(Key.UP)
            if walk == 2: type(Key.DOWN)
            return
            
        #mob at bottom
        elif (pos6 == "000000" or pos7 == "000000" or pos8 == "000000"): 
            type(Key.UP)
            walk = randint(1,2)
            if walk == 1: type(Key.LEFT)
            if walk == 2: type(Key.RIGHT)
            return

        else: return

#attack spell caster
def spell_caster_function(arg):
    while stop_threads == 0:
        while battlelist_region.exists("atk_small.png"):

            #checks if must refill ammo
            if refill_ammo == 1: 
                while ammo_region.exists("arrow.png",0): 
                    log("Refilling ammo")
                    type("r")
                    wait(0.5)

            if stay_diagonal == 1: near_targets("diagonal")
            if take_distance == 1: near_targets("distance")

            #casts recovery
            type(htk_utura)
                       
            #casts area spell            
            if lure_mode == 1:

                near_targets("box")
                near_targets("front")

            #casts target spell
            type("2"); wait(2)

            if stop_threads == 0: break
                                      
    else: print "Ending spell caster thread"

def startSpellCasterThread():
    spell_cast_thread = threading.Thread(target=spell_caster_function, args = (0,))
    if spell_cast_thread.isAlive() == False:
        print "Starting spell caster thread"
        spell_cast_thread.start()
    else: 
        print "Spell caster thread already running"
  
#################################################################
##        #######   #######  ######## ######## ######## ########  
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ######   ########  
##       ##     ## ##     ##    ##       ##    ##       ##   ##   
##       ##     ## ##     ##    ##       ##    ##       ##    ##  
########  #######   #######     ##       ##    ######## ##     ## 
#################################################################

#loot_type = 0 -> dont loot
#loot_type = 1 -> loot everything
#loot_type = 2 -> loot only valuable

def ranged_looter():
    log("Looting at mouse position")
    click(atMouse(),8)
    wait(3)

def melee_looter():
    log("Looting around char")
    click(Location(605,250),8) #1
    click(Location(640,250),8) #2
    click(Location(670,250),8) #3
    click(Location(606,280),8) #8
    click(Location(640,280),8) #9
    click(Location(670,280),8) #4
    click(Location(605,312),8) #7
    click(Location(640,312),8) #6
    click(Location(670,312),8) #5

    #moves mouse back to center of screen 
    hover(Location(screen_center_x,screen_center_y))


####################################################################
########  ########   #######  ########  ########  ######## ########  
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ########  ##     ## ########  ########  ######   ########  
##     ## ##   ##   ##     ## ##        ##        ##       ##   ##   
##     ## ##    ##  ##     ## ##        ##        ##       ##    ##  
########  ##     ##  #######  ##        ##        ######## ##     ## 
####################################################################

def drop_item(sprite,name):
    if exists(sprite,0):
        imageCount = len(list([x for x in findAll(sprite)]))
        for i in range(imageCount):
            log("Dropping "+name+" "+str(i+1)+"/"+str(imageCount))
            dragDrop(sprite, Location(screen_center_x,screen_center_y))
            wait(1)
    else: return
    
########################################################################################
 ######  ########    ###    ######## ##     ##  ######     ########     ###    ########  
##    ##    ##      ## ##      ##    ##     ## ##    ##    ##     ##   ## ##   ##     ## 
##          ##     ##   ##     ##    ##     ## ##          ##     ##  ##   ##  ##     ## 
 ######     ##    ##     ##    ##    ##     ##  ######     ########  ##     ## ########  
      ##    ##    #########    ##    ##     ##       ##    ##     ## ######### ##   ##   
##    ##    ##    ##     ##    ##    ##     ## ##    ##    ##     ## ##     ## ##    ##  
 ######     ##    ##     ##    ##     #######   ######     ########  ##     ## ##     ## 
########################################################################################

def status_bar_check():
    if statusbar_region.exists("food.png",0):type(htk_food)
    if statusbar_region.exists("poison.png",0):type(htk_poison_spell)
    if equip_ring == 1:
        if ring_region.exists("ring.png",0):
            log("Equipping ring")
            type(htk_ring)
    else:return
    
#########################################################################
 ######  ######## ##       ########  ######  ########  #######  ########  
##    ## ##       ##       ##       ##    ##    ##    ##     ## ##     ## 
##       ##       ##       ##       ##          ##    ##     ## ##     ## 
 ######  ######   ##       ######   ##          ##    ##     ## ########  
      ## ##       ##       ##       ##          ##    ##     ## ##   ##   
##    ## ##       ##       ##       ##    ##    ##    ##     ## ##    ##  
 ######  ######## ######## ########  ######     ##     #######  ##     ##
#########################################################################
    
def script_selector_function():
    script_list = (
            "-nothing selected-",
            ">>BLESS MAKER<<",
            "[NV] Poison Spider",
            "[NV] Mino Hell",
            "[EK] Venore Amazon Camp",
            "[EK] Ab Wasp Cave",
            "[EK] Meriana Island",
            "[RP] Sea Serpents",
            "[EK] Formorgar Cults",
            "[EK] Darashia Dragons"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    if prompt == script_list[1]: selected_script = "bless"
    elif prompt == script_list[2]: selected_script = "rook_psc"
    elif prompt == script_list[3]: selected_script = "mino_hell"
    elif prompt == script_list[4]: selected_script = "amazon_camp"
    elif prompt == script_list[5]: selected_script = "ab_wasp"
    elif prompt == script_list[6]: selected_script = "meriana"
    elif prompt == script_list[7]: selected_script = "sea_serpents"
    elif prompt == script_list[8]: selected_script = "formorgar_cults"
    elif prompt == script_list[9]: selected_script = "darashia_dragons"
    else:
        popup("The selected script is not valid, terminating execution")
        log("[END OF EXECUTION] No Script was selected!")
        closeFrame(0)
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)

    script_loader(selected_script)

#loads basic configuration from selected script
def script_loader(selected_script):

    global imported_script
    global loot_type
    global lure_mode
    global equip_ring
    global drop_vials
    global refill_ammo
    global stay_diagonal
    global take_distance
    global vocation
    global minimap_zoom
    global last_hunt_wp
    global last_leave_wp
    global last_go_hunt_wp
    
    log("[CORE] Selected Script: "+selected_script)

    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
    
    #read variables from imported script
    loot_type     = imported_script.loot_type
    lure_mode     = imported_script.lure_mode
    equip_ring    = imported_script.equip_ring
    drop_vials    = imported_script.drop_vials
    refill_ammo   = imported_script.refill_ammo
    stay_diagonal = imported_script.stay_diagonal
    take_distance = imported_script.take_distance
    vocation      = imported_script.vocation

    minimap_zoom    = imported_script.minimap_zoom
    last_hunt_wp    = imported_script.last_hunt_wp
    last_leave_wp   = imported_script.last_leave_wp
    last_go_hunt_wp = imported_script.last_go_hunt_wp
    
##########################################################
##     ## #### ##    ## #### ##     ##    ###    ########  
###   ###  ##  ###   ##  ##  ###   ###   ## ##   ##     ## 
#### ####  ##  ####  ##  ##  #### ####  ##   ##  ##     ## 
## ### ##  ##  ## ## ##  ##  ## ### ## ##     ## ########  
##     ##  ##  ##  ####  ##  ##     ## ######### ##        
##     ##  ##  ##   ###  ##  ##     ## ##     ## ##        
##     ## #### ##    ## #### ##     ## ##     ## ##        
##########################################################

def set_minimap_zoom(minimap_zoom):
    log("[CORE] Adjusting minimap zoom to "+str(minimap_zoom))
    #subtract zoom
    for i in range(0,3):
        click(Location(1240,246))
    
    #add zoom
    for i in range(0,minimap_zoom):
        click(Location(1240,227))
             
###############################################
######## ########     ###    ##     ## ######## 
##       ##     ##   ## ##   ###   ### ##       
##       ##     ##  ##   ##  #### #### ##       
######   ########  ##     ## ## ### ## ######   
##       ##   ##   ######### ##     ## ##       
##       ##    ##  ##     ## ##     ## ##       
##       ##     ## ##     ## ##     ## ######## 
###############################################

def closeFrame(event):
    global stop_threads
    stop_threads = 1
    frame.dispose()

def quitBot(event):
    sys.exit()

frame = JFrame("Console Log")
frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
frame.setBounds(358,22,560,70)
contentPane = JPanel()
frame.setContentPane(contentPane)

buttonS = JButton("STOP", actionPerformed = closeFrame)
buttonS.setForeground(Color.ORANGE)
frame.add(buttonS,WEST)

#buttonQ = JButton("QUIT", actionPerformed = quitBot)
#buttonQ.setForeground(Color.RED)
#frame.add(buttonQ,WEST)

textArea = JTextArea(4,38)
textArea.setEditable(False)
contentPane.add(textArea)
scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
contentPane.add(scrollPane)
frame.setUndecorated(True)
frame.setAlwaysOnTop(True)
frame.pack()
frame.setVisible(True)
log("[CORE] Initializing bot")
log("[ATTENTION] Walk interval is set to "+str(walk_lag_delay)+" seconds")

###############################################
############### BOT STARTS HERE ###############
###############################################
#calls script selector
script_selector_function()

#starting label
label = select("Please select a starting point","Available Starting Points", options = ("go_hunt","hunt","leave"), default = "go_hunt")

#starting waypoint number
if label == "go_hunt":
    available_wps = list(range(1,last_go_hunt_wp+1))
    
if label == "hunt":
    available_wps = list(range(1,last_hunt_wp+1))

if label == "leave":
    available_wps = list(range(1,last_leave_wp+1))

list_of_wps = map(str, available_wps)
wp_str = select("Choose a starting waypoint",label, list_of_wps, default = 0)
wp = int(wp_str)
log("[CORE] Starting at "+label+" waypoint "+str(wp))

#variable to count number of not-found waypoints during execution
wp_errors = 0

#set focus on game client
App.focus("Tibia")
                
#shows ping on game screen
type(Key.F8, KeyModifier.ALT)

#adjusts the minimap zoom
set_minimap_zoom(minimap_zoom)

#sets session channel
if loot_type >= 1: click("loot_channel.png")
else: click("server_log_channel.png")

#start thereads
startHealerThread()
if vocation != 0: startSpellCasterThread()

##################################################################
 ######     ###    ##     ## ######## ########   #######  ######## 
##    ##   ## ##   ##     ## ##       ##     ## ##     ##    ##    
##        ##   ##  ##     ## ##       ##     ## ##     ##    ##    
##       ##     ## ##     ## ######   ########  ##     ##    ##    
##       #########  ##   ##  ##       ##     ## ##     ##    ##    
##    ## ##     ##   ## ##   ##       ##     ## ##     ##    ##    
 ######  ##     ##    ###    ######## ########   #######     ##    
##################################################################

#Main
while stop_threads == 0:

    #[BUG] makes console frame re-appear (it may vanish after a while)
    #frame.visible = True
    
    if label == "hunt": 
        battleList = get_pixel_color(1117,495)
        if battleList != "323232": attack_function()
        #status_bar_check()
    
    try: 
        wp_action = waypointer(label,wp)
        #verifies if should perform some action when reaches destination
        if wp_action > 0:
            waypoint_action(wp_action)
            
        #After arriving at destination waypoint
        log("Arrived at "+label+" waypoint "+str(wp))
        
        #########################################
        #current waypoint is the last one for hunt
        if (label == "hunt" and wp >= last_hunt_wp):
            #check if it should leave the hunt
            log("[CORE] Checking for exit conditions...")
            label = imported_script.check_exit()
            wp = 1
            if drop_vials == 1: 
                log("[CORE] Dropping vials...")
                drop_item(Pattern("small_flask.png").exact(),"small empty flask")
                drop_item(Pattern("strong_flask.png").exact(),"strong empty flask")
    
        ##########################################
        #current waypoint is the last one for leave
        elif label == "leave" and wp >= last_leave_wp:
            logoff_function()
            
        ##########################################
        #current waypoint is the last one for go_hunt
        elif label == "go_hunt" and wp >= last_go_hunt_wp:
            log("[CORE] Setting label to Hunt")
            label = "hunt"
            wp = 1
            
        ##########################################
        #no criterea matched
        else: 
            wp+=1
    except:
        log("[ERROR] Waypoint "+str(wp)+" not found for "+label)
        wp_errors += 1
        print "WP errors:",wp_errors
        wp+=1
        pass

else: popup("END")
#end
