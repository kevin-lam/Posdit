import pickle

from PyQt5.QtWidgets import QMainWindow, QWidget, QStackedWidget, QLabel, QLineEdit, QSpacerItem, QPushButton, \
     QSizePolicy, QHBoxLayout, QVBoxLayout, QCheckBox, QMenu, QAction, QApplication
from PyQt5.QtGui import QFont, QCursor, QDesktopServices
from PyQt5.QtCore import QUrl, Qt

from os import getcwd

from request import RequestTable
from log import LogViewer
from threads import Worker


class Posttid(QMainWindow):
    """
    The main application window and functions which apply to all windows.
    """

    def __init__(self):
        super(Posttid, self).__init__()

        # Set up the main window ui including parameters such as window size and global font
        self.set_up_window()

        # Load in the saved email and requests
        self.data, self.email, self.requests = self.load()

        # Set up each individual window screen
        self.central_widget = QStackedWidget()
        self.settings_widget = SettingsWindow(self.email, self.requests, parent=self)
        self.status_widget = StatusWindow(parent=self)
        self.central_widget.addWidget(self.status_widget)
        self.central_widget.addWidget(self.settings_widget)
        self.setCentralWidget(self.central_widget)

        # Start a new background thread to run the requests
        self.worker = Worker()
        self.worker.set_values(self.email, self.requests)
        self.worker.missing_email_signal.connect(self.log.missing_email)
        self.worker.connect_signal.connect(self.log.connection)
        self.worker.reconnect_signal.connect(self.log.reconnect)
        self.worker.request_signal.connect(self.log.request_found)
        self.worker.connectionerror_signal.connect(self.log.no_connection)
        self.worker.subreddit_noexist_signal.connect(self.log.subreddit_noexists)
        self.worker.status_condition_signal.connect(self.status_widget.set_status)
        self.worker.timeout_signal.connect(self.log.timeout)
        self.worker.httperror_signal.connect(self.log.http)
        self.worker.test_inside_loop.connect(self.log.inside_loop)
        self.worker.test_query_requests.connect(self.log.query_requests)
        self.worker.start()

        # Stop the worker thread when accessing the settings window
        self.status_widget.settings.clicked.connect(self.worker.terminate)

    def set_up_window(self):
        """ Defines the features for the status window """

        self.setWindowTitle("Posttid")

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        self.resize(450, 300)

        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

    def switch_layout_status(self):
        """ Switches from the settings window to the status window """
        self.central_widget.setCurrentIndex(0)
        self.status_widget.status_disable_checkbox.setChecked(self.settings_widget.settings_disable_checkbox
                                                              .isChecked())

    def switch_layout_settings(self):
        """ Switches from the status window to the settings window """
        self.central_widget.setCurrentIndex(1)
        self.settings_widget.settings_disable_checkbox.setChecked(self.status_widget.status_disable_checkbox
                                                                  .isChecked())

    def link(self, link_string):
        QDesktopServices.openUrl(QUrl(link_string))

    @staticmethod
    def load():
        """
        Load in saved email and requests on start.
        :return: dictionary containing saved data or null if no saved data
        """
        try:
            with open(getcwd() + '/tkl.pkl', 'rb') as f:
                data = pickle.load(f)
                email = data["email"]
                requests = data["requests"]
                return data, email, requests
        except IOError:
            return {}, "", {}


class StatusWindow(QWidget):
    """
    The status window which features a log that displays request results and application status.
    """

    def __init__(self, parent=None):
        super(StatusWindow, self).__init__(parent)
        self.parent = parent
        self.set_up_status_layout()

    def set_up_status_layout(self):
        status_label = QLabel("Status: ")
        self.status_condition = QLabel()
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.status_condition.setFont(font)
        self.set_status("Down", "red")

        info_spacer = QSpacerItem(50, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.settings = QPushButton("Settings")
        self.settings.clicked.connect(self.parent.switch_layout_settings)
        self.settings.setMaximumHeight(20)

        info_container = QHBoxLayout()
        info_container.setContentsMargins(20, 0, 0, 0)
        info_container.addWidget(status_label)
        info_container.addWidget(self.status_condition)
        info_container.addItem(info_spacer)
        info_container.addWidget(self.settings)

        requests = self.parent.settings_widget.request_table.requests
        self.log = LogViewer()
        self.parent.log = self.log
        self.log.introduction()
        self.log.entries(len(requests))

        log_container = QVBoxLayout()
        log_container.addWidget(self.log)

        self.status_disable_checkbox = QCheckBox("Disable")
        self.status_disable_checkbox.stateChanged.connect(self.toggle_status)

        link = "https://github.com/kevin-lam/Posttid"
        help_link = QLabel('<a href="{}">Help</a>'.format(link))
        help_link.setAlignment(Qt.AlignRight)
        help_link.linkActivated.connect(lambda: self.parent.link(link))

        status_bottom_container = QHBoxLayout()
        status_bottom_container.setContentsMargins(10, 0, 20, 0)
        status_bottom_container.addWidget(self.status_disable_checkbox)
        status_bottom_container.addWidget(help_link)

        status_layout = QVBoxLayout()
        status_layout.addLayout(info_container)
        status_layout.addLayout(log_container)
        status_layout.addLayout(status_bottom_container)

        self.setLayout(status_layout)

    def toggle_status(self):
        """
        Called when the checkbox is marked to disable/enable the running program.
        """
        if self.status_disable_checkbox.isChecked():
            self.parent.worker.disable = True
            self.log.disabled()
            self.set_status("Down", "red")
        else:
            self.parent.worker.disable = False
            self.log.enabled()
            if self.parent.settings_widget.email_edit.text():
                self.set_status("Up", "green")

    def set_status(self, condition, color):
        """
        Sets the status of the program on the label
        :param condition: down or up status
        :param color: red or green
        :return:
        """
        self.status_condition.setText(condition)
        style = "QLabel { color : %s; }" % color
        self.status_condition.setStyleSheet(style)


class SettingsWindow(QWidget):
    """
    The settings window which allows the user to add/delete requests.
    """

    def __init__(self, email, requests, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.parent = parent
        self.email = email
        self.requests = requests
        self.set_up_settings_layout()

    def set_up_settings_layout(self):
        email_label = QLabel("Email: ")

        self.email_edit = QLineEdit()
        self.email_edit.setMaximumHeight(20)
        self.email_edit.setText(self.email)

        email_spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.request_table = RequestTable(self.email, self.requests, parent=self.parent)
        self.email_edit.setText(self.request_table.email)

        done = QPushButton("Done")
        done.setMaximumHeight(20)
        done.clicked.connect(self.parent.switch_layout_status)
        done.clicked.connect(lambda: self.finished(self.email_edit.text(), self.request_table.requests,
                                                   self.request_table.inserted, self.request_table.removed,
                                                   self.request_table))


        email_container = QHBoxLayout()
        email_container.addWidget(email_label)
        email_container.addWidget(self.email_edit)
        email_container.addItem(email_spacer)
        email_container.addWidget(done)

        table_container = QVBoxLayout()
        table_container.addWidget(self.request_table)

        self.settings_disable_checkbox = QCheckBox("Disable")

        link = "https://github.com/kevin-lam/Posttid"
        help_link = QLabel('<a href="{}">Help</a>'.format(link))
        help_link.setAlignment(Qt.AlignRight)
        help_link.linkActivated.connect(lambda: self.parent.link(link))

        settings_bottom_container = QHBoxLayout()
        settings_bottom_container.addWidget(self.settings_disable_checkbox)
        settings_bottom_container.addWidget(help_link)
        settings_bottom_container.setContentsMargins(10, 0, 20, 0)

        settings_layout = QVBoxLayout()
        settings_layout.addLayout(email_container)
        settings_layout.addLayout(table_container)
        settings_layout.addLayout(settings_bottom_container)

        self.setLayout(settings_layout)

    def contextMenuEvent(self, event):
        """
        Overrides right click menu for adding, removing, and editing requests.
        :param event: Add, remove, or edit action
        """
        self.menu = QMenu()

        add_action = QAction("Add", self)
        add_action.triggered.connect(self.request_table.add)
        self.menu.addAction(add_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.request_table.delete)
        self.menu.addAction(delete_action)

        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.request_table.edit_request)
        self.menu.addAction(edit_action)

        self.menu.popup(QCursor.pos())

    def finished(self, email, requests, inserted_list, removed_list, request_table):
        """
        When the done button is clicked, save the requests, update the worker thread with new values, and display the
        changes in the log viewer.
        :param email: Email entered by the user to be saved
        :param requests: Requests made by the user to be saved
        :param inserted_list: Added requests to be displayed in the log
        :param removed_list: Removed requests to be displayed in the log
        :param request_table: Request table to clear the inserted and removed requests
        """
        self._save(email, requests)
        self.parent.worker.set_values(email, requests)

        if len(inserted_list) != 0:
            self.parent.log.inserted(inserted_list)
        if len(removed_list) != 0:
            self.parent.log.removed(removed_list)

        request_table.inserted = {}
        request_table.removed = {}

        self.parent.worker.start()

    @staticmethod
    def _save(email, requests):
        """
        Save to external 'tkl.pkl' file in the current working directory.
        :param email: Email to be saved by pickle
        :param requests: Requests to be saved by pickle
        """
        with open(getcwd() + '/tkl.pkl', 'wb') as f:
            pickle.dump(dict(email=email, requests=requests), f, pickle.HIGHEST_PROTOCOL)