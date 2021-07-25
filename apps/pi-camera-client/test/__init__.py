from os import path
import sys

# Set base path for test code to look-up modules and packages
# See https://stackoverflow.com/a/1897665
sys.path.insert(0, path.join(path.dirname(path.dirname(__file__)), 'src'))

