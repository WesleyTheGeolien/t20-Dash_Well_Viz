import os
import glob
import pandas as pd
import numpy as np
from welly import Project, Well

# looks into root folder or subdirectories for LAS files
def multiload(path):
    asps = []
    for root, dirs, files in os.walk(path):
        asps += glob.glob(os.path.join(root, '*.las'))      
    return asps
