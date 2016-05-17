from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QTextOption

from time import strftime


class LogViewer(QPlainTextEdit):
    """
    The viewer which displays the results from the requests.
    """
    def __init__(self, parent=None):
        super(LogViewer, self).__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setCenterOnScroll(True)
        self.setMaximumBlockCount(10000)
        self.setUndoRedoEnabled(False)

    def introduction(self):
        self.appendHtml("************<br/>* <b>Welcome</b> *<br/>************<br/>")

    def entries(self, count):
        time = self.time()
        if count == 0:
            self.appendHtml("{} - No requests found.".format(time))
        elif count == 1:
            self.appendHtml("{0} - {1} request found.".format(time, count))
        else:
            self.appendHtml("{0} - {1} requests found.".format(time, count))

    def no_connection(self):
        self.appendHtml("{} - No connection detected.".format(self.time()))
        self.appendHtml("{} - Disconnected.".format(self.time()))

    def connection(self):
        self.appendHtml("{} - Connection detected.".format(self.time()))
        self.appendHtml("{} - Connected.".format(self.time()))

    def reconnect(self):
        self.appendHtml("{} - Connection detected.".format(self.time()))
        self.appendHtml("{} - Reconnecting.".format(self.time()))

    def disabled(self):
        self.appendHtml("{} - Disabled.".format(self.time()))

    def enabled(self):
        self.appendHtml("{} - Enabled.".format(self.time()))

    def missing_email(self):
        self.appendHtml("{} - No email found.".format(self.time()))

    def inserted(self, inserted_list):
        self.appendHtml("{0} - Added {1} requests.".format(self.time(), len(inserted_list)))
        self.appendHtml(self._html_list(inserted_list))

    def removed(self, removed_list):
        self.appendHtml("{0} - Removed {1} requests.".format(self.time(), len(removed_list)))
        self.appendHtml(self._html_list(removed_list))

    def request_found(self, item):
        self.appendHtml("{0} - {1}".format(self.time(), item))

    def subreddit_noexists(self, subreddit):
        self.appendHtml("{0} - {1} subreddit does not exist.".format(self.time(), subreddit))

    @staticmethod
    def time():
        return strftime("<i>%l:%M%p on %x</i>")

    @staticmethod
    def _html_list(request_list):
        html = ""
        for (key, value) in request_list.iteritems():
            html += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#9702; Keyword: {0} | Subreddit: {1} | Listing: {2}<br/>".format(
                value[0], value[1], value[2])
        return html
