from distutils.core import setup
import os

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk('ratings'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len("ratings")+1:], f))
            
version = "%s.%s" % __import__('ratings').VERSION[:2]

setup(name='django-generic-ratings',
    version=version,
    description='Django ratings tools supporting ajax, generic content type scores, multiple ratings for each content object.',
    author='Francesco Banconi',
    author_email='francesco.banconi@gmail.com',
    url='#TODOhttp://example.com/',
    zip_safe=False,
    packages=[
        'ratings', 
        'ratings.templatetags',
    ],
    package_data={'ratings': data_files},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
