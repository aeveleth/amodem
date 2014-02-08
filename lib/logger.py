# Python Library Imports
import os

# Modem Project Imports
import errors
import enum

MSG_TYPES = enum.enum(
        STDOUT   = 0,
        DEBUG    = 1,
        LOG_ONLY = 2
        )

class Logger:
    LogFileName          = ['~/.amodem.log']

    LoggingEnabled       = False
    DebuggingEnabled     = False
    RunningCurses        = False
    Initialized          = False

    # Buffer used to hold messages that should be printed to the log but the log hasn't been initialized yet
    PreInitializedBuffer = []

    def SetLogFileName(self, name):
        self.LogFileName[0] = name
    # end SetLogFileName

    def Initialize(self):
        if self.LoggingEnabled:
            self.LogFileName[0] = os.path.abspath(os.path.expandvars(os.path.expanduser(self.LogFileName[0])))

            try:
                dirName = os.path.dirname(self.LogFileName[0])
                if not os.path.exists(dirName):
                    os.makedirs(dirName)
                # end if
            except IOError as e:
                print 'Error Creating Log File Directory ({0}): {1}'.format(e.errno, e.strerror)
                exit(errors.ERROR_LOG_IO)
            except:
                raise
            # end try/except

            try:
                with file(self.LogFileName[0], mode='w') as LogFile:
                    LogFile.write('Logging Enabled\n')
                    for s in self.PreInitializedBuffer:
                        LogFile.write(s + '\n')
                    # end for
                # end with (file handle is closed)
            except IOError as e:
                print 'Log File ({0}) IO Error ({1}): {2}'.format(self.LogFileName[0], e.errno, e.strerror)
                exit(errors.ERROR_LOG_IO)
            except:
                raise
            # end try/except
        # end if
        self.Initialized = True
    # end Initialize

    def LogMessage(self, message, msgType):
        if msgType not in self.MessageTypes.keys():
            print 'Invalid Message Type'
            print message
        else:
            self.MessageTypes[msgType](self, message)
        # end if
    # end LogMessage

    # If argv is not empty, return the first element
    # otherwise, get the user's input
    def GetInput(self, argv, message):
        if argv:
            return argv.pop(0)
        else:
            return self.LogInput(message)
        # end if
    # end GetInput

    def LogInput(self, message):
        if not self.RunningCurses:
            self._logMessageLogOnly('[INPUT] ' + message)
            userInput = raw_input(message)
            self._logMessageLogOnly('[INPUT] ' + userInput)
            return userInput
        # end if
    # end LogInput

    def _logMessageStdout(self, message):
        if not self.RunningCurses:
            print message
        # end if
        self._logMessageLogOnly('[STDOUT] ' + message)
    # end _logMessageStdout

    def _logMessageDebug(self, message):
        msg = '[DEBUG] {0}'.format(message)
        if self.DebuggingEnabled and not self.RunningCurses:
            print msg
        # end if
        self._logMessageLogOnly(msg)
    # end _logMessageDebug

    def _logMessageLogOnly(self, message):
        if message[0] != '[':
            message = '[LOG] ' + message
        if self.LoggingEnabled:
            if self.Initialized:
                try:
                    with open(self.LogFileName[0], mode='a') as LogFile:
                        LogFile.write(message + '\n')
                    # end with (file handle is closed)
                except IOError as e:
                    print 'Log File IO Error ({0}): {1}'.format(e.errno, e.strerror)
                    exit(errors.ERROR_LOG_IO)
                except:
                    raise
                # end try/except
            else:
                self.PreInitializedBuffer.append(message)
            # end if
        # end if
    # end _logMessageLogOnly

    # Message Types
    # stdout - Print to stdout and log if
    #          logging is enabled
    # debug - Print to stdout if debugging
    #         is enabled and log if logging is enabled
    # logonly - Print to log if logging is enabled
    MessageTypes = {
            MSG_TYPES.STDOUT   : _logMessageStdout,
            MSG_TYPES.DEBUG    : _logMessageDebug,
            MSG_TYPES.LOG_ONLY : _logMessageLogOnly,
            }

# end Logger
