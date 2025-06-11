import sys
import os
import csv
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFileDialog, QScrollArea, QGridLayout, QDialog, QMessageBox, QTextEdit, QDialogButtonBox,
                             QMenuBar, QMenu, QAction, QStatusBar, QInputDialog, QHBoxLayout,QDockWidget)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt


class AddEditBookDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Buku" if data is None else "Edit Buku")
        self.setFixedSize(400, 400)

        self.layout = QVBoxLayout()

        self.judul_input = QLineEdit()
        self.judul_input.setPlaceholderText("Judul")

        self.pengarang_input = QLineEdit()
        self.pengarang_input.setPlaceholderText("Pengarang")

        self.tahun_input = QLineEdit()
        self.tahun_input.setPlaceholderText("Tahun")

        self.sinopsis_input = QTextEdit()
        self.sinopsis_input.setPlaceholderText("Paste sinopsis dari clipboard di sini...")

        self.cover_path = ''
        self.cover_button = QPushButton("Unggah Gambar Sampul")
        self.cover_button.clicked.connect(self.upload_cover)

        self.paste_button = QPushButton("Paste dari Clipboard")
        self.paste_button.clicked.connect(self.paste_from_clipboard)

        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.accept)

        self.layout.addWidget(QLabel("Judul"))
        self.layout.addWidget(self.judul_input)
        self.layout.addWidget(QLabel("Pengarang"))
        self.layout.addWidget(self.pengarang_input)
        self.layout.addWidget(QLabel("Tahun"))
        self.layout.addWidget(self.tahun_input)
        self.layout.addWidget(QLabel("Sinopsis"))
        self.layout.addWidget(self.sinopsis_input)
        self.layout.addWidget(self.paste_button)
        self.layout.addWidget(self.cover_button)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        if data:
            self.judul_input.setText(data[1])
            self.pengarang_input.setText(data[2])
            self.tahun_input.setText(str(data[3]))
            self.cover_path = data[4] if data[4] else ''
            self.sinopsis_input.setPlainText(data[5] if data[5] else '')

    def upload_cover(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Image Files (*.png *.jpg *.bmp *.webp *.jpeg)")
        if path:
            self.cover_path = path
            QMessageBox.information(self, "Cover", f"Gambar '{path}' berhasil dipilih.")

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.sinopsis_input.setPlainText(clipboard.text())

    def get_data(self):
        return (
            self.judul_input.text(),
            self.pengarang_input.text(),
            self.tahun_input.text(),
            self.cover_path,
            self.sinopsis_input.toPlainText()
        )


class BookDetailDialog(QDialog):
    def __init__(self, judul, pengarang, tahun, sinopsis, cover, parent=None):
        super().__init__(parent)
        self.setWindowTitle(judul)
        self.setFixedSize(400, 500)
        layout = QVBoxLayout()

        if cover:
            pixmap = QPixmap(cover).scaled(150, 200, Qt.KeepAspectRatio)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

        layout.addWidget(QLabel(f"<b>Judul:</b> {judul}"))
        layout.addWidget(QLabel(f"<b>Pengarang:</b> {pengarang}"))
        layout.addWidget(QLabel(f"<b>Tahun:</b> {tahun}"))
        layout.addWidget(QLabel("<b>Sinopsis:</b>"))
        sinopsis_label = QTextEdit(sinopsis)
        sinopsis_label.setReadOnly(True)
        layout.addWidget(sinopsis_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)


class BukuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(100, 100, 800, 600)

        self.conn = sqlite3.connect("buku.db")
        self.c = self.conn.cursor()

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                pengarang TEXT NOT NULL,
                tahun INTEGER NOT NULL,
                cover TEXT,
                sinopsis TEXT
            )
        ''')
        self.conn.commit()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.all_books = []
        self.init_ui()
        self.create_menu()

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.info_label = QLabel("Nama: Dewi Agustin Asri | NIM: F1D022039")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-weight: bold;")

        # Bungkus dalam QWidget dengan layout tengah
        container = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.info_label)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)
        
        # DockWidget untuk informasi atau menu tambahan
        dock = QDockWidget("Informasi Pengguna", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        info_widget = QWidget()
        info_layout = QVBoxLayout()
        info_label = QLabel("Dibuat oleh:\nDewi Agustin Asri\nNIM: F1D022039")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("padding: 10px; font-weight: bold;")
        info_layout.addWidget(info_label)
        info_widget.setLayout(info_layout)
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dock.setWidget(info_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        #self.status.addWidget(container, 1)

    def init_ui(self):
        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari buku berdasarkan judul...")
        self.search_input.textChanged.connect(self.filter_books)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        self.load_data()

        self.add_button = QPushButton("Tambah Buku")
        self.add_button.clicked.connect(self.show_add_book_dialog)

        layout.addWidget(self.search_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.scroll_area)
        self.central_widget.setLayout(layout)

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")

        export_action = QAction("Export CSV", self)
        export_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tambah_action = QAction("Tambah Buku", self)
        tambah_action.triggered.connect(self.show_add_book_dialog)

        edit_action = QAction("Edit Buku", self)
        edit_action.triggered.connect(self.edit_book_by_title)

        hapus_action = QAction("Hapus Buku", self)
        hapus_action.triggered.connect(self.delete_book_by_title)

        cari_action = QAction("Cari Buku", self)
        cari_action.triggered.connect(self.filter_books_manual)

        edit_menu.addAction(tambah_action)
        edit_menu.addAction(edit_action)
        edit_menu.addAction(hapus_action)
        edit_menu.addAction(cari_action)

    def load_data(self):
        self.c.execute("SELECT * FROM buku")
        self.all_books = self.c.fetchall()
        self.display_books(self.all_books)

    def display_books(self, books):
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove:
                self.grid_layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

        for index, row in enumerate(books):
            self.add_book_card(row, index)

    def add_book_card(self, row, index):
        id_buku, judul, pengarang, tahun, cover, sinopsis = row

        card = QWidget()
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)

        pixmap = QPixmap(cover)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        info_label = QLabel(f"<b>{judul}</b><br>{pengarang}<br>{tahun}")
        info_label.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(image_label)
        card_layout.addWidget(info_label)

        card.setFixedSize(170, 300)
        card.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 5px;")

        def show_detail():
            dialog = BookDetailDialog(judul, pengarang, tahun, sinopsis, cover, self)
            dialog.exec_()

        def context_menu(event):
            menu = QMenu()
            edit_action = menu.addAction("Edit Buku")
            hapus_action = menu.addAction("Hapus Buku")
            action = menu.exec_(QCursor.pos())
            if action == hapus_action:
                reply = QMessageBox.question(self, 'Konfirmasi Hapus',
                                             f"Yakin ingin menghapus buku '{judul}'?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.c.execute("DELETE FROM buku WHERE id=?", (id_buku,))
                    self.conn.commit()
                    self.load_data()
            elif action == edit_action:
                self.show_edit_book_dialog(row)

        card.mousePressEvent = lambda event: show_detail() if event.button() == Qt.LeftButton else None
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(context_menu)

        self.grid_layout.addWidget(card, index // 4, index % 4)

    def filter_books(self):
        keyword = self.search_input.text().lower()
        filtered = [b for b in self.all_books if keyword in b[1].lower()]
        self.display_books(filtered)

    def filter_books_manual(self):
        keyword, ok = QInputDialog.getText(self, "Cari Buku", "Masukkan judul:")
        if ok and keyword:
            self.search_input.setText(keyword)

    def show_add_book_dialog(self):
        dialog = AddEditBookDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            judul, pengarang, tahun, cover, sinopsis = dialog.get_data()
            if judul and pengarang and tahun:
                try:
                    tahun_int = int(tahun)
                except ValueError:
                    QMessageBox.warning(self, "Input Tidak Valid", "Tahun harus berupa angka.")
                    return
                self.c.execute('''INSERT INTO buku (judul, pengarang, tahun, cover, sinopsis)
                                  VALUES (?, ?, ?, ?, ?)''',
                               (judul, pengarang, tahun_int, cover, sinopsis))
                self.conn.commit()
                self.load_data()
            else:
                QMessageBox.warning(self, "Input Tidak Lengkap", "Semua kolom wajib diisi.")

    def show_edit_book_dialog(self, data):
        dialog = AddEditBookDialog(self, data)
        if dialog.exec_() == QDialog.Accepted:
            judul, pengarang, tahun, cover, sinopsis = dialog.get_data()
            if judul and pengarang and tahun:
                try:
                    tahun_int = int(tahun)
                except ValueError:
                    QMessageBox.warning(self, "Input Tidak Valid", "Tahun harus berupa angka.")
                    return
                self.c.execute('''UPDATE buku SET judul=?, pengarang=?, tahun=?, cover=?, sinopsis=?
                                  WHERE id=?''',
                               (judul, pengarang, tahun_int, cover, sinopsis, data[0]))
                self.conn.commit()
                self.load_data()
            else:
                QMessageBox.warning(self, "Input Tidak Lengkap", "Semua kolom wajib diisi.")

    def edit_book_by_title(self):
        title, ok = QInputDialog.getText(self, "Edit Buku", "Masukkan judul buku yang ingin diedit:")
        if ok and title:
            self.c.execute("SELECT * FROM buku WHERE judul=?", (title,))
            book = self.c.fetchone()
            if book:
                self.show_edit_book_dialog(book)
            else:
                QMessageBox.information(self, "Tidak Ditemukan", f"Buku dengan judul '{title}' tidak ditemukan.")

    def delete_book_by_title(self):
        title, ok = QInputDialog.getText(self, "Hapus Buku", "Masukkan judul buku yang ingin dihapus:")
        if ok and title:
            self.c.execute("SELECT * FROM buku WHERE judul=?", (title,))
            book = self.c.fetchone()
            if book:
                reply = QMessageBox.question(self, 'Konfirmasi Hapus',
                                             f"Yakin ingin menghapus buku '{title}'?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.c.execute("DELETE FROM buku WHERE judul=?", (title,))
                    self.conn.commit()
                    self.load_data()
            else:
                QMessageBox.information(self, "Tidak Ditemukan", f"Buku dengan judul '{title}' tidak ditemukan.")

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['ID', 'Judul', 'Pengarang', 'Tahun', 'Cover', 'Sinopsis'])
                    self.c.execute("SELECT * FROM buku")
                    for row in self.c.fetchall():
                        writer.writerow(row)
                QMessageBox.information(self, "Export Berhasil", f"Data berhasil disimpan di {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Export Gagal", f"Gagal menyimpan file CSV.\n{str(e)}")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BukuApp()
    window.show()
    sys.exit(app.exec_())
