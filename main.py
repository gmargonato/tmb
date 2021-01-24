#Gamemaster's Bot

#library imports
import os
import subprocess
import re
import math
import importlib
import json
import threading
import shutil
from datetime import *
from random import *
from javax.swing import JFrame, JButton, JLabel, JScrollPane, JTextArea, JPanel, JButton
from java.awt import BorderLayout,GridLayout,GridBagConstraints,GridBagLayout,FlowLayout,Dimension,Robot, Color
from sikuli import *

#basic settings
Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0
Settings.InfoLogs = 0
Settings.DebugLogs = 0

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
walk_interval = 2

#tools
rope   = "o"  
shovel = "p"
ring   = "l"
amulet = "k"
food   = "u"

#spells
exana_pox = "i"
haste = "v"
utura = "5"
min_to_box = 1
min_to_align = 1

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
game_region     = Region(226,124,474,348)
equip_region    = Region(1109,308,113,163)
life_bar_region = Region(9,48,910,32)

#GAME REGION INFORMATIONS
#center
gr_center_x = game_region.getCenter().getX()
gr_center_y = game_region.getCenter().getY()

#top left corner
gr_tlc_x = game_region.getTopLeft().getX()
gr_tlc_y = game_region.getTopLeft().getY()

#top right corner
gr_trc_x = game_region.getTopRight().getX()
gr_trc_y = game_region.getTopRight().getY()

#bottom left corner
gr_blc_x = game_region.getBottomLeft().getX()
gr_blc_y = game_region.getBottomLeft().getY()

#bottom right corner
gr_brc_x = game_region.getBottomRight().getX()
gr_brc_y = game_region.getBottomRight().getY()

screen_proportion = gr_brc_y/gr_trc_y

# x1y1 , x2y1 , x3y1
# x1y2 , x2y2 , x3y2
# x1y3 , x2y3 , x3y3

x1 = gr_center_x - (screen_proportion*10)
x2 = gr_center_x
x3 = gr_center_x + (screen_proportion*10)

y1 = gr_center_y - (screen_proportion*10)
y2 = gr_center_y
y3 = gr_center_y + (screen_proportion*10)

#BATTLE LIST INFORMATIONS
battlelist = find("battlelist.png")

bl_tlc_x = battlelist.getTopLeft().getX()
bl_tlc_y = battlelist.getTopLeft().getY()

bl_slot1_x = bl_tlc_x + 26
bl_slot1_y = bl_tlc_y + 33

battlelist_region = Region(bl_tlc_x,bl_tlc_y,40,200)

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
def pixelColor(posX,posY):   
    pixel = Robot().getPixelColor(posX,posY)
    r = pixel.getRed()
    g = pixel.getGreen() 
    b = pixel.getBlue() 
    color = '{:02x}{:02x}{:02x}'.format(r,g,b)
    return color

#to be used exclusively by the healer thread
def healerColor(posX,posY):
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
    
    if equip_region.exists("battleon.png"):
        log("Battle icon on - Waiting 30 secs")
        attack_function()
        wait(30)
        log("Trying to logoff again...")
        logoff_function()
        
    else:
        log("Printing Screen")
        type("3", KeyModifier.CMD + KeyModifier.SHIFT)
        type("l", KeyModifier.CMD)
        log("[END OF EXECUTION]")
        closeFrame(0)

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

    #moves the cursor back to the center of the screen
    hover(Location(gr_center_x,gr_center_y))

    #checks if the char has stopped is still walking
    walking_check(0,wp_action,label,wp)
    
    return wp_action
 
def walking_check(time_stopped,wp_action,label,wp):
    while time_stopped != walk_interval:
        minimap_region = Region(1109,161,115,119)
        minimap_region.onChange(1,changeHandler)
        minimap_region.somethingChanged = False
        minimap_region.observe(1)
        
        #if enters here, means char is still walking
        if minimap_region.somethingChanged:
            time_stopped = 0
            while equip_region.exists("paralysed.png",0): 
                type(haste)
                wait(0.5)
            
            #verifies if it should engage combat while walking
            if label == "hunt" and lure_mode == 0: 
                slot1 = pixelColor(bl_slot1_x,bl_slot1_y)
                if slot1 == "000000":
                    log("Mob detected on battle list while walking")
                    type(Key.ESC)
                    wait(0.5)
                    attack_function()
                    if running == 1: waypointer(label,wp)
                else: pass
                
            #in case shouldn't engane combat
            else: pass
        
        #if nothing changes on the screen for some time, add 1 to stopped timer
        if not minimap_region.somethingChanged:
            time_stopped+=1
            log("Walking "+str(time_stopped)+"/"+str(walk_interval)+" seconds")

        continue
    else: return

#function to verify if something is changing on screen
def changeHandler(event):
    event.region.somethingChanged = True
    event.region.stopObserver()

#wp_action list:
        #1: use rope
        #2: use ladder
        #3: use shovel

def waypoint_action(wp_action): 
    if wp_action == 1:
        type(rope)
        click(Location(gr_center_x,gr_center_y))
        log("Using rope")
        
    if wp_action == 2:
        click(Location(gr_center_x,gr_center_y))
        log("Using ladder")
        
    if wp_action == 3:
        type(shovel)
        click(Location(gr_center_x,gr_center_y))
        log("Using shovel")    
        
    wait(1)
    return

###############################################################################
   ###    ######## ########    ###     ######  ##    ## #### ##    ##  ######   
  ## ##      ##       ##      ## ##   ##    ## ##   ##   ##  ###   ## ##    ##  
 ##   ##     ##       ##     ##   ##  ##       ##  ##    ##  ####  ## ##        
##     ##    ##       ##    ##     ## ##       #####     ##  ## ## ## ##   #### 
#########    ##       ##    ######### ##       ##  ##    ##  ##  #### ##    ##  
##     ##    ##       ##    ##     ## ##    ## ##   ##   ##  ##   ### ##    ##  
##     ##    ##       ##    ##     ##  ######  ##    ## #### ##    ##  ######   
###############################################################################

def attack_function():

    type(Key.SPACE)
    wait(0.3)
    attacking()

    #checks for new mob on screen
    slot1 = pixelColor(bl_slot1_x,bl_slot1_y)
    if slot1 == "000000" and running == 1: attack_function()
    
    else:
        log("Battle list clear")
        if loot_type == 3: 
            melee_looter()
            if game_region.exists("valuable_loot.png",0):
                log("[ATTENTION] Valuable loot dropped")
                melee_looter()
        if drop_vials == 2: drop_item_vial()

        return
    
def attacking(): 
   
    battlelist_region.waitVanish("bl_target.png",30) #waits for 30 seconds before switching mob
    
    #after mob is dead:
    
    if loot_type == 1: 
        melee_looter()
        if game_region.exists("valuable_loot.png",0): 
            log("[ATTENTION] Valuable loot dropped")
            melee_looter()
        
    elif loot_type == 2 and game_region.exists("valuable_loot.png",0):
        log("[ATTENTION] Valuable loot dropped")
        melee_looter()
        melee_looter()

    else: return

#################################################################
##        #######   #######  ######## ######## ######## ########  
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ##       ##     ## 
##       ##     ## ##     ##    ##       ##    ######   ########  
##       ##     ## ##     ##    ##       ##    ##       ##   ##   
##       ##     ## ##     ##    ##       ##    ##       ##    ##  
########  #######   #######     ##       ##    ######## ##     ## 
#################################################################

#loot_type = 0 -> ignore loot
#loot_type = 1 -> loot everything
#loot_type = 2 -> loot only valuable
#loot_type = 3 -> loot only after clearing the battle list (best used with lure mode)

def melee_looter():
    log("Looting around char")
    click(Location(x1,y1),8)    
    click(Location(x2,y1),8)
    click(Location(x3,y1),8)
    click(Location(x1,y2),8)  
    click(Location(x2,y2),8)
    click(Location(x3,y2),8)
    click(Location(x1,y3),8)    
    click(Location(x2,y3),8)
    click(Location(x3,y3),8)

#######################################################
##     ##  #######  ######## ##    ## ######## ##    ## 
##     ## ##     ##    ##    ##   ##  ##        ##  ##  
##     ## ##     ##    ##    ##  ##   ##         ####   
######### ##     ##    ##    #####    ######      ##    
##     ## ##     ##    ##    ##  ##   ##          ##    
##     ## ##     ##    ##    ##   ##  ##          ##    
##     ##  #######     ##    ##    ## ########    ##    
#######################################################

#function to prevent being exhausted
def sendHotkey(actionList):
    
    #                0        1       2       3
    #actionList = ["name","hotkey","group",cooldown]
    
    global lastHeal
    global lastObj
    global lastSupp

    now = datetime.now()
               
    if actionList[2] == "heal":
    
        diff = (now - lastHeal).total_seconds()
        if diff >= actionList[3]:
            log("Casting heal spell \'"+actionList[0]+"\'")
            type(actionList[1])        
            lastHeal = datetime.now()

    elif actionList[2] == "object":
    
        diff = (now - lastObj).total_seconds()
        if diff >= actionList[3]:
            log("Using item \'"+actionList[0]+"\'")
            type(actionList[1])        
            lastObj = datetime.now()
        
    #                0        1       2       3        4
    #actionList = ["name","hotkey","group",cooldown,last_cast]
    elif actionList[2] == "atk":
    
        diff = (now - actionList[4]).total_seconds()
        if diff >= actionList[3]:
            log("Casting attack spell \'"+actionList[0]+"\'")    
            type(actionList[1])
            actionList[4] = datetime.now()
            sleep(2)
        else: return

    else: return
            
#############################################################
##     ## ########    ###    ##       #### ##    ##  ######   
##     ## ##         ## ##   ##        ##  ###   ## ##    ##  
##     ## ##        ##   ##  ##        ##  ####  ## ##        
######### ######   ##     ## ##        ##  ## ## ## ##   #### 
##     ## ##       ######### ##        ##  ##  #### ##    ##  
##     ## ##       ##     ## ##        ##  ##   ### ##    ##  
##     ## ######## ##     ## ######## #### ##    ##  ######   
#############################################################

#Healing
def healer_function(arg):
    while running == 1:

        if running == 0: break

        if vocation == 0:

            life = healerColor(15,55)
            if life == "bc8900" or life == "b01a20": 
                sendHotkey(light_heal) 
                if life == "b01a20":
                    img = capture(Screen().getBounds())
                    shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+str(session_id)+'_red_life.png'))
       
            sleep(1)
            continue
            
        else:

            life = healerColor(15,55)
            if life == "b01a20": 
                sendHotkey(intense_heal)
                sendHotkey(emergency_heal)  
                img = capture(Screen().getBounds())
                shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+session_id+"/"+str(int(time.time()))+"_red"+".png"))
                continue
            
            mana = healerColor(660,71)
            if mana != "00266d": sendHotkey(mana_pot)  
            
            if life == "bc8900": sendHotkey(intense_heal)         
            if life == "5a9200": sendHotkey(light_heal)  

    else: print "Ending healer thread"

def startHealerThread():
    healer_thread = threading.Thread(target=healer_function, args = (0,))
    if healer_thread.isAlive() == False:
        print "Starting healer thread"
        healer_thread.start()
    else: 
        print "[ERROR] Healer thread already running"
    
################################################################################
########    ###    ########   ######   ######## ######## #### ##    ##  ######   
   ##      ## ##   ##     ## ##    ##  ##          ##     ##  ###   ## ##    ##  
   ##     ##   ##  ##     ## ##        ##          ##     ##  ####  ## ##        
   ##    ##     ## ########  ##   #### ######      ##     ##  ## ## ## ##   #### 
   ##    ######### ##   ##   ##    ##  ##          ##     ##  ##  #### ##    ##  
   ##    ##     ## ##    ##  ##    ##  ##          ##     ##  ##   ### ##    ##  
   ##    ##     ## ##     ##  ######   ########    ##    #### ##    ##  ######       
################################################################################

#Targeting Spell  
def spell_caster_function(arg):
    while running == 1:  
        if battlelist_region.exists("bl_target.png",0):            
            if stay_diagonal == 1: near_targets("diagonal")

            #logic to cast atk spells
            for atk_spell in atk_spells: 

                #if its a box spell, call near_targets as mode = BOX
                spell_box_list = ["exori","exori gran"]    
                if atk_spell[0] in spell_box_list:
                    isBoxSpell = 1
                    green_light = near_targets("box")

                #if is not a box spell, but it is an spell that requeires mob alignment, call near_targets as mode = ALIGN
                elif atk_spell[0] == "exori min":
                    isBoxSpell = 1
                    green_light = near_targets("align")
                    
                else: isBoxSpell = 0
        
                if (isBoxSpell) == 0 or (isBoxSpell == 1 and green_light == 1): 
                   sendHotkey(atk_spell)
            
            if running == 0: break
        else: wait("bl_target.png",FOREVER)
    
    else: print "Ending spell caster thread"

def startSpellCasterThread():
    spell_cast_thread = threading.Thread(target=spell_caster_function, args = (0,))
    if spell_cast_thread.isAlive() == False:
        print "Starting spell caster thread"
        spell_cast_thread.start()
    else: 
        print "[ERROR] Spell caster thread already running"
    
#checks for targets around the character
def near_targets(mode):

    #                    preto    verde  vd-claro  amarelo
    life_bar_colors = ["000000","0aba00","4eb949","b3b800"]

    #1 2 3
    #4 c 5
    #6 7 8

    xm1 = 432 
    xm2 = 463 
    xm3 = 496
    
    ym1 = 246
    ym2 = 278
    ym3 = 310
    
    pos1aux = (xm1,ym1)
    pos1 = pixelColor(pos1aux[0],pos1aux[1])
    
    pos2aux = (xm2,ym1)
    pos2 = pixelColor(pos2aux[0],pos2aux[1])

    pos3aux = (xm3,ym1)
    pos3 = pixelColor(pos3aux[0],pos3aux[1])
    
    pos4aux = (xm1,ym2)
    pos4 = pixelColor(pos4aux[0],pos4aux[1])
    
    pos5aux = (xm3,ym2)
    pos5 = pixelColor(pos5aux[0],pos5aux[1])
    
    pos6aux = (xm1,ym3)
    pos6 = pixelColor(pos6aux[0],pos6aux[1]) 
    
    pos7aux = (xm2,ym3)
    pos7 = pixelColor(pos7aux[0],pos7aux[1])
    
    pos8aux = (xm3,ym3)
    pos8 = pixelColor(pos8aux[0],pos8aux[1])
    
    ######################
    if mode == "box":

        #count number of targets around
        targets_around = 0
        if pos1 in life_bar_colors: targets_around += 1   
        if pos2 in life_bar_colors: targets_around += 1
        if pos3 in life_bar_colors: targets_around += 1
        if pos4 in life_bar_colors: targets_around += 1
        if pos5 in life_bar_colors: targets_around += 1                
        if pos6 in life_bar_colors: targets_around += 1        
        if pos7 in life_bar_colors: targets_around += 1       
        if pos8 in life_bar_colors: targets_around += 1
        
        if targets_around >= min_to_box:
            return 1
        else: return 0
        
    ######################
    elif mode == "align":
        
        align_top = 0
        if pos1 in life_bar_colors: align_top += 1
        if pos2 in life_bar_colors: align_top += 1
        if pos3 in life_bar_colors: align_top += 1

        if align_top >= min_to_align: 
            type(Key.UP, KeyModifier.CMD)
            return 1

        align_right = 0
        if pos3 in life_bar_colors: align_right += 1
        if pos5 in life_bar_colors: align_right += 1
        if pos8 in life_bar_colors: align_right += 1

        if align_right >= min_to_align:
            type(Key.RIGHT, KeyModifier.CMD)
            return 1

        align_bottom = 0
        if pos6 in life_bar_colors: align_bottom += 1
        if pos7 in life_bar_colors: align_bottom += 1
        if pos8 in life_bar_colors: align_bottom += 1

        if align_bottom >= min_to_align:
            type(Key.DOWN, KeyModifier.CMD)
            return 1

        align_left = 0
        if pos1 in life_bar_colors: align_left += 1
        if pos4 in life_bar_colors: align_left += 1
        if pos6 in life_bar_colors: align_left += 1

        if align_left >= min_to_align:
            type(Key.LEFT, KeyModifier.CMD)
            return 1

    ######################
    elif mode == "diagonal":
        
        if (pos2 in life_bar_colors or pos7 in life_bar_colors): 
            walk = randint(1,2)
            if walk == 1: type(Key.LEFT)
            if walk == 2: type(Key.RIGHT)
            return 0
        
        elif (pos4 in life_bar_colors or pos5 in life_bar_colors): 
            walk = randint(1,2)
            if walk == 1: type(Key.UP)
            if walk == 2: type(Key.DOWN)
            return 0
        
        else: return 0

    #other modes
    else: return 0    

####################################################################
########  ########   #######  ########  ########  ######## ########  
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ##     ## ##     ## ##     ## ##     ## ##       ##     ## 
##     ## ########  ##     ## ########  ########  ######   ########  
##     ## ##   ##   ##     ## ##        ##        ##       ##   ##   
##     ## ##    ##  ##     ## ##        ##        ##       ##    ##  
########  ##     ##  #######  ##        ##        ######## ##     ## 
####################################################################

def drop_item_vial():
    log("Searching for vials to drop...")
    drop_item(Pattern("small_flask.png").exact(),"small empty flask")
    drop_item(Pattern("strong_flask.png").exact(),"strong empty flask")
    drop_item(Pattern("great_flask.png").exact(),"great empty flask")

def drop_item(sprite,name):
    if exists(sprite,0):
        imageCount = len(list([x for x in findAll(sprite)]))
        for i in range(imageCount):
            log("Dropping "+name+" "+str(i+1)+"/"+str(imageCount))
            dragDrop(sprite, Location(gr_center_x,gr_center_y))
            wait(0.5)
    else: return
    
#################################################################
########  ######## ########  ##     ## ######## ########  ######  
##     ## ##       ##     ## ##     ## ##       ##       ##    ## 
##     ## ##       ##     ## ##     ## ##       ##       ##       
##     ## ######   ########  ##     ## ######   ######    ######  
##     ## ##       ##     ## ##     ## ##       ##             ## 
##     ## ##       ##     ## ##     ## ##       ##       ##    ## 
########  ######## ########   #######  ##       ##        ######  
#################################################################

def status_check():
    log("Checking debuffs...")
    if exists(Pattern("utura_spell.png").exact(),0) or exists(Pattern("utura_gran_spell.png").exact(),0): type(utura)
    #while equip_region.exists("paralysed.png",0): type(haste)
    #while equip_region.exists("food.png",0): type(food)
    #while equip_region.exists("poison.png",0): type(exana_pox)
    if (equip_ring == 1 and equip_region.exists("ring.png",0)): type(ring)
    if (equip_amulet == 1 and equip_region.exists("amulet.png",0)): type (amulet)
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
            "Rook Mino Hell",
            "Rook PSC",
            "Ab Wasp Cave",
            "Venore Amazon Camp",
            "Edron Earth Cave",
            "Darashia Dragons",
            "Formorgar Mines Cults",
            "Krailos Bug Cave -1",
            "Laguna Island",
            "Sea Serpents North",
            "Yalahar Mutated Tigers",
            "Nibelor Crystal Cave -2",
            "Carlin Cults -1",
            "Krailos Knightmare Ruins",
            "Hero Fortress -2",
            "Edron Vampire Crypt",
            "Lb Braindeaths",
            "Ape City -1",
            "Port Hope Giant Spiders",
            "Muggy Plains Brimstone Bugs",
            "Zao Mutated Tigers (Fire Portal)",
            "Sea Serpents South",
            "Lb Wyrm Cave"
            
    )
    prompt = select("Please select a script from the list","Available Scripts", options = script_list, default = script_list[0])

    global selected_script
    
    if   prompt == script_list[1]: selected_script = "mino_hell" 
    elif prompt == script_list[2]: selected_script = "rook_psc"
    elif prompt == script_list[3]: selected_script = "ab_wasp"
    elif prompt == script_list[4]: selected_script = "amazon_camp"
    elif prompt == script_list[5]: selected_script = "bog_raider_edron"
    elif prompt == script_list[6]: selected_script = "darashia_dragons"
    elif prompt == script_list[7]: selected_script = "formorgar_cults"
    elif prompt == script_list[8]: selected_script = "krailos_bug_cave"
    elif prompt == script_list[9]: selected_script = "laguna_island"
    elif prompt == script_list[10]: selected_script = "sea_serpent_n"
    elif prompt == script_list[11]: selected_script = "ylr_mut_tiger"
    elif prompt == script_list[12]: selected_script = "ice_golem"
    elif prompt == script_list[13]: selected_script = "carlin_cults"
    elif prompt == script_list[14]: selected_script = "krailos_undead_cave"
    elif prompt == script_list[15]: selected_script = "edron_hero" 
    elif prompt == script_list[16]: selected_script = "vampire_crypt" 
    elif prompt == script_list[17]: selected_script = "lb_braindeath" 
    elif prompt == script_list[18]: selected_script = "ape_city"
    elif prompt == script_list[19]: selected_script = "port_hope_gs"
    elif prompt == script_list[20]: selected_script = "mp_brimstone"
    elif prompt == script_list[21]: selected_script = "zao_mut_tiger"
    elif prompt == script_list[22]: selected_script = "sea_serpent_s"
    elif prompt == script_list[23]: selected_script = "lb_wyrm_cave"
    else:
        popup("The selected script is not valid, terminating execution")
        closeFrame(0)
        raise Exception("Invalid Script")
       
    log("Selected Script: "+selected_script)

    global imported_script
    
    global vocation      
    global loot_type     
    global lure_mode  
    global equip_ring    
    global equip_amulet  
    global drop_vials    
    global stay_diagonal 
    global take_distance 
    
    global light_heal    
    global intense_heal  
    global emergency_heal
    global mana_pot   
    
    global atk_spells
    
    global minimap_zoom
    global last_hunt_wp
    global last_leave_wp
    global last_go_hunt_wp
    
    #imports the script that will be executed on this session
    imported_script = importlib.import_module(selected_script)
    
    vocation      = imported_script.vocation
    loot_type     = imported_script.loot_type                                              
    lure_mode     = imported_script.lure_mode
    equip_ring    = imported_script.equip_ring
    equip_amulet  = imported_script.equip_amulet
    drop_vials    = imported_script.drop_vials
    stay_diagonal = imported_script.stay_diagonal
    take_distance = imported_script.take_distance

    #heal
    light_heal     = imported_script.light_heal
    intense_heal   = imported_script.intense_heal
    emergency_heal = imported_script.emergency_heal
    mana_pot       = imported_script.mana_pot
    
    #atk
    atk_spells = imported_script.atk_spells

    minimap_zoom    = imported_script.minimap_zoom
    last_hunt_wp    = imported_script.last_hunt_wp
    last_leave_wp   = imported_script.last_leave_wp
    last_go_hunt_wp = imported_script.last_go_hunt_wp
    
###############################################
######## ########     ###    ##     ## ######## 
##       ##     ##   ## ##   ###   ### ##       
##       ##     ##  ##   ##  #### #### ##       
######   ########  ##     ## ## ### ## ######   
##       ##   ##   ######### ##     ## ##       
##       ##    ##  ##     ## ##     ## ##       
##       ##     ## ##     ## ##     ## ######## 
###############################################

#receives a message and print it into jframe
def log(message):
    textArea.append(str(datetime.now().strftime("%H:%M:%S.%f")[:-4])+" - "+str(message)+"\n")
    textArea.setCaretPosition(textArea.getDocument().getLength())

def closeFrame(event):
    global running
    running = 0
    frame.dispose()

#generates frame
frame = JFrame("Game Master\'s Bot - Console Log")
frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE)
frame.setResizable(False)
frame.setAlwaysOnTop(True)
frame.setBounds(8,545,600,130)
frame.contentPane.layout = FlowLayout()

#add stop button
quitButton = JButton("QUIT", actionPerformed = closeFrame)
quitButton.setForeground(Color.RED)
quitButton.setPreferredSize(Dimension(100,100))
frame.contentPane.add(quitButton)

#add text message
textArea = JTextArea(6,38)
textArea.setEditable(False)
frame.contentPane.add(textArea)
scrollPane = JScrollPane(textArea, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
frame.contentPane.add(scrollPane)

#show frame
frame.pack()
frame.setVisible(True)
log("Welcome to Game Master\'s Bot!")

##############################################
 ######  ########    ###    ########  ######## 
##    ##    ##      ## ##   ##     ##    ##    
##          ##     ##   ##  ##     ##    ##    
 ######     ##    ##     ## ########     ##    
      ##    ##    ######### ##   ##      ##    
##    ##    ##    ##     ## ##    ##     ##    
 ######     ##    ##     ## ##     ##    ##    
##############################################

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

#generates an ID for this session, and creates a folder
session_id = str(datetime.now().strftime("%d%m%Y%H%M"))
log("Session ID: "+str(session_id))
log("Starting at "+label+" waypoint "+str(wp))
log("[ATTENTION] Walk interval is set to "+str(walk_interval)+" seconds")

#If game client exists, focus on it. Else, throws exception
if(App("Tibia").isRunning() == True): App.focus("Tibia")
else:
    frame.dispose()
    raise Exception('Tibia client is not running')

#shows ping on game screen
if not exists(Pattern("ping.png").similar(0.50),0): type(Key.F8, KeyModifier.ALT)

#adjusts the starting minimap zoom for this session
def adjust_minimap_zoom():
    #subtract zoom
    for i in range(0,3):
        click(Location(1240,246))
    
    #add zoom
    for i in range(0,minimap_zoom):
        click(Location(1240,227))

log("Adjusting minimap zoom to "+str(minimap_zoom))
adjust_minimap_zoom()

#last cast time for heals, objects and spells alike
lastObj  = datetime.now()
lastHeal = datetime.now()   
for atk_spell in atk_spells:
    atk_spell.append(datetime.now())

#start threads
running = 1
startHealerThread()
if vocation > 0: startSpellCasterThread()

###########################################################################
##     ##    ###    #### ##    ##    ##        #######   #######  ########  
###   ###   ## ##    ##  ###   ##    ##       ##     ## ##     ## ##     ## 
#### ####  ##   ##   ##  ####  ##    ##       ##     ## ##     ## ##     ## 
## ### ## ##     ##  ##  ## ## ##    ##       ##     ## ##     ## ########  
##     ## #########  ##  ##  ####    ##       ##     ## ##     ## ##        
##     ## ##     ##  ##  ##   ###    ##       ##     ## ##     ## ##        
##     ## ##     ## #### ##    ##    ########  #######   #######  ##        
###########################################################################

#Main
while running == 1:
 
    if label == "hunt": 
        slot1 = pixelColor(bl_slot1_x,bl_slot1_y)
        if slot1 == "000000": 
            log("Mob detected on battle list")
            attack_function()
        if vocation > 0: status_check()

    if running == 0: closeFrame(0);break
    
    try: 
        wp_action = waypointer(label,wp)
        #verifies if should perform some action when reaches destination
        if wp_action > 0: waypoint_action(wp_action)
            
        #After arriving at destination waypoint
        log("Arrived at "+label+" waypoint "+str(wp))
        
        #########################################
        #current waypoint is the last one for hunt
        if (label == "hunt" and wp >= last_hunt_wp):

            attack_function()

            #check if should drop vials
            if drop_vials > 0: drop_item_vial()
            
            #check if it should leave the hunt
            log("Checking exit hunt conditions...")
            label = imported_script.exit_conditions()

            #reset waypoint back to 1
            wp = 1
               
            #prints the screen after a sucessfull run and saves it
            log("Printing session")            
            if not os.path.exists("/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+session_id):
                os.makedirs("/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+session_id)

            img = capture(Screen().getBounds())
            shutil.move(img,os.path.join(r"/Users/GabrielMargonato/Downloads/SIKULI/SESSIONS/"+session_id+"/"+str(int(time.time()))+".png"))
    
        ##########################################
        #current waypoint is the last one for leave
        elif label == "leave" and wp >= last_leave_wp:
            logoff_function()
            
        ##########################################
        #current waypoint is the last one for go_hunt
        elif label == "go_hunt" and wp >= last_go_hunt_wp:
            log("Setting label to Hunt")
            label = "hunt"
            wp = 1
            
        ##########################################
        #no criterea matched
        else: 
            wp+=1
    except:
        log("[ERROR] waypoint "+label+" "+str(wp)+" not found!")
        #move to next waypoint
        if (label == "go_hunt" and wp > last_go_hunt_wp) or (label == "hunt" and wp > last_hunt_wp) or (label == "leave" and wp > last_leave_wp): 
            adjust_minimap_zoom()
            wp = 1
        else: wp+=1

else: popup("END")
#end
