from setuptools import setup, find_packages
import os

version = "1.0"
 
    

setup(name='DepsDisplay',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/deps_display',
      
      description="",
      long_description="",
      keywords="",
      license="",
      
      classifiers=[
        'Development Status :: 4 - Beta',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        # 'Topic :: Software Development :: Quality Assurance',
        # 'Topic :: Software Development :: Documentation',
        # 'Topic :: Software Development :: Testing'
      ],

      version=version,
      download_url='http://github.com/AndreaCensi/deps_display/tarball/%s' % version,
      
      entry_points={
        'console_scripts': [
            'deps-find = deps_display:main_deps_find',
            'deps-plot = deps_display:main_deps_plot'
       ],
#         'nose.plugins.0.10': [
#             'xunitext = xunitext:XUnitExt'
#             ]
      },
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=['PyContracts', 'SystemCmd'],
      tests_require=['nose'],
)

