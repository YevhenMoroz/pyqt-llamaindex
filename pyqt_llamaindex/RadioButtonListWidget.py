from PyQt5.QtWidgets import QWidget, QRadioButton, QVBoxLayout


class RadioButtonListWidget(QWidget):
    context_list = ["Algo", "CON", "EQ", "FX", "MobileTrading", "PERF", "WebAdmin", "WebTrading"]

    def __init__(self):
        super().__init__()
        self.__init_ui()

        self.checked_button = self.context_list[0]

    def __init_ui(self):
        # Create radio buttons
        layout = QVBoxLayout()
        for context in self.context_list:
            self.radio_button = QRadioButton(context)
            self.radio_button.clicked.connect(self.__radio_button_clicked)
            layout.addWidget(self.radio_button)
        layout.itemAt(0).widget().setChecked(True)
        self.setLayout(layout)

    def __radio_button_clicked(self):
        selected_button = self.sender()
        if selected_button.isChecked():
            self.checked_button = selected_button.text()

    def get_checked_button(self):
        return self.checked_button
