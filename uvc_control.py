# Original source code from GitHub Gist:
# https://gist.github.com/3dsf/62dbe5c3636276289a719da246f6d95c
# The code was modified to fit our needs and new software versions


#!/usr/bin/env python3

### gist updated dec 6th
###### https://www.reddit.com/r/opencv/comments/r9tdyk/comment/hnk7g43/?utm_source=share&utm_medium=web2x&context=3
### Controls UVC setting using   v4l2-ctl

import os, sys, subprocess
import cv2
from functools import partial

cam = '/dev/video2'

# Cam can be passed as command line argument 
if len(sys.argv) > 1:
  cam = sys.argv[1]

def getCamSettings(camDevice):
  out = subprocess.Popen(['v4l2-ctl', '-d', camDevice, '--list-ctrls-menu'],
             stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT)
  stdout,stderr = out.communicate()
  
  out = stdout.decode('UTF-8').splitlines()

  camSettings = dict()

  nLines = len(out)
  for i in range(0, nLines):

    # Skip menu legend lines which are denoted by 4 tabs
    if out[i].startswith('\t\t\t\t'):
      continue

    # Skip Header lines and empty lines which don't start with spaces
    if not out[i].startswith(' '):
      continue

    a = dict()

    # parsee the setting name, ID and datatype from the line
    setting = out[i].split(':',1)[0].split()
    print("setting=" + str(setting))
            # ['brightness', '0x00980900', '(int)']

    # parse parameters from the line
    # some menu controls stuff after the parameter list in parentheses so we ignore any split results that don't contain an equal sign
    params = [param for param in (out[i].split(':',1)[1].split()) if "=" in param]
    print("param=" + str(params))
            # ['min=-64', 'max=64', 'step=1', 'default=0', 'value=0']

    # Put paramaters into a dictionary
    for j in range(0, len(params)):
      a.update({params[j].split('=',1)[0]: params[j].split('=',1)[1]})
    # Add bitName and setting type to params dictionary 
    a.update({'bitName': setting[1]})
    a.update({'type': setting[2].strip("()")})
    # Create a legend for menu entries and add to dictionary with other params
    if a['type'] == 'menu':
      h = 0
      legend = ''
      while h >= 0:
        h += 1
        ih = i + h
        if out[ih].startswith('\t\t\t\t') and (ih) <= nLines:
          legend = legend + out[i+h].strip() + "   "
        else:
          h = -1
      a.update({'legend': legend})    # additional data on settings
      a.update({'step': 1})           # adding to work with updateUVCsetting()
    # Use setting name as key and dictionary of params as value
    camSettings.update({setting[0]: a})

  for x in camSettings:
    print(x,'\n   ',camSettings[x])
  
  return camSettings

def updateUVCsetting(setting, step, value):
                  # ('gamma', 1   , 30 )
  global cam            # ex  /dev/video0
  #v4l2-ctl -d /dev/video0 --set-ctrl=brightness=50
  value = int(int(step) * round(value/int(step)))
  subprocess.call(['v4l2-ctl', '-d', cam, 
      f'--set-ctrl={setting}={value}'], shell=False)
  check = subprocess.check_output(['v4l2-ctl', '-d', cam, 
      f'--get-ctrl={setting}'], shell=False).decode('UTF-8').lstrip().split()[1]
  test = "passed" if int(value) == int(check) else "fail"
  print(f'setting requested -- {setting} -->  {value}    test: {test}')

def defaultSettings(camSettings,window):
  global cam
  for x in camSettings:
    cv2.setTrackbarPos(x, window, int(camSettings[x]['default']))

def nothingOf(value):
  z = 1

#######
#######

# Get UVC camera setings
camSettings = getCamSettings(cam)

# Create window and add sliders poputlated from camSettings
win = 'camera controls  ---  press \'d\' to set camera defaults'
cap = cv2.VideoCapture(cam)
ret, frame = cap.read()
cv2.imshow(win, frame)
for x in camSettings:
  if camSettings[x]['type'] == 'bool':
    cv2.createTrackbar(x, win,
            int(camSettings[x]['value']), # current cam value
            int(1),                       # max
            partial(updateUVCsetting,     # new value is passed implicitly
                x,                        # setting name
                1)                     )  # value step  = 1 for bool
    cv2.setTrackbarMin(x, win,            # 
            int(0)                     )  # min
  else:
    cv2.createTrackbar(x, win, 
            int(camSettings[x]['value']), # current cam value
            int(camSettings[x]['max']),   # max value
            partial(updateUVCsetting,     # new value is passed implicitly 
                x,                        # setting name
                camSettings[x]['step']))  # value step
    cv2.setTrackbarMin(x, win, 
            int(camSettings[x]['min']) )  # min value
    if 'legend' in camSettings[x]:
      text = f'{" " * 30} (for above) --  {camSettings[x]["legend"]}'
      cv2.createTrackbar(text,win,
              1,
              1,                          # if min = max --> slider locks
              nothingOf)                  # needs to be a callable function
      cv2.setTrackbarMin(text,win,1)

# Update window with frames and allow program termination on window close
while(cap.isOpened()):
  ret, frame = cap.read()
  if ret == True:
    cv2.imshow(win,frame)
    pKey = cv2.waitKey(1) & 0xFF
    # quit
    if pKey == ord('q') or cv2.getWindowProperty(win,cv2.WND_PROP_VISIBLE) < 1:
      break
    # set default settings
    elif pKey == ord('d'):
      print('--- default setting applied ---')
      defaultSettings(camSettings,win)

cap.release()
cv2.destroyAllWindows()