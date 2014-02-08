# Python Library Imports
import urwid

# Modem Project Imports
from curses_menus import MenuDisplay, MenuRoot, create_box, EditContent, OkButton, SubMenu


def create_settings_menu():
    return [SubMenu(u'General', create_general_menu()),
            SubMenu(u'Provider', create_provider_menu()),
            SaveSettings(),
            LoadConfigFile()]
# end create_settings_menu

def create_general_menu():
    settings_list = []
    for name in sorted(MenuRoot.ModemSettings.GeneralSettingsNames.keys()):
        settings_list.append(GeneralSettingsItem(name))
    # end for
    return settings_list
# end create_general_menu

def create_provider_menu():
    providers_list = [CurrentProvider()]
    for provider in MenuRoot.ModemSettings.Providers:
        provider_setting_list = []
        for name in sorted(MenuRoot.ModemSettings.ProviderSettingsNames.keys()):
            provider_setting_list.append(ProviderSettingsItem(name, provider))
        # end for
        providers_list.append(SubMenu(provider, provider_setting_list))
    # end for
    providers_list.append(AddNewProvider())
    return providers_list
# end create_provider_menu

class GeneralSettingsItem(MenuDisplay):
    content = EditContent(align='center')

    def __init__(self, caption):
        self.caption = caption

        button = OkButton()
        button.set_callback(self.ok_callback)
        box = create_box(self.caption, self.content, button)
        super(GeneralSettingsItem, self).__init__(self.caption, box)
    # end __init__

    def ok_callback(self, button):
        index = MenuRoot.ModemSettings.GeneralSettingsNames[self.caption]
        MenuRoot.ModemSettings.GeneralSettings[index] = self.content.edit_text
        MenuRoot.close_box()
    # end ok

    def open_menu(self, box):
        index = MenuRoot.ModemSettings.GeneralSettingsNames[self.caption]
        currentSetting = MenuRoot.ModemSettings.GeneralSettings[index]
        self.content.set_edit_text(currentSetting)
        self.content.set_edit_pos(len(currentSetting))
        super(GeneralSettingsItem, self).open_menu(box)
    # end open_menu

# end SettingsItem

class ProviderSettingsItem(MenuDisplay):
    content = EditContent(align='center')

    def __init__(self, caption, provider):
        self.caption = caption
        self.provider = provider

        button = OkButton()
        button.set_callback(self.ok_callback)
        box = create_box(self.caption, self.content, button)
        super(ProviderSettingsItem, self).__init__(self.caption, box)
    # end __init__

    def ok_callback(self, button):
        name = MenuRoot.ModemSettings.ProviderSettingsNames[self.caption]
        index = MenuRoot.ModemSettings.ProviderSettingList.index(name)
        MenuRoot.ModemSettings.Providers[self.provider][index] = self.content.edit_text
        MenuRoot.close_box()
    # end ok_callback

    def open_menu(self, box):
        name = MenuRoot.ModemSettings.ProviderSettingsNames[self.caption]
        index = MenuRoot.ModemSettings.ProviderSettingList.index(name)
        currentSetting = MenuRoot.ModemSettings.Providers[self.provider][index]
        self.content.set_edit_text(currentSetting)
        self.content.set_edit_pos(len(currentSetting))
        super(ProviderSettingsItem, self).open_menu(box)
    # end open_menu

# end ProviderSettingsItem

class CurrentProvider(MenuDisplay):
    caption = u'Current Provider'
    content = EditContent(align='center')

    def __init__(self):
        button = OkButton()
        button.set_callback(self.ok_callback)
        box = create_box(self.caption, self.content, button)
        super(CurrentProvider, self).__init__(self.caption, box)
    # end __init__

    def ok_callback(self, button):
        MenuRoot.ModemSettings.SetCurrentProvider(self.content.edit_text)
        MenuRoot.close_box()
    # end ok_callback

    def open_menu(self, box):
        currentProvider = MenuRoot.ModemSettings.GetCurrentProvider()
        self.content.set_edit_text(currentProvider)
        self.content.set_edit_pos(len(currentProvider))
        super(CurrentProvider, self).open_menu(box)
    # end open_menu

# end CurrentProvider

class SaveSettings(MenuDisplay):
    caption = u'Save Settings'
    content = EditContent(caption=u'Config File Name:\n', align='center')

    def __init__(self):
        button = OkButton()
        button.set_callback(self.ok_callback)
        box = create_box(self.caption, self.content, button)
        super(SaveSettings, self).__init__(self.caption, box)
    # end __init__

    def ok_callback(self, button):
        MenuRoot.ModemSettings.SaveConfigFile(self.content.edit_text)
        MenuRoot.close_box()
    # end ok_callback

    def open_menu(self, box):
        configFile = MenuRoot.ModemSettings.GetConfigFileName()
        self.content.set_edit_text(configFile)
        self.content.set_edit_pos(len(configFile))
        super(SaveSettings, self).open_menu(box)
    # end open_menu

# end SaveSettings

class LoadConfigFile(MenuDisplay):
    caption = u'Load Config File'
    content = EditContent(caption=u'Config File Name:\n', align='center')

    def __init__(self):
        button = OkButton()
        button.set_callback(self.ok_callback)
        box = create_box(self.caption, self.content, button)
        super(LoadConfigFile, self).__init__(self.caption, box)
    # end __init__

    def ok_callback(self, button):
        MenuRoot.ModemSettings.SetConfigFileName(self.content.edit_text)
        MenuRoot.ModemSettings.LoadConfigFile()
        MenuRoot.close_box()
    # end ok_callback

    def open_menu(self, box):
        configFile = MenuRoot.ModemSettings.GetConfigFileName()
        self.content.set_edit_text(configFile)
        self.content.set_edit_pos(len(configFile))
        super(LoadConfigFile, self).open_menu(box)
    # end open_menu

# end LoadConfigFile

class AddNewProvider(MenuDisplay):
    caption = u'Add New Provider'
    content = EditContent(caption=u'Provider Name:\n', align='center')
    providerSettings = []
    settingsList = []

    def __init__(self):
        self.settingsList = list(MenuRoot.ModemSettings.ProviderSettingList)
        self.content.set_callback(u'Setting \'{0}\' Value:\n'.format(self.settingsList[0]), self.enterNextSetting)
        super(AddNewProvider, self).__init__(self.caption, create_box(self.caption, self.content))
    # end __init__

    def enterNextSetting(self, main_loop, value):
        self.providerSettings.append(value)
        self.settingsList.pop(0)

        if self.settingsList:
            self.content.set_callback(u'Setting \'{0}\' Value:\n'.format(self.settingsList[0]), self.enterNextSetting)
        else:
            self.content.set_callback(u'Adding New Provider', self.addProvider)
        # end if
    # end enter_next_setting

    def addProvider(self, main_loop, value):
        self.providerSettings.append(value)
        self.providerSettings.append(MenuRoot.ModemSettings.GetConfigFileName())

        providerName = self.providerSettings[0]

        MenuRoot.ModemSettings.AddNewProvider(self.providerSettings)

        self.content.set_caption(('display', u'New Provider \'{0}\' Added'.format(providerName)))
        self.content.remove_callback()

        MenuRoot.start()
    # end addProvider

# end AddNewProvider
