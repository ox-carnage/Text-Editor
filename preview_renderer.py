# preview_renderer.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtCore import QRect

class CustomPreviewWidget(QWidget):
    def __init__(self, font_image_path='images/mgs-fonte.bmp', bg_image_path='images/mgs_demo.BMP', parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 120)
        self.font_image = QImage(font_image_path)
        self.bg_image = QImage(bg_image_path)
        self.text = ""

        # Altura dos caracteres da fonte
        self.char_height = 16

        # Tabela de caracteres VWF
        self.char_table = {
           # Caracteres especiais e pontuação
    ' ':  (0, 0, 4),   '!':  (16, 0, 4),   '"':  (32, 0, 4),   "'": (112, 0, 3),   '(': (128, 0, 3),   ')': (144, 0, 3),
    ',': (192, 0, 2),  '-': (208, 0, 4),   '.': (224, 0, 3),   ':': (160, 16, 3),  ';': (176, 16, 3),  '?': (240, 16, 7),

    # Números
    '0': (0, 16, 7),   '1': (16, 16, 7),   '2': (32, 16, 7),   '3': (48, 16, 7),   '4': (64, 16, 7),   '5': (80, 16, 7),
    '6': (96, 16, 7),  '7': (112, 16, 7),  '8': (128, 16, 7),  '9': (144, 16, 7),

    # Letras maiúsculas
    'A': (16, 32, 8),  'B': (32, 32, 9),   'C': (48, 32, 9),   'D': (64, 32, 9),   'E': (80, 32, 8),   'F': (96, 32, 8),
    'G': (112, 32,10), 'H': (128, 32,9),   'I': (144, 32,4),   'J': (160, 32,7),   'K': (176, 32,10),  'L': (193, 32,7),
    'M': (208, 32,11), 'N': (224, 32,9),   'O': (240, 32,10),  'P': (0, 48, 8),    'Q': (16, 48,10),   'R': (32, 48,9),
    'S': (48, 48, 8),  'T': (64, 48, 8),   'U': (80, 48, 9),   'V': (96, 48, 8),   'W': (112, 48,12),  'X': (128, 48,8),
    'Y': (144, 48,8),  'Z': (160, 48,7),

    # Letras minúsculas
    'a': (16, 64, 7),  'b': (32, 64, 8),   'c': (48, 64, 7),   'd': (64, 64, 8),   'e': (80, 64, 8),   'f': (96, 64, 4),
    'g': (112, 62,8),  'h': (128, 64,7),   'i': (144, 64,3),   'j': (160, 62,3),   'k': (176, 64,7),   'l': (192, 64,3),
    'm': (208, 64,10), 'n': (224, 64,7),   'o': (240, 64,7),   'p': (0, 78, 8),    'q': (16, 78, 8),   'r': (32, 80,4),
    's': (48, 80, 6),  't': (64, 80, 4),   'u': (80, 80, 7),   'v': (96, 80, 6),   'w': (112, 80,9),   'x': (128, 80,6),
    'y': (144, 78,6),  'z': (160, 80,6),

    # Acentos minúsculos
    'á': (192, 48, 7), 'à': (240, 48, 7),  'â': (224, 48, 7),  'ã': (208, 48, 7),  'é': (192, 80, 8),  'ê': (208, 80, 8),
    'í': (224, 80, 3), 'ó': (240, 80, 7),  'ô': (16, 96, 7),   'õ': (0, 96, 7),    'ú': (32, 96, 7),   'ç': (48, 94, 7),

    # Acentos maiúsculos
    'Á': (64, 95, 8),  'À': (112, 95, 8),  'Â': (96, 95, 8),   'Ã': (80, 95, 7),   'É': (128, 95, 8),  'Ê': (144, 95, 8),
    'Í': (160, 95, 4), 'Ó': (176, 95,10),  'Ô': (208, 95,10),  'Õ': (192, 95,10),  'Ú': (224, 95, 8),  'Ç': (240, 94, 8),
}

    def setText(self, text: str):
        self.text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Desenha a imagem de fundo primeiro
        painter.drawImage(0, 0, self.bg_image)

        # Posição do texto na caixa de diálogo
        x, y = 55, 184  # conforme `[dialogo] inicio_dialogo = 47 138`
        line_spacing = 16

        for char in self.text:
            if char == '\n':
                x = 55
                y += line_spacing
                continue

            if char in self.char_table:
                sx, sy, w = self.char_table[char]
                source = QRect(sx, sy, w, self.char_height)
                target = QRect(x, y, w, self.char_height)
                painter.drawImage(target, self.font_image, source)
                x += w
            else:
                x += 6  # fallback

        painter.end()


def criar_preview_widget():
    return CustomPreviewWidget()


def render_preview(editable_box, preview_box):
    texto = editable_box.toPlainText()
    preview_box.setText(texto)
