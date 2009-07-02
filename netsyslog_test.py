# Copyright (C) 2005 Graham Ashton <ashtong@users.sourceforge.net>
#
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
# $Id: netsyslog_test.py,v 1.4 2005/07/15 09:49:29 ashtong Exp $


import copy
import os
import socket
import sys
import syslog
import time
import unittest

from pmock import *

import netsyslog


class PriPartTest(unittest.TestCase):

    def test_priority_format(self):
        """Check PRI is correctly formatted"""
        pri = netsyslog.PriPart(syslog.LOG_LOCAL4, syslog.LOG_NOTICE)
        self.assertEqual(str(pri), "<165>")


DEFAULT_TIMESTAMP = "Jun  7 09:00:00"
DEFAULT_HOSTNAME = "myhost"
DEFAULT_HEADER = "%s %s" % (DEFAULT_TIMESTAMP, DEFAULT_HOSTNAME)


class MockHeaderTest(unittest.TestCase):

    def mock_localtime(self):
        return (2005, 6, 7, 9, 0, 0, 1, 158, 1)  # see DEFAULT_TIMESTAMP

    def mock_gethostname(self):
        return "myhost"

    def setUp(self):
        self.real_localtime = time.localtime
        time.localtime = self.mock_localtime
        self.real_gethostname = socket.gethostname
        socket.gethostname = self.mock_gethostname

    def tearDown(self):
        time.localtime = self.real_localtime
        socket.gethostname = self.real_gethostname

    
class HeaderPartTest(MockHeaderTest):

    def test_automatic_timestamp(self):
        """Check HEADER is automatically calculated if not set"""
        header = netsyslog.HeaderPart()
        self.assertEqual(str(header),
                         " ".join((DEFAULT_TIMESTAMP, DEFAULT_HOSTNAME)))

    def test_incorrect_characters_disallowed(self):
        """Check only valid characters are used in the HEADER"""
        # Only allowed characters are ABNF VCHAR values and space.
        # Basically, if ord() returns between 32 and 126 inclusive
        # it's okay.
        bad_char = u"\x1f"  # printable, ord() returns 31
        header = netsyslog.HeaderPart()
        header.timestamp = header.timestamp[:-1] + bad_char
        self.assertEqual(str(header),
                         " ".join((DEFAULT_TIMESTAMP, DEFAULT_HOSTNAME)))

    def test_set_timestamp_manually(self):
        """Check it is possible to set the timestamp in HEADER manually"""
        timestamp = "Jan 31 18:12:34"
        header = netsyslog.HeaderPart(timestamp=timestamp)
        self.assertEqual(str(header), "%s %s" % (timestamp, DEFAULT_HOSTNAME))

    def test_set_hostname_manually(self):
        """Check it is possible to set the hostname in HEADER manually"""
        hostname = "otherhost"
        header = netsyslog.HeaderPart(hostname=hostname)
        self.assertEqual(str(header), "%s %s" % (DEFAULT_TIMESTAMP, hostname))


# check format of time and hostname, set automatically if incorrect
#   - time is "Mmm dd hh:mm:ss" where dd has leading space, hh leading 0
#   - single space between time and hostname
#   - no space in hostname
#   - if using hostname, not IP, no dots allowed
# print message to stderr if badly formatted message encountered


DEFAULT_TAG = "program"
MOCK_PID = 1234


class MockMsgTest(unittest.TestCase):

    def mock_getpid(self):
        return MOCK_PID

    def setUp(self):
        self.real_argv = sys.argv
        sys.argv = [DEFAULT_TAG]
        self.real_getpid = os.getpid
        os.getpid = self.mock_getpid

    def tearDown(self):
        sys.argv = self.real_argv
        os.getpid = self.real_getpid


class MsgPartTest(MockMsgTest):

    def test_tag_defaults_to_progname(self):
        """Check TAG defaults to program name"""
        msg = netsyslog.MsgPart()
        self.assertEqual(msg.tag, DEFAULT_TAG)

    def test_override_tag(self):
        """Check TAG can be set manually"""
        msg = netsyslog.MsgPart(tag="mytag")
        self.assertEqual(msg.tag, "mytag")

    def test_tag_trimmed_if_too_long(self):
        """Check long TAGs are trimmed to 32 characters"""
        tag = "abcd" * 10
        msg = netsyslog.MsgPart(tag=tag)
        self.assertEqual(msg.tag, tag[:32])

    def test_space_prefixed_to_content(self):
        """Check single space inserted infront of CONTENT if necessary"""
        msg = netsyslog.MsgPart("program", content="hello")
        self.assertEqual(str(msg), "program: hello")

    def test_space_only_added_if_necessary(self):
        """Check space only added to CONTENT if necessary"""
        msg = netsyslog.MsgPart("program", content=" hello")
        self.assertEqual(str(msg), "program hello")

    def test_include_pid(self):
        """Check the program's pid can be included in CONTENT"""
        msg = netsyslog.MsgPart("program", "hello", pid=MOCK_PID)
        self.assertEqual(str(msg), "program[%d]: hello" % (MOCK_PID))


DEFAULT_PRI = netsyslog.PriPart(syslog.LOG_LOCAL4, syslog.LOG_NOTICE)
DEFAULT_HEADER = netsyslog.HeaderPart(DEFAULT_TIMESTAMP, DEFAULT_HOSTNAME)
DEFAULT_MSG = netsyslog.MsgPart(DEFAULT_TAG, "hello")


class PacketTest(unittest.TestCase):

    def test_message_format(self):
        """Check syslog message is correctly constructed"""
        packet = netsyslog.Packet(DEFAULT_PRI, DEFAULT_HEADER, DEFAULT_MSG)
        header = " ".join((DEFAULT_TIMESTAMP, DEFAULT_HOSTNAME))
        start_of_packet = "<165>%s %s" % (header, DEFAULT_TAG)
        self.assert_(str(packet).startswith(start_of_packet))

    def test_max_length(self):
        """Check that no syslog packet is longer than 1024 bytes"""
        message = "a" * 2048
        packet = netsyslog.Packet(DEFAULT_PRI, DEFAULT_HEADER, message)
        self.assertEqual(len(str(packet)), netsyslog.Packet.MAX_LEN)


class LoggerTest(MockHeaderTest, MockMsgTest):

    def mock_socket(self, family, proto):
        return self.mock_sock
        
    def setUp(self):
        MockHeaderTest.setUp(self)
        MockMsgTest.setUp(self)
        self.mock_sock = Mock()
        self.real_socket = socket.socket
        socket.socket = self.mock_socket

    def tearDown(self):
        socket.socket = self.real_socket
        MockMsgTest.tearDown(self)
        MockHeaderTest.tearDown(self)
        
    def test_send_message(self):
        """Check we can send a message via UDP"""
        logger = netsyslog.Logger()

        packet = netsyslog.Packet(DEFAULT_PRI, DEFAULT_HEADER, DEFAULT_MSG)
        hostname = "localhost"
        address = (hostname, netsyslog.Logger.PORT)
        self.mock_sock.expects(once()).sendto(eq(str(packet)), eq(address))
        logger.add_host(hostname)

        hostname = "remotehost"
        address = (hostname, netsyslog.Logger.PORT)
        self.mock_sock.expects(once()).sendto(eq(str(packet)), eq(address))
        logger.add_host(hostname)

        logger.log(syslog.LOG_LOCAL4, syslog.LOG_NOTICE, "hello")
        self.mock_sock.verify()

    def test_remove_host(self):
        """Check host can be removed from list of those receiving messages"""
        hostname = "localhost"
        logger = netsyslog.Logger()
        logger.add_host(hostname)
        logger.remove_host(hostname)
        logger.log(syslog.LOG_LOCAL4, syslog.LOG_NOTICE, "hello")
        self.mock_sock.verify()

    def test_pid_not_included_by_default(self):
        """Check the program's pid is not included by default"""
        packet = "<165>%s myhost program: hello" % DEFAULT_TIMESTAMP
        hostname = "localhost"
        address = (hostname, netsyslog.Logger.PORT)
        self.mock_sock.expects(once()).sendto(eq(packet), eq(address))
        
        logger = netsyslog.Logger()
        logger.add_host(hostname)
        logger.log(syslog.LOG_LOCAL4, syslog.LOG_NOTICE, "hello")
        self.mock_sock.verify()

    def test_include_pid(self):
        """Check the program's pid can be included in a log message"""
        packet = "<165>%s myhost program[1234]: hello" % DEFAULT_TIMESTAMP
        hostname = "localhost"
        address = (hostname, netsyslog.Logger.PORT)
        self.mock_sock.expects(once()).sendto(eq(packet), eq(address))
        
        logger = netsyslog.Logger()
        logger.add_host(hostname)
        logger.log(syslog.LOG_LOCAL4, syslog.LOG_NOTICE, "hello", pid=True)
        self.mock_sock.verify()

    def test_send_packets_by_hand(self):
        """Check we can send a hand crafted log packet"""
        hostname = "localhost"
        address = (hostname, netsyslog.Logger.PORT)
        packet_text = "<165>Jan  1 10:00:00 myhost myprog: hello"
        self.mock_sock.expects(once()).sendto(eq(packet_text), eq(address))

        pri = netsyslog.PriPart(syslog.LOG_LOCAL4, syslog.LOG_NOTICE)
        header = netsyslog.HeaderPart("Jan  1 10:00:00", "myhost")
        msg = netsyslog.MsgPart("myprog", "hello")
        packet = netsyslog.Packet(pri, header, msg)
        logger = netsyslog.Logger()
        logger.add_host(hostname)
        logger.send_packet(packet)
        self.mock_sock.verify()
    

if __name__ == "__main__":
    unittest.main()
