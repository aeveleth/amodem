# Python Library Imports
import sys
import os
import time
import serial
import glob
import string
import re
import subprocess

# PyUSB Library
import usb.core
import usb.util

# Modem Project Imports
import atcodes
import logger
import errors

class ATAPI:
    Initialized = False
    SerialPort  = serial.Serial()
    Logger      = logger.Logger()

    ModemID     = ['']

    ####################################################
    ############# Initialization Functions #############
    ####################################################

    def Initialize(self, ttyport, modemid=''):
        if self.Initialized:
            return self.SerialPort.getPort()
        # end if

        if modemid != '':
            self.ModemID[0] = modemid
        # end if

        self.Logger.LogMessage('Initializing Serial Port...', logger.MSG_TYPES.STDOUT)

        if ttyport != '':
            if os.path.exists(ttyport):
                if self._checkPort(ttyport):
                    self.SerialPort = serial.Serial(port=ttyport, timeout=15)
                    ttyport = self.SerialPort.getPort()
                else:
                    self.Logger.LogMessage('Serial Port ({0}) Did Not Respond\n'.format(ttyport), logger.MSG_TYPES.DEBUG)
                # end if
            else:
                self.Logger.LogMessage('Serial Port ({0}) Not Found\n'.format(ttyport), logger.MSG_TYPES.DEBUG)
            # end if
        # end if

        if self.SerialPort.getPort() == None:
            self.IdentifyPort(ttyport)
        # end if

        if self.SerialPort.getPort() != None:
            self.Initialized = True
            self.SetMode('sms', True)
            self.SetServiceAddress(atcodes.service_center_address, True)
            self.Logger.LogMessage('Serial Port \'{0}\' Initialized\n'.format(self.SerialPort.getPort()), logger.MSG_TYPES.STDOUT)
        # end if

        return self.SerialPort.getPort()
    # end Initialize

    # check all '/dev/ttyUSB' ports
    # sets SerialPort to the port identified
    def IdentifyPort(self, alreadytested=''):
        self.Logger.LogMessage('Attempting To Identify Port\n', logger.MSG_TYPES.DEBUG)

        # check if there are any /dev/ttyUSB ports
        # if not and the vendorid and productid of the modem is known
        # then try modprobe which might create the /dev/ttyUSB ports
        if not glob.glob('/dev/ttyUSB*') and self.ModemID[0] != '':
            modemid = self.ModemID[0].split(':')
            vendorid = '0x' + modemid[0]
            productid = '0x' + modemid[1]
            command = 'modprobe usbserial vendor=' + vendorid + ' product=' + productid
            try:
                self.Logger.LogMessage(subprocess.check_output(command, shell=True), logger.MSG_TYPES.STDOUT)
            except subprocess.CalledProcessError as e:
                self.Logger.LogMessage('modprobe error ({1}): \n{2}'.format(e.returncode, e.output), logger.MSG_TYPES.STDOUT)
            # end try/except
        # end if

        for p in glob.glob('/dev/ttyUSB*'):
            if p == alreadytested:
                continue
            # end if

            if self._checkPort(p):
                self.SerialPort = serial.Serial(port=p, timeout=15)
                return
            # end if
        # end for

        self.Logger.LogMessage('Unable To Identify Port\n', logger.MSG_TYPES.DEBUG)
        self.SerialPort = serial.Serial()
    # end IdentifyPort

    ####################################################
    ################ Internal Functions ################
    ######### Should Not Be Called By amodemcmds ########
    ####################################################

    # These modems seem to open 3 USB serial ports.
    # Only one is the control port and this seems to vary from device to device.
    # The other 2 ports appear to remain silent
    def _checkPort(self, ttyport):
        self.Logger.LogMessage('Checking Serial Port \'{0}\''.format(ttyport), logger.MSG_TYPES.DEBUG)
        with serial.Serial(port=ttyport,timeout=15) as sp:
            sp.flushInput()
            sp.flushOutput()

            self.Logger.LogMessage('Writing {0} To Serial Port'.format(repr(atcodes.Commands['at'])), logger.MSG_TYPES.DEBUG)
            sp.write(atcodes.Commands['at'])

            response = sp.readline()
            # some modems will continuously print information
            # ignore it and look for something relevant to AT
            while re.match('^\^', response) or response == '\r\n':
                response = sp.readline()
            # end while

            if 'AT' in response:
                # 'OK' should be the next line
                response = sp.readline()
            # end if

            self.Logger.LogMessage('AT Response: {0}\n'.format(repr(response)), logger.MSG_TYPES.DEBUG)

            if 'OK' in response:
                sp.close()
                return True
            # end if
        # end with
        return False
    # end _checkPort

    def _readATResponse(self):
        if self.Initialize('') == None:
            self.Logger.LogMessage('Could Not Initialize Serial Port', logger.MSG_TYPES.STDOUT)
            return ''
        # end if

        response = self.SerialPort.readline()

        # some modems will continuously print information
        # ignore it and look for something relevant to AT
        while re.match('^\^', response) or response == '\r\n':
            response = self.SerialPort.readline()
        # end while

        self.Logger.LogMessage('AT Response: {0}\n'.format(repr(response)), logger.MSG_TYPES.DEBUG)
        return response.strip()
    # end _readATResponse

    # check that the command has been written
    def _checkCmdWrite(self, command):
        if self.Initialize('') == None:
            self.Logger.LogMessage('Could Not Initialize Serial Port', logger.MSG_TYPES.STDOUT)
            return False
        # end if

        serialOutput = self.SerialPort.readline()

        # some modems will continuously print information
        # ignore it and look for something relevant to AT
        while re.match('^\^', serialOutput) or serialOutput == '\r\n':
            serialOutput = self.SerialPort.readline()
        # end while

        if command.strip() not in serialOutput:
            self.Logger.LogMessage('Unexpected Serial Output: {0}'.format(repr(serialOutput)), logger.MSG_TYPES.STDOUT)
            return False
        # end if

        return True
    # end _checkCmdWrite

    def _writeATCmd(self, commandName, formatArgs=''):
        try:
            if formatArgs != '':
                command = atcodes.Commands[commandName].format(formatArgs)
            else:
                command = atcodes.Commands[commandName]
            # end if
        except KeyError:
            self.Logger.LogMessage('Invalid Command: {0}\n'.format(commandName), logger.MSG_TYPES.DEBUG)
            return False
        except:
            print 'Error\n', sys.exc_info()[1]
        # end try/except

        if not self._write(command):
            return False

        #return self._checkCmdWrite(command)
        return True
    # end _writeATCmd

    def _write(self, message, flushInput=True):
        if self.Initialize('') == None:
            self.Logger.LogMessage('Could Not Initialize Serial Port', logger.MSG_TYPES.STDOUT)
            return False
        # end if

        if flushInput:
            self.SerialPort.flushInput()
        # end if

        self.Logger.LogMessage('Writing {0} to serial port'.format(repr(message)), logger.MSG_TYPES.DEBUG)
        writtenLength = self.SerialPort.write(message)
        if writtenLength is not len(message):
            self.Logger.LogMessage('Serial Port Write Length Mismatch', logger.MSG_TYPES.DEBUG)
        # end if

        return True
    # end _write

    def _endOfResponse(self, response):
        for s in ['OK', 'ERROR', 'NO CARRIER']:
            if s in response:
                return True
            # end if
        # end for
        return False
    # end _endOfResponse

    def _runCommand(self, commandName, formatArgs=''):
        if not self._writeATCmd(commandName, formatArgs):
            return ''
        # end if

        response = self._readATResponse()
        if commandName in response:
            response = self._readATResponse()

        while True:
            if self._endOfResponse(response):
                break
            # end if
            nextLine = self._readATResponse()
            if nextLine == '':
                break
            # end if
            response += '\n' + nextLine
        # end while

        self.Logger.LogMessage(response, logger.MSG_TYPES.DEBUG)
        return response
    # end _runCommand

    def _matchError(self, response):
        if response == 'ERROR':
            return (response, True)
        # end if

        result = response

        match = atcodes.ResponsesRegex['cms_error'].match(response)
        if match:
            errorno = match.group(1)

            try:
                errorstr = errors.CMSErrorCodes[errorno]
                result = 'CMS Error ({0}):\n{1}'.format(errorno, errorstr)
            except KeyError:
                result = 'CMS Error {0}'.format(errorno)
            # end try/except
        else:
            match = atcodes.ResponsesRegex['cme_error'].match(response)
            if match:
                errorno = match.group(1)

                try:
                    errorstr = errors.CMEErrorCodes[errorno]
                    result = 'CME Error ({0}):\n{1}'.format(errorno, errorstr)
                except KeyError:
                    result = 'CME Error {0}'.format(errorno)
                # end try/except
            # end if
        # end if

        return (result, result != response)
    # end _matchError


    ####################################################
    ########## Functions Called By amodemcmds ###########
    ####################################################

    def ATCommand(self, command):
        cmd = command if '\r\n' in command else command.strip() + '\r\n'

        self._write(cmd)

        response = self._readATResponse()
        if cmd in response:
            response = self._readATResponse()
        # end if

        while True:
            if self._endOfResponse(response):
                break
            # end if
            nextLine = self._readATResponse()
            if nextLine == '':
                break
            # end if
            response += '\n' + nextLine
        # end while

        self.Logger.LogMessage(response, logger.MSG_TYPES.STDOUT)
        return self._matchError(response)
    # end ATCommand

    def SetMode(self, mode, init=False):
        mode = mode.lower()
        if mode not in atcodes.ModeValues.keys():
            result = 'Invalid Mode: {0}'.format(mode)
            self.Logger.LogMessage(result, logger.MSG_TYPES.DEBUG)
            return (result, True)
        # end if

        response = self._runCommand('setmode', atcodes.ModeValues[mode])
        if 'OK' in response:
            msgType = logger.MSG_TYPES.DEBUG if init else logger.MSG_TYPES.STDOUT
            result = 'Mode Set: {0}'.format(mode)
            self.Logger.LogMessage(result, msgType)
            return (result, False)
        else:
            self.Logger.LogMessage('Unable To Set Mode {0}:\n{1}'.format(mode, response), logger.MSG_TYPES.STDOUT)
            return self._matchError(response)
        # end if
    # end SetMode

    def SetServiceAddress(self, address, init=False):
        response = self._runCommand('csca', address)
        if 'OK' in response:
            msgType = logger.MSG_TYPES.DEBUG if init else logger.MSG_TYPES.STDOUT
            result = 'Customer Service Address Set: {0}'.format(address)
            self.Logger.LogMessage(result, msgType)
            return (result, False)
        else:
            self.Logger.LogMessage('Unable To Set Customer Service Address {0}:\n{1}'.format(address, response), logger.MSG_TYPES.STDOUT)
            return self._matchError(response)
        # end if
    # end SetServiceAddress

    def EnterPIN(self, pin):
        response = self._runCommand('enterpin', pin)
        self.Logger.LogMessage('PIN Entered', logger.MSG_TYPES.STDOUT)
    # end EnterPIN

    def LockStatus(self):
        response = self._runCommand('cardlock')
        match = atcodes.ResponsesRegex['cardlock'].match(response)
        if match:
            lockStatus = int(match.group(1))
            remaining = int(match.group(2))
            carrier = int(match.group(3))

            result = 'Lock Status: {0}\nAttempts Remaining: {1}\nCarrier: {2}'.format(lockStatus, remaining, carrier)
            self.Logger.LogMessage(result, logger.MSG_TYPES.STDOUT)
            return (result, False)
        else:
            self.Logger.LogMessage('Card Lock Response: {0}'.format(response), logger.MSG_TYPES.STDOUT)
            return self._matchError(response)
        # end if
    # end LockStatus

    def AvailableNetworks(self):
        response = self._runCommand('networks')
        match = atcodes.ResponsesRegex['networks'].match(response)
        if match:
            mode = match.group(1)
            formatNum = match.group(2)
            networkName = match.group(3)
            status = match.group(4)

            try:
                networkMode = atcodes.NetworkModes[mode] + ' (' + mode + ')'
            except KeyError:
                networkMode = mode
            # end try/except

            try:
                networkFormat = atcodes.NetworkFormats[formatNum] + ' (' + formatNum + ')'
            except KeyError:
                networkFormat = formatNum
            # end try/except

            try:
                networkStatus = atcodes.NetworkStatuses[status] + ' (' + status + ')'
            except KeyError:
                networkStatus = status
            # end try/except

            result = 'Mode: {0}\nFormat: {1}\nNetwork: {2}\nStatus: {3}\n'.format(networkMode, networkFormat, networkName, networkStatus)
            self.Logger.LogMessage(result, logger.MSG_TYPES.STDOUT)
            return (result, False)
        else:
            self.Logger.LogMessage(response, logger.MSG_TYPES.STDOUT)
            return self._matchError(response)
        # end if
    # end AvailableNetworks

    def GetIMEI(self):
        response = self._runCommand('getimei').strip('OK\r\n')
        self.Logger.LogMessage('IMEI: {0}'.format(response), logger.MSG_TYPES.STDOUT)
        return self._matchError(response)
    # end GetIMEI

    def ModemStatus(self):
        response = self._runCommand('status').strip('OK\r\n')
        self.Logger.LogMessage(response, logger.MSG_TYPES.STDOUT)
        return self._matchError(response)
    # end ModemStatus

    def ModemExtendedInfo(self):
        response = self._runCommand('extendedinfo').strip('OK\r\n')
        (rsp, error) = self._matchError(response)
        if error:
            self.Logger.LogMessage(rsp, logger.MSG_TYPES.STDOUT)
            return (rsp, error)
        else:
            response = response.replace(';', '\n')
            self.Logger.LogMessage(response, logger.MSG_TYPES.STDOUT)
            return (response, False)
        # end if
    # end ModemExtendedInfo

    def SignalStrength(self):
        response = self._runCommand('signalstrength')
        match = atcodes.ResponsesRegex['signalstrength'].match(response)
        if match:
            rssi = int(match.group(1))
            ber = match.group(2)

            if rssi is 99:
                signal = 'Unknown'
            elif rssi >= 20:
                signal = 'Very Good'
            elif rssi >= 15:
                signal = 'Good'
            elif rssi >= 10:
                signal = 'Average'
            elif rssi >= 6:
                signal = 'Bad'
            elif rssi >= 1:
                signal = 'Very Bad'
            else:
                signal = 'No'
            # end if

            result = 'RSSI: {0} Signal ({1})\nBER: {2}'.format(signal, rssi, ber)
            self.Logger.LogMessage(result, logger.MSG_TYPES.STDOUT)
            return (result, False)
        else:
            self.Logger.LogMessage(response, logger.MSG_TYPES.STDOUT)
            return self._matchError(response)
        # end if
    # end SignalStrength

    def SendSMS(self, phoneNumber, message):
        # Send the CMGW command to write the message to memory
        self._writeATCmd('write', phoneNumber)

        # Port prompts with '>' for message
        # Write message with CTRL-Z to indicate message is finished
        time.sleep(1)
        msg = message + '\x1A\r\n' # message + CTRL-Z + \r\n
        self._write(msg, False)

        # Check for message
        response = self._readATResponse()
        if message not in response:
            self.Logger.LogMessage('Unexpected Serial Output: {0}'.format(response), logger.MSG_TYPES.STDOUT)
        # end if

        # Retrieve the index where the message was written
        match = atcodes.ResponsesRegex['write'].match(response)
        if not match:
            self.Logger.LogMessage('Could not find index of written message', logger.MSG_TYPES.STDOUT)
            return
        # end if

        # Send the CMSS command with the index to send the message
        self._runCommand('send', match.group(1))
    # end SendSMS

    def ListSMS(self, msgType):
        response = self._runCommand('list', atcodes.MessageTypes[msgType])
        if '+CMGL' in response:
            messages = response.split('+CMGL: ')
            messages = messages[1:]
            for m in messages:
                msgSplit = m.split(',')
                msgNum = msgSplit[0]
                msgType = msgSplit[1]
                msgPhoneNum = msgSplit[2]
                msg = msgSplit[4]
                if len(msgSplit) > 4:
                    for i in range(5,len(msgSplit)):
                        msg += ',' + msgSplit[i]
                    # end for
                # end if
                self.Logger.LogMessage('\nNumber: {0}\nType: {1}\nPhone Number: {2}\nMessage: {3}'.format(msgNum, msgType, msgPhoneNum, msg), logger.MSG_TYPES.STDOUT)
            # end for
        elif 'OK' in response:
            self.Logger.LogMessage('No Messages', logger.MSG_TYPES.STDOUT)
        else:
            self.Logger.LogMessage('Unable To List Messages: {0}\n{1}'.format(msgType, response), logger.MSG_TYPES.STDOUT)
        # end if
    # end ListSMS

    def DeleteSMS(self, msgToDelete):
        if msgToDelete in atcodes.MessageTypes.keys():
            messagesToDelete = []
            response = self._runCommand('list', atcodes.MessageTypes[msgToDelete])
            if '+CMGL' in response:
                messages = response.split('+CMGL: ')
                for m in messages:
                    msgSplit = m.split(',')
                    messagesToDelete.append(msgSplit[0])
                # end for
            # end if

            while len(messagesToDelete) > 0:
                msgNum = str(messagesToDelete.pop())
                if msgNum != '':
                    self.Logger.LogMessage('Deleting Message: {0}'.format(msgNum), logger.MSG_TYPES.STDOUT)
                    response = self._runCommand('delete', msgNum)
                    if 'OK' not in response:
                        self.Logger.LogMessage('Unable To Delete Message', logger.MSG_TYPES.STDOUT)
                    # end if
                # end if
            # end while
        else:
            response = self._runCommand('delete', msgToDelete)
            if 'OK' in response:
                self.Logger.LogMessage('Message Deleted', logger.MSG_TYPES.STDOUT)
            else:
                self.Logger.LogMessage('Unable To Delete Message', logger.MSG_TYPES.STDOUT)
            # end if
        # end if
    # end DeleteSMS

    def SendUSSD(self, ussdCode):
        shouldRespond = 0
        responseError = False
        self.Logger.LogMessage('Sending USSD Code {0}\n'.format(ussdCode), logger.MSG_TYPES.STDOUT)
        response = self._runCommand('ussd', ussdCode)

        if 'OK' in response:
            response = self._readATResponse()
            if response == '':
                response = 'Response Timeout'
                responseError = True
            else:
                while True:
                    match = atcodes.ResponsesRegex['ussd'].match(response)
                    if match:
                        shouldRespond = int(match.group(1))
                        message = match.group(2)
                        dcs = int(match.group(3))

                        response = 'Reply:\n{0}'.format(message)
                        break
                    # end if
                    nextLine = self._readATResponse()
                    if nextLine == '':
                        break
                    # end if
                    response += '\n' + nextLine
                # end while
                (response, responseError) = self._matchError(response)
            # end if
        else:
            (response, responseError) = self._matchError(response)
        # end if

        self.Logger.LogMessage(response + '\n', logger.MSG_TYPES.STDOUT)
        # if the first number in the reply is 1, the remote server is looking for a response
        return (response, shouldRespond==1, responseError)
        #return shouldRespond == 1
    # end SendUSSD

# end ATAPI
