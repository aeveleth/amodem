# Python Library Imports
import os
import sys
import re
import serial
import glob
import subprocess

# Modem Project Imports
import atapi
import atcodes
import settings
import errors
import logger

class Commands:
    AT              = atapi.ATAPI()
    ModemSettings   = settings.Settings()
    Logger          = logger.Logger()
    CommandAndArgs  = []

    commandsHelp    = [
            'connect [phone provider]\n    Connect to the network. Uses the specified parameters in the config file.',
            'disconnect\n    Disconnect from the current network.',
            'reconnect\n     Disconnect then reconnect to the current network.',
            'check balance [phone provider]\n    Check the current balance. Uses the USSD code for the phone provider specified in the config file.',
            'check data [phone provider]\n    Check the amount of data left. Uses the USSD code for the phone provider specified in the config file.',
            'buy bundle [phone provider]\n    Buy a bundle. Uses the USSD code for the phone provider specified in the config file.',
            'recharge [phone provider [recharge code]]\n    Recharge account. The recharge code should be 14 digits and all numbers. Uses the USSD code for the phone provider specified in the config file.',
            'topup [phone provider [topup code]]\n    Same as recharge.',
            'ussd [ussd code]\n    Send the given ussd code.',
            'lock status\n    Check if modem is unlocked',
            'get imei\n    Print the IMEI code of the mode',
            'modem status\n    Print modem status',
            'extended info\n    Print modem extended information',
            'show networks\n    Print available networks',
            'signal strength\n    Print the signal strength',
            'send sms [message [phone number]]\n    Send the message to the phone number',
            'list message [message type]\n    List all, unread, read or unsent messages',
            'delete message [message number or type]\n    Delete a given message number or all/unread/read/unsent messages',
            'set provider [phone provider]\n    Set the phone provider for this session.',
            'add provider [phone provider]\n    Add a phone provider to the configuration.',
            'current settings\n    Print the current settings.',
            'change setting [general or provider [phone provider]] [setting] [value]\n    Change a general or provider setting.',
            'save configuration [file name]\n    Save the current configuration to a file.',
            'exit\n    Exit the program.',
            ]

    ####################################################
    ############# Functions Called By Main #############
    ####################################################

    def RunCommand(self, commandAndArgs):
        try:
            if commandAndArgs:
                command = commandAndArgs[0]
                args = commandAndArgs[1:]
                self._commands[command](self, args)
                print
        except KeyboardInterrupt:
            pass
        except SystemExit:
            raise
        except:
            self.Logger.LogMessage(commandAndArgs[0] + ' error:\n{0}'.format(sys.exc_info()[1]), logger.MSG_TYPES.STDOUT)
            print
        # end try/except
    # end RunCommand

    def Initialize(self, Logger, ModemSettings, InitSerialPort):
        self.Logger = Logger
        self.AT.Logger = Logger
        self.ModemSettings = ModemSettings
        if InitSerialPort:
            self.InitializeSerialPort()
        # end if
    # end SetLogger

    def InitializeSerialPort(self):
        initialized = True

        try:
            currentPort = self._getGeneralSetting('ttyport')
            returnedPort = self.AT.Initialize(currentPort, self._getGeneralSetting('modem'))

            if returnedPort == None or returnedPort == '':
                self.Logger.LogMessage('Unable To Determine Serial Port', logger.MSG_TYPES.STDOUT)
                initialized = False
            # end if

            if currentPort != returnedPort:
                self._setGeneralSetting('ttyport', returnedPort)
            # end if
        except Exception as e:
            self.Logger.LogMessage('Error Initializing Serial Port\n{0}'.format(sys.exc_info()[1]), logger.MSG_TYPES.STDOUT)
            initialized = False
        # end try/except

        if not initialized:
            userInput = self.Logger.LogInput('Continue Without Initializing Serial Port (yes/no): ')
            while True:
                if userInput == 'yes' or userInput == 'y':
                    break
                elif userInput == 'no' or userInput == 'n':
                    exit(errors.ERROR_SERIAL_PORT)
                else:
                    userInput = self.Logger.LogInput('Continue Without Initializing Serial Port (yes/no): ')
                # end if
            # end while
            print
        # end if
    # end InitializeSerialPort

    def GetCommand(self, argv=[]):
        if argv != []:
            self.CommandAndArgs = self._matchCommand(argv)
            if self.CommandAndArgs[0] not in self._commands.keys():
                self.Logger.LogMessage('Invalid Command', logger.MSG_TYPES.STDOUT)
            else:
                return self.CommandAndArgs
            # end if
        # end if

        self.Logger.LogMessage('Enter \'cmds\' for available commands', logger.MSG_TYPES.STDOUT)
        self.Logger.LogMessage('Enter \'help\' for command details', logger.MSG_TYPES.STDOUT)
        while True:
            userInput = self.Logger.LogInput('Command: ').lower()

            if userInput.strip() == '':
                continue
            # end if

            inputList = userInput.split(' ')

            if not inputList:
                continue
            # end if

            if inputList[0] == '.':
                if len(self.CommandAndArgs) > 0:
                    print
                    return self.CommandAndArgs
                else:
                    self.Logger.LogMessage('No Commands Run Yet', logger.MSG_TYPES.STDOUT)
                # end if
            elif inputList[0] == 'help' or inputList[0] == 'h':
                print
                self.PrintCommandsHelp()
            elif inputList[0] == 'cmds':
                print
                self._listCommands()
            elif inputList[0] == 'exit' or inputList[0] == 'quit' or inputList[0] == 'q' or inputList[0] == 'x':
                exit(errors.NO_ERROR)
            else:
                self.CommandAndArgs = self._matchCommand(inputList)
                if self.CommandAndArgs[0] in self._commands.keys():
                    print
                    return self.CommandAndArgs
                else:
                    self.Logger.LogMessage('Invalid Command', logger.MSG_TYPES.STDOUT)
                # end if
            # end if
        # end while
    # end GetCommand

    def PrintCommandsHelp(self):
        commandsString = 'Commands:\n'
        for c in self.commandsHelp:
            commandsString += c + '\n'
        # end for
        self.Logger.LogMessage(commandsString, logger.MSG_TYPES.STDOUT)
    # end PrintCommandsHelp

    ####################################################
    ################ Internal Functions ################
    ############ Should Not Be Called By Main ##########
    ####################################################

    def _matchCommand(self, inputList):
        if len(inputList) is 0:
            # this case should never be reached
            return inputList
        elif len(inputList) > 1:
            # check if the first two arguments
            # match a command
            for c in self._commands.keys():
                firstArg = re.escape(inputList[0])
                secondArg = re.escape(inputList[1])
                match = re.search('^' + firstArg + '.* ' + secondArg + '.*', c)
                if match:
                    self.Logger.LogMessage('Command Matched: ' + c, logger.MSG_TYPES.STDOUT)
                    # inputList looks like ["check", "data", "vodafone"]
                    # change it to be ["check data", "vodafone"]
                    inputList[0] = c
                    inputList.pop(1)
                    return inputList
                # end if
            # end for
        # end if

        # check if the first argument matches a command
        for c in self._commands.keys():
            firstArg = re.escape(inputList[0])
            match = re.search('^' + firstArg + '.*', c)
            if match:
                self.Logger.LogMessage('Command Matched: ' + c, logger.MSG_TYPES.STDOUT)
                inputList[0] = c
                return inputList
            # end if
        # end for

        return inputList
    # end _matchCommand


    def _listCommands(self):
        commandsString = 'Commands:\n'
        for c in self._commands.keys():
            commandsString += c + '\n'
        # end for
        self.Logger.LogMessage(commandsString, logger.MSG_TYPES.STDOUT)
    # end _listCommands

    ####################################################
    ################# Sakis3g Commands #################
    ####################################################

    # use sakis3g to connect to the network of the given phone provider
    # argv may contain the phone provider as an optional parameter
    def _connect(self, argv):
        provider = self._getProvider(argv)
        if provider == '':
            return

        sakis3g = self._getGeneralSetting('sakis3g')
        apn = self._getProviderSetting(provider, 'apn')
        apn_user = self._getProviderSetting(provider, 'user')
        apn_pass = self._getProviderSetting(provider, 'pass')
        modem = self._getGeneralSetting('modem')
        usbdriver = self._getGeneralSetting('usbdriver')
        if usbdriver != '':
            usbdriver = ' USBDRIVER="' + usbdriver + '"'
        usbinterface = self._getGeneralSetting('usbinterface')
        if usbinterface != '':
            usbinterface = ' USBINTERFACE="' + usbinterface + '"'

        command = sakis3g + ' -c connect APN="' + apn + '" APN_USER="'+ apn_user + '" APN_PASS="' + apn_pass + '" MODEM="' + modem + '"' + usbdriver + usbinterface

        self._runSubprocess(command, 'Connect')
    # end _connect

    # disconnect from the current network
    # argv is unused
    def _disconnect(self, argv):
        command = self._getGeneralSetting('sakis3g') + ' -c disconnect'
        self._runSubprocess(command, 'Disconnect')
    # end _disconnect

    # disconnect then reconnect to the current network
    # argv is unused
    def _reconnect(self, argv):
        command = self._getGeneralSetting('sakis3g') + ' -c reconnect'
        self._runSubprocess(command, 'Reconnect')
    # end _reconnect

    ####################################################
    ################### ussd Commands ##################
    ####################################################

    # check the current balance on the sim card
    # argv may contain the phone provider as an optional parameter
    # the USSD code for the phone provider is specified in the config file
    def _check_balance(self, argv):
        ttyport = self._getPort()
        if ttyport == '':
            return

        provider = self._getProvider(argv)
        if provider == '':
            return

        checkBalanceUSSD = self._getProviderSetting(provider, 'checkbalance')
        if checkBalanceUSSD == '':
            return

        self.AT.SendUSSD(checkBalanceUSSD)
    # end _check_balance

    def _check_data(self, argv):
        ttyport = self._getPort()
        if ttyport == '':
            return

        provider = self._getProvider(argv)
        if provider == '':
            return

        checkDataUSSD = self._getProviderSetting(provider, 'checkdata')
        if checkDataUSSD == '':
            return

        self.AT.SendUSSD(checkDataUSSD)
    # end _check_data

    # buy a bundle for the sim card
    # argv may contain the phone provider as an optional parameter
    # the USSD code for the phone provider is specified in the config file
    def _buy_bundle(self, argv):
        ttyport = self._getPort()
        if ttyport == '':
            return

        provider = self._getProvider(argv)
        if provider == '':
            return

        buyBundleUSSD = self._getProviderSetting(provider, 'buybundle')
        if buyBundleUSSD == '':
            return

        while self.AT.SendUSSD(buyBundleUSSD):
            buyBundleUSSD = self.Logger.LogInput('Enter Option: ')
            if self._checkForCancelOrExit(buyBundleUSSD):
                return
        # end while
    # end _buy_bundle

    # recharge the sim card
    # the recharge code should be 14 digits and all numbers
    # argv may contain the phone provider as an optional parameter
    # the USSD code for the phone provider is specified in the config file
    def _recharge(self, argv):
        ttyport = self._getPort()
        if ttyport == '':
            return

        provider = self._getProvider(argv)
        if provider == '':
            return

        rechargeCode = self._getRechargeCode(provider, argv)
        if rechargeCode == '':
            return

        self.AT.SendUSSD(rechargeCode)
    # end _recharge

    # help function for _recharge
    # determine the ussd code to send
    # argv may contain the recharge code
    def _getRechargeCode(self, provider, argv):
        rechargeUSSD = self._getProviderSetting(provider, 'recharge')
        if rechargeUSSD == '':
            return

        if argv:
            code = argv.pop(0)
        else:
            code = self.Logger.LogInput('Enter Recharge Code: ')
        # end if

        while len(code) is not 14 and not code.isdigit():
            if self._checkForCancelOrExit(code):
                return ''
            self.Logger.LogMessage('Invalid Recharge Code', logger.MSG_TYPES.STDOUT)
            code = self.Logger.LogInput('Enter Recharge Code: ')
        # end while

        if 'CODE' not in rechargeUSSD:
            return rechargeUSSD[:len(rechargeUSSD)-1] + code + rechargeUSSD[len(rechargeUSSD)-1:]
        else:
            return rechargeUSSD.replace('CODE', code)
        # end if
    # end _getRechargeCode

    def _ussd(self, argv):
        ttyport = self._getPort()
        if ttyport == '':
            return

        ussdCode = self.Logger.LogInput('Enter USSD Code: ')

        while not self._checkForCancelOrExit(ussdCode):
            self.AT.SendUSSD(ussdCode)
            ussdCode = self.Logger.LogInput('Enter USSD Code: ')
        # end while
    # end _ussd

    ####################################################
    ################# Modem AT Commands ################
    ####################################################

    def _set_mode(self, argv):
        modes = '('
        for m in atcodes.ModeValues.keys():
            modes += m + ','
        # end for
        modes = modes[:len(modes)-1] + ')'

        self.Logger.LogMessage('Modes: ' + modes)
        if argv:
            mode = argv.pop(0).lower()
        else:
            mode = self.Logger.LogInput('Enter Mode: ').lower()
        # end if

        while mode not in atcodes.ModeValues.keys():
            if self._checkForCancelOrExit(mode):
                return
            # end if
            self.Logger.LogMessage('Invalid Mode', logger.MSG_TYPES.STDOUT)
            mode = self.Logger.LogInput('Enter Mode: ').lower()
        # end while

        self.AT.SetMode(mode)
    # end _set_mode

    def _set_address(self, argv):
        self.Logger.LogMessage('Address Format (+12345678901 or 12345678901)', logger.MSG_TYPES.STDOUT)
        address = self.Logger.LogInput('Enter An Address: ')

        while True:
            if len(address) is 11 and address.isdigit():
                # matches '12345678901'
                break
            elif len(address) is 12 and address[0] == '+' and address[1:].isdigit():
                # matches '+12345678901'
                break
            elif self._checkForCancelOrExit(address):
                return
            else:
                self.Logger.LogMessage('Invalid Address', logger.MSG_TYPES.STDOUT)
                address = self.Logger.LogInput('Enter An Address: ')
            # end if
        # end while

        self.AT.SetServiceAddress(address)
    # end _set_address

    def _lock_status(self, argv):
        self.AT.LockStatus()
    # end _lock_status

    def _get_imei(self, argv):
        self.AT.GetIMEI()
    # end _get_imei

    def _modem_status(self, argv):
        self.AT.ModemStatus()
    # end _modem_status

    def _extended_info(self, argv):
        self.AT.ModemExtendedInfo()
    # end _extended_info

    def _show_networks(self, argv):
        self.AT.AvailableNetworks()
    # end _show_networks

    def _signal_strength(self, argv):
        self.AT.SignalStrength()
    # end _signal_strength

    def _enter_pin(self, argv):
        if argv:
            pin = argv.pop(0)
        else:
            pin = self.Logger.LogInput('Enter PIN: ')
        # end if

        while not pin.isdigit():
            if self._checkForCancelOrExit(pin):
                return
            pin = self.Logger.LogInput('Enter PIN: ')
        # end while

        self.AT.EnterPIN(pin)
    # end _enter_pin

    def _at_commands(self, argv):
        self.Logger.LogMessage('Type \'cancel\' to quit', logger.MSG_TYPES.STDOUT)
        if argv:
            cmd = argv.pop(0).lower()
        else:
            cmd = self.Logger.LogInput('Enter AT Command: ').lower()
        # end if

        while not self._checkForCancelOrExit(cmd):
            if cmd != '':
                self.AT.ATCommand(cmd)
            # end if
            cmd = self.Logger.LogInput('Enter AT Command: ')
        # end while
    # end _at_commands

    # send an sms message
    # argv may contain the message and the phone number as optional parameters
    def _send_sms(self, argv):
        if argv:
            message = argv.pop(0)
        else:
            message = self.Logger.LogInput('Enter SMS Message: ')
        # end if

        if argv:
            phoneNumber = argv.pop(0)
        else:
            phoneNumber = self.Logger.LogInput('Enter Phone Number: ')
        # end if

        self.AT.SendSMS(phoneNumber, message)
    # end _send_sms

    # check the messages on the sim car
    # argv may be: all, unread, or read
    def _list_messages(self, argv):
        types = '('
        for t in atcodes.MessageTypes.keys():
            types += t + ','
        types = types[:len(types)-1] + ')'

        if argv:
            msgType = argv.pop(0).lower()
        else:
            msgType = self.Logger.LogInput('Enter Message Type ' + types + ': ').lower()
        # end if

        while msgType not in atcodes.MessageTypes.keys():
            if self._checkForCancelOrExit(msgType):
                return
            # end if
            msgType = self.Logger.LogInput('Enter Message Type ' + types + ': ').lower()
        # end while

        self.AT.ListSMS(msgType)
    # end _list_messages

    def _delete_message(self, argv):
        types = '('
        for t in atcodes.MessageTypes.keys():
            types += t + ','
        types = types[:len(types)-1] + ')'

        self.Logger.LogMessage('Delete Message(s)', logger.MSG_TYPES.STDOUT)
        msgToDelete = (self.Logger.GetInput(argv, 'Enter A Message Number or Message Type {0}: '.format(types))).lower()

        while not msgToDelete.isdigit() and msgToDelete not in atcodes.MessageTypes.keys():
            if self._checkForCancelOrExit(msgToDelete):
                return
            # end if
            self.Logger.LogMessage('Invalid Number or Type', logger.MSG_TYPES.STDOUT)
            msgToDelete = self.Logger.LogInput('Enter A Message Number or Message Type {0}: '.format(types)).lower()
        # end while

        self.AT.DeleteSMS(msgToDelete)
    # end _delete_message

    ####################################################
    ################# Settings Commands ################
    ####################################################

    # set the current phone provider for this session
    # argv may contain the phone provider as an optional parameter
    def _set_provider(self, argv):
        self.ModemSettings.DetermineProvider(argv, True)
    # end _set_provider

    def _add_provider(self, argv):
        self.ModemSettings.AddNewProvider(argv)
    # end _add_provider

    def _list_providers(self, argv):
        self.ModemSettings.ListProviders()
    # end _list_providers

    def _current_settings(self, argv):
        self.ModemSettings.PrintCurrentSettings()
    # end _current_settings

    def _change_setting(self, argv):
        userInput = self.Logger.GetInput(argv, 'General or Provider Setting? ')

        while True:
            if re.search('^' + userInput + '.*', 'provider'):
                self.ModemSettings.ChangeProviderSetting(argv)
                break
            elif re.search('^' + userInput + '.*', 'general'):
                self.ModemSettings.ChangeGeneralSetting(argv)
                break
            elif self._checkForCancelOrExit(userInput):
                return
            else:
                userInput = self.Logger.LogInput('General or Provider Setting? ')
            # end if
        # end while
    # end _change_setting

    def _save_configuration(self, argv):
        self.ModemSettings.SaveConfigFile(argv)
    # end _save_configuration

    ####################################################
    ################# Helper Functions #################
    ####################################################

    def _runSubprocess(self, command, name, printCommand=True):
        try:
            if printCommand:
                self.Logger.LogMessage('Running Command: ' + command, logger.MSG_TYPES.STDOUT)
                print
            # end if
            self.Logger.LogMessage(subprocess.check_output(command, shell=True), logger.MSG_TYPES.STDOUT)
        except subprocess.CalledProcessError as e:
            self.Logger.LogMessage('{0} error ({1}):\n{2}'.format(name, e.returncode, e.output), logger.MSG_TYPES.STDOUT)
        # end try/except
    # end _runSubprocess

    # returns the /dev/ttyUSB port that the modem uses
    def _getPort(self):
        if self._getGeneralSetting('ttyport') == '':
            self.Logger.LogMessage('No Port (/dev/ttyUSB) In Settings', logger.MSG_TYPES.STDOUT)
            self.Logger.LogMessage('Checking All /dev/ttyUSB Ports', logger.MSG_TYPES.STDOUT)
            port = self.AT.IdentifyPort()
            self._setGeneralSetting('ttyport', port)
            return port
        else:
            return self._getGeneralSetting('ttyport')
        # end if
    # end _getPort

    def _getProvider(self, argv):
        return self.ModemSettings.DetermineProvider(argv, False)
    # end _getProvider

    def _getProviderSetting(self, provider, setting):
        return self.ModemSettings.GetProviderSetting(provider, setting)
    # end _getProviderSetting

    def _setGeneralSetting(self, setting, value):
        self.ModemSettings.SetGeneralSetting(setting, value)
    # end _setGeneralSetting

    def _getGeneralSetting(self, setting):
        return self.ModemSettings.GetGeneralSetting(setting)
    # end _getGeneralSetting

    def _checkForCancelOrExit(self, string):
        return string == 'cancel' or string == 'exit'
    # end _checkForCancelOrExit

    ####################################################
    ################# List of Commands #################
    ####################################################
    _commands = {
            'connect'            : _connect,
            'disconnect'         : _disconnect,
            'reconnect'          : _reconnect,
            'check balance'      : _check_balance,
            'check data'         : _check_data,
            'buy bundle'         : _buy_bundle,
            'recharge'           : _recharge,
            'topup'              : _recharge,
            'ussd'               : _ussd,
            'set mode'           : _set_mode,
            'set address'        : _set_address,
            'lock status'        : _lock_status,
            'get imei'           : _get_imei,
            'modem status'       : _modem_status,
            'extended info'      : _extended_info,
            'show networks'      : _show_networks,
            'networks'           : _show_networks,
            'signal strength'    : _signal_strength,
            'at commands'        : _at_commands,
            'send sms'           : _send_sms,
            'list messages'      : _list_messages,
            'messages'           : _list_messages,
            'delete message'     : _delete_message,
            'set provider'       : _set_provider,
            'add provider'       : _add_provider,
            'providers'          : _list_providers,
            'current settings'   : _current_settings,
            'change setting'     : _change_setting,
            'save configuration' : _save_configuration,
            }

# end Commands
