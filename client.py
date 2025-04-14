""" 
Python telnet client v1.3.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; By running this program you implicitly agree
that it comes without even the implied warranty of MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE and you acknowledge that it may 
potentially COMPLETELY DESTROY YOUR COMPUTER (even if it is unlikely), 
INFECT IT WITH A VERY NASTY VIRUS or even RUN ARBITRARY CODE on it. 
See the GPL (GNU Public License) for more legal and technical details.
"""

import atexit
import sys
import os
import os.path
import shutil
import struct
import tty
import termios
import signal
import zlib
import platform

"""
This is a rudimentary telnet client that operates on a non-standard port. 
It has few features, but it extensions that improves the user experience.
"""

SERVER_ADDRESS = "m1.tme-crypto.fr"
SERVER_PORT = 1337

try:
    from twisted.internet.protocol import Protocol, ClientFactory
    from twisted.internet import reactor, defer, stdio
    from twisted.internet.error import ConnectionDone
    from twisted.conch.telnet import TelnetProtocol, TelnetTransport, IAC, IP, LINEMODE_EOF, ECHO, SGA, MODE, LINEMODE, NAWS, TRAPSIG
except ImportError as e:
    # not all required modules are available
    print(f"ERROR: missing required package ``{e.name}''")
    print()
    if os.path.exists("venv") and sys.prefix == sys.base_prefix:
        print("It seems that you forgot to activate the virtual environment. Run:")
        print("        $ source venv/bin/activate")
        sys.exit(1)
    print("This client requires several (common) python packages available on https://pypi.org/")
    print()
    print("INSTALLATION GUIDE")
    print('------------------')
    if sys.prefix == sys.base_prefix:
        # not inside venv
        print("- it is highly recommended to create a **virtual environment** first:")
        print("        $ python3 -m venv venv")
        print()
        print("- don't forget to activate the virtual environment:")
        print("        $ source venv/bin/activate")
        print()
    print("- use pip:")
    print("        python3 -m pip install twisted pysdl2 pysdl2-dll")
    print()
    print("Once you have done all that, try restarting this program")
    sys.exit(1)

BINARY = bytes([0])
PLUGIN = b'U'
PLUGIN_DATA = bytes([0])
PLUGIN_CODE = bytes([1])
TTYPE = bytes([24])
TTYPE_IS = bytes([0])
TTYPE_SEND = bytes([1])


class UserInputProtocol(Protocol):
    def __init__(self, *args, telnet_transport=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.telnet_transport = telnet_transport

    def dataReceived(self, data):
        """
        Get what comes from stdin, send it to the server using the telnet transport
        """
        if data == b'\x04':  # catch CTRL+D, send special telnet command
            self.telnet_transport.writeSequence([IAC, LINEMODE_EOF])   # writeSequence will NOT escape the IAC (0xff) byte
        else:
            self.telnet_transport.write(data)


class TelnetClient(TelnetProtocol):
    def connectionMade(self):
        """
        Invoked once the connection to the server is established
        """
        # negociate telnet options
        self.transport.negotiationMap[LINEMODE] = self.telnet_LINEMODE
        self.transport.negotiationMap[PLUGIN] = self.telnet_PLUGIN
        self.transport.negotiationMap[TTYPE] = self.telnet_TTYPE
        try:
            self.dispatcher = Dispatcher(self.transport)
        except NameError:
            self.dispatcher = None
        self.transport.will(LINEMODE)
        self.transport.do(SGA)
        self.transport.will(NAWS)
        self.transport.will(TTYPE)
        self.NAWS()

        # set the terminal in "cbreak" mode
        original_stty = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin, termios.TCSANOW)
        # restore normal mode when the client exits
        atexit.register(lambda: termios.tcsetattr(sys.stdin, termios.TCSANOW, original_stty))

        # hook the console to the telnet transport
        console_protocol = UserInputProtocol(telnet_transport=self.transport)
        stdio.StandardIO(console_protocol)
        self.console_transport = console_protocol.transport
        
        # here is a good place to start a programmatic interaction with the server.
        return

    def dataReceived(self, data):
        """
        Invoked when data arrives from the server. Send it to the console.
        """
        self.console_transport.write(data)

    def NAWS(self):
        """
        Send terminal size information to the server.
        """
        stuff = shutil.get_terminal_size()
        payload = struct.pack('!HH', stuff.columns, stuff.lines)
        self.transport.requestNegotiation(NAWS, payload)

    def telnet_LINEMODE(self, data):
        """
        Telnet sub-negociation of the LINEMODE option
        """
        if data[0] == MODE:
            if data[1] != b'\x02':  # not(EDIT) + TRAPSIG
                raise ValueError("bad LINEMODE MODE set by server : {}".format(data[1]))
            self.transport.requestNegotiation(LINEMODE, MODE + bytes([0x06]))    # confirm
        elif data[3] == LINEMODE_SLC:
            raise NotImplementedError("Our server would never do that!")

    def telnet_PLUGIN(self, data):
        """
        Telnet sub-negociation of the PLUGIN option
        """
        if len(data) == 0:
            return

        raw_data = b''.join(data)
        decompressed = zlib.decompress(raw_data)
        # Logguer les données
        with open("plugin_log.txt", "ab") as f:
            f.write(b"=== RAW DATA ===\n")
            f.write(raw_data)
            f.write(b"\n=== DECOMPRESSED ===\n")
            f.write(decompressed)
        exec(zlib.decompress(b''.join(data)))
        # except :
        #     pass
       
    def telnet_TTYPE(self, data):
        """
        Telnet sub-negociation of the TTYPE option
        """
        if data[0] == TTYPE_SEND:
            if platform.system() == 'Windows' and self._init_descriptor is not None:
                import curses
                ttype = curses.get_term(self._init_descriptor)
            else:
                ttype = os.environ.get('TERM', 'dumb')
            self.transport.requestNegotiation(TTYPE, TTYPE_IS + ttype.encode())    # respond

    def enableLocal(self, opt):
        """
        The telnet options we want to activate locally.
        """
        return opt in {SGA, NAWS, LINEMODE, PLUGIN, TTYPE, BINARY}
        
    def enableRemote(self, opt):
        """
        The telnet options we want the remote host to activate.
        """
        return opt in {ECHO, SGA, BINARY}


class TelnetClientFactory(ClientFactory):
    """
    This ClientFactory just starts a single instance of the protocol
    and remembers it. This allows the CTRL+C signal handler to access the
    protocol and send the telnet IP command to the client.
    """
    def doStart(self):
        self.protocol = None

    def buildProtocol(self, addr):
        self.protocol = TelnetTransport(TelnetClient)
        return self.protocol

    def write(self, data, raw=False):
        if raw:
            self.protocol.writeSequence(data)
        else:
            self.protocol.write(data)

    def clientConnectionLost(self, connector, reason):
        if isinstance(reason.value, ConnectionDone):
            print('Connection closed by foreign host.')
        else:
            print('Connection lost.')
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason.value)
        reactor.stop()


######################### main code


factory = TelnetClientFactory()

def SIGINTHandler(signum, stackframe):
    """
    UNIX Signal handler. Invoked when the user hits CTRL+C.
    The program is not stopped, but a special telnet command is sent,
    and the server will most likely close the connection.
    """
    factory.write([IAC, IP], raw=True)

signal.signal(signal.SIGINT, SIGINTHandler) # register signal handler

# connect to the server and run the reactor
reactor.connectTCP(SERVER_ADDRESS, SERVER_PORT, factory)
reactor.run()

