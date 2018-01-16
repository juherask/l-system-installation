# basic drawing with pygame:
#  http://lorenzod8n.wordpress.com/2007/05/27/pygame-tutorial-2-drawing-lines/
#  http://stackoverflow.com/questions/326300/python-best-library-for-drawing
#
# L-systems:
#  http://en.wikipedia.org/wiki/L-system
#  http://blog.rabidgremlin.com/2014/12/09/procedural-content-generation-l-systems/

from pygame import *
import math
from random import choice, randint, gammavariate 

import threading
import serial
import pygame


MAX_WIND_STRENGTH = 5
MAX_ANGLE = 120
MAX_SIZE = 30  
MAX_ITERATIONS_TIMES = 2  

running = False
port = '/dev/ttyUSB0'
baud = 9600
serial_port = serial.Serial(port, baud, timeout=0.01)

process_cmd = 0
parameter_values = [512]*4
parameter_string = "Not yet recieved any"

def read_from_port(ser):
    global parameter_values, process_cmd, running
    try:
        while running:
            cmd = ser.read().decode()
            if cmd == "n" or cmd == "u":
                reading = ser.readline().decode()
                
                if process_cmd==0:
                    parameter_values = [int(r) for r in reading[1:].split(";")]
                    process_cmd = ord(cmd)
                else:
                    # note: readings are lost if the previous command 
                    #  has not been processed
                    pass
    except e:
        print("Serial communication failure", e)
        

MAX_PLANT_SYSTEM_SIZE = 500000

def get_predefined_system(system_nbr):
    if system_nbr==1:
        # Pythagoras Tree
        rules = {
          "F":"FF",
          "X":"F[+X]-X"}
        start = "X"
        size = 7
        iterations = 6
    
    elif system_nbr==2:
        # Wikipedia Tree (Tree F)
        start = "X"
        rules = {
          "X":"F-[[X]+X]+F[+FX]-X",
          "F":"FF"}
        size = 10
        iterations = 4
    
    elif system_nbr==3:
        # Tree A
        start = "F"
        rules = {
          "F":"F[+F]F[-F]F"}
        size = 5
        iterations = 4
    
    elif system_nbr==4:
        # Tree B
        start = "F"
        rules = {"F":"F[+F]F[-F][F]"}
        size = 7
        iterations = 5
    
    elif system_nbr==5:
        # Tree C
        start = "F"
        rules = {"F":"FF-[-F+F+F]+[+F-F-F]"}
        size = 7
        iterations = 4
    
    elif system_nbr==6:
        # Tree D
        start = "X"
        rules = {"F":"FF", "X":"F[+X]F[-X]+X" }
        size = 2
        iterations = 7
    
    elif system_nbr==7:
        # Tree E
        start = "X"
        rules = {"F":"FF", "X":"F[+X][-X]FX"}
        size = 2
        iterations = 7
        
    return start, rules, size, iterations

def generate_random_system():
    start = choice(["X","F"]*10+["+","-"])
    rules = {}
    for ri in range(randint(1,6)):
        # todo: add also [ ] but then balance
        fromsym = choice(["X","F"]*3+["+","-"])
        if fromsym in rules:
            continue

        rand_rule_len = 1+int(4*gammavariate(2.0, 1.0))
        print rand_rule_len
        tosym = ""
        tail = []
        for ri in range(rand_rule_len):
            # we let the rulette choose from the tail also 
            #  to increase the probability of pop to avoid
            #  all the pops happen at the tail
            nextsym = choice(["X","F","+","-","[","]"]+tail)
            if nextsym=="[":
                tail.append("]")
            elif nextsym=="]":
                if len(tail)>0:
                    tail = tail[:-1]
                else:
                    # would produce empty stack popping plants
                    continue
            tosym+=nextsym
        tosym+="".join(tail)
        
        # remove useless combinations
        prevto = None
        while not prevto or len(prevto)>len(tosym):
            print "try"
            prevto=tosym
            tosym = tosym.replace("[]","")
        
        rules[fromsym]=tosym

    size = randint(2,11)
    iterations = randint(4,11-size/2)
    return start, rules, size, iterations
                        
# define a function that is used to grow l-systems
def grow_Lsystem(start, rules, depth):
    if len(start)>MAX_PLANT_SYSTEM_SIZE:
        return start
    if depth==0:
        return start
    output = ""
    for l in start:
        if l in rules:
            output+=rules[l]
        else:
            output+=l
    return grow_Lsystem(output, rules, depth-1)

# define a function that is used to plot
def draw_Lsystem(instructions, angle, surface, start=(100,100),
                 base_length=10,
                 wind_strength=1.0, branch_momentum=1.05, wind_phase=0.0):
    cur_pos, cur_angle = (start, -90)
    stack = []
    stack.append( (cur_pos, cur_angle) )

    for cmd in instructions:
        depth = len(stack)
        angle_offset = wind_strength*depth*\
                        math.sin(wind_phase+depth*branch_momentum)
        if cmd=="F":
            dx = math.cos(cur_angle/360.0*2*math.pi)*base_length
            dy = math.sin(cur_angle/360.0*2*math.pi)*base_length
            end_pos = tuple(map(sum, zip(cur_pos,(dx,dy))))
            draw.line( surface, (100,225,100), cur_pos, end_pos )
            cur_pos=end_pos
        elif cmd=="X":
            pass #leaf, nop
        elif cmd=="[":
            stack.append( (cur_pos, cur_angle) )
        elif cmd=="]":
            cur_pos, cur_angle = stack.pop()
            if len(stack)==0: # for robustness
                stack.append( (cur_pos, cur_angle) )
        elif cmd=="+":
            cur_angle+=angle+angle_offset
        elif cmd=="-":
            cur_angle+=-angle+angle_offset

def interactive_display(predefined_system_number):
    global parameter_string, process_cmd, running
        
    # Start a thread that reads physical controls (over serial)
    running = True
    thread = threading.Thread(target=read_from_port, args=(serial_port,))
    thread.start()

    # Init pygame
    init()
    screen = display.set_mode( (400,600) )
    display.set_caption("L-Systems, press 1-7 to select")
 
    myfont = pygame.font.SysFont("monospace", 15)
    
    start, rules, size, iterations = get_predefined_system(predefined_system_number)
    plant = grow_Lsystem(start, rules, iterations).replace("X","F")
    base_iterations = iterations
    prev_iterations = iterations
    wind_phase = 0.0
    
    wind_strength = 1.5
    angle = 25
    size = 10
    
    while True:
        label = myfont.render(parameter_string, 1, (0,0,0))
        screen.blit(label, (100, 100))
        pygame.display.flip()

        for ev in event.get():
            if ev.type == QUIT:
                running = False
                sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_1:
                    start, rules, size, iterations = get_predefined_system(1)
                if ev.key == K_2:
                    start, rules, size, iterations = get_predefined_system(2)
                if ev.key == K_3:
                    start, rules, size, iterations = get_predefined_system(3)
                if ev.key == K_4:
                    start, rules, size, iterations = get_predefined_system(4)
                if ev.key == K_5:
                    start, rules, size, iterations = get_predefined_system(5)
                if ev.key == K_6:
                    start, rules, size, iterations = get_predefined_system(6)
                if ev.key == K_7:
                    start, rules, size, iterations = get_predefined_system(7)
                if ev.key == K_r:
                    start, rules, size, iterations = generate_random_system()
                    print start, rules, size, iterations 
                    
                # Grow plant in case system changed
                plant = grow_Lsystem(start, rules, iterations).replace("X","F")
                print len(plant)
                
                base_iterations = iterations
                prev_iterations = iterations
        
        # a command from the serial!        
        if process_cmd!=0:
            cmd = chr(process_cmd)
            parameter_string = cmd+" / "+" ".join( ("%.2f"%(pv/1024.0))
                                            for pv in parameter_values)
            process_cmd = 0
            
            wind_strength = (parameter_values[0]/1024.0)*MAX_WIND_STRENGTH
            angle = (parameter_values[1]/1024.0)*MAX_ANGLE
            size = (parameter_values[2]/1024.0)*MAX_SIZE
            iterations = int((parameter_values[3]/1024.0)*
                                base_iterations*MAX_ITERATIONS_TIMES)
            
            if prev_iterations!=iterations:
                plant = grow_Lsystem(start, rules, iterations).replace("X","F")
                prev_iterations = iterations
                
        # Empty screen
        screen.fill(color.THECOLORS["black"])
  
        # Plot plant
        draw_Lsystem(plant, angle, screen, (200,590), size,
            wind_strength=wind_strength, wind_phase=wind_phase)
        wind_phase+=0.01*wind_strength
        display.flip()
        

if __name__=="__main__":
    import sys
    first_system_nbr = 1
    if (len(sys.argv)>1):
        first_system_nbr = int(sys.argv[1]) 
    
    interactive_display(first_system_nbr)        


