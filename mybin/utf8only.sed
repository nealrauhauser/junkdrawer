#!/bin/bash
#
# non UTF8 chars found in international news titles
#
sed 's/[“é”ü|áö‘ńçä—–яьурзДşŠôòóñğèÇč]//g'

#grep "[“é”ü|áö‘ńçä—–яьурзДşŠôòóñğèÇč]" $1
