# Python Library Imports
import sys
import re
import os

# Modem Project Imports
import logger
import errors

class Settings:
    GeneralSettings = {
            'modem'        : '',
            'ttyport'      : '',
            'sakis3g'      : '',
            'usbdriver'    : '',
            'usbinterface' : '',
            }

    GeneralSettingsNames = {
            'Modem'            : 'modem',
            'TTY Port'         : 'ttyport',
            'Sakis3g Location' : 'sakis3g',
            'USB Driver'       : 'usbdriver',
            'USB Interface'    : 'usbinterface',
            }

    DefaultSettings = {
            'modem'        : '',
            'ttyport'      : '/dev/ttyUSB0',
            'sakis3g'      : '/usr/local/bin/sakis3g',
            'usbdriver'    : '',
            'usbinterface' : '',
            }

    CursesSettings = {
            'menu_width'  : '25',
            'menu_height' : '14',
            }

    Providers = {} # list of phone providers

    ProviderSettingList = [
            'apn',
            'checkbalance',
            'checkdata',
            'user',
            'pass',
            'pin',
            'recharge',
            'buybundle'
            ]

    ProviderSettingsNames = {
            'Access Point Name'  : 'apn',
            'Check Balance USSD' : 'checkbalance',
            'Check Data USSD'    : 'checkdata',
            'User'               : 'user',
            'Password'           : 'pass',
            'SIM PIN'            : 'pin',
            'Recharge USSD'      : 'recharge',
            'Buy Bundle USSD'    : 'buybundle',
            }

    CurrentProvider = ['']

    ConfigFileName = ['~/.amodemrc']

    Logger = logger.Logger()

    #############################################################
    ################## Get and Set Settings #####################
    #############################################################

    def GetConfigFileName(self):
        return self.ConfigFileName[0]
    # end GetConfigFileName

    def GetGeneralSetting(self, setting):
        return self.GeneralSettings[setting]
    # end GetGeneralSetting

    def SetGeneralSetting(self, setting, value):
        self.GeneralSettings[setting] = value
    # end SetGeneralSetting

    def ChangeGeneralSetting(self, argv):
        currentSettings = 'Current General Settings:\n'
        for setting, value in self.GeneralSettings.items():
            currentSettings += '  ' + setting + ': ' + value + '\n'
        # end for
        self.Logger.LogMessage(currentSettings, logger.MSG_TYPES.STDOUT)

        self.Logger.LogMessage('Enter \'cancel\' to quit', logger.MSG_TYPES.STDOUT)
        settingToChange = argv.pop(0) if len(argv) > 0 else self.Logger.LogInput('Setting To Change: ')
        while settingToChange not in self.GeneralSettings:
            if settingToChange == 'cancel':
                return
            # end if
            self.Logger.LogMessage('Invalid Setting')
            settingToChange = self.Logger.LogInput('Setting To Change: ')
        # end for

        settingValue = argv.pop(0) if len(argv) > 0 else self.Logger.LogInput('Enter New Value: ')
        if settingValue == 'cancel':
            return
        # end if

        self.SetGeneralSetting(settingToChange, settingValue)

        self.Logger.LogMessage('Setting \'{0}\' Changed to \'{1}\''.format(settingToChange, settingValue), logger.MSG_TYPES.STDOUT)

        self.SaveConfigFile()
    # end ChangeGeneralSetting

    # called my main to set the current provider for the session
    # the provider is given on the command line and the config
    # file might not have been loaded yet
    def SetCurrentProvider(self, provider):
        self.CurrentProvider[0] = provider
    # end SetCurrentProvider

    def GetCurrentProvider(self):
        return self.CurrentProvider[0]
    # end GetCurrentProvider

    # determine the provider to use
    # argv may contain the provider
    # self.CurrentProvider may be set
    def DetermineProvider(self, argv, setCurrent=False):
        if len(self.Providers) == 0:
            self.Logger.LogMessage('No Phone Providers In Current Settings')
            self.AddNewProvider([])
            if len(self.Providers) == 0:
                return ''
            # end if
        # end if

        if argv:
            provider = argv.pop(0)
        elif not setCurrent and self.CurrentProvider[0] != '':
            provider = self.CurrentProvider[0]
        else:
            self.Logger.LogMessage('Enter \'list\' to show available phone providers', logger.MSG_TYPES.STDOUT)
            provider = self.Logger.LogInput('Enter Phone Provider: ').lower()
            self.Logger.LogMessage('', logger.MSG_TYPES.STDOUT)
        # end if

        while provider not in self.Providers.keys():
            if provider == 'list':
                self.ListProviders()
            elif provider == 'cancel':
                provider = ''
                break
            else:
                self.Logger.LogMessage('Invalid Phone Provider\n', logger.MSG_TYPES.STDOUT)
            # end if
            provider = self.Logger.LogInput('Enter Phone Provider: ').lower()
        # end while

        if provider != '':
            self.CurrentProvider[0] = provider
        # end if

        return provider
    # end DetermineProvider

    def GetProviderSetting(self, provider, setting):
        if setting not in self.ProviderSettingList:
            self.Logger.LogMessage('Invalid Provider Setting', logger.MSG_TYPES.STDOUT)
            return ''
        elif provider not in self.Providers.keys():
            self.Logger.LogMessage('Invalid Provider', logger.MSG_TYPES.STDOUT)
            return ''
        else:
            index = self.ProviderSettingList.index(setting)
            if self.Providers[provider][index] == '':
                self.Logger.LogMessage('Setting \'{0}\' For Provider \'{1}\' Is Empty'.format(setting, provider), logger.MSG_TYPES.STDOUT)
                settingValue = self.Logger.LogInput('Enter Setting Value: ')
                if settingValue == 'cancel' or settingValue == '':
                    return ''
                self.Providers[provider][index] = settingValue
            # end if
            return self.Providers[provider][index]
        # end if
    # end GetProviderSetting

    def GetProviderSetting2(self, provider, setting):
        index = self.ProviderSettingList.index(setting)
        return self.Providers[provider][index]
    # end GetProviderSetting2

    def ChangeProviderSetting(self, argv):
        provider = argv.pop(0) if len(argv) > 0 else self.Logger.LogInput('Enter Provider: ')
        while provider not in self.Providers.keys():
            if provider == 'cancel':
                return
            # end if
            self.Logger.LogMessage('Invalid Provider', logger.MSG_TYPES.STDOUT)
            provider = self.Logger.LogInput('Enter Provider: ')
        # end while

        currentSettings = 'Current Settings For ' + provider + ':\n'
        for setting in self.ProviderSettingList:
            index = self.ProviderSettingList.index(setting)
            currentSettings += '  ' + setting + ': ' + self.Providers[provider][index] + '\n'
        # end for
        self.Logger.LogMessage(currentSettings, logger.MSG_TYPES.STDOUT)

        self.Logger.LogMessage('Enter \'cancel\' to quit', logger.MSG_TYPES.STDOUT)
        setting = argv.pop(0) if len(argv) > 0 else self.Logger.LogInput('Setting To Change: ')
        while setting not in self.ProviderSettingList:
            if setting == 'cancel':
                return
            # end if
            self.Logger.LogMessage('Invalid Setting')
            setting = self.Logger.LogInput('Setting To Change: ')
        # end for

        index = self.ProviderSettingList.index(setting)

        settingValue = argv.pop(0) if len(argv) > 0 else self.Logger.LogInput('Enter New Value: ')
        if settingValue == 'cancel':
            return
        # end if

        self.Providers[provider][index] = settingValue

        self.Logger.LogMessage('Setting \'{0}\' Changed to \'{1}\''.format(setting, settingValue), logger.MSG_TYPES.STDOUT)

        self.SaveConfigFile()
    # end ChangeProviderSetting

    def AddNewProvider(self, argv):
        newProvider = self.Logger.GetInput(argv, 'Enter A Name For A New Phone Provider: ')
        if newProvider == 'cancel':
            return

        tempSettingList = []
        for setting in self.ProviderSettingList:
            settingValue = self.Logger.GetInput(argv, 'Setting \'{0}\' Value: '.format(setting))
            tempSettingList.append(settingValue)
        # end for

        self.Providers[newProvider] = tempSettingList
        self.Logger.LogMessage('New Provider \'{0}\' Added'.format(newProvider), logger.MSG_TYPES.STDOUT)

        if argv:
            self.SaveConfigFile(argv.pop(0))
        else:
            self.SaveConfigFile()
        # end if
    # end AddNewProvider

    def ListProviders(self):
        providerList = 'Providers:'
        for p in self.Providers.keys():
            providerList += '    ' + p + '\n'
        # end for
        providerList.rstrip('\n')
        self.Logger.LogMessage(providerList, logger.MSG_TYPES.STDOUT)
    # end ListProviders

    def PrintCurrentSettings(self):
        currentSettings = 'Current Provider Set: ' + self.CurrentProvider[0] + '\n\n'
        currentSettings += 'Current General Settings:\n'
        for setting, value in self.GeneralSettings.items():
            currentSettings += '  ' + setting + ': ' + value + '\n'
        # end for

        for provider in self.Providers:
            currentSettings += '\nCurrent Settings For ' + provider + ':\n'
            for setting in self.ProviderSettingList:
                index = self.ProviderSettingList.index(setting)
                currentSettings += '  ' + setting + ': ' + self.Providers[provider][index] + '\n'
            # end for
        # end for

        self.Logger.LogMessage(currentSettings, logger.MSG_TYPES.STDOUT)
    # end PrintCurrentSettings

    #############################################################
    ######## Loading and Processing Configuration File ##########
    #############################################################

    def SaveConfigFile(self, fileNameToSave=None):
        if fileNameToSave == None:
            userInput = self.Logger.LogInput('Save Configuration (yes/no): ')
            while True:
                if userInput == 'yes' or userInput == 'y':
                    break
                elif userInput == 'no' or userInput == 'n':
                    return
                else:
                    userInput = self.Logger.LogInput('Save Configuration (yes/no): ')
                # end if
            # end while

            userInput = self.Logger.LogInput('Save To Loaded Config File \'{0}\' (yes/no): '.format(self.ConfigFileName[0]))
            while True:
                if userInput == 'yes' or userInput == 'y':
                    fileNameToSave = self.ConfigFileName[0]
                    break
                elif userInput == 'no' or userInput == 'n':
                    fileNameToSave = self.Logger.LogInput('Enter Config File Name: ')
                    break
                elif userInput == 'cancel':
                    return
                else:
                    userInput = self.Logger.LogInput('Save To Loaded Config File \'{0}\' (yes/no): '.format(self.ConfigFileName[0]))
                # end if
            # end while
        # end if

        fileNameToSave = os.path.abspath(os.path.expandvars(os.path.expanduser(fileNameToSave)))
        if fileNameToSave != self.ConfigFileName[0]:
            self.ConfigFileName[0] = fileNameToSave
        # end if

        self.Logger.LogMessage('Saving Config File: {0}'.format(self.ConfigFileName[0]), logger.MSG_TYPES.STDOUT)

        try:
            with open(self.ConfigFileName[0], mode='w') as configFile:
                self.Logger.LogMessage('[Settings]', logger.MSG_TYPES.DEBUG)
                configFile.write('[Settings]\n')
                for setting, value in self.GeneralSettings.items():
                    line = '{0}=\"{1}\"'.format(setting, value)
                    self.Logger.LogMessage(line, logger.MSG_TYPES.DEBUG)
                    configFile.write(line + '\n')
                # end for
                line = 'provider=\"{0}\"\n'.format(self.CurrentProvider[0])
                self.Logger.LogMessage(line, logger.MSG_TYPES.DEBUG)
                configFile.write(line)

                self.Logger.LogMessage('\n[Curses]', logger.MSG_TYPES.DEBUG)
                configFile.write('\n[Curses]\n')
                for setting, value in self.CursesSettings.items():
                    line = '{0}=\"{1}\"'.format(setting, value)
                    self.Logger.LogMessage(line, logger.MSG_TYPES.DEBUG)
                    configFile.write(line + '\n')
                # end for

                for provider in self.Providers:
                    self.Logger.LogMessage('\n[{0}]'.format(provider), logger.MSG_TYPES.DEBUG)
                    configFile.write('\n[{0}]\n'.format(provider))
                    for setting in self.ProviderSettingList:
                        index = self.ProviderSettingList.index(setting)
                        self.Logger.LogMessage('{0}=\"{1}\"'.format(setting, self.Providers[provider][index]), logger.MSG_TYPES.DEBUG)
                        configFile.write('{0}=\"{1}\"\n'.format(setting, self.Providers[provider][index]))
                    # end for
                # end for

            # end with
        except IOError as e:
            self.Logger.LogMessage('Config File IO Error ({0}): {1}'.format(e.errno, e.strerror), logger.MSG_TYPES.STDOUT)
            exit(errors.ERROR_CONFIG_IO)
        except:
            raise
        # end try/except
    # end SaveConfigFile

    def _processGeneralSettings(self, settings):
        self.Logger.LogMessage('  Processing General Settings', logger.MSG_TYPES.DEBUG)
        for setting in self.GeneralSettings.keys():
            match = re.search(setting + '=\"([^\"]*)\"', settings)
            if not match:
                match = re.search(setting + '=\'([^\']*)\'', settings)
            # end if

            if self.GeneralSettings[setting] == '':
                # setting has not already been set on the command line
                if match:
                    # found the setting in the config file
                    self.GeneralSettings[setting] = match.group(1)
                else:
                    # setting not found in config file
                    # use default setting
                    self.GeneralSettings[setting] = self.DefaultSettings[setting]
                # end if
            # end if

            self.Logger.LogMessage('    {0}: {1}'.format(setting, self.GeneralSettings[setting]), logger.MSG_TYPES.DEBUG)
        # end for

        match = re.search('provider=\"([^\"]*)\"', settings)
        if not match:
            match = re.search('provider=\'([^\']*)\'', settings)
        # end if

        if match:
            self.Logger.LogMessage('    provider: {0}'.format(match.group(1)), logger.MSG_TYPES.DEBUG)
            if self.CurrentProvider[0] == '':
                # if provider was not set on the command line
                # use the default provider in the config file
                self.CurrentProvider[0] = match.group(1)
            else:
                # if provider was set on the command line
                # save the provider given in the config file
                # in case the command line provider is invalid
                self.CurrentProvider.append(match.group(1))
            # end if
        # end if

        self.Logger.LogMessage('  General Settings Loaded', logger.MSG_TYPES.DEBUG)
    # end _processGeneralSettings

    def _processCursesSettings(self, settings):
        self.Logger.LogMessage('  Processing Curses Settings', logger.MSG_TYPES.DEBUG)
        for setting in self.CursesSettings.keys():
            match = re.search(setting + '=\"([^\"]*)\"', settings)
            if not match:
                match = re.search(setting + '=\'([^\']*)\'', settings)
            # end if

            if match:
                # found the setting in the config file
                self.CursesSettings[setting] = match.group(1)
            # end if
            self.Logger.LogMessage('    {0}: {1}'.format(setting, self.CursesSettings[setting]), logger.MSG_TYPES.DEBUG)
        # end for

        self.Logger.LogMessage('  Curses Settings Loaded', logger.MSG_TYPES.DEBUG)
    # end _processCursesSettings

    def _processProviderSettings(self, providerName, providerSetting):
        self.Logger.LogMessage('  Processing: {0}'.format(providerName), logger.MSG_TYPES.DEBUG)

        tempSettingList = []
        for setting in self.ProviderSettingList:
            settingValue = ''
            match = re.search(setting + '=\"([^\"]*)\"', providerSetting)
            if not match:
                match = re.search(setting + '=\'([^\']*)\'', providerSetting)
            # end if

            if match:
                settingValue = match.group(1)
                self.Logger.LogMessage('    {0}: {1}'.format(setting, settingValue), logger.MSG_TYPES.DEBUG)
            # end if

            tempSettingList.append(settingValue)
        # end for

        self.Providers[providerName] = tempSettingList
        self.Logger.LogMessage('  Provider {0} Loaded'.format(providerName), logger.MSG_TYPES.DEBUG)
    # end _processProviderSettings

    def _processConfigFile(self, configFile):
        sections = configFile.split('[')
        for section in sections:
            if section == '':
                continue
            # end if
            match = re.search('[^\]]*', section)
            if match:
                sectionName = match.group()
                sectionData = section.strip(sectionName + ']')
                sectionName = sectionName.lower()
                if sectionName == 'settings' or sectionName == 'general':
                    self._processGeneralSettings(sectionData)
                elif sectionName == 'curses':
                    self._processCursesSettings(sectionData)
                else:
                    self._processProviderSettings(sectionName, sectionData)
                # end if
            # end if
        # end for

        # check to make sure the provider set in the config file
        # or the command line is in the list of providers
        if self.CurrentProvider[0] != '':
            if self.CurrentProvider[0] not in self.Providers.keys():
                if len(self.CurrentProvider) > 1:
                    self.Logger.LogMessage('Invalid Provider: {0}'.format(self.CurrentProvider[0]), logger.MSG_TYPES.STDOUT)
                    self.CurrentProvider[0] = self.CurrentProvider.pop(1)
                    if self.CurrentProvider[0] not in self.Providers.keys():
                        self.Logger.LogMessage('Invalid Provider: {0}'.format(self.CurrentProvider[0]), logger.MSG_TYPES.STDOUT)
                        self.CurrentProvider[0] = ''
                    else:
                        self.Logger.LogMessage('Current Provider: {0}'.format(self.CurrentProvider[0]), logger.MSG_TYPES.STDOUT)
                    # end if
                else:
                    self.Logger.LogMessage('Invalid Provider: {0}'.format(self.CurrentProvider[0]), logger.MSG_TYPES.STDOUT)
                    self.CurrentProvider[0] = ''
                # end if
            elif len(self.CurrentProvider) > 1:
                # provider given on the command line is valid
                self.CurrentProvider.pop(1)
            # end if
        # end if
    # end _processConfigFile

    def SetConfigFileName(self, fileName):
        self.ConfigFileName[0] = fileName
    # end SetConfigFileName

    def LoadConfigFile(self):
        self.ConfigFileName[0] = os.path.abspath(os.path.expandvars(os.path.expanduser(self.ConfigFileName[0])))
        self.Logger.LogMessage('Loading Config File: {0}'.format(self.ConfigFileName[0]), logger.MSG_TYPES.DEBUG)

        try:
            if not os.path.exists(self.ConfigFileName[0]):
                self.Logger.LogMessage('Config File \'{0}\' does not exists'.format(self.ConfigFileName[0]), logger.MSG_TYPES.STDOUT)
                exit(errors.ERROR_CONFIG_IO)
            # end if

            with open(self.ConfigFileName[0], mode='r') as configFile:
                output = ''
                while True:
                # keep reading until the whole file is read
                    temp = configFile.read()
                    if temp == '':
                        break
                    else:
                        output += temp
                    # end if
                # end while
                self._processConfigFile(output)
                self.Logger.LogMessage('Config File Loaded', logger.MSG_TYPES.DEBUG)
            # end with (file handle is closed)
        except IOError as e:
            self.Logger.LogMessage('Config File IO Error ({0}): {1}'.format(e.errno, e.strerror), logger.MSG_TYPES.STDOUT)
            exit(errors.ERROR_CONFIG_IO)
        except:
            raise
        # end try/except
    # end LoadConfigFile

# end Settings
