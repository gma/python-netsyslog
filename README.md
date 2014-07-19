README
======

netsyslog enables you to construct syslog messages and send them (via
UDP) to a remote syslog server directly from Python. Unlike other
syslog modules it allows you to set the metadata (e.g. time, host
name, program name, etc.) yourself, giving you full control over the
contents of the UDP packets that it creates.

netsyslog was initially developed for the Hack Saw project, where it
was used to read log messages from a file and inject them into a
network of syslog servers, whilst maintaining the times and hostnames
recorded in the original messages.

The module also allows you to send log messages that contain the
current time, local hostname and calling program name (i.e. the
typical requirement of a logging package) to one or more syslog
servers.

The format of the UDP packets sent by netsyslog adheres closely to
that defined in [RFC 3164][].

[RFC 3164]: http://tools.ietf.org/html/rfc3164

Installation
------------

    $ python setup.py install

Usage
-----

    $ python
    Python 2.4.1 (#2, Mar 30 2005, 21:51:10)
    [GCC 3.3.5 (Debian 1:3.3.5-8ubuntu2)] on linux2
    Type "help", "copyright", "credits" or "license" for more
    information.
    >>> import netsyslog
    >>> import syslog
    >>> logger = netsyslog.Logger()
    >>> logger.add_host("somehost.mydomain.com")
    >>> logger.add_host("otherhost.mydomain.com")
    >>> logger.log(syslog.LOG_USER, syslog.LOG_NOTICE, "Hey, it works!", pid=True)

The [API docs][] are also available over on the (old) SourceForge site.

[API docs]: http://hacksaw.sourceforge.net/netsyslog/doc/
