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
#life
htk_greenHealth  = "1"
htk_yellowHealth = Key.F1
htk_redHealth    = Key.F3

#mana
htk_mana_pot     = "3"

#tools
htk_food         = Key.F12
htk_rope         = "o"
htk_shovel       = "p"
htk_ring         = "l"

#spells
htk_poison_spell = Key.F10
htk_target_spell = "2"
htk_area_spell   = "f"
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
statusbar_region  = Region(1111,335,110,14)
battlelist_region = Region(929,60,34,187)
warning_region    = Region(658,440,34,14)
game_region       = Region(401,105,478,350)
valuable_region   = Region(360,732,546,41)

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
    textArea.append(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S - "))+str(message)+"\n")
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

#applescript function that returns the color of 1 exact pixel on the screen
def get_pixel_color(posX,posY):   
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    return color

#to be used exclusively by the healer thread
def get_mana_health_color(posX,posY):
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    #DEBUG: print "getManaHealthColor:",posX,posY,color
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

#Exit condition: Leave hunt in case stamina in no longer green
def exit_on_low_stamina():
    returned_color = get_pixel_color(14,332)
    if returned_color != "00ff00":
        label = "leave"
    else: label = "hunt"

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
        minimap_region    = Region(1111,47,110,115)
        minimap_region.onChange(1,changeHandler)
        minimap_region.somethingChanged = False
        minimap_region.observe(1)
        
        #if enters here, means char is still walking
        if minimap_region.somethingChanged:
            
            time_stopped = 0
            
            #verifies if it should engage combat while walking
            if label == "hunt" and lure_mode == 0: 
                battleList = get_pixel_color(941,70)
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

ok_health     = '09a600'
green_health  = '528400'
yellow_health = 'aa7c00'
red_health    = '9f191e'
ok_mana       = '002362'
not_ok_mana   = '20201f'

def healer_function(arg):
    while stop_threads == 0:
        
        #defines exhaust for objects (pot) and spells
        exhaustedPot   = 0
        exhaustedSpell = 0
        
        #check health and mana pixel colors
        health_color = get_mana_health_color(365,60)
        
        #if the script is runnnig for non-vocation, checks just health and continue
        if vocation == 0:
            if health_color == yellow_health: 
                log("[TARGETING] Using small health potion...")
                type(htk_yellowHealth)            
                wait(1)
            continue
        
        #if script is running for any other vocation
        else:

            mana_color = get_mana_health_color(735,60)
            
            #print "Cor da mana", mana_color
            if mana_color == not_ok_mana: 
                log("[HEALER] Using mana potion")
                type(htk_mana_pot)
                exhaustedPot = 1

            #print "Cor da vida", health_color
            if health_color == red_health:
                log("[HEALER] Using health potion")
                if exhaustedPot == 1: wait(1)
                type(htk_redHealth)
                exhaustedPot = 1

            mana_color = get_mana_health_color(735,60)
    
            if health_color == yellow_health and mana_color == ok_mana:
                log("[HEALER] Casting intense heal spell")
                type(htk_yellowHealth)
                exhaustedSpell = 1
            
            if health_color == green_health and mana_color == ok_mana:
                if exhaustedSpell == 1: wait(1)
                type(htk_greenHealth)
                exhaustedSpell = 1

            #if exhaustedPot == 1 or exhaustedSpell == 1: wait(1)
            continue
    
    #terminating Thread        
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
    log("Mob detected on screen")
    type(Key.SPACE)
    attacking()
    #checks for new mob on screen
    battleList = get_pixel_color(941,70)
    if battleList != "323232": attack_function()
    else:
        log("Battle list clear")
        return
    
def attacking(): 
    log("Attacking mob...")
    battlelist_region.waitVanish("atk_small.png",30) #waits for 30 seconds before switching mob
    if loot_type == 0: return
    elif loot_type == 1: melee_looter()
    elif loot_type == 2 and valuable_region.exists("valuable_loot.png",0):
        melee_looter();melee_looter()
    else: return

#attack spell caster
def spell_caster_function(arg):
    while stop_threads == 0:
        while battlelist_region.exists("atk_small.png"):

            #casts recovery
            type(Key.htk_utura)

            #casts target spell
            type(htk_target_spell); wait(2)
            
            #casts area spell            
            if lure_mode == 1:
                targets_around = 0
                pos1 = get_pixel_color(595,228)
                if pos1 == "000000": targets_around += 1
                pos2 = get_pixel_color(627,228)
                if pos2 == "000000": targets_around += 1
                pos3 = get_pixel_color(659,228)
                if pos3 == "000000": targets_around += 1
                pos4 = get_pixel_color(595,260)
                if pos4 == "000000": targets_around += 1
                pos5 = get_pixel_color(659,260)
                if pos5 == "000000": targets_around += 1
                pos6 = get_pixel_color(595,292)
                if pos6 == "000000": targets_around += 1
                pos7 = get_pixel_color(627,292)
                if pos7 == "000000": targets_around += 1
                pos8 = get_pixel_color(659,292)
                if pos8 == "000000": targets_around += 1
                if targets_around >= 4: 
                    log("[TARGETING] Casting area spell "+str(targets_around))
                    type(htk_area_spell)
                
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
        if exists(Pattern("empty_ring.png").exact(),0):type(htk_ring)
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
            "[RK] Poison Spider",
            "[RK] Mino Hell",
            "[EK] Venore Amazon Camp",
            "[EK] Ab Wasp Cave",
            "[EK] Ice Golems"
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    if prompt == script_list[1]: selected_script = "rook_psc"
    elif prompt == script_list[2]: selected_script = "mino_hell"
    elif prompt == script_list[3]: selected_script = "amazon_camp"
    elif prompt == script_list[4]: selected_script = "ab_wasp"
    elif prompt == script_list[5]: selected_script = "ice_golem"
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
    global vocation
    global minimap_zoom
    global last_hunt_wp
    global last_leave_wp
    global last_go_hunt_wp
    
    log("[CORE] Selected Script: "+selected_script)

    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
    
    #read variables from imported script
    loot_type          = imported_script.loot_type
    lure_mode          = imported_script.lure_mode
    equip_ring         = imported_script.equip_ring
    drop_vials         = imported_script.drop_vials
    vocation           = imported_script.vocation

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
    #reset zoom
    click(Location(1240,128))
    click(Location(1240,128))
    click(Location(1240,128))
    
    #adjust to selected
    for i in range(0,minimap_zoom):
        click(Location(1240,110))
             
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

frame = JFrame("Console Log")
frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
frame.setBounds(358,562,560,130)
contentPane = JPanel()
frame.setContentPane(contentPane)
buttonQ = JButton("QUIT", actionPerformed = closeFrame)
buttonQ.setForeground(Color.RED)
frame.add(buttonQ,NORTH)
textArea = JTextArea(5,44)
textArea.setEditable(False)
contentPane.add(textArea)
scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
contentPane.add(scrollPane)
frame.setUndecorated(True)
frame.setAlwaysOnTop(True)
frame.setVisible(True)
log("[CORE] Initializing bot")

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

#set focus on game client
App.focus("Tibia")
                
#shows ping on game screen
type(Key.F8, KeyModifier.ALT)

#adjusts the minimap zoom
set_minimap_zoom(minimap_zoom)

#sets session channel
if loot_type >= 1: click(Pattern("loot_channel.png").similar(0.69))
else: click("log_channel.png")

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

    #makes console frame appear ([BUG] it may vanish after a while)
    #frame.visible = True
    
    if label == "hunt": 
        battleList = get_pixel_color(941,70)
        if battleList != "323232": attack_function()
        #statusBar_check()
    
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
        wp+=1
        pass

#end
