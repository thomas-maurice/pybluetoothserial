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

## Using the script
Once you've run it, it will go in discovery mode, it will search
for devices which offer a serial port service. Once the discovery
process is over it will print out in the console the names of the
devices so that you can choose the right one.

Once you've selected your device just hit "Connect" and here you go !
If some problem occur during both the discovery and connexion process
then the errors will be output to the **terminal**

If you have trouble connecting to the device please take care of
pairing it first ! In my case *blueman*, my bluetooth manager takes
care of pairing with the device if I didn't do it prior to connect but
I'm not sure every bluetooth manager does, so check it.

## Display modes
Once you have connected to the device, it will print in the console
every byte recieved which can be a problem if the characters are not
printable. Your console can quickly become a mess !

To avoid that you can select the way you want data to be output in
the console :

 * ASCII (default) : Will just print out the characters to the console regardless of their printability
 * Hex : Will output the hexadecimal value of the characters
 * Both : will output the hex value, and the ASCII one if the character is printable

To be more clear, here is a small recap :

Character 'a'. ASCII : **a**, Hex : **[0x61]**, Both **[0x61 a]**

Another exemple with a non printable one :

Character '\n'. ASCII : **\n**, Hex : **[0xa ]**, Both **[0xa  .]**

Enjoy :)
