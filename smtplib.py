#! /usr/bin/env python

# Source: SMTPLIB plucked from python 2.5.4
# Author: The Dragon De Monsyne <dragondm@integral.org>
# Modified: by R.somers to run on ESXI

import socket
import re
import email.Utils
# import base64
#import hmac
#from email.base64MIME import encode as encode_base64
from sys import stderr

__all__ = ["SMTPException","SMTPServerDisconnected","SMTPResponseException",
           "SMTPSenderRefused","SMTPRecipientsRefused","SMTPDataError",
           "SMTPConnectError","SMTPHeloError","SMTPAuthenticationError",
           "quoteaddr","quotedata","SMTP"]

SMTP_PORT = 25
CRLF="\r\n"

OLDSTYLE_AUTH = re.compile(r"auth=(.*)", re.I)

# Exception classes used by this module.
class SMTPException(Exception):
    """Base class for all exceptions raised by this module."""

class SMTPServerDisconnected(SMTPException):
    """Not connected to any SMTP server."""

class SMTPResponseException(SMTPException):
    """Base class for all exceptions that include an SMTP error code.
    """

    def __init__(self, code, msg):
        self.smtp_code = code
        self.smtp_error = msg
        self.args = (code, msg)

class SMTPSenderRefused(SMTPResponseException):
    """Sender address refused.
    """

    def __init__(self, code, msg, sender):
        self.smtp_code = code
        self.smtp_error = msg
        self.sender = sender
        self.args = (code, msg, sender)

class SMTPRecipientsRefused(SMTPException):
    """All recipient addresses refused.
    """

    def __init__(self, recipients):
        self.recipients = recipients
        self.args = ( recipients,)


class SMTPDataError(SMTPResponseException):
    """The SMTP server didn't accept the data."""

class SMTPConnectError(SMTPResponseException):
    """Error during connection establishment."""

class SMTPHeloError(SMTPResponseException):
    """The server refused our HELO reply."""

def quoteaddr(addr):
    """Quote a subset of the email addresses defined by RFC 821.

    Should be able to handle anything rfc822.parseaddr can handle.
    """
    m = (None, None)
    try:
        m = email.Utils.parseaddr(addr)[1]
    except AttributeError:
        pass
    if m == (None, None): # Indicates parse failure or AttributeError
        # something weird here.. punt -ddm
        return "<%s>" % addr
    elif m is None:
        # the sender wants an empty return address
        return "<>"
    else:
        return "<%s>" % m

def quotedata(data):
    """Quote data for email.

    Double leading '.', and change Unix newline '\\n', or Mac '\\r' into
    Internet CRLF end-of-line.
    """
    return re.sub(r'(?m)^\.', '..',
        re.sub(r'(?:\r\n|\n|\r(?!\n))', CRLF, data))


class SMTP:
    """This class manages a connection to an SMTP or ESMTP server.
    """
    debuglevel = 0
    file = None
    helo_resp = None
    ehlo_resp = None
    does_esmtp = 0

    def __init__(self, host = '', port = 0, local_hostname = None):
        """Initialize a new instance."""
        self.esmtp_features = {}
        if host:
            (code, msg) = self.connect(host, port)
            if code != 220:
                raise SMTPConnectError(code, msg)
        if local_hostname is not None:
            self.local_hostname = local_hostname
        else:
            # RFC 2821 says we should use the fqdn in the EHLO/HELO verb, and
            # if that can't be calculated, that we should use a domain literal
            # instead (essentially an encoded IP address like [A.B.C.D]).
            fqdn = socket.getfqdn()
            if '.' in fqdn:
                self.local_hostname = fqdn
            else:
                # We can't find an fqdn hostname, so use a domain literal
                addr = '127.0.0.1'
                try:
                    addr = socket.gethostbyname(socket.gethostname())
                except socket.gaierror:
                    pass
                self.local_hostname = '[%s]' % addr

    def set_debuglevel(self, debuglevel):
        """Set the debug output level.

        A non-false value results in debug messages for connection and for all
        messages sent to and received from the server.

        """
        self.debuglevel = debuglevel

    def connect(self, host='localhost', port = 0):
        """Connect to a host on a given port.
	"""
        if not port: port = SMTP_PORT
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0: print>>stderr, 'connect fail:', msg
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg
        (code, msg) = self.getreply()
        if self.debuglevel > 0: print>>stderr, "connect:", msg
        return (code, msg)

    def send(self, str):
        """Send `str' to the server."""
        if self.debuglevel > 0: print>>stderr, 'send:', repr(str)
        if hasattr(self, 'sock') and self.sock:
            try:
                self.sock.sendall(str)
            except socket.error:
                self.close()
                raise SMTPServerDisconnected('Server not connected')
        else:
            raise SMTPServerDisconnected('please run connect() first')

    def putcmd(self, cmd, args=""):
        """Send a command to the server."""
        if args == "":
            str = '%s%s' % (cmd, CRLF)
        else:
            str = '%s %s%s' % (cmd, args, CRLF)
        self.send(str)

    def getreply(self):
        """Get a reply from the server.

        Returns a tuple consisting of:

          - server response code (e.g. '250', or such, if all goes well)
            Note: returns -1 if it can't read response code.

          - server response string corresponding to response code (multiline
            responses are converted to a single, multiline string).

        Raises SMTPServerDisconnected if end-of-file is reached.
        """
        resp=[]
        if self.file is None:
            self.file = self.sock.makefile('rb')
        while 1:
            line = self.file.readline()
            if line == '':
                self.close()
                raise SMTPServerDisconnected("Connection unexpectedly closed")
            if self.debuglevel > 0: print>>stderr, 'reply:', repr(line)
            resp.append(line[4:].strip())
            code=line[:3]
            # Check that the error code is syntactically correct.
            # Don't attempt to read a continuation line if it is broken.
            try:
                errcode = int(code)
            except ValueError:
                errcode = -1
                break
            # Check if multiline response.
            if line[3:4]!="-":
                break

        errmsg = "\n".join(resp)
        if self.debuglevel > 0:
            print>>stderr, 'reply: retcode (%s); Msg: %s' % (errcode,errmsg)
        return errcode, errmsg

    def docmd(self, cmd, args=""):
        """Send a command, and return its response code."""
        self.putcmd(cmd,args)
        return self.getreply()

    # std smtp commands
    def helo(self, name=''):
        """SMTP 'helo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        """
        self.putcmd("helo", name or self.local_hostname)
        (code,msg)=self.getreply()
        self.helo_resp=msg
        return (code,msg)

    def ehlo(self, name=''):
        """ SMTP 'ehlo' command.
        Hostname to send for this command defaults to the FQDN of the local
        host.
        """
        self.esmtp_features = {}
        self.putcmd("ehlo", name or self.local_hostname)
        (code,msg)=self.getreply()
        return (code,msg)

    def has_extn(self, opt):
        """Does the server support a given SMTP service extension?"""
        return opt.lower() in self.esmtp_features

    def help(self, args=''):
        """SMTP 'help' command.
        Returns help text from server."""
        self.putcmd("help", args)
        return self.getreply()[1]

    def rset(self):
        """SMTP 'rset' command -- resets session."""
        return self.docmd("rset")

    def noop(self):
        """SMTP 'noop' command -- doesn't do anything :>"""
        return self.docmd("noop")

    def mail(self,sender,options=[]):
        """SMTP 'mail' command -- begins mail xfer session."""
        optionlist = ''
        if options and self.does_esmtp:
            optionlist = ' ' + ' '.join(options)
        self.putcmd("mail", "FROM:%s%s" % (quoteaddr(sender) ,optionlist))
        return self.getreply()

    def rcpt(self,recip,options=[]):
        """SMTP 'rcpt' command -- indicates 1 recipient for this mail."""
        optionlist = ''
        if options and self.does_esmtp:
            optionlist = ' ' + ' '.join(options)
        self.putcmd("rcpt","TO:%s%s" % (quoteaddr(recip),optionlist))
        return self.getreply()

    def data(self,msg):
        """SMTP 'DATA' command -- sends message data to server.

        Automatically quotes lines beginning with a period per rfc821.
        Raises SMTPDataError if there is an unexpected reply to the
        DATA command; the return value from this method is the final
        response code received when the all data is sent.
        """
        self.putcmd("data")
        (code,repl)=self.getreply()
        if self.debuglevel >0 : print>>stderr, "data:", (code,repl)
        if code != 354:
            raise SMTPDataError(code,repl)
        else:
            q = quotedata(msg)
            if q[-2:] != CRLF:
                q = q + CRLF
            q = q + "." + CRLF
            self.send(q)
            (code,msg)=self.getreply()
            if self.debuglevel >0 : print>>stderr, "data:", (code,msg)
            return (code,msg)

    def verify(self, address):
        """SMTP 'verify' command -- checks for address validity."""
        self.putcmd("vrfy", quoteaddr(address))
        return self.getreply()
    # a.k.a.
    vrfy=verify

    def expn(self, address):
        """SMTP 'expn' command -- expands a mailing list."""
        self.putcmd("expn", quoteaddr(address))
        return self.getreply()

    # some useful methods
    def sendmail(self, from_addr, to_addrs, msg, mail_options=[],
                 rcpt_options=[]):
        """This command performs an entire mail transaction.

        The arguments are:
            - from_addr    : The address sending this mail.
            - to_addrs     : A list of addresses to send this mail to.  A bare
                             string will be treated as a list with 1 address.
            - msg          : The message to send.
            - mail_options : List of ESMTP options (such as 8bitmime) for the
                             mail command.
            - rcpt_options : List of ESMTP options (such as DSN commands) for
                             all the rcpt commands.

        If there has been no previous EHLO or HELO command this session, this
        method tries ESMTP EHLO first.  If the server does ESMTP, message size
        and each of the specified options will be passed to it.  If EHLO
        fails, HELO will be tried and ESMTP options suppressed.

        This method will return normally if the mail is accepted for at least
        one recipient.  It returns a dictionary, with one entry for each
        recipient that was refused.  Each entry contains a tuple of the SMTP
        error code and the accompanying error message sent by the server.

        This method may raise the following exceptions:

         SMTPHeloError          The server didn't reply properly to
                                the helo greeting.
         SMTPRecipientsRefused  The server rejected ALL recipients
                                (no mail was sent).
         SMTPSenderRefused      The server didn't accept the from_addr.
         SMTPDataError          The server replied with an unexpected
                                error code (other than a refusal of
                                a recipient).

        Note: the connection will be open even after an exception is raised.

        Example:

         >>> import smtplib
         >>> s=smtplib.SMTP("localhost")
         >>> tolist=["one@one.org","two@two.org","three@three.org","four@four.org"]
         >>> msg = '''\\
         ... From: Me@my.org
         ... Subject: testin'...
         ...
         ... This is a test '''
         >>> s.sendmail("me@my.org",tolist,msg)
         { "three@three.org" : ( 550 ,"User unknown" ) }
         >>> s.quit()

        In the above example, the message was accepted for delivery to three
        of the four addresses, and one was rejected, with the error code
        550.  If all addresses are accepted, then the method will return an
        empty dictionary.

        """
        if self.helo_resp is None and self.ehlo_resp is None:
            if not (200 <= self.ehlo()[0] <= 299):
                (code,resp) = self.helo()
                if not (200 <= code <= 299):
                    raise SMTPHeloError(code, resp)
        esmtp_opts = []
        if self.does_esmtp:
            # Hmmm? what's this? -ddm
            # self.esmtp_features['7bit']=""
            if self.has_extn('size'):
                esmtp_opts.append("size=%d" % len(msg))
            for option in mail_options:
                esmtp_opts.append(option)

        (code,resp) = self.mail(from_addr, esmtp_opts)
        if code != 250:
            self.rset()
            raise SMTPSenderRefused(code, resp, from_addr)
        senderrs={}
        if isinstance(to_addrs, basestring):
            to_addrs = [to_addrs]
        for each in to_addrs:
            (code,resp)=self.rcpt(each, rcpt_options)
            if (code != 250) and (code != 251):
                senderrs[each]=(code,resp)
        if len(senderrs)==len(to_addrs):
            # the server refused all our recipients
            self.rset()
            raise SMTPRecipientsRefused(senderrs)
        (code,resp) = self.data(msg)
        if code != 250:
            self.rset()
            raise SMTPDataError(code, resp)
        #if we got here then somebody got our mail
        return senderrs


    def close(self):
        """Close the connection to the SMTP server."""
        if self.file:
            self.file.close()
        self.file = None
        if self.sock:
            self.sock.close()
        self.sock = None


    def quit(self):
        """Terminate the SMTP session."""
        self.docmd("quit")
        self.close()


# Test the sendmail method, which tests most of the others.
# Note: This always sends to localhost.
if __name__ == '__main__':
    import sys

    def prompt(prompt):
        sys.stdout.write(prompt + ": ")
        return sys.stdin.readline().strip()

    fromaddr = prompt("From")
    toaddrs  = prompt("To").split(',')
    print "Enter message, end with ^D:"
    msg = ''
    while 1:
        line = sys.stdin.readline()
        if not line:
            break
        msg = msg + line
    print "Message length is %d" % len(msg)

    server = SMTP('localhost')
    server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
