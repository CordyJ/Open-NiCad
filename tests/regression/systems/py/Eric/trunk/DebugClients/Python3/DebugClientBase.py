# -*- coding: utf-8 -*-

# Copyright (c) 2009 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a debug client base class.
"""

import sys
import socket
import select
import codeop
import traceback
import os
import time
import imp
import re
import distutils.sysconfig
import imp


from DebugProtocol import *
import DebugClientCapabilities
from DebugBase import setRecursionLimit, printerr
from AsyncFile import *
from DebugConfig import ConfigVarTypeStrings
from FlexCompleter import Completer


DebugClientInstance = None

################################################################################

def DebugClientInput(prompt = ""):
    """
    Replacement for the standard input builtin.
    
    This function works with the split debugger.
    
    @param prompt The prompt to be shown. (string)
    """
    if DebugClientInstance is None or not DebugClientInstance.redirect:
        return DebugClientOrigInput(prompt)

    return DebugClientInstance.input(prompt)

# Use our own input().
try:
    DebugClientOrigInput = __builtins__.__dict__['input']
    __builtins__.__dict__['input'] = DebugClientInput
except (AttributeError, KeyError):
    import __main__
    DebugClientOrigInput = __main__.__builtins__.__dict__['input']
    __main__.__builtins__.__dict__['input'] = DebugClientInput

################################################################################

def DebugClientFork():
    """
    Replacement for the standard os.fork().
    """
    if DebugClientInstance is None:
        return DebugClientOrigFork()
    
    return DebugClientInstance.fork()

# use our own fork().
if 'fork' in dir(os):
    DebugClientOrigFork = os.fork
    os.fork = DebugClientFork

################################################################################

def DebugClientClose(fd):
    """
    Replacement for the standard os.close(fd).
    
    @param fd open file descriptor to be closed (integer)
    """
    if DebugClientInstance is None:
        DebugClientOrigClose(fd)
    
    DebugClientInstance.close(fd)

# use our own close().
if 'close' in dir(os):
    DebugClientOrigClose = os.close
    os.close = DebugClientClose

################################################################################

def DebugClientSetRecursionLimit(limit):
    """
    Replacement for the standard sys.setrecursionlimit(limit).
    
    @param limit recursion limit (integer)
    """
    rl = max(limit, 64)
    setRecursionLimit(rl)
    DebugClientOrigSetRecursionLimit(rl + 64)

# use our own setrecursionlimit().
if 'setrecursionlimit' in dir(sys):
    DebugClientOrigSetRecursionLimit = sys.setrecursionlimit
    sys.setrecursionlimit = DebugClientSetRecursionLimit
    DebugClientSetRecursionLimit(sys.getrecursionlimit())

################################################################################

class DebugClientBase(object):
    """
    Class implementing the client side of the debugger.

    It provides access to the Python interpeter from a debugger running in another
    process whether or not the Qt event loop is running.

    The protocol between the debugger and the client assumes that there will be
    a single source of debugger commands and a single source of Python
    statements.  Commands and statement are always exactly one line and may be
    interspersed.

    The protocol is as follows.  First the client opens a connection to the
    debugger and then sends a series of one line commands.  A command is either
    &gt;Load&lt;, &gt;Step&lt;, &gt;StepInto&lt;, ... or a Python statement. 
    See DebugProtocol.py for a listing of valid protocol tokens.

    A Python statement consists of the statement to execute, followed (in a
    separate line) by &gt;OK?&lt;.  If the statement was incomplete then the response
    is &gt;Continue&lt;.  If there was an exception then the response is 
    &gt;Exception&lt;.
    Otherwise the response is &gt;OK&lt;.  The reason for the &gt;OK?&lt; part is to
    provide a sentinal (ie. the responding &gt;OK&lt;) after any possible output as a
    result of executing the command.

    The client may send any other lines at any other time which should be
    interpreted as program output.

    If the debugger closes the session there is no response from the client.
    The client may close the session at any time as a result of the script
    being debugged closing or crashing.
    
    <b>Note</b>: This class is meant to be subclassed by individual DebugClient classes.
    Do not instantiate it directly.
    """
    clientCapabilities = DebugClientCapabilities.HasAll
    
    def __init__(self):
        """
        Constructor
        """
        self.breakpoints = {}
        self.redirect = True

        # The next couple of members are needed for the threaded version.
        # For this base class they contain static values for the non threaded
        # debugger
        
        # dictionary of all threads running
        self.threads = {}
        
        # the "current" thread, basically the thread we are at a breakpoint for.
        self.currentThread = self
        
        # special objects representing the main scripts thread and frame
        self.mainThread = self
        self.mainFrame = None
        self.framenr = 0
        
        # The context to run the debugged program in.
        self.debugMod = imp.new_module('__main__')

        # The list of complete lines to execute.
        self.buffer = ''
        
        # The list of regexp objects to filter variables against
        self.globalsFilterObjects = []
        self.localsFilterObjects = []

        self.pendingResponse = ResponseOK
        self.fncache = {}
        self.dircache = []
        self.inRawMode = False
        self.mainProcStr = None     # used for the passive mode
        self.passive = False        # used to indicate the passive mode
        self.running = None
        self.test = None
        self.tracePython = False
        self.debugging = False
        
        self.fork_auto = False
        self.fork_child = False

        self.readstream = None
        self.writestream = None
        self.errorstream = None
        self.pollingDisabled = False
        
        self.skipdirs = sys.path[:]
        
        self.variant = 'You should not see this'
        
        # commandline completion stuff
        self.complete = Completer(self.debugMod.__dict__).complete
        
        self.compile_command = codeop.CommandCompiler()
        
        self.coding_re = re.compile(r"coding[:=]\s*([-\w_.]+)")
        self.defaultCoding = 'utf-8'
        self.__coding = self.defaultCoding
        self.noencoding = False
    
    def getCoding(self):
        """
        Public method to return the current coding.
        
        @return codec name (string)
        """
        return self.__coding
    
    def __setCoding(self, filename):
        """
        Private method to set the coding used by a python file.
        
        @param filename name of the file to inspect (string)
        """
        if self.noencoding:
            self.__coding = sys.getdefaultencoding()
        else:
            default = 'utf-8'
            try:
                f = open(filename, 'rb')
                # read the first and second line
                text = f.readline()
                text = "{0}{1}".format(text, f.readline())
                f.close()
            except IOError:
                self.__coding = default
                return
            
            for l in text.splitlines():
                m = self.coding_re.search(l)
                if m:
                    self.__coding = m.group(1)
                    return
            self.__coding = default

    def attachThread(self, target = None, args = None, kwargs = None, mainThread = False):
        """
        Public method to setup a thread for DebugClient to debug.
        
        If mainThread is non-zero, then we are attaching to the already 
        started mainthread of the app and the rest of the args are ignored.
        
        @param target the start function of the target thread (i.e. the user code)
        @param args arguments to pass to target
        @param kwargs keyword arguments to pass to target
        @param mainThread True, if we are attaching to the already 
              started mainthread of the app
        @return The identifier of the created thread
        """
        if self.debugging:
            sys.setprofile(self.profile)

    def __dumpThreadList(self):
        """
        Public method to send the list of threads.
        """
        threadList = []
        if self.threads:    # indication for the threaded debugger
            currentId = self.currentThread.get_ident()
            for t in self.threads.values():
                d = {}
                d["id"] = t.get_ident()
                d["name"] = t.get_name()
                d["broken"] = t.isBroken()
                threadList.append(d)
        else:
            currentId = -1
            d = {}
            d["id"] = -1
            d["name"] = "MainThread"
            d["broken"] = self.isBroken()
            threadList.append(d)
        
        self.write("{0}{1!r}\n".format(ResponseThreadList, (currentId, threadList)))
    
    def input(self, prompt):
        """
        Public method to implement input() using the event loop.
        
        @param prompt the prompt to be shown (string)
        @return the entered string
        """
        self.write("{0}{1!r}\n".format(ResponseRaw, (prompt, 1)))
        self.inRawMode = True
        self.eventLoop(True)
        return self.rawLine

    def __exceptionRaised(self):
        """
        Private method called in the case of an exception
        
        It ensures that the debug server is informed of the raised exception.
        """
        self.pendingResponse = ResponseException
    
    def sessionClose(self, exit = True):
        """
        Public method to close the session with the debugger and optionally terminate.
        
        @param exit flag indicating to terminate (boolean)
        """
        try:
            self.set_quit()
        except:
            pass

        # clean up asyncio.
        self.disconnect()
        self.debugging = False
        
        # make sure we close down our end of the socket
        # might be overkill as normally stdin, stdout and stderr
        # SHOULD be closed on exit, but it does not hurt to do it here
        self.readstream.close(True)
        self.writestream.close(True)
        self.errorstream.close(True)

        if exit:
            # Ok, go away.
            sys.exit()

    def __compileFileSource(self, filename, mode = 'exec'):
        """
        Private method to compile source code read from a file.
        
        @param filename name of the source file (string)
        @param mode kind of code to be generated (string, exec or eval)
        @return compiled code object (None in case of errors)
        """
        with open(filename) as fp:
            statement = fp.read()
        
        try:
            code = compile(statement + '\n', filename, mode)
        except SyntaxError:
            exctype, excval, exctb = sys.exc_info()
            try:
                message, (filename, linenr, charnr, text) = excval[0], excval[1]
            except ValueError:
                exclist = []
            else:
                exclist = [message, [filename, linenr, charnr]]
            
            self.write("{0}{1}\n".format(ResponseSyntax, str(exclist)))
            return None
        
        return code
    
    def handleLine(self,line):
        """
        Public method to handle the receipt of a complete line.

        It first looks for a valid protocol token at the start of the line. Thereafter
        it trys to execute the lines accumulated so far.
        
        @param line the received line
        """
        # Remove any newline.
        if line[-1] == '\n':
            line = line[:-1]

##        printerr(line)          ##debug

        eoc = line.find('<')

        if eoc >= 0 and line[0] == '>':
            # Get the command part and any argument.
            cmd = line[:eoc + 1]
            arg = line[eoc + 1:]
            
            if cmd == RequestVariables:
                frmnr, scope, filter = eval(arg.replace("u'", "'"))
                self.__dumpVariables(int(frmnr), int(scope), filter)
                return
            
            if cmd == RequestVariable:
                var, frmnr, scope, filter = eval(arg.replace("u'", "'"))
                self.__dumpVariable(var, int(frmnr), int(scope), filter)
                return
            
            if cmd == RequestThreadList:
                self.__dumpThreadList()
                return
            
            if cmd == RequestThreadSet:
                tid = eval(arg)
                if tid in self.threads:
                    self.setCurrentThread(tid)
                    self.write(ResponseThreadSet + '\n')
                    stack = self.currentThread.getStack()
                    self.write('{0}{1!r}\n'.format(ResponseStack, stack))
                return
            
            if cmd == RequestStep:
                self.currentThread.step(True)
                self.eventExit = True
                return

            if cmd == RequestStepOver:
                self.currentThread.step(False)
                self.eventExit = True
                return
            
            if cmd == RequestStepOut:
                self.currentThread.stepOut()
                self.eventExit = True
                return
            
            if cmd == RequestStepQuit:
                if self.passive:
                    self.progTerminated(42)
                else:
                    self.set_quit()
                    self.eventExit = True
                return

            if cmd == RequestContinue:
                special = int(arg)
                self.currentThread.go(special)
                self.eventExit = True
                return

            if cmd == RequestOK:
                self.write(self.pendingResponse + '\n')
                self.pendingResponse = ResponseOK
                return

            if cmd == RequestEnv:
                env = eval(arg.replace("u'", "'"))
                for key, value in env.items():
                    if key.endswith("+"):
                        if key[:-1] in os.environ:
                            os.environ[key[:-1]] += value
                        else:
                            os.environ[key[:-1]] = value
                    else:
                        os.environ[key] = value
                return

            if cmd == RequestLoad:
                self.fncache = {}
                self.dircache = []
                sys.argv = []
                wd, fn, args, tracePython = arg.split('|')
                self.__setCoding(fn)
                try:
                    sys.setappdefaultencoding(self.__coding)
                except AttributeError:
                    pass
                sys.argv.append(fn)
                sys.argv.extend(eval(args.replace("u'", "'")))
                sys.path[0] = os.path.dirname(sys.argv[0])
                sys.path.insert(0, '')
                if wd == '':
                    os.chdir(sys.path[1])
                else:
                    os.chdir(wd)
                tracePython = int(tracePython)
                self.running = sys.argv[0]
                self.mainFrame = None
                self.inRawMode = False
                self.debugging = True
                
                self.threads.clear()
                self.attachThread(mainThread = True)
                
                # set the system exception handling function to ensure, that
                # we report on all unhandled exceptions
                sys.excepthook = self.__unhandled_exception
                
                # clear all old breakpoints, they'll get set after we have started
                self.mainThread.clear_all_breaks()
                
                self.mainThread.tracePython = tracePython
                
                # This will eventually enter a local event loop.
                # Note the use of backquotes to cause a repr of self.running. The
                # need for this is on Windows os where backslash is the path separator.
                # They will get inadvertantly stripped away during the eval causing 
                # IOErrors, if self.running is passed as a normal str.
                self.debugMod.__dict__['__file__'] = self.running
                sys.modules['__main__'] = self.debugMod
                code = self.__compileFileSource(self.running)
                if code:
                    res = self.mainThread.run(code, self.debugMod.__dict__)
                    self.progTerminated(res)
                return

            if cmd == RequestRun:
                sys.argv = []
                wd, fn, args = arg.split('|')
                self.__setCoding(fn)
                try:
                    sys.setappdefaultencoding(self.__coding)
                except AttributeError:
                    pass
                sys.argv.append(fn)
                sys.argv.extend(eval(args.replace("u'", "'")))
                sys.path[0] = os.path.dirname(sys.argv[0])
                sys.path.insert(0, '')
                if wd == '':
                    os.chdir(sys.path[1])
                else:
                    os.chdir(wd)

                self.running = sys.argv[0]
                self.mainFrame = None
                self.botframe = None
                self.inRawMode = False
                
                self.threads.clear()
                self.attachThread(mainThread = True)
                
                # set the system exception handling function to ensure, that
                # we report on all unhandled exceptions
                sys.excepthook = self.__unhandled_exception
                
                self.mainThread.tracePython = False
                
                self.debugMod.__dict__['__file__'] = sys.argv[0]
                sys.modules['__main__'] = self.debugMod
                exec(open(sys.argv[0]).read(), self.debugMod.__dict__)
                self.writestream.flush()
                return

            if cmd == RequestProfile:
                sys.setprofile(None)
                import PyProfile
                sys.argv = []
                wd, fn, args, erase = arg.split('|')
                self.__setCoding(fn)
                try:
                    sys.setappdefaultencoding(self.__coding)
                except AttributeError:
                    pass
                sys.argv.append(fn)
                sys.argv.extend(eval(args.replace("u'", "'")))
                sys.path[0] = os.path.dirname(sys.argv[0])
                sys.path.insert(0, '')
                if wd == '':
                    os.chdir(sys.path[1])
                else:
                    os.chdir(wd)

                # set the system exception handling function to ensure, that
                # we report on all unhandled exceptions
                sys.excepthook = self.__unhandled_exception
                
                # generate a profile object
                self.prof = PyProfile.PyProfile(sys.argv[0])
                
                if int(erase):
                    self.prof.erase()
                self.debugMod.__dict__['__file__'] = sys.argv[0]
                sys.modules['__main__'] = self.debugMod
                fp = open(sys.argv[0])
                try:
                    script = fp.read()
                finally:
                    fp.close()
                if script:
                    self.prof.run("exec({0!r}\n)".format(script))
                    self.prof.save()
                    self.writestream.flush()
                return

            if cmd == RequestCoverage:
                from coverage import coverage
                sys.argv = []
                wd, fn, args, erase = arg.split('@@')
                self.__setCoding(fn)
                try:
                    sys.setappdefaultencoding(self.__coding)
                except AttributeError:
                    pass
                sys.argv.append(fn)
                sys.argv.extend(eval(args.replace("u'", "'")))
                sys.path[0] = os.path.dirname(sys.argv[0])
                sys.path.insert(0, '')
                if wd == '':
                    os.chdir(sys.path[1])
                else:
                    os.chdir(wd)
                
                # set the system exception handling function to ensure, that
                # we report on all unhandled exceptions
                sys.excepthook = self.__unhandled_exception
                
                # generate a coverage object
                self.cover = coverage(auto_data = True, 
                    data_file = "{0}.coverage".format(os.path.splitext(sys.argv[0])[0]))
                self.cover.use_cache(True)
                
                if int(erase):
                    self.cover.erase()
                sys.modules['__main__'] = self.debugMod
                self.debugMod.__dict__['__file__'] = sys.argv[0]
                self.cover.start()
                exec(open(sys.argv[0]).read(), self.debugMod.__dict__)
                self.cover.stop()
                self.cover.save()
                self.writestream.flush()
                return

            if cmd == RequestShutdown:
                self.sessionClose()
                return
            
            if cmd == RequestBreak:
                fn, line, temporary, set, cond = arg.split('@@')
                line = int(line)
                set = int(set)
                temporary = int(temporary)

                if set:
                    if cond == 'None' or cond == '':
                        cond = None
                    else:
                        try:
                            compile(cond, '<string>', 'eval')
                        except SyntaxError:
                            self.write('{0}{1},{2:d}\n'.format(
                                       ResponseBPConditionError, fn, line))
                            return
                    self.mainThread.set_break(fn, line, temporary, cond)
                else:
                    self.mainThread.clear_break(fn, line)

                return
            
            if cmd == RequestBreakEnable:
                fn, line, enable = arg.split(',')
                line = int(line)
                enable = int(enable)
                
                bp = self.mainThread.get_break(fn, line)
                if bp is not None:
                    if enable:
                        bp.enable()
                    else:
                        bp.disable()
                
                return
            
            if cmd == RequestBreakIgnore:
                fn, line, count = arg.split(',')
                line = int(line)
                count = int(count)
                
                bp = self.mainThread.get_break(fn, line)
                if bp is not None:
                    bp.ignore = count
                
                return
            
            if cmd == RequestWatch:
                cond, temporary, set = arg.split('@@')
                set = int(set)
                temporary = int(temporary)

                if set:
                    if not cond.endswith('??created??') and \
                       not cond.endswith('??changed??'):
                        try:
                            compile(cond, '<string>', 'eval')
                        except SyntaxError:
                            self.write('{0}{1}\n'.format(ResponseWPConditionError, cond))
                            return
                    self.mainThread.set_watch(cond, temporary)
                else:
                    self.mainThread.clear_watch(cond)

                return
            
            if cmd == RequestWatchEnable:
                cond, enable = arg.split(',')
                enable = int(enable)
                
                bp = self.mainThread.get_watch(cond)
                if bp is not None:
                    if enable:
                        bp.enable()
                    else:
                        bp.disable()
                
                return
            
            if cmd == RequestWatchIgnore:
                cond, count = arg.split(',')
                count = int(count)
                
                bp = self.mainThread.get_watch(cond)
                if bp is not None:
                    bp.ignore = count
                
                return
            
            if cmd == RequestEval:
                try:
                    value = eval(arg, self.currentThread.getCurrentFrame().f_globals,
                                      self.currentThread.getCurrentFrame().f_locals)
                except:
                    # Report the exception and the traceback
                    try:
                        type, value, tb = sys.exc_info()
                        sys.last_type = type
                        sys.last_value = value
                        sys.last_traceback = tb
                        tblist = traceback.extract_tb(tb)
                        del tblist[:1]
                        list = traceback.format_list(tblist)
                        if list:
                            list.insert(0, "Traceback (innermost last):\n")
                            list[len(list):] = \
                                traceback.format_exception_only(type, value)
                    finally:
                        tblist = tb = None

                    for l in list:
                        self.write(l)

                    self.write(ResponseException + '\n')
                
                else:
                    self.write(str(value) + '\n')
                    self.write(ResponseOK + '\n')
                
                return
            
            if cmd == RequestExec:
                _globals = self.currentThread.getCurrentFrame().f_globals
                _locals = self.currentThread.getCurrentFrame().f_locals
                try:
                    code = compile(arg + '\n', '<stdin>', 'single')
                    exec(code, _globals, _locals)
                except:
                    # Report the exception and the traceback
                    try:
                        type, value, tb = sys.exc_info()
                        sys.last_type = type
                        sys.last_value = value
                        sys.last_traceback = tb
                        tblist = traceback.extract_tb(tb)
                        del tblist[:1]
                        list = traceback.format_list(tblist)
                        if list:
                            list.insert(0, "Traceback (innermost last):\n")
                            list[len(list):] = \
                                traceback.format_exception_only(type, value)
                    finally:
                        tblist = tb = None

                    for l in list:
                        self.write(l)

                    self.write(ResponseException + '\n')
                
                return
            
            if cmd == RequestBanner:
                self.write('{0}{1}\n'.format(ResponseBanner, 
                    str(("Python {0}".format(sys.version), 
                         socket.gethostname(), self.variant))))
                return
            
            if cmd == RequestCapabilities:
                self.write('{0}{1:d}, "Python3"\n'.format(ResponseCapabilities, 
                    self.__clientCapabilities()))
                return
            
            if cmd == RequestCompletion:
                self.__completionList(arg.replace("u'", "'"))
                return
            
            if cmd == RequestSetFilter:
                scope, filterString = eval(arg.replace("u'", "'"))
                self.__generateFilterObjects(int(scope), filterString)
                return
            
            if cmd == RequestUTPrepare:
                fn, tn, tfn, cov, covname, erase = arg.split('|')
                sys.path.insert(0, os.path.dirname(os.path.abspath(fn)))
                os.chdir(sys.path[0])

                # set the system exception handling function to ensure, that
                # we report on all unhandled exceptions
                sys.excepthook = self.__unhandled_exception
                
                try:
                    import unittest
                    utModule = imp.load_source(tn, fn)
                    try:
                        self.test = unittest.defaultTestLoader\
                                    .loadTestsFromName(tfn, utModule)
                    except AttributeError:
                        self.test = unittest.defaultTestLoader\
                                    .loadTestsFromModule(utModule)
                except:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    self.write('{0}{1}\n'.format(ResponseUTPrepared,
                        str((0, str(exc_type), str(exc_value)))))
                    self.__exceptionRaised()
                    return
                
                # generate a coverage object
                if int(cov):
                    from coverage import coverage
                    self.cover = coverage(auto_data = True, 
                        data_file = "{0}.coverage".format(os.path.splitext(covname)[0]))
                    self.cover.use_cache(True)
                    if int(erase):
                        self.cover.erase()
                else:
                    self.cover = None
                
                self.write('{0}{1}\n'.format(ResponseUTPrepared,
                    str((self.test.countTestCases(), "", ""))))
                return
            
            if cmd == RequestUTRun:
                from DCTestResult import DCTestResult
                self.testResult = DCTestResult(self)
                if self.cover:
                    self.cover.start()
                self.test.run(self.testResult)
                if self.cover:
                    self.cover.stop()
                    self.cover.save()
                self.write('{0}\n'.format(ResponseUTFinished))
                return
            
            if cmd == RequestUTStop:
                self.testResult.stop()
                return
        
            if cmd == ResponseForkTo:
                # this results from a separate event loop
                self.fork_child = (arg == 'child')
                self.eventExit = True
                return
            
            if cmd == RequestForkMode:
                self.fork_auto, self.fork_child = eval(arg)
                return
        
        # If we are handling raw mode input then reset the mode and break out
        # of the current event loop.
        if self.inRawMode:
            self.inRawMode = False
            self.rawLine = line
            self.eventExit = True
            return

        if self.buffer:
            self.buffer = self.buffer + '\n' + line
        else:
            self.buffer = line

        try:
            code = self.compile_command(self.buffer, self.readstream.name)
        except (OverflowError, SyntaxError, ValueError):
            # Report the exception
            sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
            for l in traceback.format_exception_only(sys.last_type, sys.last_value):
                self.write(l)
            self.buffer = ''

            self.__exceptionRaised()
        else:
            if code is None:
                self.pendingResponse = ResponseContinue
            else: 
                self.buffer = ''

                try:
                    if self.running is None:
                        exec(code, self.debugMod.__dict__)
                    else:
                        if self.currentThread is None:
                            # program has terminated
                            self.running = None
                            _globals = self.debugMod.__dict__
                            _locals = _globals
                        else:
                            cf = self.currentThread.getCurrentFrame()
                            # program has terminated
                            if cf is None:
                                self.running = None
                                _globals = self.debugMod.__dict__
                                _locals = _globals
                            else:
                                frmnr = self.framenr
                                while cf is not None and frmnr > 0:
                                    cf = cf.f_back
                                    frmnr -= 1
                                _globals = cf.f_globals
                                _locals = cf.f_locals
                        # reset sys.stdout to our redirector (unconditionally)
                        if "sys" in _globals:
                            __stdout = _globals["sys"].stdout
                            _globals["sys"].stdout = self.writestream
                            exec(code, _globals, _locals)
                            _globals["sys"].stdout = __stdout
                        elif "sys" in _locals:
                            __stdout = _locals["sys"].stdout
                            _locals["sys"].stdout = self.writestream
                            exec(code, _globals, _locals)
                            _locals["sys"].stdout = __stdout
                        else:
                            exec(code, _globals, _locals)
                except SystemExit as exc:
                    self.progTerminated(exc.code)
                except:
                    # Report the exception and the traceback
                    try:
                        exc_type, exc_value, exc_tb = sys.exc_info()
                        sys.last_type = exc_type
                        sys.last_value = exc_value
                        sys.last_traceback = exc_tb
                        tblist = traceback.extract_tb(exc_tb)
                        del tblist[:1]
                        list = traceback.format_list(tblist)
                        if list:
                            list.insert(0, "Traceback (innermost last):\n")
                            list[len(list):] = \
                                traceback.format_exception_only(exc_type, exc_value)
                    finally:
                        tblist = exc_tb = None

                    for l in list:
                        self.write(l)

                    self.__exceptionRaised()

    def __clientCapabilities(self):
        """
        Private method to determine the clients capabilities.
        
        @return client capabilities (integer)
        """
        try:
            import PyProfile
            try:
                del sys.modules['PyProfile']
            except KeyError:
                pass
            return self.clientCapabilities
        except ImportError:
            return self.clientCapabilities & ~DebugClientCapabilities.HasProfiler
    
    def write(self,s):
        """
        Public method to write data to the output stream.
        
        @param s data to be written (string)
        """
        self.writestream.write(s)
        self.writestream.flush()

    def __interact(self):
        """
        Private method to Interact with  the debugger.
        """
        global DebugClientInstance

        self.setDescriptors(self.readstream, self.writestream)
        DebugClientInstance = self

        if not self.passive:
            # At this point simulate an event loop.
            self.eventLoop()

    def eventLoop(self, disablePolling = False):
        """
        Public method implementing our event loop.
        
        @param disablePolling flag indicating to enter an event loop with
            polling disabled (boolean)
        """
        self.eventExit = None
        self.pollingDisabled = disablePolling

        while self.eventExit is None:
            wrdy = []

            if AsyncPendingWrite(self.writestream):
                wrdy.append(self.writestream)

            if AsyncPendingWrite(self.errorstream):
                wrdy.append(self.errorstream)
            
            try:
                rrdy, wrdy, xrdy = select.select([self.readstream], wrdy, [])
            except (select.error, KeyboardInterrupt, socket.error):
                # just carry on
                continue

            if self.readstream in rrdy:
                self.readReady(self.readstream.fileno())

            if self.writestream in wrdy:
                self.writeReady(self.writestream.fileno())

            if self.errorstream in wrdy:
                self.writeReady(self.errorstream.fileno())

        self.eventExit = None
        self.pollingDisabled = False

    def eventPoll(self):
        """
        Public method to poll for events like 'set break point'.
        """
        if self.pollingDisabled:
            return
        
        # the choice of a ~0.5 second poll interval is arbitrary.
        lasteventpolltime = getattr(self, 'lasteventpolltime', time.time())
        now = time.time()
        if now - lasteventpolltime < 0.5:
            self.lasteventpolltime = lasteventpolltime
            return
        else:
            self.lasteventpolltime = now

        wrdy = []
        if AsyncPendingWrite(self.writestream):
            wrdy.append(self.writestream)

        if AsyncPendingWrite(self.errorstream):
            wrdy.append(self.errorstream)
        
        # immediate return if nothing is ready.
        try:
            rrdy, wrdy, xrdy = select.select([self.readstream], wrdy, [], 0)
        except (select.error, KeyboardInterrupt, socket.error):
            return

        if self.readstream in rrdy:
            self.readReady(self.readstream.fileno())

        if self.writestream in wrdy:
            self.writeReady(self.writestream.fileno())

        if self.errorstream in wrdy:
            self.writeReady(self.errorstream.fileno())
    
    def connectDebugger(self, port, remoteAddress = None, redirect = True):
        """
        Public method to establish a session with the debugger. 
        
        It opens a network connection to the debugger, connects it to stdin, 
        stdout and stderr and saves these file objects in case the application
        being debugged redirects them itself.
        
        @param port the port number to connect to (int)
        @param remoteAddress the network address of the debug server host (string)
        @param redirect flag indicating redirection of stdin, stdout and stderr (boolean)
        """
        if remoteAddress is None:                               # default: 127.0.0.1
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((DebugAddress, port))
        elif ":" in remoteAddress:                              # IPv6
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((remoteAddress, port))
        else:                                                   # IPv4
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((remoteAddress, port))

        self.readstream = AsyncFile(sock, sys.stdin.mode, sys.stdin.name)
        self.writestream = AsyncFile(sock, sys.stdout.mode, sys.stdout.name)
        self.errorstream = AsyncFile(sock, sys.stderr.mode, sys.stderr.name)
        
        if redirect:
            sys.stdin = self.readstream
            sys.stdout = self.writestream
            sys.stderr = self.errorstream
        self.redirect = redirect
        
        # attach to the main thread here
        self.attachThread(mainThread = True)

    def __unhandled_exception(self, exctype, excval, exctb):
        """
        Private method called to report an uncaught exception.
        
        @param exctype the type of the exception
        @param excval data about the exception
        @param exctb traceback for the exception
        """
        self.mainThread.user_exception(None, (exctype, excval, exctb), True)
    
    def absPath(self, fn):
        """
        Public method to convert a filename to an absolute name.

        sys.path is used as a set of possible prefixes. The name stays 
        relative if a file could not be found.
        
        @param fn filename (string)
        @return the converted filename (string)
        """
        if os.path.isabs(fn):
            return fn

        # Check the cache.
        if fn in self.fncache:
            return self.fncache[fn]

        # Search sys.path.
        for p in sys.path:
            afn = os.path.abspath(os.path.join(p, fn))
            afn = os.path.normcase(afn)

            if os.path.exists(afn):
                self.fncache[fn] = afn
                d = os.path.dirname(afn)
                if (d not in sys.path) and (d not in self.dircache):
                    self.dircache.append(d)
                return afn

        # Search the additional directory cache
        for p in self.dircache:
            afn = os.path.abspath(os.path.join(p, fn))
            afn = os.path.normcase(afn)
            
            if os.path.exists(afn):
                self.fncache[fn] = afn
                return afn
        
        # Nothing found.
        return fn

    def shouldSkip(self, fn):
        """
        Public method to check if a file should be skipped.
        
        @param fn filename to be checked
        @return non-zero if fn represents a file we are 'skipping', zero otherwise.
        """
        if self.mainThread.tracePython:     # trace into Python library
            return False
            
        # Eliminate anything that is part of the Python installation.
        afn = self.absPath(fn)
        for d in self.skipdirs:
            if afn.startswith(d):
                return True
        
        
        return False
    
    def getRunning(self):
        """
        Public method to return the main script we are currently running.
        """
        return self.running

    def progTerminated(self, status):
        """
        Public method to tell the debugger that the program has terminated.
        
        @param status the return status
        """
        if status is None:
            status = 0
        else:
            try:
                int(status)
            except ValueError:
                status = 1

        if self.running:
            self.set_quit()
            self.running = None
            self.write('{0}{1:d}\n'.format(ResponseExit, status))
        
        # reset coding
        self.__coding = self.defaultCoding
        try:
            sys.setappdefaultencoding(self.defaultCoding)
        except AttributeError:
            pass

    def __dumpVariables(self, frmnr, scope, filter):
        """
        Private method to return the variables of a frame to the debug server.
        
        @param frmnr distance of frame reported on. 0 is the current frame (int)
        @param scope 1 to report global variables, 0 for local variables (int)
        @param filter the indices of variable types to be filtered (list of int)
        """
        if scope == 0:
            self.framenr = frmnr
        
        f = self.currentThread.getCurrentFrame()
        
        while f is not None and frmnr > 0:
            f = f.f_back
            frmnr -= 1
        
        if f is None:
            return
        
        if scope:
            dict = f.f_globals
        else:
            dict = f.f_locals
            
            if f.f_globals is f.f_locals:
                scope = -1
        
        varlist = [scope]
        
        if scope != -1:
            keylist = dict.keys()
            
            vlist = self.__formatVariablesList(keylist, dict, scope, filter)
            varlist.extend(vlist)
        
        self.write('{0}{1}\n'.format(ResponseVariables, str(varlist)))
    
    def __dumpVariable(self, var, frmnr, scope, filter):
        """
        Private method to return the variables of a frame to the debug server.
        
        @param var list encoded name of the requested variable (list of strings)
        @param frmnr distance of frame reported on. 0 is the current frame (int)
        @param scope 1 to report global variables, 0 for local variables (int)
        @param filter the indices of variable types to be filtered (list of int)
        """
        f = self.currentThread.getCurrentFrame()
        
        while f is not None and frmnr > 0:
            f = f.f_back
            frmnr -= 1
        
        if f is None:
            return
        
        if scope:
            dict = f.f_globals
        else:
            dict = f.f_locals
            
            if f.f_globals is f.f_locals:
                scope = -1
        
        varlist = [scope, var]
        
        if scope != -1:
            # search the correct dictionary
            i = 0
            rvar = var[:]
            dictkeys = None
            obj = None
            isDict = False
            formatSequences = False
            access = ""
            oaccess = ""
            odict = dict
            
            while i < len(var):
                if len(dict):
                    udict = dict
                ndict = {}
                # this has to be in line with VariablesViewer.indicators
                if var[i][-2:] in ["[]", "()", "{}"]:
                    if i + 1 == len(var):
                        if var[i][:-2] == '...':
                            dictkeys = [var[i - 1]]
                        else:
                            dictkeys = [var[i][:-2]]
                        formatSequences = True
                        if not access and not oaccess:
                            if var[i][:-2] == '...':
                                access = '["{0!s}"]'.format(var[i - 1])
                                dict = odict
                            else:
                                access = '["{0!s}"]'.format(var[i][:-2])
                        else:
                            if var[i][:-2] == '...':
                                if oaccess:
                                    access = oaccess
                                else:
                                    access = '{0!s}[{1!s}]'.format(access, var[i - 1])
                                dict = odict
                            else:
                                if oaccess:
                                    access = '{0!s}[{1!s}]'.format(oaccess, var[i][:-2])
                                    oaccess = ''
                                else:
                                    access = '{0!s}[{1!s}]'.format(access, var[i][:-2])
                        if var[i][-2:] == "{}":
                            isDict = True
                        break
                    else:
                        if not access:
                            if var[i][:-2] == '...':
                                access = '["{0!s}"]'.format(var[i - 1])
                                dict = odict
                            else:
                                access = '["{0!s}"]'.format(var[i][:-2])
                        else:
                            if var[i][:-2] == '...':
                                access = '{0!s}[{1!s}]'.format(access, var[i - 1])
                                dict = odict
                            else:
                                if oaccess:
                                    access = '{0!s}[{1!s}]'.format(oaccess, var[i][:-2])
                                    oaccess = ''
                                else:
                                    access = '{0!s}[{1!s}]'.format(access, var[i][:-2])
                else:
                    if access:
                        if oaccess:
                            access = '{0!s}[{1!s}]'.format(oaccess, var[i])
                        else:
                            access = '{0!s}[{1!s}]'.format(access, var[i])
                        if var[i-1][:-2] == '...':
                            oaccess = access
                        else:
                            oaccess = ''
                        try:
                            loc = {"dict" : dict}
                            exec('mdict = dict{0!s}.__dict__\nobj = dict{0!s}'\
                                 .format(access), globals(), loc)
                            mdict = loc["mdict"]
                            obj = loc["obj"]
                            ndict.update(mdict)
                            if mdict and not "sipThis" in mdict.keys():
                                del rvar[0:2]
                                access = ""
                        except:
                            pass
                        try:
                            loc = {"cdict" : {}, "dict" : dict}
                            exec('slv = dict{0!s}.__slots__'.format(access), 
                                 globals(), loc)
                            for v in loc["slv"]:
                                try:
                                    loc["v"] = v
                                    exec('cdict[v] = dict{0!s}.{1!s}'.format(access, v), 
                                         globals, loc)
                                except:
                                    pass
                            ndict.update(loc["cdict"])
                            exec('obj = dict{0!s}'.format(access), globals(), loc)
                            obj = loc["obj"]
                            access = ""
                        except:
                            pass
                    else:
                        try:
                            ndict.update(dict[var[i]].__dict__)
                            del rvar[0]
                            obj = dict[var[i]]
                        except:
                            pass
                        try:
                            slv = dict[var[i]].__slots__
                            loc = {"cdict" : {}, "dict" : dict, "var" : var, "i" : i}
                            for v in slv:
                                try:
                                    loc["v"] = v
                                    exec('cdict[v] = dict[var[i]].{0!s}'.format(v), 
                                         globals(), loc)
                                except:
                                    pass
                            ndict.update(loc["cdict"])
                            obj = dict[var[i]]
                        except:
                            pass
                    odict = dict
                    dict = ndict
                i += 1
            
            if ("sipThis" in dict.keys() and len(dict) == 1) or \
               (len(dict) == 0 and len(udict) > 0):
                if access:
                    loc = {"udict" : udict}
                    exec('qvar = udict{0!s}'.format(access), globals(), loc)
                    qvar = loc["qvar"]
                # this has to be in line with VariablesViewer.indicators
                elif rvar and rvar[0][-2:] in ["[]", "()", "{}"]:
                    loc = {"udict" : udict}
                    exec('qvar = udict["{0!s}"][{1!s}]'.format(rvar[0][:-2], rvar[1]), 
                         globals(), loc)
                    qvar = loc["qvar"]
                else:
                    qvar = udict[var[-1]]
                qvtype = str(type(qvar))[1:-1].split()[1][1:-1]
                if qvtype.startswith("PyQt4"):
                    vlist = self.__formatQt4Variable(qvar, qvtype)
                else:
                    vlist = []
            else:
                # format the dictionary found
                if dictkeys is None:
                    dictkeys = dict.keys()
                else:
                    # treatment for sequences and dictionaries
                    if access:
                        loc = {"dict" : dict}
                        exec("dict = dict{0!s}".format(access), globals(), loc)
                        dict = loc["dict"]
                    else:
                        dict = dict[dictkeys[0]]
                    if isDict:
                        dictkeys = dict.keys()
                    else:
                        dictkeys = range(len(dict))
                vlist = self.__formatVariablesList(dictkeys, dict, scope, filter, 
                                                   formatSequences)
            varlist.extend(vlist)
        
            if obj is not None and not formatSequences:
                if repr(obj).startswith('{'):
                    varlist.append(('...', 'dict', "{0:d}".format(len(obj.keys()))))
                elif repr(obj).startswith('['):
                    varlist.append(('...', 'list', "{0:d}".format(len(obj))))
                elif repr(obj).startswith('('):
                    varlist.append(('...', 'tuple', "{0:d}".format(len(obj))))
        
        self.write('{0}{1}\n'.format(ResponseVariable, str(varlist)))
        
    def __formatQt4Variable(self, value, vtype):
        """
        Private method to produce a formatted output of a simple Qt4 type.
        
        @param value variable to be formatted
        @param vtype type of the variable to be formatted (string)
        @return A tuple consisting of a list of formatted variables. Each 
            variable entry is a tuple of three elements, the variable name, 
            its type and value.
        """
        qttype = vtype.split('.')[-1]
        varlist = []
        if qttype == 'QString':
            varlist.append(("", "QString", "{0}".format(value)))
        elif qttype == 'QStringList':
            for s in value:
                varlist.append(("", "QString", "{0}".format(s)))
        elif qttype == 'QChar':
            varlist.append(("", "QChar", "{0}".format(chr(value.unicode()))))
            varlist.append(("", "int", "{0:d}".format(value.unicode())))
        elif qttype == 'QPoint':
            varlist.append(("x", "int", "{0:d}".format(value.x())))
            varlist.append(("y", "int", "{0:d}".format(value.y())))
        elif qttype == 'QPointF':
            varlist.append(("x", "float", "{0:g}".format(value.x())))
            varlist.append(("y", "float", "{0:g}".format(value.y())))
        elif qttype == 'QRect':
            varlist.append(("x", "int", "{0:d}".format(value.x())))
            varlist.append(("y", "int", "{0:d}".format(value.y())))
            varlist.append(("width", "int", "{0:d}".format(value.width())))
            varlist.append(("height", "int", "{0:d}".format(value.height())))
        elif qttype == 'QRectF':
            varlist.append(("x", "float", "{0:g}".format(value.x())))
            varlist.append(("y", "float", "{0:g}".format(value.y())))
            varlist.append(("width", "float", "{0:g}".format(value.width())))
            varlist.append(("height", "float", "{0:g}".format(value.height())))
        elif qttype == 'QSize':
            varlist.append(("width", "int", "{0:d}".format(value.width())))
            varlist.append(("height", "int", "{0:d}".format(value.height())))
        elif qttype == 'QSizeF':
            varlist.append(("width", "float", "{0:g}".format(value.width())))
            varlist.append(("height", "float", "{0:g}".format(value.height())))
        elif qttype == 'QColor':
            varlist.append(("name", "QString", "{0}".format(value.name())))
            r, g, b, a = value.getRgb()
            varlist.append(("rgb", "int", 
                            "{0:d}, {1:d}, {2:d}, {3:d}".format(r, g, b, a)))
            h, s, v, a = value.getHsv()
            varlist.append(("hsv", "int", 
                            "{0:d}, {1:d}, {2:d}, {3:d}".format(h, s, v, a)))
            c, m, y, k, a = value.getCmyk()
            varlist.append(("cmyk", "int", 
                            "{0:d}, {1:d}, {2:d}, {3:d}, {4:d}".format(c, m, y, k, a)))
        elif qttype == 'QDate':
            varlist.append(("", "QDate", "{0}".format(value.toString())))
        elif qttype == 'QTime':
            varlist.append(("", "QTime", "{0}".format(value.toString())))
        elif qttype == 'QDateTime':
            varlist.append(("", "QDateTime", "{0}".format(value.toString())))
        elif qttype == 'QDir':
            varlist.append(("path", "QString", "{0}".format(value.path())))
            varlist.append(("absolutePath", "QString", 
                            "{0}".format(value.absolutePath())))
            varlist.append(("canonicalPath", "QString", 
                            "{0}".format(value.canonicalPath())))
        elif qttype == 'QFile':
            varlist.append(("fileName", "QString", "{0}".format(value.fileName())))
        elif qttype == 'QFont':
            varlist.append(("family", "QString", "{0}".format(value.family())))
            varlist.append(("pointSize", "int", "{0:d}".format(value.pointSize())))
            varlist.append(("weight", "int", "{0:d}".format(value.weight())))
            varlist.append(("bold", "bool", "{0}".format(value.bold())))
            varlist.append(("italic", "bool", "{0}".format(value.italic())))
        elif qttype == 'QUrl':
            varlist.append(("url", "QString", "{0}".format(value.toString())))
            varlist.append(("scheme", "QString", "{0}".format(value.scheme())))
            varlist.append(("user", "QString", "{0}".format(value.userName())))
            varlist.append(("password", "QString", "{0}".format(value.password())))
            varlist.append(("host", "QString", "{0}".format(value.host())))
            varlist.append(("port", "int", "%d" % value.port()))
            varlist.append(("path", "QString", "{0}".format(value.path())))
        elif qttype == 'QModelIndex':
            varlist.append(("valid", "bool", "{0}".format(value.isValid())))
            if value.isValid():
                varlist.append(("row", "int", "{0}".format(value.row())))
                varlist.append(("column", "int", "{0}".format(value.column())))
                varlist.append(("internalId", "int", "{0}".format(value.internalId())))
                varlist.append(("internalPointer", "void *", 
                                "{0}".format(value.internalPointer())))
        elif qttype == 'QRegExp':
            varlist.append(("pattern", "QString", "{0}".format(value.pattern())))
        
        # GUI stuff
        elif qttype == 'QAction':
            varlist.append(("name", "QString", "{0}".format(value.objectName())))
            varlist.append(("text", "QString", "{0}".format(value.text())))
            varlist.append(("icon text", "QString", "{0}".format(value.iconText())))
            varlist.append(("tooltip", "QString", "{0}".format(value.toolTip())))
            varlist.append(("whatsthis", "QString", "{0}".format(value.whatsThis())))
            varlist.append(("shortcut", "QString", 
                            "{0}".format(value.shortcut().toString())))
        elif qttype == 'QKeySequence':
            varlist.append(("value", "", "{0}".format(value.toString())))
            
        # XML stuff
        elif qttype == 'QDomAttr':
            varlist.append(("name", "QString", "{0}".format(value.name())))
            varlist.append(("value", "QString", "{0}".format(value.value())))
        elif qttype == 'QDomCharacterData':
            varlist.append(("data", "QString", "{0}".format(value.data())))
        elif qttype == 'QDomComment':
            varlist.append(("data", "QString", "{0}".format(value.data())))
        elif qttype == "QDomDocument":
            varlist.append(("text", "QString", "{0}".format(value.toString())))
        elif qttype == 'QDomElement':
            varlist.append(("tagName", "QString", "{0}".format(value.tagName())))
            varlist.append(("text", "QString", "{0}".format(value.text())))
        elif qttype == 'QDomText':
            varlist.append(("data", "QString", "{0}".format(value.data())))
            
        # Networking stuff
        elif qttype == 'QHostAddress':
            varlist.append(("address", "QHostAddress", "{0}".format(value.toString())))
            
        return varlist
    
    def __formatVariablesList(self, keylist, dict, scope, filter = [], 
                              formatSequences = False):
        """
        Private method to produce a formated variables list.
        
        The dictionary passed in to it is scanned. Variables are
        only added to the list, if their type is not contained 
        in the filter list and their name doesn't match any of the filter expressions.
        The formated variables list (a list of tuples of 3 values) is returned.
        
        @param keylist keys of the dictionary
        @param dict the dictionary to be scanned
        @param scope 1 to filter using the globals filter, 0 using the locals 
            filter (int).
            Variables are only added to the list, if their name do not match any of the
            filter expressions.
        @param filter the indices of variable types to be filtered. Variables are
            only added to the list, if their type is not contained in the filter 
            list.
        @param formatSequences flag indicating, that sequence or dictionary variables
            should be formatted. If it is 0 (or false), just the number of items contained
            in these variables is returned. (boolean)
        @return A tuple consisting of a list of formatted variables. Each variable
            entry is a tuple of three elements, the variable name, its type and 
            value.
        """
        varlist = []
        if scope:
            patternFilterObjects = self.globalsFilterObjects
        else:
            patternFilterObjects = self.localsFilterObjects
        
        for key in keylist:
            # filter based on the filter pattern
            matched = False
            for pat in patternFilterObjects:
                if pat.match(str(key)):
                    matched = True
                    break
            if matched:
                continue
            
            # filter hidden attributes (filter #0)
            if 0 in filter and str(key)[:2] == '__':
                continue
            
            # special handling for '__builtins__' (it's way too big)
            if key == '__builtins__':
                rvalue = '<module __builtin__ (built-in)>'
                valtype = 'module'
            else:
                value = dict[key]
                valtypestr = str(type(value))[1:-1]
                
                valtype = valtypestr[7:-1]
                if valtype not in ConfigVarTypeStrings:
                    if ConfigVarTypeStrings.index('instance') in filter:
                        continue
                    valtype = valtypestr
                else:
                    try:
                        if ConfigVarTypeStrings.index(valtype) in filter:
                            continue
                    except ValueError:
                        if valtype == "classobj":
                            if ConfigVarTypeStrings.index('instance') in filter:
                                continue
                        elif ConfigVarTypeStrings.index('other') in filter:
                            continue
                
                try:
                    if valtype not in ['list', 'tuple', 'dict']:
                        rvalue = repr(value)
                        if valtype.startswith('class') and \
                           rvalue[0] in ['{', '(', '[']:
                            rvalue = ""
                    else:
                        if valtype == 'dict':
                            rvalue = "{0:d}".format(len(value.keys()))
                        else:
                            rvalue = "{0:d}".format(len(value))
                except:
                    rvalue = ''
            
            if formatSequences:
                if str(key) == key:
                    key = "'{0!s}'".format(key)
                else:
                    key = str(key)
            varlist.append((key, valtype, rvalue))
        
        return varlist
    
    def __generateFilterObjects(self, scope, filterString):
        """
        Private slot to convert a filter string to a list of filter objects.
        
        @param scope 1 to generate filter for global variables, 0 for local 
            variables (int)
        @param filterString string of filter patterns separated by ';'
        """
        patternFilterObjects = []
        for pattern in filterString.split(';'):
            patternFilterObjects.append(re.compile('^{0}$'.format(pattern)))
        if scope:
            self.globalsFilterObjects = patternFilterObjects[:]
        else:
            self.localsFilterObjects = patternFilterObjects[:]
    
    def __completionList(self, text):
        """
        Private slot to handle the request for a commandline completion list.
        
        @param text the text to be completed (string)
        """
        completerDelims = ' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>/?'
        
        completions = []
        state = 0
        # find position of last delim character
        pos = -1
        while pos >= -len(text):
            if text[pos] in completerDelims:
                if pos == -1:
                    text = ''
                else:
                    text = text[pos+1:]
                break
            pos -= 1
        
        try:
            comp = self.complete(text, state)
        except:
            comp = None
        while comp is not None:
            completions.append(comp)
            state += 1
            try:
                comp = self.complete(text, state)
            except:
                comp = None
        
        self.write("{0}{1}||{2}\n".format(ResponseCompletion, str(completions), text))

    def startDebugger(self, filename = None, host = None, port = None,
            enableTrace = True, exceptions = True, tracePython = False, redirect = True):
        """
        Public method used to start the remote debugger.
        
        @param filename the program to be debugged (string)
        @param host hostname of the debug server (string)
        @param port portnumber of the debug server (int)
        @param enableTrace flag to enable the tracing function (boolean)
        @param exceptions flag to enable exception reporting of the IDE (boolean)
        @param tracePython flag to enable tracing into the Python library (boolean)
        @param redirect flag indicating redirection of stdin, stdout and stderr (boolean)
        """
        global debugClient
        if host is None:
            host = os.getenv('ERICHOST', 'localhost')
        if port is None:
            port = os.getenv('ERICPORT', 42424)
        
        remoteAddress = self.__resolveHost(host)
        self.connectDebugger(port, remoteAddress, redirect)
        if filename is not None:
            self.running = os.path.abspath(filename)
        else:
            try:
                self.running = os.path.abspath(sys.argv[0])
            except IndexError:
                self.running = None
        if self.running:
            self.__setCoding(self.running)
            try:
                sys.setappdefaultencoding(self.defaultCoding)
            except AttributeError:
                pass
        self.passive = True
        self.write("{0}{1}|{2:d}\n".format(PassiveStartup, self.running, exceptions))
        self.__interact()
        
        # setup the debugger variables
        self.fncache = {}
        self.dircache = []
        self.mainFrame = None
        self.inRawMode = False
        self.debugging = True
        
        self.attachThread(mainThread = True)
        self.mainThread.tracePython = tracePython
        
        # set the system exception handling function to ensure, that
        # we report on all unhandled exceptions
        sys.excepthook = self.__unhandled_exception
        
        # now start debugging
        if enableTrace:
            self.mainThread.set_trace()
    
    def startProgInDebugger(self, progargs, wd = '', host = None, 
            port = None, exceptions = True, tracePython = False, redirect = True):
        """
        Public method used to start the remote debugger.
        
        @param progargs commandline for the program to be debugged 
            (list of strings)
        @param wd working directory for the program execution (string)
        @param host hostname of the debug server (string)
        @param port portnumber of the debug server (int)
        @param exceptions flag to enable exception reporting of the IDE (boolean)
        @param tracePython flag to enable tracing into the Python library (boolean)
        @param redirect flag indicating redirection of stdin, stdout and stderr (boolean)
        """
        if host is None:
            host = os.getenv('ERICHOST', 'localhost')
        if port is None:
            port = os.getenv('ERICPORT', 42424)
        
        remoteAddress = self.__resolveHost(host)
        self.connectDebugger(port, remoteAddress, redirect)
        
        self.fncache = {}
        self.dircache = []
        sys.argv = progargs[:]
        sys.argv[0] = os.path.abspath(sys.argv[0])
        sys.path[0] = os.path.dirname(sys.argv[0])
        sys.path.insert(0, '')
        if wd == '':
            os.chdir(sys.path[1])
        else:
            os.chdir(wd)
        self.running = sys.argv[0]
        self.__setCoding(self.running)
        try:
            sys.setappdefaultencoding(self.__coding)
        except AttributeError:
            pass
        self.mainFrame = None
        self.inRawMode = False
        self.debugging = True
        
        self.passive = True
        self.write("{0}{1}|{2:d}\n".format(PassiveStartup, self.running, exceptions))
        self.__interact()
        
        self.attachThread(mainThread = True)
        self.mainThread.tracePython = tracePython
        
        # set the system exception handling function to ensure, that
        # we report on all unhandled exceptions
        sys.excepthook = self.__unhandled_exception
        
        # This will eventually enter a local event loop.
        # Note the use of backquotes to cause a repr of self.running. The
        # need for this is on Windows os where backslash is the path separator.
        # They will get inadvertantly stripped away during the eval causing IOErrors
        # if self.running is passed as a normal str.
        self.debugMod.__dict__['__file__'] = self.running
        sys.modules['__main__'] = self.debugMod
        res = self.mainThread.run('exec(open(' + repr(self.running) + ').read())',
                                  self.debugMod.__dict__)
        self.progTerminated(res)

    def run_call(self, scriptname, func, *args):
        """
        Public method used to start the remote debugger and call a function.
        
        @param scriptname name of the script to be debugged (string)
        @param func function to be called
        @param *args arguments being passed to func
        @return result of the function call
        """
        self.startDebugger(scriptname, enableTrace = False)
        res = self.mainThread.runcall(func, *args)
        self.progTerminated(res)
        return res
    
    def __resolveHost(self, host):
        """
        Private method to resolve a hostname to an IP address.
        
        @param host hostname of the debug server (string)
        @return IP address (string)
        """
        try:
            host, version = host.split("@@")
        except ValueError:
            version = 'v4'
        if version == 'v4':
            family = socket.AF_INET
        else:
            family = socket.AF_INET6
        return socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)[0][4][0]
    
    def main(self):
        """
        Public method implementing the main method.
        """
        if '--' in sys.argv:
            args = sys.argv[1:]
            host = None
            port = None
            wd = ''
            tracePython = False
            exceptions = True
            redirect = True
            while args[0]:
                if args[0] == '-h':
                    host = args[1]
                    del args[0]
                    del args[0]
                elif args[0] == '-p':
                    port = int(args[1])
                    del args[0]
                    del args[0]
                elif args[0] == '-w':
                    wd = args[1]
                    del args[0]
                    del args[0]
                elif args[0] == '-t':
                    tracePython = True
                    del args[0]
                elif args[0] == '-e':
                    exceptions = False
                    del args[0]
                elif args[0] == '-n':
                    redirect = False
                    del args[0]
                elif args[0] == '--no-encoding':
                    self.noencoding = True
                    del args[0]
                elif args[0] == '--':
                    del args[0]
                    break
                else:   # unknown option
                    del args[0]
            if not args:
                print("No program given. Aborting!")
            else:
                if not self.noencoding:
                    self.__coding = self.defaultCoding
                    try:
                        sys.setappdefaultencoding(self.defaultCoding)
                    except AttributeError:
                        pass
                self.startProgInDebugger(args, wd, host, port, 
                                         exceptions = exceptions, 
                                         tracePython = tracePython,
                                         redirect = redirect)
        else:
            if sys.argv[1] == '--no-encoding':
                self.noencoding = True
                del sys.argv[1]
            if sys.argv[1] == '':
                del sys.argv[1]
            try:
                port = int(sys.argv[1])
            except (ValueError, IndexError):
                port = -1
            try:
                redirect = int(sys.argv[2])
            except (ValueError, IndexError):
                redirect = True
            try:
                ipOrHost = sys.argv[3]
                if ':' in ipOrHost:
                    remoteAddress = ipOrHost
                elif ipOrHost[0] in '0123456789':
                    remoteAddress = ipOrHost
                else:
                    remoteAddress = self.__resolveHost(ipOrHost)
            except:
                remoteAddress = None
            sys.argv = ['']
            if not '' in sys.path:
                sys.path.insert(0, '')
            if port >= 0:
                if not self.noencoding:
                    self.__coding = self.defaultCoding
                    try:
                        sys.setappdefaultencoding(self.defaultCoding)
                    except AttributeError:
                        pass
                self.connectDebugger(port, remoteAddress, redirect)
                self.__interact()
            else:
                print("No network port given. Aborting...")
        
    def fork(self):
        """
        Public method implementing a fork routine deciding which branch to follow.
        """
        if not self.fork_auto:
            self.write(RequestForkTo + '\n')
            self.eventLoop(True)
        pid = DebugClientOrigFork()
        if pid == 0:
            # child
            if not self.fork_child:
                sys.settrace(None)
                sys.setprofile(None)
                self.sessionClose(0)
        else:
            # parent
            if self.fork_child:
                sys.settrace(None)
                sys.setprofile(None)
                self.sessionClose(0)
        return pid
        
    def close(self, fd):
        """
        Private method implementing a close method as a replacement for os.close().
        
        It prevents the debugger connections from being closed.
        
        @param fd file descriptor to be closed (integer)
        """
        if fd in [self.readstream.fileno(), self.writestream.fileno(), 
                  self.errorstream.fileno()]:
            return
        
        DebugClientOrigClose(fd)
