# Nreal Multiple Virtual Display Framework

This project is a Proof of Concept (POC) for creating a framework that enables multiple virtual displays in Augmented Reality (AR) space on Nreal Air. It is a very early alpha version, but unfortunately, I won't have time to work on it for the foreseeable future. The project builds off the great work of Tobias Frisch to make USB drivers available in the following repository: https://gitlab.com/TheJackiMonster/nrealAirLinuxDriver.

The project was developed on Ubuntu 22.04.2 LTS with X11 and Gnome 42.5. It might be possible to adapt GStreamer for Wayland in the future.  The framework currently works best for putting existing real displays in AR space. However, I have had some success using xrandr to create virtual displays and use them too.

## Instructions
1. Clone this repository 
2. Ensure that the NReal is the rightmost display in system settings
3. Run `xhost +SI:localuser:root` on the host to give access to X11 (docker container runs as root due to USB driver requirement) (revert this change when you are done for security reasons)
4. Run the devcontainer
5. Run main.py
6. Calibrate left and right by following the instructions 
7. The output should be displayed on the Nreal glasses.

To create virtual displays (glitchy for me), follow these instructions:

- Find empty displays using `xrandr` and look for 'disconnected' (e.g., DVI-I-5-4)
- `xrandr --addmode DVI-I-5-4 1920x1080`
- `xrandr --output DVI-I-5-4 --mode 1920x1080 --left-of eDP-1`

## Limitations
- The project is currently in an alpha state, and some features will not work as expected. 
- IMU readings from the driver can be glitchy, and due to this calibration routines haven't been implemented.
- I couldn't use the latest version of the USB drivers due to build errors (I've pinned a commit in the Dockerfile)
- The Nreal display needs to be disabled from interaction with the window manager as we just want to use it to display a mirror of all the other screens. I haven't found a way to do this yet.
- Only yaw has been implemented (not pitch or roll)

## Developed on
- Ubuntu 22.04.2 LTS with X11 and Gnome 42.5
- Nreal Air
- DP Alt Mode capable laptop/PC

## Credits
The project builds off the USB drivers developed by Tobias Frisch in the following repository: https://gitlab.com/TheJackiMonster/nrealAirLinuxDriver

## License
This project is licensed under the MIT License.

## Disclaimer
This project is a Proof of Concept (POC), and the developer will not be held responsible for any damage caused by the use of this software. Use at your own risk.

