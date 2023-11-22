import os
from inspect import getsourcefile


root_path = getsourcefile(lambda: 0)[:-8]

print(f'NOW I INSTALL REQUIREMENTS TO WORK TO {root_path}')
os.system(f'pip install -r "{root_path+"requirements.txt"}"')
