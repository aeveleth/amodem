import urwid
from curses_menus import MenuDisplay, MenuRoot, create_box, EditContent

def create_sms_menu():
    return [SendSMS(), ListMessages(), DeleteMessage()]
# end create_sms_menu

class SendSMS(MenuDisplay):
    caption = u'Send SMS'
    content = EditContent(align='center')

    def __init__(self):
        content_attr = urwid.AttrMap(self.content, 'display')
        super(SendSMS, self).__init__(self.caption, create_box(self.caption, content_attr))
    # end __init__

# end SendSMS

class ListMessages(MenuDisplay):
    caption = u'List Messages'

    def __init__(self):
        super(ListMessages, self).__init__(self.caption)
    # end __init__
# end ListMessages

class DeleteMessage(MenuDisplay):
    caption = u'Delete Message'

    def __init__(self):
        super(DeleteMessage, self).__init__(self.caption)
    # end __init__
# end DeleteMessage
