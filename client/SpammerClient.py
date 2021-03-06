import os
import logging
import getpass
import time
from optparse import OptionParser
from sleekxmpp import ClientXMPP

class SpammerClient(ClientXMPP):
    # Automated client for testing.
    # Sends a message at session start (format: prefix/sequence_number)
    # and waits for messages with the same prefix and replies to them
    # with a message with the next sequence number.

    def __init__(self, jid, password, to, msg_count, sleep, msg_prefix):
        ClientXMPP.__init__(self, jid, password)

        self.to = to
        self.msg_count = msg_count
        self.msg_prefix = msg_prefix
        self.sleep = sleep

        self.i = 0

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

        # Make the keepalive interval smaller so that the AWS load balancer 
        # doesn't close the connection.
        self.whitespace_keepalive_interval = 30

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

        xmpp.send_message(mto=self.to, 
                mbody="{}/{}".format(self.msg_prefix, self.i), 
                mtype='chat')

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            # Reply only to this test run's messages
            if msg['body'].find(self.msg_prefix) != -1:
                # Sleep before replying
                time.sleep(self.sleep)
                msg.reply("{}/{}".format(self.msg_prefix, self.i)).send()
                self.i += 1

                if self.i > self.msg_count:
                    self.disconnect(wait=True)


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

    # Logging directory.
    optp.add_option('-l', '--log', help="set directory for log files", dest="log_directory")

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
            help="JID to use")
    optp.add_option("-p", "--password", dest="password",
            help="password to use")

    # Message and recipient
    optp.add_option("-t", "--to", dest="to",
            help="JID to send the message to")
    optp.add_option("-m", "--messages", dest="message",
            help="number of messages to send")
    optp.add_option("--prefix", dest="prefix",
            help="message prefix")
    optp.add_option("--sleep", dest="sleep",
            help="delay between each sent message in seconds")

    # Server to connect
    optp.add_option("-s", "--connect_server", dest="server",
            help="server to connect")
    optp.add_option("--port", dest="port",
            help="connect server port")

    opts, args = optp.parse_args()

    # Get the options from the user if not given as parameters.
    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")
    if opts.to is None:
        opts.to = raw_input("Send To: ")
    if opts.message is None:
        opts.message = raw_input("Number of messages: ")

    # Setup logging.
    logfile = os.path.join(opts.log_directory or "", "{}_to_{}.log".format(opts.jid, opts.to))
    logging.basicConfig(level=opts.loglevel,
            format='%(levelname)-8s %(asctime)s : %(message)s',
            filename=logfile)

    # Defaults
    if opts.port is None:
        opts.port = 5222
    if opts.sleep is None:
        opts.sleep = 5
    if opts.log_directory is None:
        opts.log_directory = "logs"
    if opts.prefix is None:
        opts.prefix = "test"

    xmpp = SpammerClient(opts.jid, opts.password, opts.to, int(opts.message), opts.sleep, opts.prefix)

    server_address = () if opts.server is None else (opts.server, opts.port)

    xmpp.connect(address=server_address)
    xmpp.process(block=True)
