# -*- coding: utf-8 -*-

"""
The Tab Nanny despises ambiguous indentation.  She knows no mercy.

tabnanny -- Detection of ambiguous indentation

For the time being this module is intended to be called as a script.
However it is possible to import it into an IDE and use the function
check() described below.

Warning: The API provided by this module is likely to change in future
releases; such changes may not be backward compatible.

This is a modified version to make the original tabnanny better suitable
for being called from within the eric4 IDE.

@exception ValueError The tokenize module is too old.
"""

# Released to the public domain, by Tim Peters, 15 April 1998.

# XXX Note: this is now a standard library module.
# XXX The API needs to undergo changes however; the current code is too
# XXX script-like.  This will be addressed later.

#
# This is a modified version to make the original tabnanny better suitable
# for being called from within the eric4 IDE. The modifications are as
# follows:
#
# - there is no main function anymore
# - check function has been modified to only accept a filename and return
#   a tuple indicating status (1 = an error was found), the filename, the
#   linenumber and the error message (boolean, string, string, string). The
#   values are only valid, if the status equals 1.
#
# Mofifications copyright (c) 2003 Detlev Offenbach <detlev@die-offenbachs.de>
#

__version__ = "6_eric"

import os
import sys
import tokenize
import cStringIO

import Utilities

if not hasattr(tokenize, 'NL'):
    raise ValueError("tokenize.NL doesn't exist -- tokenize module too old")

__all__ = ["check", "NannyNag", "process_tokens"]

class NannyNag(Exception):
    """
    Raised by tokeneater() if detecting an ambiguous indent.
    Captured and handled in check().
    """
    def __init__(self, lineno, msg, line):
        """
        Constructor
        
        @param lineno Line number of the ambiguous indent.
        @param msg Descriptive message assigned to this problem.
        @param line The offending source line.
        """
        self.lineno, self.msg, self.line = lineno, msg, line
        
    def get_lineno(self):
        """
        Method to retrieve the line number.
        
        @return The line number (integer)
        """
        return self.lineno
        
    def get_msg(self):
        """
        Method to retrieve the message.
        
        @return The error message (string)
        """
        return self.msg
        
    def get_line(self):
        """
        Method to retrieve the offending line.
        
        @return The line of code (string)
        """
        return self.line

def check(file):
    """
    Private function to check one Python source file for whitespace related problems.
    
    @param file source filename (string)
    @return A tuple indicating status (True = an error was found), the
        filename, the linenumber and the error message
        (boolean, string, string, string). The values are only
        valid, if the status is True.
    """
    global indents, check_equal
    indents = [Whitespace("")]
    check_equal = 0

    try:
        f = open(file)
    except IOError, msg:
        return (True, file, "1", "I/O Error: %s" % unicode(msg))

    try:
        text = Utilities.decode(f.read())[0].encode('utf-8')
    finally:
        f.close()
        
    # convert eols
    text = Utilities.convertLineEnds(text, os.linesep)
    
    source = cStringIO.StringIO(text)
    try:
        process_tokens(tokenize.generate_tokens(source.readline))
    
    except tokenize.TokenError, msg:
        f.close()
        return (True, file, "1", "Token Error: %s" % unicode(msg))
    
    except IndentationError, err:
        f.close()
        return (True, file, err.lineno, "Indentation Error: %s" % unicode(err.msg))
    
    except NannyNag, nag:
        badline = nag.get_lineno()
        line = nag.get_line()
        f.close()
        return (True, file, str(badline), line)
    
    except Exception, err:
        f.close()
        return (True, file, "1", "Unspecific Error: %s" % unicode(err))
    
    f.close()
    return (False, None, None, None)

class Whitespace(object):
    """
    Class implementing the whitespace checker.
    """
    # the characters used for space and tab
    S, T = ' \t'

    # members:
    #   raw
    #       the original string
    #   n
    #       the number of leading whitespace characters in raw
    #   nt
    #       the number of tabs in raw[:n]
    #   norm
    #       the normal form as a pair (count, trailing), where:
    #       count
    #           a tuple such that raw[:n] contains count[i]
    #           instances of S * i + T
    #       trailing
    #           the number of trailing spaces in raw[:n]
    #       It's A Theorem that m.indent_level(t) ==
    #       n.indent_level(t) for all t >= 1 iff m.norm == n.norm.
    #   is_simple
    #       true iff raw[:n] is of the form (T*)(S*)

    def __init__(self, ws):
        """
        Constructor
        
        @param ws The string to be checked.
        """
        self.raw  = ws
        S, T = Whitespace.S, Whitespace.T
        count = []
        b = n = nt = 0
        for ch in self.raw:
            if ch == S:
                n = n + 1
                b = b + 1
            elif ch == T:
                n = n + 1
                nt = nt + 1
                if b >= len(count):
                    count = count + [0] * (b - len(count) + 1)
                count[b] = count[b] + 1
                b = 0
            else:
                break
        self.n    = n
        self.nt   = nt
        self.norm = tuple(count), b
        self.is_simple = len(count) <= 1

    # return length of longest contiguous run of spaces (whether or not
    # preceding a tab)
    def longest_run_of_spaces(self):
        """
        Method to calculate the length of longest contiguous run of spaces.
        
        @return The length of longest contiguous run of spaces (whether or not
            preceding a tab)
        """
        count, trailing = self.norm
        return max(len(count)-1, trailing)

    def indent_level(self, tabsize):
        """
        Method to determine the indentation level.
        
        @param tabsize The length of a tab stop. (integer)
        @return indentation level (integer)
        """
        # count, il = self.norm
        # for i in range(len(count)):
        #    if count[i]:
        #        il = il + (i/tabsize + 1)*tabsize * count[i]
        # return il

        # quicker:
        # il = trailing + sum (i/ts + 1)*ts*count[i] =
        # trailing + ts * sum (i/ts + 1)*count[i] =
        # trailing + ts * sum i/ts*count[i] + count[i] =
        # trailing + ts * [(sum i/ts*count[i]) + (sum count[i])] =
        # trailing + ts * [(sum i/ts*count[i]) + num_tabs]
        # and note that i/ts*count[i] is 0 when i < ts

        count, trailing = self.norm
        il = 0
        for i in range(tabsize, len(count)):
            il = il + i/tabsize * count[i]
        return trailing + tabsize * (il + self.nt)

    # return true iff self.indent_level(t) == other.indent_level(t)
    # for all t >= 1
    def equal(self, other):
        """
        Method to compare the indentation levels of two Whitespace objects for equality.
        
        @param other Whitespace object to compare against.
        @return True, if we compare equal against the other Whitespace object.
        """
        return self.norm == other.norm

    # return a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) != other.indent_level(ts) == i2.
    # Intended to be used after not self.equal(other) is known, in which
    # case it will return at least one witnessing tab size.
    def not_equal_witness(self, other):
        """
        Method to calculate a tuple of witnessing tab size.
        
        Intended to be used after not self.equal(other) is known, in which
        case it will return at least one witnessing tab size.
        
        @param other Whitespace object to calculate against.
        @return A list of tuples (ts, i1, i2) such that
            i1 == self.indent_level(ts) != other.indent_level(ts) == i2.
        """
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        for ts in range(1, n+1):
            if self.indent_level(ts) != other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        return a

    # Return True iff self.indent_level(t) < other.indent_level(t)
    # for all t >= 1.
    # The algorithm is due to Vincent Broman.
    # Easy to prove it's correct.
    # XXXpost that.
    # Trivial to prove n is sharp (consider T vs ST).
    # Unknown whether there's a faster general way.  I suspected so at
    # first, but no longer.
    # For the special (but common!) case where M and N are both of the
    # form (T*)(S*), M.less(N) iff M.len() < N.len() and
    # M.num_tabs() <= N.num_tabs(). Proof is easy but kinda long-winded.
    # XXXwrite that up.
    # Note that M is of the form (T*)(S*) iff len(M.norm[0]) <= 1.
    def less(self, other):
        """
        Method to compare the indentation level against another Whitespace objects to 
        be smaller.
        
        @param other Whitespace object to compare against.
        @return True, if we compare less against the other Whitespace object.
        """
        if self.n >= other.n:
            return False
        if self.is_simple and other.is_simple:
            return self.nt <= other.nt
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        # the self.n >= other.n test already did it for ts=1
        for ts in range(2, n+1):
            if self.indent_level(ts) >= other.indent_level(ts):
                return False
        return True

    # return a list of tuples (ts, i1, i2) such that
    # i1 == self.indent_level(ts) >= other.indent_level(ts) == i2.
    # Intended to be used after not self.less(other) is known, in which
    # case it will return at least one witnessing tab size.
    def not_less_witness(self, other):
        """
        Method to calculate a tuple of witnessing tab size.
        
        Intended to be used after not self.less(other is known, in which
        case it will return at least one witnessing tab size.
        
        @param other Whitespace object to calculate against.
        @return A list of tuples (ts, i1, i2) such that
            i1 == self.indent_level(ts) >= other.indent_level(ts) == i2.
        """
        n = max(self.longest_run_of_spaces(),
                other.longest_run_of_spaces()) + 1
        a = []
        for ts in range(1, n+1):
            if self.indent_level(ts) >= other.indent_level(ts):
                a.append( (ts,
                           self.indent_level(ts),
                           other.indent_level(ts)) )
        return a

def format_witnesses(w):
    """
    Function to format the witnesses as a readable string.
    
    @param w A list of witnesses
    @return A formated string of the witnesses.
    """
    firsts = map(lambda tup: str(tup[0]), w)
    prefix = "at tab size"
    if len(w) > 1:
        prefix = prefix + "s"
    return prefix + " " + ', '.join(firsts)

def process_tokens(tokens):
    """
    Function processing all tokens generated by a tokenizer run.
    
    @param tokens list of tokens
    """
    indent = tokenize.indent
    dedent = tokenize.dedent
    NEWLINE = tokenize.NEWLINE
    JUNK = tokenize.COMMENT, tokenize.NL
    indents = [Whitespace("")]
    check_equal = 0
    
    for (type, token, start, end, line) in tokens:
        if type == NEWLINE:
            # a program statement, or ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            # If an INDENT appears, setting check_equal is wrong, and will
            # be undone when we see the INDENT.
            check_equal = 1

        elif type == indent:
            check_equal = 0
            thisguy = Whitespace(token)
            if not indents[-1].less(thisguy):
                witness = indents[-1].not_less_witness(thisguy)
                msg = "indent not greater e.g. " + format_witnesses(witness)
                raise NannyNag(start[0], msg, line)
            indents.append(thisguy)

        elif type == dedent:
            # there's nothing we need to check here!  what's important is
            # that when the run of DEDENTs ends, the indentation of the
            # program statement (or ENDMARKER) that triggered the run is
            # equal to what's left at the top of the indents stack

            # Ouch!  This assert triggers if the last line of the source
            # is indented *and* lacks a newline -- then DEDENTs pop out
            # of thin air.
            # assert check_equal  # else no earlier NEWLINE, or an earlier INDENT
            check_equal = 1

            del indents[-1]

        elif check_equal and type not in JUNK:
            # this is the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, or an
            # ENDMARKER; the "line" argument exposes the leading whitespace
            # for this statement; in the case of ENDMARKER, line is an empty
            # string, so will properly match the empty string with which the
            # "indents" stack was seeded
            check_equal = 0
            thisguy = Whitespace(line)
            if not indents[-1].equal(thisguy):
                witness = indents[-1].not_equal_witness(thisguy)
                msg = "indent not equal e.g. " + format_witnesses(witness)
                raise NannyNag(start[0], msg, line)
