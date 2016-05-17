from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QDialog, QPushButton, QLabel, \
     QLineEdit, QFormLayout, QComboBox, QVBoxLayout, QHBoxLayout, QHeaderView
from PyQt5.QtCore import Qt


class RequestTable(QTableWidget):
    """
    The table which stores all of the user's requests.
    """
    def __init__(self, email, requests, parent=None):
        super(RequestTable, self).__init__(parent)
        self.parent = parent
        self.email = email
        self.requests = requests
        self.inserted = {}
        self.removed = {}
        self.set_up_table()

    def set_up_table(self):
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Keyword", "Subreddit", "Listing"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Takes the saved requests and fills the table
        self.setRowCount(len(self.requests))
        for counter, (key, value) in enumerate(self.requests.iteritems()):
            row = [QTableWidgetItem(item) for item in value]
            self._format_table(row)

            for index, items in enumerate(row):
                self.setItem(counter, index, items)

    def add(self, dialog=None):
        """
        Handles adding new requests in the right click context menu.
        :param dialog: Dialog that is filled with old request information
        """
        if not dialog:
            dialog = RequestDialog(parent=self.parent)

        if dialog.exec_():
            row = [QTableWidgetItem(item) for item in dialog.values()]
            key = row[0].text() + row[1].text() + row[2].text()
            request = row[0].text(), row[1].text(), row[2].text()
            self._format_table(row)
            self.requests[key] = request
            self.inserted[key] = request

            self.insertRow(self.rowCount())
            for index, items in enumerate(row):
                self.setItem(self.rowCount() - 1, index, items)

    def delete(self):
        """
        Handles removing requests in the right click context menu.
        """
        current_row = self.currentRow()
        key = self.item(current_row, 0).text() + self.item(current_row, 1).text() + self.item(current_row, 2).text()
        request = self.requests.pop(key)

        # If the requests was recently added, remove it from the inserted list. Otherwise, add it to the removed list
        if key in self.inserted.keys():
            del self.inserted[key]
        else:
            self.removed[key] = request

        self.removeRow(current_row)

    def edit_request(self):
        """
        Handles editing pre-existing requests in the right click context menu.
        """
        # Creates a dialog and fills in the dialog with the request information.
        dialog = RequestDialog(parent=self.parent)

        current_row = self.currentRow()
        prev_keyword = self.item(current_row, 0).text()
        prev_subreddit = self.item(current_row, 1).text()
        prev_listing = self.item(current_row, 2).text()

        dialog.keyword_edit.setText(prev_keyword)
        dialog.subreddit_edit.setText(prev_subreddit)
        dialog.listing_combo_box.setCurrentIndex(dialog.listing_combo_box.findText(prev_listing))

        self.delete()
        self.add(dialog=dialog)

    @staticmethod
    def _format_table(headers):
        """
        Formats each cell in the table before inserting in the data.
        :param headers: Each cell in the table's row
        """
        for entries in headers:
            entries.setTextAlignment(Qt.AlignCenter)
            entries.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)


class RequestDialog(QDialog):
    """
    The dialog used to add and edit requests.
    """
    def __init__(self, parent=None):
        super(RequestDialog, self).__init__(parent)
        self.parent = parent

        self.set_up_window()
        self.set_up_request_dialog()

    def set_up_window(self):
        self.resize(200, 150)

        center_x = self.parent.x() + (self.parent.frameGeometry().width() - self.frameGeometry().width()) / 2
        center_y = self.parent.y() + (self.parent.frameGeometry().height() - self.frameGeometry().height()) / 2

        self.move(center_x, center_y)

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

    def set_up_request_dialog(self):
        keyword_label = QLabel("Keyword ")
        self.keyword_edit = QLineEdit()

        subreddit_label = QLabel("Subreddit ")
        self.subreddit_edit = QLineEdit()

        listing_label = QLabel("Listing")
        self.listing_combo_box = QComboBox()
        self.listing_combo_box.addItems(["Hot", "New", "Rising", "Controversial", "Top"])

        info_layout = QFormLayout()
        info_layout.addRow(keyword_label, self.keyword_edit)
        info_layout.addRow(subreddit_label, self.subreddit_edit)
        info_layout.addRow(listing_label, self.listing_combo_box)

        add_button = QPushButton("Add")
        add_button.setMaximumWidth(100)
        add_button.clicked.connect(self.accept)

        add_button_layout = QHBoxLayout()
        add_button_layout.addWidget(add_button)

        dialog_layout = QVBoxLayout()
        dialog_layout.addLayout(info_layout)
        dialog_layout.addLayout(add_button_layout)

        self.setLayout(dialog_layout)

    def values(self):
        return self.keyword_edit.text(), self.subreddit_edit.text(), self.listing_combo_box.currentText()
