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
            return ("\033[38;2;{};{};{}m".format(rgbin[0],rgbin[1],rgbin[2]))
        else:
            return ""
    if COLOR:
        WORKING_IMAGE_PRE_RGB = image_input.copy()   
        WORKING_IMAGE = cv2.cvtColor(WORKING_IMAGE_PRE_RGB, cv2.COLOR_BGR2RGB)
    else:
        WORKING_IMAGE = image_input.copy()   
    BW = []
    for y in WORKING_IMAGE:
        for x in y:
            BW.append(int((int(x[0])+int(x[1])+int(x[2]))/3))   
    output_list = []
    for i in BW:
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
    if setting_output:
        txt = open(dirName + "/frame{}.txt".format(int(vidcap.get(cv2.CAP_PROP_POS_FRAMES))),"w+")
    else:
        os.system("cls")
    for y in range(len(WORKING_IMAGE)):
        line = ""
        for x in range(len(WORKING_IMAGE[y])):
            line = line + rgbme(((WORKING_IMAGE[y])[x])) + str(output_list[count]) + rgbme([255,255,255])
            if setting_output and setting_out_progress:
                sys.stdout.write("\rCompleted Frame {} out of {} ".format(int(vidcap.get(cv2.CAP_PROP_POS_FRAMES)),int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))))
                sys.stdout.flush()
            count += 1      
        if setting_output:
            txt.writelines(line + "\n")
        else:
            print(line)

def main():
    global First_Time,delay,img,Status,vidcap,settings_output,FILE
    vidcap = cv2.VideoCapture(img)
    fps = vidcap.get(cv2.CAP_PROP_FPS) 
    success,image = vidcap.read()
    vid_res_x = int((len(image[0]) * 1   ) * SCALE)
    vid_res_y = int((len(image)    * 0.51) * SCALE)
    scaled_frame = cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)   
    if First_Time:
        if setting_output == False:
            os.system('mode con: cols={} lines={}'.format(vid_res_x,vid_res_y + 1))
        start_time = time.time()
        frame_2_ascii((cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)),[vid_res_x,vid_res_y],setting_color)
        delay = (1-((time.time()-start_time)*fps)) / fps
        if delay < 0 or setting_output:
            delay = 0
        First_Time = False  
    success = True
    count_ = 0
    while success:
        success,image = vidcap.read()    
        if success:
            time.sleep(delay)
            frame_2_ascii((cv2.resize(image,(vid_res_x,vid_res_y),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)),[vid_res_x,vid_res_y],setting_color)
            count_ += 1
    vidcap.release()
    if setting_loop == False and setting_output == False:
        wait = input("")

if __name__ == "__main__":
    if setting_output:
        print("Starting to render frames...")
        start_time = time.time()
        main()
        #os.system("cls")
        print("\nAll Frames extracted!, this took {}".format(str((time.time()-start_time))))
        x = input("")
    else:
        main()
        while setting_loop:
            main()