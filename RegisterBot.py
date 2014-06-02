#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class RegisterBot(sleekxmpp.ClientXMPP):
    """
    Bot that registers users in batches.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start, threaded=True)

        # The register event provides an Iq result stanza with
        # a registration form from the server. This may include
        # the basic registration fields, a data form, an
        # out-of-band URL, or any combination. For more advanced
        # cases, you will need to examine the fields provided
        # and respond accordingly. SleekXMPP provides plugins
        # for data forms and OOB links that will make that easier.
        self.add_event_handler("register", self.register, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        # We're only concerned about registering, so nothing more to do here.
        self.disconnect()

    def register(self, iq):
        """
        Fill out and submit a registration form.
        """
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            logging.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logging.error("Could not register account: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("No response from server.")
            self.disconnect()


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

    # Domain
    optp.add_option("--domain", dest="domain",
            help="chat domain")

    # Server to connect
    optp.add_option("-s", "--connect_server", dest="server",
            help="server to connect")
    optp.add_option("--port", dest="port",
            help="connect server port")

    opts, args = optp.parse_args()

    if opts.port is None:
        opts.port = 5222

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
            format='%(levelname)-8s %(message)s')

    # Create 99 users: user1, user2, ..., user99.
    for i in xrange(1, 100):
        # Setup the RegisterBot and register plugins. Note that while plugins may
        # have interdependencies, the order in which you register them does
        # not matter.
        username = "user{}".format(i)
        xmpp = RegisterBot("{}@{}".format(username, opts.domain), username)
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0004') # Data forms
        xmpp.register_plugin('xep_0066') # Out-of-band Data
        xmpp.register_plugin('xep_0077') # In-band Registration

        # Some servers don't advertise support for inband registration, even
        # though they allow it. If this applies to your server, use:
        xmpp['xep_0077'].force_registration = True

        # Connect to the XMPP server and start processing XMPP stanzas.
        if xmpp.connect():
            xmpp.process(block=True)
            print("Done")
        else:
            print("Unable to connect.")
