import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QRadioButton,
    QLineEdit, QGroupBox
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtCore import Qt


class FontMapGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de Mapeamento de Fonte")
        self.image = None
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom = 2

        self.image_label.setMinimumWidth(512)
        self.image_label.setMinimumHeight(256)

        main_layout = QHBoxLayout(self)

        # Lado esquerdo: imagem
        self.image_frame = QVBoxLayout()
        self.image_frame.addWidget(self.image_label)

        # Lado direito: botões e tabela
        right_panel = QVBoxLayout()

        # Grupo de botões
        button_box = QGroupBox("Opções")
        button_layout = QVBoxLayout()

        self.load_button = QPushButton("Carregar Imagem")
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)

        self.generate_button = QPushButton("Gerar mapa automaticamente")
        self.generate_button.clicked.connect(self.generate_map)
        button_layout.addWidget(self.generate_button)

        self.vwf_radio = QRadioButton("Fonte com largura variável (VWF)")
        self.vwf_radio.toggled.connect(self.toggle_vwf_inputs)
        button_layout.addWidget(self.vwf_radio)

        vwf_size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Largura")
        self.width_input.setFixedWidth(50)
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Altura")
        self.height_input.setFixedWidth(50)
        vwf_size_layout.addWidget(self.width_input)
        vwf_size_layout.addWidget(self.height_input)
        button_layout.addLayout(vwf_size_layout)

        self.width_input.setEnabled(False)
        self.height_input.setEnabled(False)

        button_box.setLayout(button_layout)
        right_panel.addWidget(button_box)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Char", "X", "Y"])
        right_panel.addWidget(self.table)

        main_layout.addLayout(self.image_frame)
        main_layout.addLayout(right_panel)

    def toggle_vwf_inputs(self):
        is_vwf = self.vwf_radio.isChecked()
        self.width_input.setEnabled(is_vwf)
        self.height_input.setEnabled(is_vwf)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Imagem", "", "Imagens (*.png *.bmp)")
        if file_path:
            self.image = QImage(file_path)
            self.update_image_preview()

    def update_image_preview(self, block_w=8, block_h=16):
        if self.image is None:
            return

        image_copy = self.image.copy()
        painter = QPainter(image_copy)
        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(1)
        painter.setPen(pen)

        cols = image_copy.width() // block_w
        rows = image_copy.height() // block_h

        for x in range(0, cols + 1):
            painter.drawLine(x * block_w, 0, x * block_w, image_copy.height())

        for y in range(0, rows + 1):
            painter.drawLine(0, y * block_h, image_copy.width(), y * block_h)

        painter.end()

        # Aplicar zoom
        pixmap = QPixmap.fromImage(image_copy).scaled(
            image_copy.width() * self.zoom, image_copy.height() * self.zoom, Qt.AspectRatioMode.KeepAspectRatio
        )
        self.image_label.setPixmap(pixmap)

    def generate_map(self):
        if self.image is None:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma imagem antes de gerar o mapa.")
            return

        self.table.setRowCount(0)

        if self.vwf_radio.isChecked():
            try:
                char_width = int(self.width_input.text())
                char_height = int(self.height_input.text())
            except ValueError:
                QMessageBox.warning(self, "Erro", "Largura e altura devem ser números.")
                return
        else:
            char_width, char_height = 8, 16  # padrão

        self.update_image_preview(block_w=char_width, block_h=char_height)

        columns = self.image.width() // char_width
        rows = self.image.height() // char_height
        ascii_chars = [chr(i) for i in range(32, 127)]

        idx = 0
        for y in range(rows):
            for x in range(columns):
                if idx >= len(ascii_chars):
                    break
                char = ascii_chars[idx]
                self.table.insertRow(self.table.rowCount())
                self.table.setItem(idx, 0, QTableWidgetItem(char))
                self.table.setItem(idx, 1, QTableWidgetItem(str(x * char_width)))
                self.table.setItem(idx, 2, QTableWidgetItem(str(y * char_height)))
                idx += 1
            if idx >= len(ascii_chars):
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FontMapGenerator()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())
