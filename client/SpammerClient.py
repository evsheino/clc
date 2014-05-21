import sys
import logging
import getpass
import time
from optparse import OptionParser

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout


class SpammerClient(ClientXMPP):

    def __init__(self, jid, password, to, msg):
        ClientXMPP.__init__(self, jid, password)

	self.to = to
	self.msg = msg

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
    	self.whitespace_keepalive_interval=30

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

	while True and not self.stop.is_set():
            time.sleep(5)
            xmpp.send_message(mto=self.to, mbody=self.msg, mtype='chat')

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-t", "--to", dest="to",
                    help="JID to send the message to")
    optp.add_option("-m", "--message", dest="message",
                    help="message to send")
    optp.add_option("-s", "--connect_server", dest="server",
		    help="server to connect")
    optp.add_option("--port", dest="port",
		    help="connect server port")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.to is None:
        opts.to = raw_input("Send To: ")
    if opts.message is None:
        opts.message = raw_input("Message: ")
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    xmpp = SpammerClient(opts.jid, opts.password, opts.to, opts.message)
    xmpp.connect(address=(opts.server, opts.port))
    xmpp.process(block=True)
