from distutils.core import setup
import glob
import imp
import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# Load the 'pypungi' module from the ./src/ dir.
modImp = imp.find_module("__version__", [os.path.join(THIS_DIR, "src", "pypungi")])
assert modImp, modImp
version = imp.load_module("my_pypungi_version", *modImp)
if modImp[0]:
      modImp[0].close()

setup(
      name='pungi',
      version=version.version,
      description='Distribution compose tool',
      author='Jesse Keating & Ilja Orlovs',
      author_email='jkeating@redhat.com',
      url='https://github.com/VRGhost/pungi',
      license='GPLv2',
      package_dir = {'': 'src'},
      packages = ['pypungi'],
      scripts = ['src/bin/pungi.py', 'src/bin/pkgorder'],
      data_files=[('/usr/share/pungi', glob.glob('share/*'))]
)