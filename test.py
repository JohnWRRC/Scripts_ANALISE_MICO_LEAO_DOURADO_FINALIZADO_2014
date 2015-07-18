import grass.script as grass
from grass.script import raster as grassR
import os
import string
import glob
import re
import fnmatch
grass.run_command('v.to.rast', input='amostras_apa_sao_joao_shp', out='amostras_raster', use='attr', column='COD', overwrite=True)