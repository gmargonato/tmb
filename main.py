#desenvolvido por gmargonato
#inicio da construcao: 08/junho/2020

import os
import subprocess
import re
import importlib
import json
import datetime

Settings.ObserveScanRate = 10
Settings.MoveMouseDelay = 0
Settings.ActionLogs = 0

##########################################################
#funcao verificar cor de um pixel utilizando funcao em applescript
def get_pixel_color(posX,posY):   
    comando = "screencapture -R"+str(posX)+","+str(posY)+",1,1 -t bmp $TMPDIR/test.bmp && xxd -p -l 3 -s 54 $TMPDIR/test.bmp | sed 's/\\(..\\)\\(..\\)\\(..\\)/\\3\\2\\1/'"
    output = re.sub(r"\s+", "", os.popen(comando).read(), flags=re.UNICODE)
    return output

##########################################################
#Seletor de scripts com base no input do usuario
def seletor_scripts():
    lista_scripts = ("nada selecionado", "rook_psc", "cyc_thais","stonerefiner","forest_fury","rook_wasp")
    selected = select("Selecione um script da lista","Seletor de Scripts", options = lista_scripts)

    global script_selecionado
 
    if selected == lista_scripts[0]:
        popup("Voce nao escolheu nenhum script - Finalizando!")
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)
        
    if selected == lista_scripts[1]:
        script_selecionado = "rook_psc"
        configs_script()
    
    if selected == lista_scripts[2]:
        script_selecionado = "cyc_thais"
        configs_script()

    if selected == lista_scripts[3]:
        script_selecionado = "stonerefiner"
        configs_script()

    if selected == lista_scripts[4]:
        script_selecionado = "forest_fury"
        configs_script()   

    if selected == lista_scripts[5]:
        script_selecionado = "rook_wasp"
        configs_script()

#configuracoes basicas do script importado
def configs_script():
    global loot; global drop; global wp_final; global equip_ring;global modulo
    
    print "Script Selecionado:",script_selecionado        
    modulo = importlib.import_module(script_selecionado)     
    loot = modulo.loot
    drop = modulo.drop
    wp_final = modulo.wp_final
    equip_ring = modulo.equip_ring
    
##########################################################
def dropar():
    print "dropando items..."
    
    if script_selecionado == "rook_psc":
        if exists("smallaxe.png"):dropar_item("smallaxe.png","small axe")
        if exists("leatherhelmet.png"):dropar_item("leatherhelmet.png","leather helmet")
        if exists("spear.png"):dropar_item("spear.png","spear")
    if script_selecionado == "rook_wasp":
        if exists("1596220559045.png"): dropar_item("1596220559045.png","hatchet")
        if exists("1596220591667.png"): dropar_item("1596220591667.png","viking helmet")
        if exists("1596220607452.png"): dropar_item("1596220607452.png","studded shield")
        if exists("1596220626287.png"): dropar_item("1596220626287.png","bone")
        if exists("1596221479773.png"): dropar_item("1596221479773.png","studded helmet")
        if exists("1596221994953.png"): dropar_item("1596221994953.png","heavy tome")
        if exists("1596222023378.png"): dropar_item("1596222023378.png","studded armor")
        if exists(Pattern("1596223046626.png").similar(0.80)): dropar_item(Pattern("1596223046626.png").similar(0.80),"torch")
        if exists("1596223057218.png"): dropar_item("1596223057218.png","pelvis bone")
        if exists("1596223848531.png"): dropar_item("1596223848531.png","mace")
        

    print "todos os items dropados"

def dropar_item(sprite_item,item_name):
    #vida() #para curar minha vida enquanto estou dropando
    if exists(sprite_item):
        imageCount = len(list([x for x in findAll(sprite_item)]))
        for i in range(imageCount):
            print "dropando",item_name,i+1,"de",imageCount
            dragDrop(sprite_item, Location(550, 375))
            wait(1)
    else:return

##########################################################
#função recuperar a vida      
def vida():
    output = get_pixel_color(326,55)
    
    if output == "313131":
        #print "usando health potion"
        type(life_pot_htk) #40% da vida
        return
    else:
        output = get_pixel_color(460,55)
        if output == "2f2f2f":
            #print "usando heal spell"
            type(life_spell_htk) #85% da vida
            return
    
##########################################################
#função recuperar a mana
def mana():
    output = get_pixel_color(765,51)    
    if output != '004bb0': type(mana_pot_htk)
    
##########################################################
#função comer
def statusBar_check():

    statusBar = Region(499,82,106,13)
    
    if statusBar.exists("food.png"):type(food_htk)
    if statusBar.exists("poison.png"):type(poison_spell_htk)
    else: return

##########################################################
#função equipar ring
def check_ring():

    ring_slot = Region(1106,246,45,41)
    
    if ring_slot.exists(Pattern("ring_slot.png").exact()).highlight(1):
        print "equipando ring"
        type(ring_htk)
    else:return

##########################################################
#função pegar loot
def loot_automatico():
    print "pegando loot"
    #8 = print KeyModifier.ALT
    click(Location(500,315),8) 
    click(Location(550,315),8)
    click(Location(600,315),8)
    click(Location(600,365),8)
    click(Location(600,415),8)
    click(Location(555,410),8)
    click(Location(500,410),8)
    click(Location(505,365),8)
    click(Location(555,375),8)
    
def loot_manual():
    print "-nao implementado-"

##########################################################
def atacar():

    output = get_pixel_color(960,77)
    if output == "3f3f3f": 
        print "battlelist limpo"
        return
    
    else:
        print "detectado monstro na tela, atacando"
        type(Key.SPACE)        
        atacando()
        if loot == 1:
            if loot_type == "auto": loot_automatico()
            if loot_type == "manual": loot_manual()
        atacar()
 
##########################################################
#função verificar se estou atacando
def atacando():

    vida()
    mana()
    
    if use_spell == 1: magia_atk(6)
    
    output = get_pixel_color(932,60)

    if (output == 'ff0000' or output == 'ff7f7d'): #vermelho ou vermelho-claro
        wait(1)
        atacando()

    if output == 'ffffff': #branco
       type(Key.SPACE)
       atacando()
        
    else:return

##########################################################    
def magia_atk(cooldown):
    segundos = datetime.datetime.now().strftime("%S")
    segundos = int(segundos)
    if (segundos % cooldown == 0):type(atk_spell_htk)
    return
    
##########################################################
#função verificar se cheguei ao wp
def changeHandler(event):
    event.region.somethingChanged = True
    event.region.stopObserver()

def cheguei_wp(tempo_parado):
    while True:
        nav = Region(1111,47,110,115)
        nav.onChange(1,changeHandler)
        nav.somethingChanged = False
        nav.observe(1)
        
        if nav.somethingChanged:
            #estou andando
            tempo_parado = 0
            
        if not nav.somethingChanged:
            tempo_parado+=1
            
        if tempo_parado == 2:
            print "cheguei!"
            break
    
        continue

##########################################################
#tenta subir com corda ou escada
def executar_action(action): 
    if action == 1:
        type(rope_htk)
        click(Location(555,375))
        print "subindo com corda"
        
    if action == 2:
        click(Location(555,375))
        print "subindo com escada"

    if action == 3:

        if exists("hole_closed.png"):
            print "usando shovel"
            type(shovel_htk)
            click("hole_closed.png")
        if exists("hole_open.png"): click("hole_open.png")
    return  

##########################################################
#função andar para o proximo waypoint
def andar(wp):
    
    print "indo para waypoint:",wp
    action = modulo.hunt(wp)
    cheguei_wp(0)
    if action > 0: executar_action(action)
   
##########################################################
#######################   MAIN   #########################
##########################################################

#configuracoes
life_pot_htk = Key.F1
life_spell_htk = Key.F2
mana_pot_htk = Key.F3
atk_spell_htk = Key.F5
poison_spell_htk = Key.F10
food_htk = Key.F12

rope_htk = "o"
shovel_htk = "p"
ring_htk = "l"

wp = 4
use_spell = 0
loot_type = "auto"

seletor_scripts()
App.focus("Tibia")

#loop principal de execucao
while True:

    atacar()
    statusBar_check()
    atacar()
    
    if equip_ring == 1: check_ring()

    try:andar(wp)
    except:
        print "[ERRO] Waypoint", wp,"nao encontrado!"    
        pass

    #verificacoes no ultimo wp
    if wp == wp_final: 

        #verifica se deve dropar items
        if drop == 1: dropar()
        
        #verifica se deve sair da hunt
        try: print "verificando status..."; modulo.check_exit()
        except: print "metodo check_exit nao existe!";pass
    
    wp+=1
    if wp > wp_final: wp = 1
