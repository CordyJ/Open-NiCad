# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

=begin edoc
File implementing a command line completer class.
=end

#
# This code is mostly based on the completer found in irb of the Ruby package
# Original copyright
#       by Keiju ISHITSUKA(keiju@ishitsuka.com)
#       From Original Idea of shugo@ruby-lang.org
#

if RUBY_VERSION < "1.9"
    $KCODE = 'UTF8'
    require 'jcode'
end

class Completer
=begin edoc
Class implementing a command completer.
=end
    ReservedWords = [
        "BEGIN", "END",
        "alias", "and", 
        "begin", "break", 
        "case", "class",
        "def", "defined", "do",
        "else", "elsif", "end", "ensure",
        "false", "for", 
        "if", "in", 
        "module", 
        "next", "nil", "not",
        "or", 
        "redo", "rescue", "retry", "return",
        "self", "super",
        "then", "true",
        "undef", "unless", "until",
        "when", "while",
        "yield",
    ]
    
    def initialize(binding)
=begin edoc
constructor

@param binding binding object used to determine the possible completions
=end
        @binding = binding
    end
    
    def complete(input)
=begin edoc
Public method to select the possible completions

@param input text to be completed (String)
@return list of possible completions (Array)
=end
        case input
        when /^(\/[^\/]*\/)\.([^.]*)$/
        # Regexp
            receiver = $1
            message = Regexp.quote($2)

            candidates = Regexp.instance_methods(true)
            select_message(receiver, message, candidates)

        when /^([^\]]*\])\.([^.]*)$/
        # Array
            receiver = $1
            message = Regexp.quote($2)

            candidates = Array.instance_methods(true)
            select_message(receiver, message, candidates)

        when /^([^\}]*\})\.([^.]*)$/
        # Proc or Hash
            receiver = $1
            message = Regexp.quote($2)

            candidates = Proc.instance_methods(true) | Hash.instance_methods(true)
            select_message(receiver, message, candidates)
    
        when /^(:[^:.]*)$/
        # Symbol
            if Symbol.respond_to?(:all_symbols)
                sym = $1
                candidates = Symbol.all_symbols.collect{|s| ":" + s.id2name}
                candidates.grep(/^#{sym}/)
            else
                []
            end

        when /^::([A-Z][^:\.\(]*)$/
        # Absolute Constant or class methods
            receiver = $1
            candidates = Object.constants
            candidates.grep(/^#{receiver}/).collect{|e| "::" + e}

        when /^(((::)?[A-Z][^:.\(]*)+)::?([^:.]*)$/
        # Constant or class methods
            receiver = $1
            message = Regexp.quote($4)
            begin
                candidates = eval("#{receiver}.constants | #{receiver}.methods", @binding)
            rescue Exception
                candidates = []
            end
            candidates.grep(/^#{message}/).collect{|e| receiver + "::" + e}

        when /^(:[^:.]+)\.([^.]*)$/
        # Symbol
            receiver = $1
            message = Regexp.quote($2)

            candidates = Symbol.instance_methods(true)
            select_message(receiver, message, candidates)

        when /^([0-9_]+(\.[0-9_]+)?(e[0-9]+)?)\.([^.]*)$/
        # Numeric
            receiver = $1
            message = Regexp.quote($4)

            begin
                candidates = eval(receiver, @binding).methods
            rescue Exception
                candidates
            end
            select_message(receiver, message, candidates)

        when /^(\$[^.]*)$/
        # Global variable
            candidates = global_variables.grep(Regexp.new(Regexp.quote($1)))

#        when /^(\$?(\.?[^.]+)+)\.([^.]*)$/
        when /^((\.?[^.]+)+)\.([^.]*)$/
        # variable
            receiver = $1
            message = Regexp.quote($3)

            gv = eval("global_variables", @binding)
            lv = eval("local_variables", @binding)
            cv = eval("self.class.constants", @binding)
    
            if (gv | lv | cv).include?(receiver)
                # foo.func and foo is local var.
                candidates = eval("#{receiver}.methods", @binding)
            elsif /^[A-Z]/ =~ receiver and /\./ !~ receiver
                # Foo::Bar.func
                begin
                    candidates = eval("#{receiver}.methods", @binding)
                rescue Exception
                    candidates = []
                end
            else
                # func1.func2
                candidates = []
                ObjectSpace.each_object(Module){|m|
                    next if m.name != "IRB::Context" and 
                    /^(IRB|SLex|RubyLex|RubyToken)/ =~ m.name
                    candidates.concat m.instance_methods(false)
                }
                candidates.sort!
                candidates.uniq!
            end
            select_message(receiver, message, candidates)

        when /^\.([^.]*)$/
        # unknown(maybe String)

            receiver = ""
            message = Regexp.quote($1)

            candidates = String.instance_methods(true)
            select_message(receiver, message, candidates)

        else
            candidates = eval("methods | private_methods | local_variables | self.class.constants", @binding)
              
            (candidates|ReservedWords).grep(/^#{Regexp.quote(input)}/)
        end
    end

    Operators = ["%", "&", "*", "**", "+",  "-",  "/",
      "<", "<<", "<=", "<=>", "==", "===", "=~", ">", ">=", ">>",
      "[]", "[]=", "^",]

    def select_message(receiver, message, candidates)
=begin edoc
Method used to pick completion candidates.

@param receiver object receiving the message
@param message message to be sent to object
@param candidates possible completion candidates
@return filtered list of candidates
=end
        candidates.grep(/^#{message}/).collect do |e|
            case e
            when /^[a-zA-Z_]/
                receiver + "." + e
            when /^[0-9]/
            when *Operators
                #receiver + " " + e
            end
        end
    end
end
