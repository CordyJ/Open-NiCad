# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

=begin edoc
File defining the different Ruby types
=end

if RUBY_VERSION < "1.9"
    $KCODE = 'UTF8'
    require 'jcode'
end

ConfigVarTypeStrings = ['__', 'NilClass', '_unused_',
        'bool', 'Fixnum', 'Bignum', 'Float', 'Complex',
        'String', 'String', '_unused_', 'Array',
        'Hash', '_unused_', '_unused_', 'File', '_unused_',
        '_unused_', '_unused_', 'Class', 'instance',
        '_unused_', '_unused_', '_unused_',
        'Proc', '_unused_', '_unused_', 'Module',
        '_unused_', '_unused_', '_unused_', 'other']
