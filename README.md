# l-system-installation

Source code for an L-system visualziation &amp; installation / demo.

To build one you need following elements and things:
1. At least 24 blocks with following symbols `F`, `X`, `+`, `-`, `[`, and `]`. I used plastic 40x40mm blocks from kids puzzle with letters `<` and `>` instead of `[` and `]` to make OCR to work better.
1. A custom made table with a part of the table top being transparent. Preferably there are slots where the blocks fit with some slack.
1. 4 potentiometers and one on/off type switch and an Arduino to read the values and send the readings to the PC via USB-serial. Source code for the Arduino is in `lsystem_pots`.
  1. First pot adjusts how many rewrite iterations are applied with the current set of rules.
  1. First pot adjusts how many rewrite iterations are applied with the current set of rules.
  
1. A PC with Python 2.7, PyGame, OpenCV and Arduino IDE installed. I used Ubuntu Linux 16.04 LTS.
1. A monitor or a flat TV and some way of fixing it in portrait mode.
1. USB webcam and a light source and a adjustable mount to hold it them position under the table. I used a PS3 PlayStation Eye camera and an 220V LED spot.

Unfortunately I have no detailed plans, but feel free to consult following photo. 



There are three Python scripts in the repository:
* `l-system.py` which is the main application. It opens a PyGame window to display the plant, reads the parameter values from the USB-serial and can be used to control the application.
  * Keys `[ESC]` and `[Q]` exit the application.
  * Keys `[1]` to `[7]` intializes one of the predefined L-Systems.
  * Key `[M]` reads a L-System from a file `manual_rules.txt`. Can be used to override the recognized system if OCR fails.
  * Key `[P]` takes a picture using the webcam, saves it on the disk and and detects the symbols on the table using the funcionality in `read_ocr.py`.
  * Also toggling the button connected to the Arduino will send a command which takes a picture and tries to recognize the system from it.
  * Key `[S]` reintializes the serial communication.
* `read_cam.py` can be used to position the camera. Just continuously grabs images from the webcam.
* `train_ocr.py` is used to label the data in `trainingdata` folder for training OCR classifiers. Please take care to adjust `MAX_CHAR_SIZE_IN_PIX`, `MIN_CHAR_NARROW_SIZE_IN_PIX`, and `MIN_CHAR_WIDE_SIZE_IN_PIX` constants to fit your setup. `[ESC]` stops training and stores the data files in the working directory, here they can be transferred to a `labeled_data` folder. Use following keys for the block symbols:
  * `n` = not a symbol (glitch)
  * `9` = `>` or `]`
  * `8` = `<` or `[`
  * `i` = `|`/`-`
  * `p` = `+`
  * `f` = `F`
  * `e` = upsidedown `F`
  * `x` = `X`
  * `z` = `X` rotated 90 degrees
* `read_ocr.py` offers the OCR recognition funcitionality. It builds a classifier model and applies it when asked to detect symbols from an image. If run as a script OCRs the images in the `img_source_folder`. The recognized characters can then be interpreted as starting condition and rules.

## Example Plants/Systems
### 1. Plant

X : F<+X>-X

F : FF


### 2. Plant

X : F-<<X>+X>+F<+FX>-X
 
F : FF


### 3. Plant

F : F<+F>F<-F>F


### 4. Plant

F : F<+F>F<-F><F>


### 5. Plant

F : FF-<-F+F+F>+<+F-F-F>


### 6. Plant

X : F<+X>F<-X>+X 

F : FF
 
 
### 7. Plant

X : F<+X><-X>FX

F : FF
