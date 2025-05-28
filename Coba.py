import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QDockWidget, QScrollArea, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QMimeData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi CRUD Enhanced (Contoh)")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.init_status_bar()

    def init_ui(self):
        # --- Main Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Input Form (Wrapped in QScrollArea) ---
        self.form_frame = QFrame()
        self.form_frame.setFrameShape(QFrame.StyledPanel)
        self.form_layout = QVBoxLayout(self.form_frame)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama Produk")
        self.form_layout.addWidget(QLabel("Nama Produk:"))
        self.form_layout.addWidget(self.name_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Harga")
        self.form_layout.addWidget(QLabel("Harga:"))
        self.form_layout.addWidget(self.price_input)

        # QClipboard Integration Example
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Deskripsi")
        self.form_layout.addWidget(QLabel("Deskripsi:"))
        self.form_layout.addWidget(self.description_input)

        self.paste_button = QPushButton("Tempel dari Clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        self.form_layout.addWidget(self.paste_button)

        # Add some dummy widgets to demonstrate scrollability
        for i in range(5):
            self.form_layout.addWidget(QLabel(f"Field Tambahan {i+1}:"))
            self.form_layout.addWidget(QLineEdit(f"Data {i+1}"))

        self.form_scroll_area = QScrollArea()
        self.form_scroll_area.setWidgetResizable(True)
        self.form_scroll_area.setWidget(self.form_frame)
        self.form_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.form_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_layout.addWidget(self.form_scroll_area)

        # --- CRUD Buttons ---
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Tambah Data")
        self.add_button.clicked.connect(self.add_data)
        self.button_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Data")
        self.button_layout.addWidget(self.update_button) # Not implemented for simplicity
        self.delete_button = QPushButton("Hapus Data")
        self.button_layout.addWidget(self.delete_button) # Not implemented for simplicity

        self.main_layout.addLayout(self.button_layout)

        # --- QTableWidget (for displaying data) ---
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Nama Produk", "Harga", "Deskripsi"])
        # Ensure scrollability for the table
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.resizeColumnsToContents()
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.main_layout.addWidget(self.table_widget)

        # --- QDockWidget (Search/Info Panel) ---
        self.dock_widget = QDockWidget("Panel Informasi/Pencarian", self)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)

        self.dock_content_widget = QWidget()
        self.dock_content_layout = QVBoxLayout(self.dock_content_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari data...")
        self.dock_content_layout.addWidget(QLabel("Cari:"))
        self.dock_content_layout.addWidget(self.search_input)

        self.info_label = QLabel("Ini adalah panel dockable.\nAnda bisa memindahkannya.")
        self.info_label.setWordWrap(True)
        self.dock_content_layout.addWidget(self.info_label)
        self.dock_content_layout.addStretch() # Push content to top

        self.dock_widget.setWidget(self.dock_content_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

    def init_status_bar(self):
        # QStatusBar Example
        self.statusBar().showMessage("Nama: [Nama Anda] | NIM: [NIM Anda]", 0) # 0 means permanent

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasText():
            self.description_input.setText(mime_data.text())
        else:
            self.statusBar().showMessage("Clipboard tidak mengandung teks.", 3000)

    def add_data(self):
        name = self.name_input.text()
        price = self.price_input.text()
        description = self.description_input.text()

        if name and price and description:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(name))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(price))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(description))

            self.name_input.clear()
            self.price_input.clear()
            self.description_input.clear()
            self.statusBar().showMessage("Data berhasil ditambahkan!", 3000)
        else:
            self.statusBar().showMessage("Semua field harus diisi!", 3000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())