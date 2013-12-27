# pybluetoothserial.py
## Developpement information

 * Maintainer : Thomas Maurice <tmaurice59@gmail.com>
 * Current version : 0.2
 * Developpement status : Still being developped :)
 * Portability : Linux and Windows (with Python 2.6)

## What is this ?
This is a python script which allow you to communicate with
bluetooth devices which offer a serial port service. Typically
it has initially been developped for a serial dongle plugged to
an Arduino board to enable some kind of wireless serial link.

It's purpose is to easien the communication so that you are not
forced to go through virtual files in */dev/rfcommX* after the 
pairing and use minicom to communicate with your device. This can
avoid you tons of permission issues ;)

Basically, instead of creating a virtual */dev/rfcommX* file,
the script uses Bluetooth socket to communicate with the device.

## Requirements
To run this software you need:

 * python (version 2.7.5 in my case but works fine with 2.6 too)
 * pyGTK (version >= 2.0)
 * pyBluez (the latest the better)
 * A bluetooth adapter

You simply run the program by typing ```./pybluetoothserial.py``` in
a terminal and here you go !
