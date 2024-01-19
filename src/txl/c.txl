% Null transform - format output according to grammar
include "c.grm"

% Ignore byte order marks on source files
include "bom.grm"

% Uncomment this line to approximately parse and preserve comments
% include "c-comments.grm"

function main
    match [program]
        _ [program]
end function
