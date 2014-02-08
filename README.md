This is a Python program which can be used to do some limited management of a 3G USB Modem on Linux, allowing the user to send SMS messages, send USSD commands, and send AT command to the modem. There are two interfaces the command line version and the curses interface.

This has only been tested on Xubuntu 12.04.

To install, run the command:
    sudo ./install.sh

The 'amodem' program will be installed to '/usr/local/bin' with the 'lib' folder being copied to '/usr/local/lib/amodem'


Running amodem:
    amodem needs to access the /dev/ttyUSB files, so it will probably require sudo access
    run 'amodem -h' or 'amodem --help' for a list of options and commands
    run 'amodem -i' or 'amodem --curses' to start the curses interface
    run 'amodem -l' or 'amodem --enable-logging' to start with logging, by default to the file '~/.amodem.log'
    run 'amodem -d' or 'amodem --debug' to print debug information

amodem configuration file:
    By default the amodem configuration file is '~/.amodemrc'

    An example configuration file has been added to the git directory called 'amodemrc'

    The format for the configuration file:

    [Settings]
    ttyport="/dev/ttyUSB3"
    modem="12d1:1506"
    usbdriver="option"
    sakis3g="/usr/local/bin/sakis3g"
    usbinterface=""
    provider="mtn"

    [Curses]
    menu_height="15"
    menu_width="30"

    [mtn]
    apn="internet"
    checkbalance="*124#"
    checkdata=""
    user="blank"
    pass="blank"
    pin=""
    recharge="*123*CODE#"
    buybundle="*138#"
