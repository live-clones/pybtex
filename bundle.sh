#!/bin/sh

set -e

TARGET="./bundle"
PIP_ARGS="--target=${TARGET} --no-compile"

rm -rf "${TARGET:?}"
pip install $PIP_ARGS -r requirements.txt
rm -rf "${TARGET:?}/bin"
pip install $PIP_ARGS --no-deps .
rm -rf "${TARGET:?}/tests"
for script in "${TARGET:?}/bin/"*;
do
    cat > "$script" << 'END'
#!/usr/bin/env python
  
# -*- coding: utf-8 -*-
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pybtex.__main__ import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
END
done
