# Python Library Imports
import urwid

# Modem Project Imports
from curses_menus import MenuDisplay, MenuRoot, create_box, EditContent, OkButton

def create_ussd_menu():
    return [CheckBalance(), CheckData(), BuyBundle(), Recharge(), EnterCode()]
# end create_ussd_menu

def get_ussd(name):
    provider = MenuRoot.ModemSettings.GetCurrentProvider()
    if provider == '':
        return ('', u'Current Provider Not Set')
    else:
        ussd = MenuRoot.ModemSettings.GetProviderSetting2(provider, name)
        if ussd == '':
            return ('', u'USSD Code Not Set')
        else:
            return (ussd, u'Sending USSD (' + ussd + u')\N{HORIZONTAL ELLIPSIS}')
        # end if
    # end if
# end get_ussd

class CheckBalance(MenuDisplay):
    caption = u'Check Balance'
    name = 'checkbalance'
    content = urwid.Text([u'Sending USSD'], 'center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(CheckBalance, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        (ussd, display) = get_ussd(self.name)

        if ussd == '':
            self.content.set_text(('error display', display))
        else:
            self.content.set_text(('display', display))
        # end if

        def sendUSSD(main_loop, user_data):
            (response, shouldRespond, responseError) = MenuRoot.AT.SendUSSD(ussd)
            if responseError:
                self.content.set_text(('error display', response))
            else:
                self.content.set_text(('display', response))
            # end if
        # end sendUSSD

        if ussd != '':
            super(CheckBalance, self).set_callback(sendUSSD)
        # end if

        super(CheckBalance, self).open_menu(box)
    # end open_menu

# end CheckBalance

class CheckData(CheckBalance):
    def __init__(self):
        self.caption = u'Check Data'
        self.name = 'checkdata'
        super(CheckData, self).__init__()
    # end __init__
# end CheckData

class BuyBundle(MenuDisplay):
    caption = u'Buy Bundle'
    name = 'buybundle'
    content = EditContent(caption=u'Sending USSD', align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(BuyBundle, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        (ussd, display) = get_ussd(self.name)

        if ussd== '':
            self.content.set_caption(('error display', display))
        else:
            self.content.set_caption(('display', display))
        # end if

        self.content.set_edit_text('')

        def sendUSSD(main_loop, ussd):
            (response, shouldRespond, responseError) = MenuRoot.AT.SendUSSD(ussd)

            if responseError:
                self.content.set_caption(('error display', response))
                self.content.remove_callback()
            else:
                if shouldRespond:
                    response += '\n\nResponse:\n'
                    self.content.set_callback(u'Sending USSD ({0})\N{HORIZONTAL ELLIPSIS}', sendUSSD)
                else:
                    self.content.remove_callback()
                # end if
                self.content.set_caption(('display', response))
            # end if
        # end sendUSSD

        if ussd != '':
            super(BuyBundle, self).set_callback(sendUSSD)
        # end if

        super(BuyBundle, self).open_menu(box)
    # end open_menu

# end BuyBundle

class Recharge(MenuDisplay):
    caption = u'Recharge'
    name = 'recharge'
    initial_text = u'Enter Recharge Code:\n'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(Recharge, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_caption(self.initial_text)
        self.content.set_edit_text('')

        (ussd, display) = get_ussd(self.name)

        def sendUSSD(main_loop, recharge_code):
            if len(recharge_code) is not 14 and not recharge_code.isdigit():
                self.content.set_caption(('error display', u'Code must 14 digits'))
            else:
                if 'CODE' in ussd:
                    ussdCode = ussd.replace('CODE', recharge_code)
                else:
                    ussdCode = ussd[:len(ussd)-1] + recharge_code + ussd[len(ussd)-1:]
                # end if

                (response, shouldRespond, responseError) = MenuRoot.AT.SendUSSD(ussdCode)
                if responseError:
                    self.content.set_caption(('error display', response))
                else:
                    self.content.set_caption(('display', response))
                # end if
            # end if
        # end sendUSSD

        if ussd == '':
            self.content.set_caption(('error display', display))
        else:
            if 'CODE' in ussd:
                ussdCode = ussd.replace('CODE', '{0}')
            else:
                ussdCode = ussd[:len(ussd)-1] + '{0}' + ussd[len(ussd)-1:]
            # end if
            self.content.set_callback(u'Sending USSD (' + ussdCode + u')\N{HORIZONTAL ELLIPSIS}', sendUSSD)
        # end if

        super(Recharge, self).open_menu(box)
    # end open_menu

# end Recharge

class EnterCode(MenuDisplay):
    caption = u'Enter Code'
    initial_text = u'Enter USSD Code:\n'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(EnterCode, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

    def open_menu(self, box):
        self.content.set_caption(self.initial_text)
        self.content.set_edit_text('')

        def sendUSSD(main_loop, ussd):
            (response, shouldRespond, responseError) = MenuRoot.AT.SendUSSD(ussd)

            if responseError:
                self.content.set_caption(('error display', response))
            else:
                self.content.set_caption(('display', response + '\n\nEnter USSD Code:\n'))
            # end if
        # end sendUSSD

        self.content.set_callback(u'Sending USSD ({0})\N{HORIZONTAL ELLIPSIS}', sendUSSD)

        super(EnterCode, self).open_menu(box)
    # end open_menu

# end EnterCode
