# Copyright (C) 2005 Graham Ashton <ashtong@users.sourceforge.net>
#
# $Id: setup.py,v 1.3 2006/02/13 01:53:56 ashtong Exp $


from distutils.core import setup

import netsyslog


if __name__ == "__main__":
    setup(py_modules=["netsyslog"],
          name="netsyslog",
          version=netsyslog.__version__,
          author="Graham Ashton",
          author_email="ashtong@users.sourceforge.net",
          url="http://hacksaw.sourceforge.net/netsyslog/",
          description="Send log messages to remote syslog servers",
          long_description="""netsyslog is a Python module that enables
          you to construct syslog messages and send them (via UDP) to a
          remote syslog server. Unlike other syslog modules it allows you
          to set the metadata (e.g. time, host name, program name, etc.)
          yourself, giving you full control over the contents of the UDP
          packets that it creates.""",
          )
