# -*- coding: utf-8 -*-

# Copyright (c) 2002 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the debug base class.
"""

import sys
import traceback
import bdb
import os
import types
import atexit
import inspect

from DebugProtocol import *

gRecursionLimit = 64

def printerr(s):
    """
    Module function used for debugging the debug client.
    
    @param s data to be printed
    """
    import sys
    sys.__stderr__.write('%s\n' % unicode(s))
    sys.__stderr__.flush()

def setRecursionLimit(limit):
    """
    Module function to set the recursion limit.
    
    @param limit recursion limit (integer)
    """
    global gRecursionLimit
    gRecursionLimit = limit

class DebugBase(bdb.Bdb):
    """
    Class implementing base class of the debugger.

    Provides simple wrapper methods around bdb for the 'owning' client to
    call to step etc.
    """
    def __init__(self, dbgClient):
        """
        Constructor
        
        @param dbgClient the owning client
        """
        bdb.Bdb.__init__(self)

        self._dbgClient = dbgClient
        self._mainThread = 1
        
        self.breaks = self._dbgClient.breakpoints
        
        self.__event = ""
        self.__isBroken = ""
        self.cFrame = None
        
        # current frame we are at
        self.currentFrame = None
        
        # frame that we are stepping in, can be different than currentFrame
        self.stepFrame = None
        
        # provide a hook to perform a hard breakpoint
        # Use it like this:
        # if hasattr(sys, 'breakpoint): sys.breakpoint()
        sys.breakpoint = self.set_trace
        
        # initialize parent
        bdb.Bdb.reset(self)
        
        self.__recursionDepth = -1
        self.setRecursionDepth(inspect.currentframe())
    
    def getCurrentFrame(self):
        """
        Public method to return the current frame.
        
        @return the current frame
        """
        return self.currentFrame        
    
    def step(self, traceMode):
        """
        Public method to perform a step operation in this thread.
        
        @param traceMode If it is non-zero, then the step is a step into,
              otherwise it is a step over.
        """
        self.stepFrame = self.currentFrame
        
        if traceMode:
            self.currentFrame = None
            self.set_step()
        else:
            self.set_next(self.currentFrame)
    
    def stepOut(self):
        """
        Public method to perform a step out of the current call.
        """
        self.stepFrame = self.currentFrame
        self.set_return(self.currentFrame)
    
    def go(self, special):
        """
        Public method to resume the thread.

        It resumes the thread stopping only at breakpoints or exceptions.
        
        @param special flag indicating a special continue operation
        """
        self.currentFrame = None
        self.set_continue(special)
    
    def setRecursionDepth(self, frame):
        """
        Public method to determine the current recursion depth.
        
        @param frame The current stack frame.
        """
        self.__recursionDepth = 0
        while frame is not None:
            self.__recursionDepth += 1
            frame = frame.f_back
    
    def profile(self, frame, event, arg):
        """
        Public method used to trace some stuff independant of the debugger 
        trace function.
        
        @param frame The current stack frame.
        @param event The trace event (string)
        @param arg The arguments
        """
        if event == 'return':  
            self.cFrame = frame.f_back
            self.__recursionDepth -= 1
        elif event == 'call':
            self.cFrame = frame
            self.__recursionDepth += 1
            if self.__recursionDepth > gRecursionLimit:
                raise RuntimeError('maximum recursion depth exceeded\n'
                    '(offending frame is two down the stack)')
    
    def trace_dispatch(self, frame, event, arg):
        """
        Reimplemented from bdb.py to do some special things.
        
        This specialty is to check the connection to the debug server
        for new events (i.e. new breakpoints) while we are going through
        the code.
        
        @param frame The current stack frame.
        @param event The trace event (string)
        @param arg The arguments
        @return local trace function
        """
        if self.quitting:
            return # None
        
        # give the client a chance to push through new break points.
        self._dbgClient.eventPoll()
        
        self.__event == event
        self.__isBroken = False
        
        if event == 'line':
            return self.dispatch_line(frame)
        if event == 'call':
            return self.dispatch_call(frame, arg)
        if event == 'return':
            return self.dispatch_return(frame, arg)
        if event == 'exception':
            return self.dispatch_exception(frame, arg)
        if event == 'c_call':
            return self.trace_dispatch
        if event == 'c_exception':
            return self.trace_dispatch
        if event == 'c_return':
            return self.trace_dispatch
        print 'DebugBase.trace_dispatch: unknown debugging event:', `event`
        return self.trace_dispatch

    def dispatch_line(self, frame):
        """
        Reimplemented from bdb.py to do some special things.
        
        This speciality is to check the connection to the debug server
        for new events (i.e. new breakpoints) while we are going through
        the code.
        
        @param frame The current stack frame.
        @return local trace function
        """
        if self.stop_here(frame) or self.break_here(frame):
            self.user_line(frame)
            if self.quitting: raise bdb.BdbQuit
        return self.trace_dispatch

    def dispatch_return(self, frame, arg):
        """
        Reimplemented from bdb.py to handle passive mode cleanly.
        
        @param frame The current stack frame.
        @param arg The arguments
        @return local trace function
        """
        if self.stop_here(frame) or frame == self.returnframe:
            self.user_return(frame, arg)
            if self.quitting and not self._dbgClient.passive:
                raise bdb.BdbQuit
        return self.trace_dispatch

    def dispatch_exception(self, frame, arg):
        """
        Reimplemented from bdb.py to always call user_exception.
        
        @param frame The current stack frame.
        @param arg The arguments
        @return local trace function
        """
        if not self.__skip_it(frame):
            self.user_exception(frame, arg)
            if self.quitting: raise bdb.BdbQuit
        return self.trace_dispatch

    def set_trace(self, frame = None):
        """
        Overridden method of bdb.py to do some special setup.
        
        @param frame frame to start debugging from
        """
        bdb.Bdb.set_trace(self, frame)
        sys.setprofile(self.profile)
    
    def set_continue(self, special):
        """
        Reimplemented from bdb.py to always get informed of exceptions.
        
        @param special flag indicating a special continue operation
        """
        # Modified version of the one found in bdb.py
        # Here we only set a new stop frame if it is a normal continue.
        if not special:
            self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = 0

    def set_quit(self):
        """
        Public method to quit. 
        
        It wraps call to bdb to clear the current frame properly.
        """
        self.currentFrame = None
        sys.setprofile(None)
        bdb.Bdb.set_quit(self)
    
    def fix_frame_filename(self, frame):
        """
        Public method used to fixup the filename for a given frame.
        
        The logic employed here is that if a module was loaded
        from a .pyc file, then the correct .py to operate with
        should be in the same path as the .pyc. The reason this
        logic is needed is that when a .pyc file is generated, the
        filename embedded and thus what is readable in the code object
        of the frame object is the fully qualified filepath when the
        pyc is generated. If files are moved from machine to machine
        this can break debugging as the .pyc will refer to the .py
        on the original machine. Another case might be sharing
        code over a network... This logic deals with that.
        
        @param frame the frame object
        """
        # get module name from __file__
        if frame.f_globals.has_key('__file__') and \
           frame.f_globals['__file__'] and \
           frame.f_globals['__file__'] == frame.f_code.co_filename:
            root, ext = os.path.splitext(frame.f_globals['__file__'])
            if ext == '.pyc' or ext == '.py' or ext == '.pyo':
                fixedName = root + '.py'
                if os.path.exists(fixedName):
                    return fixedName

        return frame.f_code.co_filename

    def set_watch(self, cond, temporary=0):
        """
        Public method to set a watch expression.
        
        @param cond expression of the watch expression (string)
        @param temporary flag indicating a temporary watch expression (boolean)
        """
        bp = bdb.Breakpoint("Watch", 0, temporary, cond)
        if cond.endswith('??created??') or cond.endswith('??changed??'):
            bp.condition, bp.special = cond.split()
        else:
            bp.condition = cond
            bp.special = ""
        bp.values = {}
        if not self.breaks.has_key("Watch"):
            self.breaks["Watch"] = 1
        else:
            self.breaks["Watch"] += 1
    
    def clear_watch(self, cond):
        """
        Public method to clear a watch expression.
        
        @param cond expression of the watch expression to be cleared (string)
        """
        try: 
            possibles = bdb.Breakpoint.bplist["Watch", 0]
            for i in range(0, len(possibles)):
                b = possibles[i]
                if b.cond == cond:
                    b.deleteMe()
                    self.breaks["Watch"] -= 1
                    if self.breaks["Watch"] == 0:
                        del self.breaks["Watch"]
                    break
        except KeyError:
            pass
    
    def get_watch(self, cond):
        """
        Public method to get a watch expression.
        
        @param cond expression of the watch expression to be cleared (string)
        """
        possibles = bdb.Breakpoint.bplist["Watch", 0]
        for i in range(0, len(possibles)):
            b = possibles[i]
            if b.cond == cond:
                return b
    
    def __do_clearWatch(self, cond):
        """
        Private method called to clear a temporary watch expression.
        
        @param cond expression of the watch expression to be cleared (string)
        """
        self.clear_watch(cond)
        self._dbgClient.write('%s%s\n' % (ResponseClearWatch, cond))

    def __effective(self, frame):
        """
        Private method to determine, if a watch expression is effective.
        
        @param frame the current execution frame
        @return tuple of watch expression and a flag to indicate, that a temporary
            watch expression may be deleted (bdb.Breakpoint, boolean)
        """
        possibles = bdb.Breakpoint.bplist["Watch", 0]
        for i in range(0, len(possibles)):
            b = possibles[i]
            if b.enabled == 0:
                continue
            if not b.cond:
                # watch expression without expression shouldn't occur, just ignore it
                continue
            try:
                val = eval(b.condition, frame.f_globals, frame.f_locals)
                if b.special:
                    if b.special == '??created??':
                        if b.values[frame][0] == 0:
                            b.values[frame][0] = 1
                            b.values[frame][1] = val
                            return (b, 1)
                        else:
                            continue
                    b.values[frame][0] = 1
                    if b.special == '??changed??':
                        if b.values[frame][1] != val:
                            b.values[frame][1] = val
                            if b.values[frame][2] > 0:
                                b.values[frame][2] -= 1
                                continue
                            else:
                                return (b, 1)
                        else:
                            continue
                    continue
                if val:
                    if b.ignore > 0:
                        b.ignore -= 1
                        continue
                    else:
                        return (b, 1)
            except:
                if b.special:
                    try:
                        b.values[frame][0] = 0
                    except KeyError:
                        b.values[frame] = [0, None, b.ignore]
                continue
        return (None, None)
    
    def break_here(self, frame):
        """
        Reimplemented from bdb.py to fix the filename from the frame. 
        
        See fix_frame_filename for more info.
        
        @param frame the frame object
        @return flag indicating the break status (boolean)
        """
        filename = self.canonic(self.fix_frame_filename(frame))
        if not self.breaks.has_key(filename) and not self.breaks.has_key("Watch"):
            return 0
        
        if self.breaks.has_key(filename):
            lineno = frame.f_lineno
            if lineno in self.breaks[filename]:
                # flag says ok to delete temp. bp
                (bp, flag) = bdb.effective(filename, lineno, frame)
                if bp:
                    self.currentbp = bp.number
                    if (flag and bp.temporary):
                        self.__do_clear(filename, lineno)
                    return 1
        
        if self.breaks.has_key("Watch"):
            # flag says ok to delete temp. bp
            (bp, flag) = self.__effective(frame)
            if bp:
                self.currentbp = bp.number
                if (flag and bp.temporary):
                    self.__do_clearWatch(bp.cond)
                return 1
        
        return 0

    def break_anywhere(self, frame):
        """
        Reimplemented from bdb.py to do some special things.
        
        These speciality is to fix the filename from the frame
        (see fix_frame_filename for more info).
        
        @param frame the frame object
        @return flag indicating the break status (boolean)
        """
        return self.breaks.has_key(
            self.canonic(self.fix_frame_filename(frame))) or \
            (self.breaks.has_key("Watch") and self.breaks["Watch"])

    def get_break(self, filename, lineno):
        """
        Reimplemented from bdb.py to get the first breakpoint of a particular line.
        
        Because eric4 supports only one breakpoint per line, this overwritten
        method will return this one and only breakpoint.
        
        @param filename the filename of the bp to retrieve (string)
        @param ineno the linenumber of the bp to retrieve (integer)
        @return breakpoint or None, if there is no bp
        """
        filename = self.canonic(filename)
        return self.breaks.has_key(filename) and \
            lineno in self.breaks[filename] and \
            bdb.Breakpoint.bplist[filename, lineno][0] or None
    
    def __do_clear(self, filename, lineno):
        """
        Private method called to clear a temporary breakpoint.
        
        @param filename name of the file the bp belongs to
        @param lineno linenumber of the bp
        """
        self.clear_break(filename, lineno)
        self._dbgClient.write('%s%s,%d\n' % (ResponseClearBreak, filename, lineno))

    def getStack(self):
        """
        Public method to get the stack.
        
        @return list of lists with file name (string), line number (integer)
            and function name (string)
        """
        fr = self.cFrame
        stack = []
        while fr is not None:
            fname = self._dbgClient.absPath(self.fix_frame_filename(fr))
            fline = fr.f_lineno
            ffunc = fr.f_code.co_name
            
            if ffunc == '?':
                ffunc = ''
            
            stack.append([fname, fline, ffunc])
            
            if fr == self._dbgClient.mainFrame:
                fr = None
            else:
                fr = fr.f_back
        
        return stack
    
    def user_line(self, frame):
        """
        Reimplemented to handle the program about to execute a particular line.
        
        @param frame the frame object
        """
        line = frame.f_lineno

        # We never stop on line 0.
        if line == 0:
            return

        fn = self._dbgClient.absPath(self.fix_frame_filename(frame))

        # See if we are skipping at the start of a newly loaded program.
        if self._dbgClient.mainFrame is None:
            if fn != self._dbgClient.getRunning():
                return
            self._dbgClient.mainFrame = frame

        self.currentFrame = frame
        
        fr = frame
        stack = []
        while fr is not None:
            # Reset the trace function so we can be sure
            # to trace all functions up the stack... This gets around
            # problems where an exception/breakpoint has occurred
            # but we had disabled tracing along the way via a None
            # return from dispatch_call
            fr.f_trace = self.trace_dispatch
            fname = self._dbgClient.absPath(self.fix_frame_filename(fr))
            fline = fr.f_lineno
            ffunc = fr.f_code.co_name
            
            if ffunc == '?':
                ffunc = ''
            
            stack.append([fname, fline, ffunc])
            
            if fr == self._dbgClient.mainFrame:
                fr = None
            else:
                fr = fr.f_back
        
        self.__isBroken = True
        
        self._dbgClient.write('%s%s\n' % (ResponseLine, unicode(stack)))
        self._dbgClient.eventLoop()

    def user_exception(self,frame,(exctype,excval,exctb),unhandled=0):
        """
        Reimplemented to report an exception to the debug server.
        
        @param frame the frame object
        @param exctype the type of the exception
        @param excval data about the exception
        @param exctb traceback for the exception
        @param unhandled flag indicating an uncaught exception
        """
        if exctype in [SystemExit, bdb.BdbQuit]:
            atexit._run_exitfuncs()
            if isinstance(excval, int):
                self._dbgClient.progTerminated(excval)
            else:
                self._dbgClient.progTerminated(excval.code)
            return
        
        elif exctype in [SyntaxError, IndentationError]:
            try:
                message, (filename, linenr, charnr, text) = excval
            except ValueError:
                exclist = []
            else:
                exclist = [message, [filename, linenr, charnr]]
            
            self._dbgClient.write("%s%s\n" % (ResponseSyntax, unicode(exclist)))
        
        else:
            if type(exctype) in [types.ClassType,   # Python up to 2.4
                                 types.TypeType]:   # Python 2.5+
                exctype = exctype.__name__
            
            if excval is None:
                excval = ''
            
            if unhandled:
                exctypetxt = "unhandled %s" % unicode(exctype)
            else:
                exctypetxt = unicode(exctype)
            try:
                exclist = [exctypetxt, 
                           unicode(excval).encode(self._dbgClient.getCoding())]
            except TypeError:
                exclist = [exctypetxt, str(excval)]
            
            if exctb:
                frlist = self.__extract_stack(exctb)
                frlist.reverse()
                
                self.currentFrame = frlist[0]
                
                for fr in frlist:
                    filename = self._dbgClient.absPath(self.fix_frame_filename(fr))
                    linenr = fr.f_lineno
                    
                    if os.path.basename(filename).startswith("DebugClient") or \
                       os.path.basename(filename) == "bdb.py":
                        break
                    
                    exclist.append([filename, linenr])
            
            self._dbgClient.write("%s%s\n" % (ResponseException, unicode(exclist)))
            
            if exctb is None:
                return
        
        self._dbgClient.eventLoop()
    
    def __extract_stack(self, exctb):
        """
        Private member to return a list of stack frames.
        
        @param exctb exception traceback
        @return list of stack frames
        """
        tb = exctb
        stack = []
        while tb is not None:
            stack.append(tb.tb_frame)
            tb = tb.tb_next
        tb = None
        return stack

    def user_return(self,frame,retval):
        """
        Reimplemented to report program termination to the debug server.
        
        @param frame the frame object
        @param retval the return value of the program
        """
        # The program has finished if we have just left the first frame.
        if frame == self._dbgClient.mainFrame and \
            self._mainThread:
            atexit._run_exitfuncs()
            self._dbgClient.progTerminated(retval)
        elif frame is not self.stepFrame:
            self.stepFrame = None
            self.user_line(frame)

    def stop_here(self,frame):
        """
        Reimplemented to filter out debugger files.
        
        Tracing is turned off for files that are part of the
        debugger that are called from the application being debugged.
        
        @param frame the frame object
        @return flag indicating whether the debugger should stop here
        """
        if self.__skip_it(frame):
            return 0
        return bdb.Bdb.stop_here(self,frame)

    def __skip_it(self, frame):
        """
        Private method to filter out debugger files.
        
        Tracing is turned off for files that are part of the
        debugger that are called from the application being debugged.
        
        @param frame the frame object
        @return flag indicating whether the debugger should skip this frame
        """
        fn = self.fix_frame_filename(frame)

        # Eliminate things like <string> and <stdin>.
        if fn[0] == '<':
            return 1

        #XXX - think of a better way to do this.  It's only a convience for
        #debugging the debugger - when the debugger code is in the current
        #directory.
        if os.path.basename(fn) in [\
            'AsyncFile.py', 'AsyncIO.py',
            'DebugConfig.py', 'DCTestResult.py',
            'DebugBase.py', 'DebugClientBase.py', 
            'DebugClientCapabilities.py', 'DebugClient.py', 
            'DebugClientThreads.py', 'DebugProtocol.py',
            'DebugThread.py', 'FlexCompleter.py',
            'PyProfile.py'] or \
           os.path.dirname(fn).endswith("coverage"):
            return 1

        if self._dbgClient.shouldSkip(fn):
            return 1
        
        return 0
    
    def isBroken(self):
        """
        Public method to return the broken state of the debugger.
        
        @return flag indicating the broken state (boolean)
        """
        return self.__isBroken
    
    def getEvent(self):
        """
        Public method to return the last debugger event.
        
        @return last debugger event (string)
        """
        return self.__event
