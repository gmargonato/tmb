#desenvolvido por gmargonato
#inicio do projeto: 08/junho/2020

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
    lista_scripts = ("nada selecionado", "rook_psc", "cyc_thais","stonerefiner")
    selected = select("Selecione um script da lista","Seletor de Scripts", options = lista_scripts)

    global modulo
    
    if selected == lista_scripts[0]:
        popup("Voce nao escolheu nenhum script - Finalizando!")
        type('c', KeyModifier.CMD + KeyModifier.SHIFT)
        
    if selected == lista_scripts[1]:
        print "Script Selecionado: rook_psc"
        modulo = importlib.import_module("rook_psc")
        configs_script()
    
    if selected == lista_scripts[2]:
        print "Script Selecionado: cyc_thais"
        modulo = importlib.import_module("cyc_thais")
        configs_script()

    if selected == lista_scripts[3]:
        print "Script Selecionado: stonerefiner"
        modulo = importlib.import_module("stonerefiner")
        configs_script()

#configuracoes basicas do script importado
def configs_script():
    global loot; global drop; global wp_final; global equip_ring;
    loot = modulo.loot
    drop = modulo.drop
    wp_final = modulo.wp_final
    equip_ring = modulo.equip_ring

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
    #if statusBar.exists().type(poison_spell_htk)
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
        type(Key.SPACE)
        print "detectado monstro na tela, atacando"
        atacando(0)
        if loot == 1:
            if loot_type == "auto": loot_automatico()
            if loot_type == "manual": loot_manual()
        atacar()
 
##########################################################
#função verificar se estou atacando
def atacando(atkCount):

    vida()
    mana()
    
    if use_spell == 1: magia_atk(6)

    if atkCount > 30:
        type(Key.SPACE)
        print "[ATENCAO] trocando de alvo"
        wait(5)
        atacando(0)

    output = get_pixel_color(932,60)

    if (output == 'ff0000' or output == 'ff7f7d'): #vermelho ou vermelho-claro
        atkCount+=1
        wait(1)
        atacando(atkCount)

    if output == 'ffffff': #branco
       type(Key.SPACE)
       atacando(atkCount)
        
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
        vida() #enquanto anda, verifica a vida
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

wp = 1
use_spell = 0
loot_type = "auto"

seletor_scripts()
App.focus("Tibia")

#loop principal de execucao
while True:

    atacar()
    statusBar_check()
    
    if equip_ring == 1: check_ring()

    try:andar(wp)
    except:
        print "[ERRO] Waypoint", wp,"nao encontrado!"    
        pass

    #dropa o item no ultimo Wp
    if wp == wp_final and drop == 1: modulo.dropar()
    
    wp+=1
    if wp > wp_final: wp = 1
