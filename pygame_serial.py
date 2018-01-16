import threading
import serial
import pygame

running = False
port = '/dev/ttyUSB0'
baud = 9600
serial_port = serial.Serial(port, baud, timeout=0.01)

background_colour = (255,255,255)
width, height = (640, 480)

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
        

def main():
    global parameter_string, process_cmd, running
        
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('L-system')
    myfont = pygame.font.SysFont("monospace", 15)

    running = True
    thread = threading.Thread(target=read_from_port, args=(serial_port,))
    thread.start()
    
    while running:
        screen.fill(background_colour)
        label = myfont.render(parameter_string, 1, (0,0,0))
        screen.blit(label, (100, 100))
        pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if process_cmd!=0:
            cmd = chr(process_cmd)
            parameter_string = cmd+" / "+" ".join( ("%.2f"%(pv/1024.0))
                                            for pv in parameter_values)
            process_cmd = 0
            
if __name__=="__main__":
    main()
