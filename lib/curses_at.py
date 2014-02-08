import urwid

import atcodes
from curses_menus import MenuDisplay, MenuRoot, EditContent, create_box

def create_at_menu():
    return [SetMode(), SetAddress(), LockStatus(), GetIMEI(), ModemStatus(), ExtendedInfo(), ShowNetworks(), SignalStrength(), EnterCommand()]
# end create_at_menu

class SetMode(MenuDisplay):
    caption = u'Set Mode'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(SetMode, self).__init__(self.caption, create_box(self.caption, self.content))
    # end __init__

    def open_menu(self, box):
        modes = ''
        for m in atcodes.ModeValues.keys():
            modes += m + ', '
        # end for
        modes = modes[:len(modes)-2] + '\n\nEnter Mode:\n'

        text = u'Modes: ' + modes
        self.content.set_caption(('display', text))
        self.content.set_edit_text('')

        def set_mode(main_loop, mode):
            (response, responseError) = MenuRoot.AT.SetMode(mode)
            response = response.strip()
            if responseError:
                self.content.set_caption(('error display', [u'\n', response]))
            else:
                self.content.set_caption(('display', [u'\n', response]))
            # end if
            self.content.remove_callback()
        # end set_mode

        self.content.set_callback(u'Setting Mode to {0}', set_mode)
        super(SetMode, self).open_menu(box)
    # end open_menu

# end SetMode

class SetAddress(MenuDisplay):
    caption = u'Set Address'
    initial_text = u'Set Address:\n'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(SetAddress, self).__init__(self.caption, create_box(self.caption, self.content))
    # end __init__

    def open_menu(self, box):
        self.content.set_caption(('display', self.initial_text))
        self.content.set_edit_text('')

        def set_address(main_loop, address):
            (response, responseError) = MenuRoot.AT.SetAddress(address)
            response = response.strip()
            if responseError:
                self.content.set_caption(('error display', [u'\n', response]))
            else:
                self.content.set_caption(('display', [u'\n', response]))
            # end if
            self.content.remove_callback()
        # end set_address

        self.content.set_callback(u'Setting Address to {0}', set_address)
        super(SetAddress, self).open_menu(box)
    # end open_menu

# end SetAddress

class LockStatus(MenuDisplay):
    caption = u'Lock Status'
    initial_text = u'Getting Lock Status\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(LockStatus, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getLockStatus(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.LockStatus()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\n', response]))
            # end if
        # end getLockStatus

        super(LockStatus, self).set_callback(getLockStatus)
        super(LockStatus, self).open_menu(box)
    # end open_menu
# end LockStatus

class GetIMEI(MenuDisplay):
    caption = u'Get IMEI'
    initial_text = u'Getting IMEI\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(GetIMEI, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getIMEI(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.GetIMEI()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\nIMEI:\n', response]))
            # end if
        # end getIMEI

        super(GetIMEI, self).set_callback(getIMEI)
        super(GetIMEI, self).open_menu(box)
    # end open_menu

# end GetIMEI

class ModemStatus(MenuDisplay):
    caption = u'Modem Status'
    initial_text = u'Getting Modem Status\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(ModemStatus, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getModemStatus(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.ModemStatus()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\nModem Status:\n', response]))
            # end if
        # end getModemStatus

        super(ModemStatus, self).set_callback(getModemStatus)
        super(ModemStatus, self).open_menu(box)
    # end open_menu

# end ModemStatus

class ExtendedInfo(MenuDisplay):
    caption = u'Extended Info'
    initial_text = u'Getting Extended Info\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(ExtendedInfo, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getExtendedInfo(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.ModemExtendedInfo()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\nExtended Info:\n', response.decode('unicode-escape')]))
            # end if
        # end getExtendedInfo

        super(ExtendedInfo, self).set_callback(getExtendedInfo)
        super(ExtendedInfo, self).open_menu(box)
    # end open_menu
# end ExtendedInfo

class ShowNetworks(MenuDisplay):
    caption = u'Show Networks'
    initial_text = u'Getting Networks\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(ShowNetworks, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getNetworks(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.AvailableNetworks()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\nNetworks:\n', response]))
            # end if
        # end getNetworks

        super(ShowNetworks, self).set_callback(getNetworks)
        super(ShowNetworks, self).open_menu(box)
    # end open_menu

# end ShowNetworks

class SignalStrength(MenuDisplay):
    caption = u'Signal Strength'
    initial_text = u'Getting Signal Strength\N{HORIZONTAL ELLIPSIS}'
    content = urwid.Text([u''], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(SignalStrength, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_text(('display', self.initial_text))

        def getSignalStrength(main_loop, user_data):
            (response, responseError) = MenuRoot.AT.SignalStrength()
            response = response.strip()
            if responseError:
                self.content.set_text(('error display', [u'\n', response]))
            else:
                self.content.set_text(('display', [u'\n', response]))
            # end if
        # end getSignalStrength

        super(SignalStrength, self).set_callback(getSignalStrength)
        super(SignalStrength, self).open_menu(box)
    # end open_menu

# end SignalStrength

class EnterCommand(MenuDisplay):
    caption = u'Enter Command'
    initial_text = u'Enter AT Command:\n'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(EnterCommand, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_caption(self.initial_text)
        self.content.set_edit_text('')

        def enterCommand(main_loop, command):
            (response, responseError) = MenuRoot.AT.ATCommand(command)
            response = response.strip() + '\n\nEnter AT Command:\n'

            if responseError:
                self.content.set_caption(('error display', response))
            else:
                self.content.set_caption(('display', response))
            # end if
        # end enterCommand

        self.content.set_callback(u'AT Command: {0}\N{HORIZONTAL ELLIPSIS}', enterCommand)

        super(EnterCommand, self).open_menu(box)
    # end open_menu

# end EnterCommand
