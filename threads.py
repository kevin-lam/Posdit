import requests
import praw
import time
import smtplib
import re

from PyQt5.QtCore import QThread, pyqtSignal

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def run_once(function):
    """
    Allows the connect log message to be run only once on start up.
    :param function: The connect method
    :return: the wrapper to allowing it to be called again.
    """
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return function(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


class Worker(QThread):
    """
    Worker thread to retrieve requests from Reddit and relay the results to the log viewer.
    """
    # Signal to log that there is no email found.
    missing_email_signal = pyqtSignal()
    # Signal to log successful connection.
    connect_signal = pyqtSignal()
    # Signal to log successful reconnection.
    reconnect_signal = pyqtSignal()
    # Signal to log successful requests found.
    request_signal = pyqtSignal(str)
    # Signal to log when there is no internet connection.
    connectionerror_signal = pyqtSignal()
    # Signal to log when subreddit does not exist.
    subreddit_noexist_signal = pyqtSignal(str)
    # Signal to log when failing to get requests from Reddit and times out.
    timeout_signal = pyqtSignal()
    # Signal to log http error
    httperror_signal = pyqtSignal()
    # Signal to change Posttid status condition to up or down.
    status_condition_signal = pyqtSignal(str, str)

    test_inside_loop = pyqtSignal()

    test_query_requests = pyqtSignal(str)

    def __init__(self):
        super(Worker, self).__init__()
        self.initialize = True
        self.reconnect = False
        self.disable = False
        self.previous_posts = []

    def __del__(self):
        self.wait()

    def run(self):
        if self.email:
            self.get_requests()
        else:
            self.missing_email_signal.emit()
            self.status_condition_signal.emit("Down", "red")

    def get_requests(self):
        """
        Retrieve the requests from Reddit.
        """

        while True:

            while self.disable:
                time.sleep(1)

            connecting = run_once(self.connect)

            try:
                for key, (keyword, subreddit, listing) in self.requests.iteritems():

                    reddit = praw.Reddit(user_agent="desktop:posttid:v1.0")
                    subreddit_addr = reddit.get_subreddit(subreddit)
                    request_method = getattr(subreddit_addr, 'get_{}'.format(listing.lower()))

                    self.test_query_requests.emit(keyword)

                    for post in request_method():
                        # Connecting/Reconnecting log message
                        #connecting(self.initialize, self.reconnect)

                        self.test_inside_loop.emit()

                        phrases = keyword.split()
                        for index, term in enumerate(phrases):
                            phrases[index] = re.sub('[^0-9A-Za-z%]', '', term)
                            phrases[index] = re.sub('(.)', '\\1\s*\W?', phrases[index])


                        # Check if the post has been checked already. If not, send email notification and add it to the
                        # checked list.
                        for adjusted in phrases:
                            if post.id not in self.previous_posts and re.search(adjusted, post.title, re.IGNORECASE):
                                self._send_email(post.title, keyword, subreddit, listing, post.url, post.permalink)
                                self.previous_posts.append(post.id)
                                self.request_signal.emit(post.title)

            # No internet error
            except requests.ConnectionError:
                self.connectionerror_signal.emit()
                self.status_condition_signal.emit("Down", "red")
                self.reconnect = True
                connecting.has_run = False

            # No such subreddit error
            except praw.errors.InvalidSubreddit:
                self.subreddit_noexist_signal.emit(subreddit)
                self.status_condition_signal.emit("Down", "red")
                self.reconnect = True
                return

            # Fail to get requests and time out
            except requests.exceptions.ReadTimeout:
                self.timeout_signal.emit()

            except praw.errors.HTTPException:
                self.httperror_signal.emit()

            else:
                self.status_condition_signal.emit("Up", "green")

            self.initialize = False
            time.sleep(60)

    def _send_email(self, subject, keyword, subreddit, listing, link, reddit_link):
        """
        Sends email notification when a post with the keyword in the title has been found.
        :param subject: Title of the post
        :param keyword: Keyword to be found
        :param subreddit: Subreddit to check
        :param listing: Hot, New, Rising, Controversial
        :param link: Url of the store or item
        :param reddit_link: Url of the reddit post
        """
        msg = MIMEMultipart()
        msg['From'] = 'posditsmtp@gmail.com'
        msg['To'] = self.email
        msg['Subject'] = subject
        body = u"{0} - Keyword: {1} | Subreddit: {2} | Listing: {3}\n <br />Reddit Link: {4} <br />Link: {5}"\
            .format(time.ctime(), keyword, subreddit, listing, reddit_link, link)
        msg.attach(MIMEText(body, 'html'))
        text = msg.as_string()

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login("posditsmtp", "posditpassword")
        try:
            server.sendmail('posditsmtp@gmail.com', self.email, text)
        except smtplib.SMTPAuthenticationError:
            pass
        server.close()

    def set_values(self, new_email, new_requests):
        """
        Updates the worker thread with new email and requests
        :param new_email: User's email
        :param new_requests: User's requests
        :return:
        """
        self.email = new_email
        self.requests = new_requests

    def connect(self, initialize, reconnect):
        """
        Checks whether the program has recently started or is resuming from a disconnect.
        :param initialize: Recently started?
        :param reconnect: Recently disconnected?
        """
        if initialize:
            self.connect_signal.emit()
        elif reconnect:
            self.reconnect_signal.emit()
            self.reconnect = False

