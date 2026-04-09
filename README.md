Edubot is a vexcode program that allows for users to program a vex brain to move around a classroom and playback videos to help children learn.

EduBot Setup Guide
What You Need
Hardware:

VEX V5 Brain + Drivetrain robot (already built)
VEX V5 Inertial Sensor (plugged into Port 16)
Raspberry Pi with WiFi (Pi Zero 2 W, Pi 3B, Pi 4, or Pi 5)
MicroSD card (16GB+) with Raspberry Pi OS installed
USB cable from Pi to VEX Brain
USB battery pack to power the Pi on the robot
iPad (for video display)
Phone (for controlling the robot)
A computer (for the merge step and uploading code)

Software (all pre-installed, nothing to download):

VEXcode V5 Python on your computer
Python 3 on the Raspberry Pi (comes with Raspberry Pi OS)


Project Structure
EduBot/
├── vex/
│   ├── main.py                  # Original drivetrain test (optional)
│   ├── routeRecorder.py         # Records sensor data on the brain
│   ├── routeNavigator.py        # Listens for commands, drives to checkpoints
│   └── routePlayer.py           # Utility: computes distances from CSV
├── pi/
│   ├── piServer.py              # Runs on the Pi, bridges everything
│   └── videos/                  # Put your checkpoint videos here
│       ├── cp1.mp4
│       ├── cp2.mp4
│       └── ...
├── web/
│   ├── checkpointMarker.html    # Mark checkpoints during recording
│   ├── checkpointController.html # Phone remote control
│   └── videoPlayer.html         # iPad video display
└── tools/
    └── mergeCheckpoints.py      # Merges checkpoints into CSV

Step 1: Record a Route
This captures the robot's path so it can retrace it later.

Open VEXcode V5 on your computer
Load vex/routeRecorder.py as your project
Make sure the Inertial Sensor is plugged into Port 16
Insert an SD card into the VEX Brain
Connect the brain and download the program
On your phone or computer, open web/checkpointMarker.html in a browser (just double-click the file)
At the same moment, press Start on the web page and Run on the brain
Manually drive the robot along the path you want it to learn
Every time the robot reaches a spot where you want it to stop and play a video, tap Mark Checkpoint on the web page
When the route is done, press Stop on the web page
Tap Export checkpoints.json — save the file to your computer
Pull the SD card from the brain and copy envRecording.csv to your computer

You now have two files: envRecording.csv (sensor data) and checkpoints.json (your marked points).

Step 2: Merge Checkpoints into the Recording
On your computer, open a terminal in the tools/ folder and run:
python mergeCheckpoints.py /path/to/envRecording.csv /path/to/checkpoints.json /path/to/envRecording_merged.csv
Or if all three files are in the same folder:
python mergeCheckpoints.py envRecording.csv checkpoints.json envRecording_merged.csv
This produces envRecording_merged.csv with a checkpoint column added. Copy this file to the VEX Brain's SD card.

Step 3: Set Up the Raspberry Pi
3a: Install Raspberry Pi OS

Download Raspberry Pi Imager from raspberrypi.com
Flash Raspberry Pi OS Lite (no desktop needed) to your MicroSD card
In the imager settings, enable SSH and configure your WiFi network name and password
Insert the SD card into the Pi and power it on
Find the Pi's IP address (check your router's admin page, or use ping raspberrypi.local)
SSH into it: ssh pi@<pi-ip-address> (default password: raspberry)

3b: Copy Files to the Pi
From your computer, copy the necessary files:
scp pi/piServer.py pi@<pi-ip>:~/
scp web/checkpointController.html pi@<pi-ip>:~/
scp web/videoPlayer.html pi@<pi-ip>:~/
3c: Add Your Videos
Create the videos folder and copy your video files:
ssh pi@<pi-ip> "mkdir -p ~/videos"
scp your_videos/cp1.mp4 pi@<pi-ip>:~/videos/
scp your_videos/cp2.mp4 pi@<pi-ip>:~/videos/
Name each video to match the checkpoint: cp1.mp4 plays at checkpoint cp1, cp2.mp4 plays at cp2, etc. Supported formats: .mp4, .webm, .mov, .m4v.
3d: Wire the Pi to the VEX Brain
Connect a USB cable from the Raspberry Pi to the VEX V5 Brain's USB port. The brain appears as /dev/ttyACM0 on the Pi.

Step 4: Upload the Navigator to the VEX Brain

Open VEXcode V5 on your computer
Load vex/routeNavigator.py as your project
Make sure the SD card with envRecording_merged.csv is in the brain
Download and run the program on the brain
The brain screen should say "Ready - X CPs" (where X is your number of checkpoints)


Step 5: Start the Pi Server
SSH into the Pi and run:
cd ~
python3 piServer.py
You should see:
Serial connected on /dev/ttyACM0
Checkpoints: ['cp1', 'cp2', 'cp3']
Starting server on http://0.0.0.0:5000
If it says "Waiting for VEX brain..." make sure the USB cable is connected and the navigator program is running on the brain.

Step 6: Connect Your Devices
On your phone (controller):

Make sure you're on the same WiFi network as the Pi
Open Safari/Chrome and go to http://<pi-ip>:5000
You should see the EduBot controller with your checkpoint buttons

On the iPad (video display):

Same WiFi network
Open Safari and go to http://<pi-ip>:5000/display
You should see the EduBot idle screen with "Connected — Waiting"
Tap the screen once so Safari allows video autoplay
Optional: tap the share button and Add to Home Screen for a fullscreen app experience


Step 7: Run It

Tap a checkpoint button on your phone (e.g. cp2)
The robot drives from its current position to that checkpoint
When it arrives, the iPad automatically plays cp2.mp4
When the video ends, the iPad returns to the idle screen
Tap another checkpoint or Return to Start to send it home


Troubleshooting
"Server Offline" on phone/iPad:

Make sure python3 piServer.py is running on the Pi
Make sure all devices are on the same WiFi network
Try http://raspberrypi.local:5000 if you don't know the IP

"Waiting for VEX brain..." on the Pi:

Check the USB cable between Pi and brain
Make sure routeNavigator.py is running on the brain
Try unplugging and replugging the USB cable
Run ls /dev/ttyACM* on the Pi to verify the serial port exists

Robot doesn't move:

Check that envRecording_merged.csv is on the SD card
Make sure motor ports match your robot (Ports 8, 10, 11, 12 by default)
Verify checkpoints exist: the brain screen should say "Ready - X CPs"

Video doesn't play on iPad:

Tap the iPad screen once to allow autoplay
Check that video files are in ~/videos/ on the Pi with matching names
Open http://<pi-ip>:5000/display and tap the "Videos" button to see the mapping
Make sure videos are .mp4 (H.264) — this is the most compatible format for iPad Safari

Checkpoint timing is off:

The recording timer and the web marker timer need to start at the exact same moment
Try a countdown: "3, 2, 1, go" and press both Start and Run simultaneously
The merge script matches each checkpoint to the nearest CSV timestamp, so small offsets (under 500ms) are fine

Pi serial port is different:

If your brain doesn't show up as /dev/ttyACM0, run ls /dev/ttyACM* or ls /dev/ttyUSB*
Edit the SERIAL_PORT line at the top of piServer.py to match

Motor ports are different on your robot:

Edit the port numbers at the top of routeNavigator.py to match your wiring


Making the Pi Start Automatically
So you don't have to SSH in every time, add the server to the Pi's crontab:
crontab -e
Add this line at the bottom:
@reboot sleep 10 && cd /home/pi && python3 piServer.py > /home/pi/server.log 2>&1 &
Now the server starts automatically 10 seconds after the Pi boots. Just power on the Pi and everything is ready.

Setting Up the Pi as Its Own WiFi Hotspot
If you're in a classroom without WiFi, the Pi can create its own network:
sudo nmcli device wifi hotspot ssid EduBot password edubot123
Then connect your phone and iPad to the "EduBot" network (password: edubot123), and use http://10.42.0.1:5000 as the address.
