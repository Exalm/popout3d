from setuptools import setup, find_packages
setup(
    name="popout3d",
    version="1.5.0",
    packages=find_packages(),                     
    scripts=['popout3d'],
    
    install_requires=['PIL'],
    python_requires='>=3',
    #platform='OPTIONS UNKNOWN',
    #package_data={'': ['*.png']},               #ONLY TEXT OR RST OR MSG
    data_files=[('share/popout3d/', ['popout3d_spawn','popout3d_start.png','popout3d_logo.png','popout3d_about.png','popout3d.glade','popout3d.dat']), ('share/man/man1', ['popout3d.1']), ('share/applications/', ['popout3d.desktop'])],

    include_package_data=True,
    
    # metadata to display on PyPI
    author="Chris Rogers",
    author_email="popout3d@yahoo.com",
    description="Creates 3D images from photographs taken with an ordinary camera.",
    long_description="Take a set of photos of a subject and the software will create a 3D image from each pair of photos in the set, so that you can choose the best. Vertical and rotational alignment of the left and right images is essential for a convincing 3D effect, but difficult to achieve with an ordinary camera. The software corrects any misalignment. Formats available are anaglyph (red/cyan), side-by-side and crossover. Several sets of photos can be processed at once, they can be previewed and poor ones can be deleted.",
    license="GNU GENERAL PUBLIC LICENSE GPLv3",
    keywords="graphics",
    url="https://github.com/popout3d",
)

