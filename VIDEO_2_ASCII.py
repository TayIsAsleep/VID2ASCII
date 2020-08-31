import cv2
import os
import sys
import subprocess
import time
from pyautogui import confirm,prompt
import easygui
subprocess.call('', shell=True)
#DEFAULT SETTINGS:
setting_loop         = True
setting_color        = False
setting_output       = False
setting_out_progress = True
setting_scale        = 0.1
setting_asciichars   = [" ",".","-","*","x","#","@"]
#DEFAULT SETTINGS:
SCALE = setting_scale
img = "NONE"
First_Time = True
delay = 0
PROGRAM_NAME = "VID2ASCII"
def shutdown(reason):
    print(str(reason) + ", closing program")
    exit()
    
def YN(_ask): 
    ans = confirm(text=_ask, title=PROGRAM_NAME, buttons=['Yes', 'No',"Quit"])
    if ans == "Yes":
        return True
    elif ans == "No":
        return False
    else:
        shutdown("User selected the quit option, closing program")

try: # Check if user passed a video or not, so we dont waste no time
    img =(sys.argv[1])
except:
    print("No file passed in, opening file explorer...")
    img = easygui.fileopenbox()
    if str(img) == "None":
        shutdown("User closed the file explorer, or did not select a file, closing program")
# MODE SELECTOR
ans = confirm(text="Welcome to {}, please press one of the buttons below to get started!".format(PROGRAM_NAME), title=PROGRAM_NAME, buttons=["Playback with Ascii","Save frames as a txt file","Custom mode","Quit"])
if ans == "Save frames as a txt file":
    setting_output = True
elif ans == "Custom mode":
    setting_output = confirm(text="Do you want to play the video here or extract the frames into files?", title=PROGRAM_NAME, buttons=['View video','Extract frames', "Quit"])
    if setting_output == 'Extract frames':
        setting_output = True
        setting_color = YN("Do you want the output to include color Ascii escape codes? (Color text not supported by Notepad)")
    elif setting_output == "View video":
        setting_output = False
    else:
        shutdown("User selected the quit option, closing program")
    if setting_output == False:
        setting_loop  = YN("Do you want the video to loop?")
        setting_color = YN("Do you want the video to have color? \n(This may create alot of lag)")    
    if YN("Do you want to enter a custom character set?"):
        setting_asciichars = prompt(text='Please enter the Ascii characters you want to use.\nPlease enter them in sorted from "smallest" to "biggest", e.g ". o @"\nSeperate them with a spacebar', title=PROGRAM_NAME , default='').split(" ")    
    setting_scale = (int(prompt(text="Please enter how much % of the original resolution should be kept \n('100' would mean every pixel in the video will be ascii character)\n10 - 20 is the recommended for most videos, the only limit is the limit of the console.", title=PROGRAM_NAME , default="10")) / 100)
elif ans == "Quit" or ans == "None":
    shutdown("User selected the quit option or the buttonpress returned as 'None', closing program")
else:
    pass
if setting_output:
    dirName = 'frames'
    try:
        os.mkdir(dirName) # Make folder for frames
    except FileExistsError:
        pass
# Frame 2 ascii converter function:
def frame_2_ascii(image_input,image_size,COLOR): 
    def rgbme(rgbin): #Script to color text (New and simple)
        if COLOR:
            return ("\033[38;2;{};{};{}m".format(rgbin[0],rgbin[1],rgbin[2])) #Returns ascii escape code with rgb 
        else:
            return ""
    if COLOR:
        WORKING_IMAGE_PRE_RGB = image_input.copy()  #Converts the image to RGB format  
        WORKING_IMAGE = cv2.cvtColor(WORKING_IMAGE_PRE_RGB, cv2.COLOR_BGR2RGB)
    else:
        WORKING_IMAGE = image_input.copy()    #Creates a clone of the frame to work with
    BW = []
    for y in WORKING_IMAGE:
        for x in y:
            BW.append(int((int(x[0])+int(x[1])+int(x[2]))/3)) #Generates b&w luma values (not using the standard values for simplicity)
    output_list = []
    for i in BW: #Selects what ascii character to use, based on the luma values generated above
        _c = False
        _a = 1
        while _c != True:
            if (255/len(setting_asciichars))*_a >= i:
                output_list.append(setting_asciichars[_a-1])
                _c = True
            else:
                _a += 1        
    string = ""
    count = 0    
    if setting_output: #prepares a text file if it needs to output to one
        txt = open(dirName + "/frame{}.txt".format(int(vidcap.get(cv2.CAP_PROP_POS_FRAMES))),"w+")
    else:
        os.system("cls") #removes the last frame, and clears the screen
    for y in range(len(WORKING_IMAGE)):
        line = ""
        for x in range(len(WORKING_IMAGE[y])):
            line = line + rgbme(((WORKING_IMAGE[y])[x])) + str(output_list[count]) + rgbme([255,255,255]) #Combines the rgb value, ascii character, and then resets the color
            if setting_output and setting_out_progress:
                sys.stdout.write("\rCompleted Frame {} out of {} ".format(int(vidcap.get(cv2.CAP_PROP_POS_FRAMES)),int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))) #Updates progress bar if its on
                sys.stdout.flush()
            count += 1      
        if setting_output:
            txt.writelines(line + "\n") #If set to output, it puts the line in the txt file
        else:
            print(line) #Renders the line on screen

def main():
    global First_Time,delay,img,Status,vidcap,settings_output,FILE
    vidcap = cv2.VideoCapture(img) #sets 'vidcap' as the video
    fps = vidcap.get(cv2.CAP_PROP_FPS) #Gets framerate of video
    success,image = vidcap.read() #Gets first frame of the video
    vid_res_x = int((len(image[0]) * 1   ) * SCALE)
    vid_res_y = int((len(image)    * 0.51) * SCALE)
    scaled_frame = cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC) #Scales the frame to the correct size
    if First_Time: #This code is ran once at startup, and it sets some values, so that they dont have to be calculated every frame
        if setting_output == False:
            os.system('mode con: cols={} lines={}'.format(vid_res_x,vid_res_y + 1)) #Sets console size
        start_time = time.time() #Starts time measurement, that will be used to decide the delay to keep the framerate stable
        frame_2_ascii((cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)),[vid_res_x,vid_res_y],setting_color) #renders first frame, while measuring time
        delay = (1-((time.time()-start_time)*fps)) / fps #Sets delay so that it wont run to fast, based on how long it took to render 1 frame, and based on the videos FPS
        if delay < 0 or setting_output:
            delay = 0 #Removes the delay if its under 0 (throws error otherwice), or if it doesnt need to render, only generate.
        First_Time = False  #Removes the first time trigger, so that this code wont be run again, since it jidders the screen slightly everytime the video loops, since it has to rescale the console and everything.
    success = True
    count_ = 0
    while success: #Loops until there is no more frames in the video
        success,image = vidcap.read()    #Gets next frame 
        if success:
            time.sleep(delay) #accounts for the delay if rendering a frame is too fast
            frame_2_ascii((cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)),[vid_res_x,vid_res_y],setting_color) #runs the main converter, and scales the image (NEEDS IMPROVEMENT (MAYBE SCALE ALL THE FRAMES FIRST??))------------------!!
            count_ += 1
    vidcap.release() #Unloads vidcap
    if setting_loop == False and setting_output == False:
        wait = input("") #Pauses at the final frame, if not set to loop
try:
    if __name__ == "__main__":
        if setting_output: 
            print("Starting to render frames...")
            start_time = time.time() #Starts timer
            main() #Runs the main script
            print("\nAll Frames extracted!, this took {}".format(str((time.time()-start_time))))
            x = input("")
        else:
            main() #Runs the code once, and...
            while setting_loop: #... then loops it if looping is on
                main()
except Exception as e:
    print(e)
    x = input("")