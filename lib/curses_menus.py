# Python Library Imports
import urwid
import time
import sys

# Modem Project Imports
import settings
import atapi
import logger
import errors

DIVIDER_BLOCK = urwid.AttrMap(urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}'), 'line')

palette = [
        (None, 'light gray', 'black'),
        ('heading', 'black', 'light gray'),
        ('line', 'black', 'light gray'),
        ('options', 'dark gray', 'black'),
        ('display', 'black', 'light gray'),
        ('error display', 'black', 'light red'),
        ('setting', 'black', 'dark green'),
        ('focus heading', 'white', 'dark red'),
        ('focus line', 'black', 'dark red'),
        ('focus options', 'black', 'light gray'),
        ('selected', 'white', 'dark blue')
        ]

focus_map = {
        'heading' : 'focus heading',
        'options' : 'focus options',
        'line' : 'focus line'
        }


class EditContent(urwid.Edit):
    callback = None
    callback_caption = ['']
    accept_blank_input = False

    def keypress(self, size, key):
        if key == 'tab' or key == 'shift tab':
            return super(EditContent, self).keypress(size, 'down')
        elif key == 'enter' or key == 'return':
            if self.callback != None:
                if self.edit_text == '' and not self.accept_blank_input:
                    return super(EditContent, self).keypress(size, 'down')
                # end if

                if '{0}' in self.callback_caption[0]:
                    self.callback_caption[0] = self.callback_caption[0].format(self.edit_text)
                # end if
                self.set_caption(('display', self.callback_caption))

                args = self.edit_text
                self.set_edit_text('')

                MenuRoot.loop.set_alarm_in(0.01, self.callback, args)
            else:
                return super(EditContent, self).keypress(size, 'down')
            # end if
        else:
            return super(EditContent, self).keypress(size, key)
        # end if
    # end keypress

    def set_callback(self, caption, callback, acceptBlankInput=False):
        self.callback_caption[0] = caption
        self.callback = callback
        self.accept_blank_input = acceptBlankInput
    # end set_callback

    def remove_callback(self):
        self.callback = None
        self.callback_caption[0] = ''
    # end remove_callback

    def set_edit_text(self, text):
        if text == None:
            text = ''
        # end if
        super(EditContent, self).set_edit_text(text)
        self.set_edit_pos(len(text))
    # end set_edit_text

# end EditContent

class MenuButton(urwid.Button):
    def __init__(self, caption, callback, *args):
        super(MenuButton, self).__init__('')
        if args == ():
            urwid.connect_signal(self, 'click', callback)
        else:
            urwid.connect_signal(self, 'click', callback, args)
        # end if
        self.caption = caption
        icon = CustomIcon([u'\N{BULLET} ', caption], 'left', 2)
        self._w = urwid.AttrMap(icon, None, 'selected')
    # end __init__

    def keypress(self, size, key):
        if key == 'esc' or key == 'h' or key == 'left':
            MenuRoot.close_box(key)
        elif key == 'j':
            return super(MenuButton, self).keypress(size, 'down')
        elif key == 'k':
            return super(MenuButton, self).keypress(size, 'up')
        elif key == 'l' or key == 'right':
            if not MenuRoot.last_box:
                return super(MenuButton, self).keypress(size, 'enter')
            else:
                return super(MenuButton, self).keypress(size, key)
            # end if
        else:
            return super(MenuButton, self).keypress(size, key)
        # end if
    # end keypress

# end MenuButton

class OkButton(urwid.Button):
    def default_callback(self, args):
        MenuRoot.close_box()
    # end default_callback

    def __init__(self, caption=u'OK'):
        super(OkButton, self).__init__('')
        urwid.connect_signal(self, 'click', self.default_callback)
        self.caption = caption
        icon = CustomIcon([self.caption], 'center', 0)
        self._w = urwid.AttrMap(icon, None, 'selected')
    # end __init__

    def set_callback(self, callback, *args):
        urwid.disconnect_signal(self, 'click', self.default_callback)
        if args == ():
            urwid.connect_signal(self, 'click', callback)
        else:
            urwid.connect_signal(self, 'click', callback, args)
        # end if
    # end set_callback

    def keypress(self, size, key):
        if key == 'tab' or key == 'shift tab':
            return super(OkButton, self).keypress(size, 'up')
        else:
            return super(OkButton, self).keypress(size, key)
        # end if
    # end keypress

# end OkButton

# pulled from the Icon class in the urwid library
# allows the icon to be aligned
class CustomIcon(urwid.Text):
    _selectable = True
    def __init__(self, text, align='left', cursor_position=1):
        self.__super.__init__(text, align)
        self._cursor_position = cursor_position
    # end __init__

    def render(self, size, focus=False):
        c = self.__super.render(size, focus)
        if focus:
            # create a new canvas so we can add a cursor
            c = urwid.canvas.CompositeCanvas(c)
            c.cursor = self.get_cursor_coords(size)
        # end if
        return c
    # end render

    def get_cursor_coords(self, size):
        if self._cursor_position > len(self.text):
            return None
        # end if

        # find out where the cursor will be displayed based on
        # the text layout
        (maxcol,) = size
        trans = self.get_line_translation(maxcol)
        x, y = urwid.text_layout.calc_coords(self.text, trans, self._cursor_position)

        if maxcol <= x:
            return None
        # end if

        return x, y
    # end get_cursor_coords

    def keypress(self, size, key):
        return key
    # end keypress

# end CustomIcon

class MenuDisplay(urwid.WidgetWrap):

    def default_callback(self, main_loop, user_data):
        pass
    # end default_callback

    def __init__(self, caption, box=None):
        self.callback = self.default_callback
        self.args = ()

        num_of_spaces = MenuRoot.MENU_WIDTH - len(caption) - 4
        spaces = ' ' * num_of_spaces

        super(MenuDisplay, self).__init__(MenuButton(
            [caption, spaces, u'\N{HORIZONTAL ELLIPSIS}'],
            self.open_menu))

        if box == None:
            content = urwid.AttrMap(urwid.Text([u'\n', caption], 'center'), 'display')
            box = create_box(caption, content)
        # end if

        self.menu = urwid.AttrMap(box, 'options')
    # end __init__

    def set_callback(self, callback, *args):
        self.callback = callback
        self.args = args
    # end set_callback

    def open_menu(self, box):
        MenuRoot.open_menu_display(self.menu, self.callback, self.args)
    # end open_menu

    def keypress(self, size, key):
        if key == 'esc':
            MenuRoot.close_box()
        else:
            return super(MenuDisplay, self).keypress(size, key)
        # end if
    # end keypress

# end MenuDisplay

class SubMenu(urwid.WidgetWrap):
    body = urwid.SimpleFocusListWalker([])

    def __init__(self, caption, choices):
        num_of_spaces = MenuRoot.MENU_WIDTH - len(caption) - 4
        spaces = ' ' * num_of_spaces

        super(SubMenu, self).__init__(MenuButton(
            [caption, spaces, u'\N{RIGHTWARDS ARROW}'],
            self.open_menu))

        heading = urwid.Text([u'\n', caption], 'center')
        line = urwid.Divider(u'\N{LOWER ONE QUARTER BLOCK}')
        self.body = urwid.SimpleFocusListWalker([urwid.AttrMap(heading, 'heading'),
            urwid.AttrMap(line, 'line'),
            urwid.Divider()]
            + choices
            + [urwid.Divider()])
        listbox = urwid.ListBox(self.body)

        self.menu = urwid.AttrMap(listbox, 'options')
    # end __init__

    def add_choice(self, index, choice):
        self.body.insert(index, choice)
    # end add_choice

    def open_menu(self, button):
        MenuRoot.open_sub_menu(self.menu)
    # end open_menu

# end SubMenu

class InitializeSerialPortDialog:
    palette = [
        ('body','black','light gray', 'standout'),
        ('border','black','dark blue'),
        ('shadow','white','black'),
        ('selected','white','dark blue'),
        ('focus','black','dark red','bold'),
        ]

    def __init__(self):
        width = ('relative', 45)
        height = ('relative', 70)

        body = urwid.Filler(urwid.Divider(),'top')
        self.body = body

        self.frame = urwid.Frame(body, focus_part='footer')
        self.frame.header = urwid.Pile([urwid.Text(u'Initializing Serial Port\N{HORIZONTAL ELLIPSIS}', 'center'), urwid.Divider()])
        w = self.frame

        # pad area around listbox
        w = urwid.Padding(w, ('fixed left',2), ('fixed right',2))
        w = urwid.Filler(w, ('fixed top',1), ('fixed bottom',1))
        w = urwid.AttrWrap(w, 'body')

        # "shadow" effect
        w = urwid.Columns( [w,('fixed', 2, urwid.AttrWrap(
            urwid.Filler(urwid.Text(('border','  ')), "top")
            ,'shadow'))])
        w = urwid.Frame( w, footer =
            urwid.AttrWrap(urwid.Text(('border','  ')),'shadow'))

        # outermost border area
        w = urwid.Padding(w, 'center', width )
        w = urwid.Filler(w, 'middle', height )
        w = urwid.AttrWrap( w, 'border' )

        self.view = w

        cancelButton = OkButton(u'Cancel')
        cancelButton.set_callback(self.exit_loop)
        b = urwid.AttrWrap(cancelButton, 'selected', 'focus')
        self.frame.footer = urwid.Pile([urwid.Divider(), b], focus_item=1)
    # end __init__

    def exit_loop(self, item):
        raise urwid.ExitMainLoop()
    # end exit_loop

    def exit_program(self, item):
        MenuRoot.serial_port_error()
        raise urwid.ExitMainLoop()
    # end exit_program

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette)
        self.loop.set_alarm_in(0.1, self.initialize)
        self.loop.run()
    # end main

    def initialize(self, loop, args):
        message = ''
        initialized = True

        try:
            currentPort = MenuRoot.ModemSettings.GetGeneralSetting('ttyport')
            modemId = MenuRoot.ModemSettings.GetGeneralSetting('modem')
            returnedPort = MenuRoot.AT.Initialize(currentPort, modemId)

            if returnedPort == None or returnedPort == '':
                message = u'Unable To Determine Serial Port'
                initialized = False
            # end if

            if currentPort != returnedPort:
                MenuRoot.ModemSettings.SetGeneralSetting('ttyport', returnedPort)
            # end if

        except Exception as e:
            message = u'Error Initializing Serial Port\n{0}'.format(sys.exc_info()[1])
            initialized = False
        # end try/except

        if not initialized:
            self.frame.header = urwid.Pile([urwid.Text(message, 'center'), urwid.Divider()])

            yesButton = OkButton(u'Continue')
            yesButton.set_callback(self.exit_loop)
            yesButton = urwid.AttrWrap(yesButton, 'focus', 'selected')

            noButton = OkButton(u'Exit')
            noButton.set_callback(self.exit_program)
            noButton = urwid.AttrWrap(noButton, 'focus', 'selected')

            self.frame.footer = urwid.Pile([urwid.Divider(), yesButton, urwid.Divider(), noButton], focus_item=1)
        else:
            raise urwid.ExitMainLoop()
        # end if
    # end intitialize

# end InitializeSerialPortDialog

class HorizontalBoxes(urwid.Columns):
    Logger          = logger.Logger()
    AT              = atapi.ATAPI()
    ModemSettings   = settings.Settings()
    MENU_HEIGHT     = 25
    MENU_WIDTH      = 20
    error           = errors.NO_ERROR

    def __init__(self):
        super(HorizontalBoxes, self).__init__([], dividechars=1)
        self.box_level = 0
        self.last_box = False
    # end __init__

    def start(self):
        if self.error == errors.NO_ERROR:
            self.loop = urwid.MainLoop(urwid.Filler(self, ('relative', 25), self.MENU_HEIGHT), palette)
            self.loop.run()
        else:
            exit(self.error)
        # end if
    # end start

    def serial_port_error(self):
        self.error = errors.ERROR_SERIAL_PORT
    # end serial_port_error

    def set_dimensions(self):
        self.MENU_HEIGHT = int(self.ModemSettings.CursesSettings['menu_height'])
        self.MENU_WIDTH = int(self.ModemSettings.CursesSettings['menu_width'])
    # end set_dimensions

    def open_sub_menu(self, box):
        self.last_box = False
        self.open_box(box)
    # end open_sub_menu

    def open_menu_display(self, box, callback, args):
        self.last_box = True
        self.open_box(box)
        if callback != None:
            # have to let the main loop redraw the screen
            # delay before running the callback function
            self.loop.set_alarm_in(0.01, callback, args)
        # end if
    # end open_menu_display

    def open_box(self, box):
        if self.contents:
            del self.contents[self.focus_position + 1:]
        # end if

        self.contents.append(
            (urwid.AttrMap(box,
            'options',
            focus_map),
            self.options('given', MenuRoot.MENU_WIDTH))
            )
        self.focus_position = len(self.contents) - 1
        self.box_level += 1
    # end open_box

    def close_box(self, key=''):
        if self.box_level > 1:
            # remove the current menu
            del self.contents[self.focus_position:]
            # set the focus to the previous menu
            self.focus_position = len(self.contents) - 1
            self.box_level -= 1
            self.last_box = False
        elif key == 'esc':
            raise urwid.ExitMainLoop()
        # end if
    # end close_box

    def keypress(self, size, key):
        if key == 'esc':
            self.close_box(key)
        else:
            return super(HorizontalBoxes, self).keypress(size, key)
        # end if
    # end keypress

# end HorizontalBoxes

def create_heading(caption):
    return urwid.AttrMap(urwid.Text([u'\n', caption], 'center'), 'heading')
# end create_heading

def create_box(caption, content, button=OkButton()):
    return urwid.Filler(urwid.Pile(
        [create_heading(caption),
            DIVIDER_BLOCK,
            urwid.Divider(),
            content,
            urwid.Divider(),
            button]
        ), 'top')
# end create_box

MenuRoot = HorizontalBoxes()
