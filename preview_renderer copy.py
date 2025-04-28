import os
import json
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtCore import QRect, Qt, QSize

class CustomPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 240)
        self.setMaximumSize(320, 240)
        self.font_image = None
        self.bg_image = None
        self.text = ""
        self.char_height = 16
        self.text_x = 55
        self.text_y = 184
        self.line_spacing = 16
        self.char_limit = 35
        self.current_file = None

        # Obter diretório do script para caminhos relativos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.default_config = {
            "background": os.path.join(script_dir, "images", "mgs_demo.BMP"),
            "font_image": os.path.join(script_dir, "images", "mgs-fonte.bmp"),
            "text_position": {"x": 55, "y": 184},
            "line_spacing": 16,
            "char_limit": 35
        }

        # Tabela de caracteres VWF
        self.char_table = {
            ' ': (0, 0, 4), '!': (16, 0, 4), '"': (32, 0, 4), "'": (112, 0, 3),
            '(': (128, 0, 3), ')': (144, 0, 3), ',': (192, 0, 2), '-': (208, 0, 4),
            '.': (224, 0, 3), ':': (160, 16, 3), ';': (176, 16, 3), '?': (240, 16, 7),
            '0': (0, 16, 7), '1': (16, 16, 7), '2': (32, 16, 7), '3': (48, 16, 7),
            '4': (64, 16, 7), '5': (80, 16, 7), '6': (96, 16, 7), '7': (112, 16, 7),
            '8': (128, 16, 7), '9': (144, 16, 7), 'A': (16, 32, 8), 'B': (32, 32, 9),
            'C': (48, 32, 9), 'D': (64, 32, 9), 'E': (80, 32, 8), 'F': (96, 32, 8),
            'G': (112, 32, 10), 'H': (128, 32, 9), 'I': (144, 32, 4), 'J': (160, 32, 7),
            'K': (176, 32, 10), 'L': (193, 32, 7), 'M': (208, 32, 11), 'N': (224, 32, 9),
            'O': (240, 32, 10), 'P': (0, 48, 8), 'Q': (16, 48, 10), 'R': (32, 48, 9),
            'S': (48, 48, 8), 'T': (64, 48, 8), 'U': (80, 48, 9), 'V': (96, 48, 8),
            'W': (112, 48, 12), 'X': (128, 48, 8), 'Y': (144, 48, 8), 'Z': (160, 48, 7),
            'a': (16, 64, 7), 'b': (32, 64, 8), 'c': (48, 64, 7), 'd': (64, 64, 8),
            'e': (80, 64, 8), 'f': (96, 64, 4), 'g': (112, 62, 8), 'h': (128, 64, 7),
            'i': (144, 64, 3), 'j': (160, 62, 3), 'k': (176, 64, 7), 'l': (192, 64, 3),
            'm': (208, 64, 10), 'n': (224, 64, 7), 'o': (240, 64, 7), 'p': (0, 78, 8),
            'q': (16, 78, 8), 'r': (32, 80, 4), 's': (48, 80, 6), 't': (64, 80, 4),
            'u': (80, 80, 7), 'v': (96, 80, 6), 'w': (112, 80, 9), 'x': (128, 80, 6),
            'y': (144, 78, 6), 'z': (160, 80, 6), 'á': (192, 48, 7), 'à': (240, 48, 7),
            'â': (224, 48, 7), 'ã': (208, 48, 7), 'é': (192, 80, 8), 'ê': (208, 80, 8),
            'í': (224, 80, 3), 'ó': (240, 80, 7), 'ô': (16, 96, 7), 'õ': (0, 96, 7),
            'ú': (32, 96, 7), 'ç': (48, 94, 7), 'Á': (64, 95, 8), 'À': (112, 95, 8),
            'Â': (96, 95, 8), 'Ã': (80, 95, 7), 'É': (128, 95, 8), 'Ê': (144, 95, 8),
            'Í': (160, 95, 4), 'Ó': (176, 95, 10), 'Ô': (208, 95, 10), 'Õ': (192, 95, 10),
            'Ú': (224, 95, 8), 'Ç': (240, 94, 8)
        }

        # Carrega imagens padrão imediatamente
        self.load_images(self.default_config["background"], self.default_config["font_image"])

    def setText(self, text: str):
        """Define o texto a ser renderizado e verifica o limite de caracteres"""
        clean_text = text.replace("｜", "")
        lines = clean_text.split('\n')
        
        for line in lines:
            if len(line) > self.char_limit:
                print(f"Aviso: Linha excede {self.char_limit} caracteres: '{line}'")
                
        self.text = text
        self.update()

    def load_config_from_json(self, file_path: str):
        """Carrega configurações do arquivo JSON"""
        self.current_file = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get("metadata", {})
            self.char_limit = metadata.get("char_limit", 35)

            # Diretório raiz do projeto (Text Editor\images)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(script_dir, "images")

            # Obtém nomes dos arquivos do JSON
            bg_file = metadata.get("background", "mgs_demo.BMP")
            font_file = metadata.get("font_image", "mgs-fonte.bmp")

            # Constrói caminhos absolutos com base em Text Editor\images
            bg_path = os.path.join(images_dir, os.path.basename(bg_file))
            font_path = os.path.join(images_dir, os.path.basename(font_file))

            self.load_images(bg_path, font_path)

            # Atualiza posição do texto
            text_pos = metadata.get("text_position", self.default_config["text_position"])
            self.text_x = text_pos.get("x", 55)
            self.text_y = text_pos.get("y", 184)
            self.line_spacing = metadata.get("line_spacing", 16)
        
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            # Fallback para imagens padrão
            self.load_images(self.default_config["background"], self.default_config["font_image"])

    def load_images(self, bg_path: str, font_path: str):
        """Carrega as imagens de fundo e fonte com tratamento de erros"""
        print(f"Tentando carregar imagens:")
        print(f"Background: {bg_path}")
        print(f"Font: {font_path}")
        
        try:
            # Verifica e carrega imagem de fundo
            if os.path.exists(bg_path):
                self.bg_image = QImage(bg_path)
                if self.bg_image.isNull():
                    raise ValueError(f"Formato inválido para imagem de fundo: {bg_path}")
                self.setFixedSize(self.bg_image.size())
                print("Imagem de fundo carregada com sucesso")
            else:
                raise FileNotFoundError(f"Arquivo não encontrado: {bg_path}")
                
            # Verifica e carrega imagem da fonte
            if os.path.exists(font_path):
                self.font_image = QImage(font_path)
                if self.font_image.isNull():
                    raise ValueError(f"Formato inválido para imagem da fonte: {font_path}")
                print("Fonte carregada com sucesso")
            else:
                raise FileNotFoundError(f"Arquivo não encontrado: {font_path}")
                
        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")
            # Fallback para imagens padrão
            try:
                print("Tentando carregar imagens padrão...")
                self.bg_image = QImage(self.default_config["background"])
                self.font_image = QImage(self.default_config["font_image"])
                self.setFixedSize(320, 240)
                print("Imagens padrão carregadas como fallback")
            except Exception as fallback_error:
                print(f"Erro ao carregar imagens padrão: {fallback_error}")
                self.bg_image = None
                self.font_image = None

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Desenha fundo
        if self.bg_image and not self.bg_image.isNull():
            painter.drawImage(0, 0, self.bg_image)
        else:
            painter.fillRect(self.rect(), Qt.GlobalColor.black)

        # Desenha texto
        if self.font_image and not self.font_image.isNull():
            x, y = self.text_x, self.text_y
            line_height = self.char_height + 2  # Ajuste fino para espaçamento
            
            for char in self.text:
                if char == '\n':
                    x = self.text_x
                    y += line_height  # Usa o espaçamento ajustado
                    continue
                    
                if char in self.char_table:
                    sx, sy, w = self.char_table[char]
                    # Ajuste fino no posicionamento vertical (subtrai 2 pixels)
                    target_y = y - 2  
                    source = QRect(sx, sy, w, self.char_height)
                    target = QRect(x, target_y, w, self.char_height)
                    painter.drawImage(target, self.font_image, source)
                    x += w
                else:
                    x += 6  # fallback para caracteres desconhecidos
        painter.end()

def criar_preview_widget():
    """Factory function para criar o widget de preview"""
    return CustomPreviewWidget()

def render_preview(editable_box, preview_box, file_path: str = None):
    """Atualiza o preview com o texto atual"""
    texto = editable_box.toPlainText()
    preview_box.setText(texto)
    
    if file_path and file_path != preview_box.current_file:
        preview_box.load_config_from_json(file_path)