#!/usr/bin/env python3

import os, sys
sys.path.append('../')
import utils.event_globals as EG

path = os.path.join(os.path.dirname(__file__), EG.DOCUMENT_ROOT)
print(path)
