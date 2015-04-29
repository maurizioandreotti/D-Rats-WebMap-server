import sys

from mapserverversion import VERSION
import os

def win32_build():
    from distutils.core import setup
    import py2exe

    try:
        # if this doesn't work, try import modulefinder
        import py2exe.mf as modulefinder
        import win32com
        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath("win32com", p)
        for extra in ["win32com.shell"]: #,"win32com.mapi"
            __import__(extra)
            m = sys.modules[extra]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(extra, p)
    except ImportError:
        # no build path setup, no worries.
        pass

# win32gui,win32com,win32com.shell

    opts = {
        "py2exe" : {
            "includes" : "sys,optparse,greenlet,gevent,gevent.core,jinja2.*,flask",
            "compressed" : 1,
            "optimize" : 2,
            "bundle_files" : 1,
            #        "packages" : ""
            }
        }

    setup(
        windows=[{'script' : "listeningserver.py"},
                 {'script' : 'GPSfixClientStub.py'}],
        #data_files=["C:\\GTK\\bin\\jpeg62.dll"],
        options=opts)


def default_build():
    from distutils.core import setup
    from glob import glob

    man_files = []
    for f in _man_files:
        os.system("gzip -c %s > %s" % (f, f+".gz"))
	man_files.append(f+".gz")

    locale_files = []
#    for f in _locale_files:
 #       locale_files.append(("/usr/share/d-rats/%s" % os.path.dirname(f), [f]))

  #  print "LOC: %s" % str(ui_files)

    setup(
        name="D-Rats-WebMap-server",
        description="D-Rats WebMap server",
        long_description="A extension for D-STAR implementing a Web Server to output GPS positions collected from heard radios",
        author="Maurizio Andreotti IZ2LXI",
        author_email="iz2lxi@yahoo.it",
   #     packages=["listeningserver", "GPSfixClientStub"],
        version=DRATS_VERSION,
        scripts=["listeningserver", "GPSfixClientStub"],
        data_files=[('./templates', templates),
                    ('./static', static),
                    ] + locale_files)
                    
if sys.platform == "darwin":
    macos_build()
elif sys.platform == "win32":
    win32_build()
else:
    default_build()


