import sys
import logging
import getpass
import time
from optparse import OptionParser
from Tkinter import *
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

# FIXME: Command to close the app
# FIXME: Display roster
# FIXME: Start a chat with a buddy

class InteractiveClient(ClientXMPP):
    """Interactive chat client"""

    def __init__(self, jid, password, gui):
        ClientXMPP.__init__(self, jid, password)

        self.gui = gui

        self.add_event_handler("session_start", self.session_start, threaded=True)
        self.add_event_handler("message", self.message)

        # Make the keepalive interval smaller so that the AWS load balancer 
        # doesn't close the connection.
    	self.whitespace_keepalive_interval=30

        self.chats = {}

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            window = self.chats.get(msg['from'], None)
            if window is None:
               window = ChatWindow(self, self.gui, msg['from'])
               self.chats[msg['from']] = window
            
            window.display_message(msg)

class ChatWindow(object):
    """Window for a chat with a partner"""

    def __init__(self, app, root, buddy):
        self.buddy = buddy
        self.root = root
        self.app = app
        
        self.window = Toplevel(root)

        self.main_body = Frame(self.window, height=20, width=50)

        self.main_body_text = Text(self.main_body)
        self.body_text_scroll = Scrollbar(self.main_body)
        self.main_body_text.focus_set()
        self.body_text_scroll.pack(side=RIGHT, fill=Y)
        self.main_body_text.pack(side=LEFT, fill=Y)
        self.body_text_scroll.config(command=self.main_body_text.yview)
        self.main_body_text.config(yscrollcommand=self.body_text_scroll.set)
        self.main_body.pack()

        self.main_body_text.config(state=DISABLED)

        self.text_input = Entry(self.window, width=60)
        self.text_input.bind("<Return>", self.send_message)
        self.text_input.pack()

    def display_message(self, msg):
        self.main_body_text.config(state=NORMAL)
        self.main_body_text.insert(END, '\n')
        self.main_body_text.insert(END, str(msg.get('from', '')) + ": ")
        self.main_body_text.insert(END, str(msg.get('body', '')))
        self.main_body_text.yview(END)
        self.main_body_text.config(state=DISABLED)

    def send_message(self, event):
        msg = {}
        msg['from'] = 'me'
        msg['body'] = self.text_input.get()
        self.display_message(msg)
        self.app.send_message(mto=self.buddy, mbody=msg['body'], mtype='chat')

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
    
    # Server to connect
    optp.add_option("-s", "--connect_server", dest="server",
		    help="server to connect")
    optp.add_option("--port", dest="port",
		    help="connect server port")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Get the options from the user if not given as parameters.
    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    # Defaults
    if opts.port is None:
        opts.port = 5222

    # Main GUI window
    root = Tk()
    root.title("Chat")

    main_body = Frame(root, height=20, width=50)

    main_body_text = Text(main_body)
    body_text_scroll = Scrollbar(main_body)
    main_body_text.focus_set()
    body_text_scroll.pack(side=RIGHT, fill=Y)
    main_body_text.pack(side=LEFT, fill=Y)
    body_text_scroll.config(command=main_body_text.yview)
    main_body_text.config(yscrollcommand=body_text_scroll.set)
    main_body.pack()

    main_body_text.insert(END, "Welcome to the chat program!")
    main_body_text.config(state=DISABLED)

    # Initialize client
    xmpp = InteractiveClient(opts.jid, opts.password, root)

    server_address = () if opts.server is None else (opts.server, opts.port)

    xmpp.connect(address=server_address)
    xmpp.process()

    root.mainloop()
