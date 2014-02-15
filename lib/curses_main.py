# Python Library Imports
import sys
import urwid

# Modem Project Imports
import logger
from curses_menus import MenuButton, SubMenu, MenuRoot, HorizontalBoxes, InitializeSerialPortDialog
from curses_ussd import create_ussd_menu
from curses_sms import create_sms_menu
from curses_at import create_at_menu
from curses_settings import create_settings_menu

def exit_program(key):
    raise urwid.ExitMainLoop()

class CursesInterface:
    def Initialize(self, Logger, ModemSettings, InitSerialPort):
        Logger.RunningCurses = True
        MenuRoot.Logger = Logger
        MenuRoot.AT.Logger = Logger
        MenuRoot.ModemSettings = ModemSettings
        if InitSerialPort:
            InitializeSerialPortDialog().main()
        # end if
    # end Initialize

    def main(self):
        MenuRoot.set_dimensions()

        menu = SubMenu(u'Main Menu', [
            SubMenu(u'USSD', create_ussd_menu()),
            SubMenu(u'SMS', create_sms_menu()),
            SubMenu(u'Modem AT Commands', create_at_menu()),
            SubMenu(u'Settings', create_settings_menu()),
            MenuButton(u'Exit', exit_program),
            ])

        MenuRoot.open_box(menu.menu)
        MenuRoot.start()
    # end main

# end CursesInterface
