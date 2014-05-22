import sys
import logging
import getpass
import time
from optparse import OptionParser
from Tkinter import *
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout

# FIXME: Command to close the app
# FIXME: Remove closed windows from list

class InteractiveClient(ClientXMPP):
    """Interactive chat client with GUI for a single user account"""

    def __init__(self, jid, password, gui):
        ClientXMPP.__init__(self, jid, password)

        self.gui = gui

        self.add_event_handler("session_start", self.session_start, threaded=True)
        self.add_event_handler("message", self.message)
        self.add_event_handler("roster_update", self.display_roster)

        # Make the keepalive interval smaller so that the AWS load balancer 
        # doesn't close the connection.
    	self.whitespace_keepalive_interval=30

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        self.gui.display_chat_message(msg)

    def display_roster(self, event):
        #TODO: Move to MainWindow

        groups = self.client_roster.groups()
        for group in groups:
            self.gui.display_message(group)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    self.gui.display_message(' %s (%s) [%s]' % (name, jid, sub))
                else:
                    self.gui.display_message(' %s [%s]' % (jid, sub))

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    self.gui.display_message(' - %s (%s)' % (res, show))
                    if pres['status']:
                        self.gui.display_message(' %s' % pres['status'])

    def get_domain(self):
        return self.boundjid.bare[self.boundjid.bare.find('@'):]

class ChatWindow(object):
    """Window for a chat with a partner"""

    def __init__(self, app, main_window, buddy):
        self.buddy = buddy
        self.main_window = main_window
        self.app = app
        
        self.window = Toplevel(main_window)
        self.window.title(buddy)

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
        self.text_input.bind("<Return>", self.process_input)
        self.text_input.pack()

    def display_message(self, msg):
        self.main_body_text.config(state=NORMAL)
        self.main_body_text.insert(END, '\n')
        self.main_body_text.insert(END, str(msg.get('from', '')) + ": ")
        self.main_body_text.insert(END, str(msg.get('body', '')))
        self.main_body_text.yview(END)
        self.main_body_text.config(state=DISABLED)

    def process_input(self, event):
        self.send_message(self.text_input.get())

    def send_message(self, msg_text):
        msg = {}
        msg['from'] = 'me'
        msg['body'] = msg_text
        self.display_message(msg)
        self.app.send_message(mto=self.buddy, mbody=msg['body'], mtype='chat')

class MainWindow(object):
    """The main window of the GUI"""

    def __init__(self):
        self.root = Tk()
        self.root.title("Chat")

        self.windows = {}
        
        self.main_body = Frame(self.root, height=20, width=50)

        self.main_body_text = Text(self.main_body)
        self.body_text_scroll = Scrollbar(self.main_body)
        self.main_body_text.focus_set()
        self.body_text_scroll.pack(side=RIGHT, fill=Y)
        self.main_body_text.pack(side=LEFT, fill=Y)
        self.body_text_scroll.config(command=self.main_body_text.yview)
        self.main_body_text.config(yscrollcommand=self.body_text_scroll.set)
        self.main_body.pack()

        self.main_body_text.insert(END, "Welcome to the chat program!")
        self.main_body_text.config(state=DISABLED)

        self.text_input = Entry(self.root, width=60)
        self.text_input.bind("<Return>", self.process_command)
        self.text_input.pack()

    def start(self, app):
        self.app = app
        self.root.mainloop()

    def display_message(self, msg):
        """Display a message in the main window"""

        self.main_body_text.config(state=NORMAL)
        self.main_body_text.insert(END, '\n')
        self.main_body_text.insert(END, msg)
        self.main_body_text.yview(END)
        self.main_body_text.config(state=DISABLED)

    def process_command(self, event):
        """Process the user's command."""

        command_array = self.text_input.get().split()

        # Send chat message: /msg receiver[@domain] message
        if command_array[0].strip() == '/msg':
            buddy = command_array[1]
            if buddy.find('@') == -1:
                # No domain specified, use the user's domain.
                buddy += self.app.get_domain()
            self.get_window(buddy).send_message(' '.join(command_array[2:]))

    def display_chat_message(self, msg):
        """Display message in a chat window"""

        if msg['type'] in ('chat', 'normal'):
            self.get_window(str(msg['from'])).display_message(msg)

    def get_window(self, buddy):
        """Get the chat window with the given buddy or create a new one
        if a chat is not open yet"""

        cut = buddy.find('/')
        if cut != -1:
            buddy = buddy[:cut]
        window = self.windows.get(buddy, None)
        if window is None:
           window = ChatWindow(self.app, self.root, buddy)
           self.windows[buddy] = window

        return window

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
    gui = MainWindow()
    # Initialize client
    xmpp = InteractiveClient(opts.jid, opts.password, gui)

    server_address = () if opts.server is None else (opts.server, opts.port)

    xmpp.connect(address=server_address)
    xmpp.process()

    gui.start(xmpp)
