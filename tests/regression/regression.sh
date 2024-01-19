# Regression test of NiCad
# v7.0, January 2024

cd ../..
set NICAD=./bin/nicad
set NICADCROSS=./bin/nicadcross

echo y | ./bin/nicadclean
echo ""

# Step 1 - are all languages working for functions in default mode?
echo "===== Functions in default mode ====="
${NICAD} functions c tests/regression/systems/c/httpd-2.2.8
${NICAD} functions cs tests/regression/systems/cs/RssBandit1.5.0.17sources
${NICAD} functions java tests/regression/systems/java/jEdit
${NICAD} functions py tests/regression/systems/py/Django
${NICAD} functions atl tests/regression/systems/atl/ATL_Zoo
${NICAD} functions php tests/regression/systems/php/phpBB3
${NICAD} functions rb tests/regression/systems/ruby/spree-master
${NICAD} functions swift tests/regression/systems/swift/boltmobile
${NICAD} functions sol tests/regression/systems/sol/smart_contracts
${NICAD} functions rs tests/regression/systems/rust/nushell-main
echo "====="
echo ""
echo ""

# Step 2 - are all languages working for blocks in default mode?
echo "===== Blocks in default mode ====="
${NICAD} blocks c tests/regression/systems/c/httpd-2.2.8
${NICAD} blocks cs tests/regression/systems/cs/RssBandit1.5.0.17sources
${NICAD} blocks java tests/regression/systems/java/jEdit
${NICAD} blocks py tests/regression/systems/py/Django
${NICAD} blocks swift tests/regression/systems/swift/boltmobile
${NICAD} blocks rs tests/regression/systems/rust/nushell-main
echo "====="
echo ""
echo ""

# Step 2a - are all languages working for files in default mode?
echo "===== Files in default mode ====="
${NICAD} files c tests/regression/systems/c/httpd-2.2.8
${NICAD} files cs tests/regression/systems/cs/RssBandit1.5.0.17sources
${NICAD} files java tests/regression/systems/java/jEdit
${NICAD} files py tests/regression/systems/py/Django
${NICAD} files swift tests/regression/systems/swift/boltmobile
${NICAD} files sol tests/regression/systems/sol/smart_contracts
${NICAD} files rs tests/regression/systems/rust/nushell-main
echo "====="
echo ""
echo ""

# Step 3 - is blind renaming working for functions in all languages?
echo "===== Functions with blind renaming ====="
${NICAD} functions c tests/regression/systems/c/httpd-2.2.8 rename-blind
${NICAD} functions cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-blind
${NICAD} functions java tests/regression/systems/java/jEdit rename-blind
${NICAD} functions py tests/regression/systems/py/Django rename-blind
${NICAD} functions atl tests/regression/systems/atl/ATL_Zoo rename-blind
${NICAD} functions php tests/regression/systems/php/phpBB3 rename-blind
${NICAD} functions rb tests/regression/systems/ruby/spree-master rename-blind
${NICAD} functions swift tests/regression/systems/swift/boltmobile rename-blind
${NICAD} functions sol tests/regression/systems/sol/smart_contracts rename-blind
${NICAD} functions rs tests/regression/systems/rust/nushell-main rename-blind
echo "====="
echo ""
echo ""

# Step 4 - is blind renaming working for blocks in all languages?
echo "===== Blocks with blind renaming ====="
${NICAD} blocks c tests/regression/systems/c/httpd-2.2.8 rename-blind
${NICAD} blocks cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-blind
${NICAD} blocks java tests/regression/systems/java/jEdit rename-blind
${NICAD} blocks py tests/regression/systems/py/Django rename-blind
${NICAD} blocks swift tests/regression/systems/swift/boltmobile rename-blind
${NICAD} blocks rs tests/regression/systems/rust/nushell-main rename-blind
echo "====="
echo ""
echo ""

# Step 4a - is blind renaming working for files in all languages?
echo "===== Files with blind renaming ====="
${NICAD} files c tests/regression/systems/c/httpd-2.2.8 rename-blind
${NICAD} files cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-blind
${NICAD} files java tests/regression/systems/java/jEdit rename-blind
${NICAD} files py tests/regression/systems/py/Django rename-blind
${NICAD} files swift tests/regression/systems/swift/boltmobile rename-blind
${NICAD} files sol tests/regression/systems/sol/smart_contracts rename-blind
${NICAD} files rs tests/regression/systems/rust/nushell-main rename-blind
echo "====="
echo ""
echo ""

# Step 5 - is consistent renaming working for functions in all languages?
echo "===== Functions with consistent renaming ====="
${NICAD} functions c tests/regression/systems/c/httpd-2.2.8 rename-consistent
${NICAD} functions cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-consistent
${NICAD} functions java tests/regression/systems/java/jEdit rename-consistent
${NICAD} functions py tests/regression/systems/py/Django rename-consistent
${NICAD} functions swift tests/regression/systems/swift/boltmobile rename-consistent
${NICAD} functions sol tests/regression/systems/sol/smart_contracts rename-consistent
${NICAD} functions rs tests/regression/systems/rust/nushell-main rename-consistent
echo "====="
echo ""
echo ""

# Step 6 - is consistent renaming working for blocks in all languages?
echo "===== Blocks with consistent renaming ====="
${NICAD} blocks c tests/regression/systems/c/httpd-2.2.8 rename-consistent
${NICAD} blocks cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-consistent
${NICAD} blocks java tests/regression/systems/java/jEdit rename-consistent
${NICAD} blocks py tests/regression/systems/py/Django rename-consistent
${NICAD} blocks swift tests/regression/systems/swift/boltmobile rename-consistent
${NICAD} blocks rs tests/regression/systems/rust/nushell-main rename-consistent
echo "====="
echo ""
echo ""

# Step 6a - is consistent renaming working for files in all languages?
echo "===== Files with consistent renaming ====="
${NICAD} files c tests/regression/systems/c/httpd-2.2.8 rename-consistent
${NICAD} files cs tests/regression/systems/cs/RssBandit1.5.0.17sources rename-consistent
${NICAD} files java tests/regression/systems/java/jEdit rename-consistent
${NICAD} files py tests/regression/systems/py/Django rename-consistent
${NICAD} files swift tests/regression/systems/swift/boltmobile rename-consistent
${NICAD} files sol tests/regression/systems/sol/smart_contracts rename-consistent
${NICAD} files rs tests/regression/systems/rust/nushell-main rename-consistent
echo "====="
echo ""
echo ""

# Step 7 - is filtering working for functions in all languages?
echo "===== Functions with filtering ====="
${NICAD} functions c tests/regression/systems/c/httpd-2.2.8 filter-declarations
${NICAD} functions cs tests/regression/systems/cs/RssBandit1.5.0.17sources filter-declarations
${NICAD} functions java tests/regression/systems/java/jEdit filter-declarations
${NICAD} functions py tests/regression/systems/py/Django filter-declarations
echo "====="
echo ""
echo ""

# Step 8 - is filtering working for blocks in all languages?
echo "===== Blocks with filtering ====="
${NICAD} blocks c tests/regression/systems/c/httpd-2.2.8 filter-declarations
${NICAD} blocks cs tests/regression/systems/cs/RssBandit1.5.0.17sources filter-declarations
${NICAD} blocks java tests/regression/systems/java/jEdit filter-declarations
${NICAD} blocks py tests/regression/systems/py/Django filter-declarations
echo "====="
echo ""
echo ""

# Step 8a - is filtering working for files in all languages?
echo "===== FIles with filtering ====="
${NICAD} files c tests/regression/systems/c/httpd-2.2.8 filter-declarations
${NICAD} files cs tests/regression/systems/cs/RssBandit1.5.0.17sources filter-declarations
${NICAD} files java tests/regression/systems/java/jEdit filter-declarations
${NICAD} files py tests/regression/systems/py/Django filter-declarations
echo "====="
echo ""
echo ""

# Step 9 - is abstraction working for functions in all languages?
echo "===== Functions with abstraction ====="
${NICAD} functions c tests/regression/systems/c/httpd-2.2.8 abstract-expressions
${NICAD} functions cs tests/regression/systems/cs/RssBandit1.5.0.17sources abstract-expressions
${NICAD} functions java tests/regression/systems/java/jEdit abstract-expressions
${NICAD} functions py tests/regression/systems/py/Django abstract-expressions
echo "====="
echo ""
echo ""

# Step 10 - is abstraction working for blocks in all languages?
echo "===== Blocks with abstraction ====="
${NICAD} blocks c tests/regression/systems/c/httpd-2.2.8 abstract-expressions
${NICAD} blocks cs tests/regression/systems/cs/RssBandit1.5.0.17sources abstract-expressions
${NICAD} blocks java tests/regression/systems/java/jEdit abstract-expressions
${NICAD} blocks py tests/regression/systems/py/Django abstract-expressions
echo "====="
echo ""
echo ""

# Step 10a - is abstraction working for files in all languages?
echo "===== Files with abstraction ====="
${NICAD} files c tests/regression/systems/c/httpd-2.2.8 abstract-expressions
${NICAD} files cs tests/regression/systems/cs/RssBandit1.5.0.17sources abstract-expressions
${NICAD} files java tests/regression/systems/java/jEdit abstract-expressions
${NICAD} files py tests/regression/systems/py/Django abstract-expressions
echo "====="
echo ""
echo ""

# Step 11 - is custom normalization working for functions in Java?
echo "===== Java functions with custom normalization  ====="
${NICAD} functions java tests/regression/systems/java/jEdit java-normalize-ifconditions
echo "====="
echo ""
echo ""

# Step 12 - is clustering working?
echo "===== Java functions with clustering ====="
${NICAD} functions java tests/regression/systems/java/jEdit default-report
echo "====="
echo ""
echo ""

# Step 13 - is cros-clone detection working?
echo "===== Java function cross-clones ====="
${NICADCROSS} functions java tests/regression/systems/java/JHotDraw54b1 tests/regression/systems/java/jEdit default-report
echo "====="
echo ""
echo ""

# Step 14 - can we handle long paths and file names with spaces?
echo "===== C long paths and space names ===="
${NICAD} functions c tests/regression/systems/robust/c/"dir with spaces"
${NICAD} blocks c tests/regression/systems/robust/c/hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname
${NICAD} functions c tests/regression/systems/robust/c rename-blind
${NICAD} blocks c tests/regression/systems/robust/c rename-blind
${NICAD} functions c tests/regression/systems/robust/c rename-consistent
${NICAD} blocks c tests/regression/systems/robust/c rename-consistent
${NICAD} functions c tests/regression/systems/robust/c filter-declarations
${NICAD} blocks c tests/regression/systems/robust/c filter-declarations
${NICAD} functions c tests/regression/systems/robust/c abstract-expressions
${NICAD} blocks c tests/regression/systems/robust/c abstract-expressions
${NICAD} functions c tests/regression/systems/robust/c/"dir with spaces" default-report
${NICAD} blocks c tests/regression/systems/robust/c/hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname default-report
${NICADCROSS} functions c "tests/regression/systems/robust/c/dir with spaces" tests/regression/systems/robust/c/hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname default-report
${NICADCROSS} blocks c "tests/regression/systems/robust/c/dir with spaces" tests/regression/systems/robust/c/hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname_hugelnghumungousdirectoryname default-report
echo "====="
echo ""
echo ""

echo "===== END ====="
