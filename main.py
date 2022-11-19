import sys
import re
import requests
import threading
import pandas as pd

from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
from PySide6 import *
from ui_interface import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Remove title bar
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        # Set main background transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Shadow effect style
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(50)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 92, 157, 550))

        # apply shadow to central widget
        self.ui.centralwidget.setGraphicsEffect(self.shadow)

        # Set window icon
        # wont show cus windows title bar has been made transparent
        self.setWindowIcon(QtGui.QIcon("gmail-icon-1.svg"))

        # Set windows title
        self.setWindowTitle('Email Extractor')

        # Window size grip
        QSizeGrip(self.ui.resizer)

        # Minimize Window
        self.ui.minimize.clicked.connect(lambda: self.showMinimized())

        # Close Window
        self.ui.close.clicked.connect(lambda: self.close())

        # Maximize window
        self.ui.maximize.clicked.connect(lambda: self.restore_or_maximize_window())

        # Start the extracting
        self.ui.start_button.clicked.connect(lambda: self.scraping())

        # exportig to csv file
        self.ui.pushButton_4.clicked.connect(lambda: self.csv_file())
        self.ui.pushButton_5.clicked.connect(lambda: self.new())

        # stop extracting
        # self.ui.pushButton.clicked.connect(lambda: self.end_process())

        self.show()

    def new(self):
        self.ui.website.clear()
        self.ui.result.clear()

    def csv_file(self):
        if not self.ui.result.toPlainText():
            self.ui.result.setText('No emails found')
        else:
            df = pd.DataFrame(emails, columns=['Emails'])
            df.to_csv('email_extracted.csv')

    def restore_or_maximize_window(self):
        # if window is maximized
        if self.isMaximized():
            self.showNormal()
            # change icon
            self.ui.maximize.setIcon(QtGui.QIcon("maximize-2.svg"))
        else:
            self.showMaximized()
            # Change Icon
            self.ui.maximize.setIcon(QtGui.QIcon("minimize-2.svg"))

    # def thread(self):
    #     t1 = Thread(target=self.scraping)
    #     t1.start()

    def scraping(self):
        global emails

        website_url = self.ui.website.text()

        unscraped = deque([website_url])

        scraped = set()

        emails = set()

        while len(unscraped):
            url = unscraped.popleft()
            scraped.add(url)
            parts = urlsplit(url)

            base_url = "{0.scheme}://{0.netloc}".format(parts)
            if '/' in parts.path:
                path = url[:url.rfind('/') + 1]
            else:
                path = url

        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout,
                requests.exceptions.InvalidSchema, requests.exceptions.RequestException,
                requests.exceptions.BaseHTTPError,
                requests.exceptions.TooManyRedirects):
            self.ui.result.setText('Connection Error or Invalid Link')

        new_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I)

        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'html.parser')

        self.ui.result.append(str('\n'.join(emails)))

        for anchor in soup.find_all("a"):

            # extract linked url from the anchor
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''

            # resolve relative links (starting with /)
            if link.startswith('/'):
                link = base_url + link

            elif not link.startswith('http'):
                link = path + link

            if not link.endswith(".gz"):
                if not link in unscraped and not link in scraped:
                    unscraped.append(link)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
