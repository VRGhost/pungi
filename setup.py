from distutils.core import setup
import glob

setup(
      name='pungi',
      version='2.0.23_vrg',
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