import os
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QCheckBox, QLabel, QMessageBox, QLineEdit, QGroupBox, QComboBox,
    QWidget
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt

# Configuration paths
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
# Removido CACHE_PATH, pois não usaremos mais o cache

# Chave fixa do DeepL
DEEPL_API_KEY = "4aac2bdb-1e65-4a35-9964-8c014b642341:fx"

# Dicionário de idiomas (completo)
IDIOMAS = {
    "pt_BR": {
        "main_title": "Editor de Texto",
        "config_title": "Configurações",
        "menu_arquivo": "Arquivo",
        "menu_abrir": "Abrir",
        "menu_opcoes": "Opções",
        "grupo_traducao": "Tradução Automática",
        "grupo_aparencia": "Aparência",
        "grupo_idioma": "Idioma",
        "grupo_textos": "Blocos de Texto",
        "label_tema": "Selecione o tema:",
        "label_idioma": "Selecione o idioma:",
        "label_api_key": "Chave API ChatGPT (opcional):",
        "ativar_traducao": "Ativar tradução automática",
        "texto_original": "Texto Original",
        "texto_editavel": "Texto Editável",
        "btn_aplicar": "Aplicar",
        "btn_salvar": "Salvar",
        "btn_cancelar": "Cancelar",
        "btn_voltar": "Voltar",
        "btn_avancar": "Avançar",
        "btn_limpar": "Limpar",
        "btn_traduzir": "Traduzir",
        "status_online": "Online ✅",
        "status_offline": "Offline ❌",
        "msg_traducao_desativada": "Ative a tradução nas Configurações",
        "msg_erro_traducao": "Erro na tradução"
    },
    "en_US": {
        "main_title": "Text Editor",
        "config_title": "Settings",
        "menu_arquivo": "File",
        "menu_abrir": "Open",
        "menu_opcoes": "Options",
        "grupo_traducao": "Auto Translation",
        "grupo_aparencia": "Appearance",
        "grupo_idioma": "Language",
        "grupo_textos": "Text Blocks",
        "label_tema": "Select theme:",
        "label_idioma": "Select language:",
        "label_api_key": "ChatGPT API Key (optional):",
        "ativar_traducao": "Enable auto translation",
        "texto_original": "Original Text",
        "texto_editavel": "Editable Text",
        "btn_aplicar": "Apply",
        "btn_salvar": "Save",
        "btn_cancelar": "Cancel",
        "btn_voltar": "Back",
        "btn_avancar": "Next",
        "btn_limpar": "Clear",
        "btn_traduzir": "Translate",
        "status_online": "Online ✅",
        "status_offline": "Offline ❌",
        "msg_traducao_desativada": "Enable translation in Settings",
        "msg_erro_traducao": "Translation error"
    },
    "es_ES": {
        "main_title": "Editor de Texto",
        "config_title": "Configuración",
        "menu_arquivo": "Archivo",
        "menu_abrir": "Abrir",
        "menu_opcoes": "Opciones",
        "grupo_traducao": "Traducción Automática",
        "grupo_aparencia": "Apariencia",
        "grupo_idioma": "Idioma",
        "grupo_textos": "Bloques de Texto",
        "label_tema": "Seleccione tema:",
        "label_idioma": "Seleccione idioma:",
        "label_api_key": "Clave API ChatGPT (opcional):",
        "ativar_traducao": "Activar traducción automática",
        "texto_original": "Texto Original",
        "texto_editavel": "Texto Editable",
        "btn_aplicar": "Aplicar",
        "btn_salvar": "Guardar",
        "btn_cancelar": "Cancelar",
        "btn_voltar": "Atrás",
        "btn_avancar": "Adelante",
        "btn_limpar": "Limpiar",
        "btn_traduzir": "Traducir",
        "status_online": "Online ✅",
        "status_offline": "Offline ❌",
        "msg_traducao_desativada": "Active traducción en Configuración",
        "msg_erro_traducao": "Error en traducción"
    }
}

def get_text(key, language="pt_BR"):
    """Retorna texto traduzido"""
    return IDIOMAS.get(language, {}).get(key, key)

def load_settings():
    """Carrega configurações com suporte a idioma e tema"""
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            if "tema" in settings:
                settings["theme"] = settings.pop("tema")
            if "language" not in settings:
                settings["language"] = "pt_BR"
            return settings
    return {
        "translation_enabled": False,
        "chatgpt_api_key": "",
        "theme": "Claro",
        "language": "pt_BR",
        "widget_positions": {},
        "translation_target_lang": "pt"
    }

def save_settings(settings):
    """Save settings to file with error handling"""
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        raise

# Removidas as funções load_cache e save_cache, pois não usaremos mais o cache

THEMES = {
    "Claro": {"window": "#ffffff", "window_text": "#000000", "base": "#ffffff", "text": "#000000", "button": "#f0f0f0", "button_text": "#000000", "highlight": "#0066cc", "highlight_text": "#ffffff", "border": "#c0c0c0", "groupbox": "#f8f8f8"},
    "Escuro": {"window": "#2d2d2d", "window_text": "#ffffff", "base": "#252525", "text": "#ffffff", "button": "#3a3a3a", "button_text": "#ffffff", "highlight": "#0066cc", "highlight_text": "#ffffff", "border": "#555555", "groupbox": "#353535"},
    "Azul": {"window": "#e6f3ff", "window_text": "#003366", "base": "#ffffff", "text": "#003366", "button": "#cce0ff", "button_text": "#003366", "highlight": "#0066cc", "highlight_text": "#ffffff", "border": "#99c2ff", "groupbox": "#d9ecff"},
    "Escuro Profundo": {"window": "#121212", "window_text": "#e0e0e0", "base": "#1e1e1e", "text": "#e0e0e0", "button": "#2a2a2a", "button_text": "#e0e0e0", "highlight": "#0066cc", "highlight_text": "#ffffff", "border": "#444444", "groupbox": "#1a1a1a"},
    "Verde Natureza": {"window": "#edf7ed", "window_text": "#1e4620", "base": "#ffffff", "text": "#1e4620", "button": "#d8e8d8", "button_text": "#1e4620", "highlight": "#4caf50", "highlight_text": "#ffffff", "border": "#a5d6a7", "groupbox": "#e1f1e1"},
    "Militar": {"window": "#121212", "window_text": "#c8c8c8", "base": "#1a1a1a", "text": "#e0e0e0", "button": "#2a2a2a", "button_text": "#00ff00", "highlight": "#006400", "highlight_text": "#ffffff", "border": "#3a3a3a", "groupbox": "#1e1e1e"},
    "Cinza Contrastante": {"window": "#e0e0e0", "window_text": "#333333", "base": "#f5f5f5", "text": "#222222", "button": "#d0d0d0", "button_text": "#333333", "highlight": "#607d8b", "highlight_text": "#ffffff", "border": "#b0b0b0", "groupbox": "#eeeeee"},
    "Metal Gear Solid": {"window": "#0a0a12", "window_text": "#e0e0e0", "base": "#1a1a2a", "text": "#f0f0f0", "button": "#333344", "button_text": "#ffcc00", "highlight": "#b22222", "highlight_text": "#ffffff", "border": "#555577", "groupbox": "#252538"}
}

def aplicar_tema(app, theme_name):
    """Apply the selected theme to the application"""
    theme = THEMES.get(theme_name, THEMES["Claro"])
    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(theme["window"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["window_text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme["base"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme["button"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["button_text"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["highlight"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["highlight_text"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7f7f7f"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
    
    app.setPalette(palette)
    
    app.setStyleSheet(f"""
        QWidget {{ background-color: {theme["window"]}; color: {theme["window_text"]}; }}
        QTextEdit, QPlainTextEdit {{ background-color: {theme["base"]}; color: {theme["text"]}; border: 1px solid {theme["border"]}; }}
        QGroupBox {{ background-color: {theme["groupbox"]}; border: 1px solid {theme["border"]}; border-radius: 3px; margin-top: 0.5em; padding-top: 10px; }}
        QGroupBox::title {{ color: {theme["text"]}; subcontrol-origin: margin; left: 10px; padding: 0 3px; }}
        QPushButton {{ background-color: {theme["button"]}; color: {theme["button_text"]}; border: 1px solid {theme["border"]}; padding: 5px; border-radius: 3px; }}
        QPushButton:hover {{ background-color: {theme["highlight"]}; color: {theme["highlight_text"]}; }}
        QComboBox, QLineEdit {{ background-color: {theme["base"]}; color: {theme["text"]}; border: 1px solid {theme["border"]}; }}
        QLabel {{ color: {theme["text"]}; }}
        QTreeWidget::item:selected {{ font-weight: bold; }}
    """)

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.idioma = parent.idioma if parent else "pt_BR"
        self.settings = load_settings()
        
        self.setWindowTitle(get_text("config_title", self.idioma))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Seção de Tradução
        translation_group = QGroupBox(get_text("grupo_traducao", self.idioma), self)
        translation_layout = QVBoxLayout()
        
        self.chk_translation = QCheckBox(get_text("ativar_traducao", self.idioma), self)
        self.chk_translation.setChecked(self.settings["translation_enabled"])
        translation_layout.addWidget(self.chk_translation)
        
        self.lbl_api_key = QLabel(get_text("label_api_key", self.idioma), self)
        self.txt_api_key = QLineEdit(self)
        self.txt_api_key.setText(self.settings.get("chatgpt_api_key", ""))
        
        self.lbl_target_lang = QLabel("Idioma de Tradução:", self)
        self.combo_target_lang = QComboBox(self)
        self.combo_target_lang.addItem("Português", "pt")
        self.combo_target_lang.addItem("Inglês", "en")
        self.combo_target_lang.addItem("Espanhol", "es")
        self.combo_target_lang.addItem("Francês", "fr")
        self.combo_target_lang.addItem("Alemão", "de")
        self.combo_target_lang.addItem("Italiano", "it")
        
        lang_code = self.settings.get("translation_target_lang", "pt")
        index = self.combo_target_lang.findData(lang_code)
        self.combo_target_lang.setCurrentIndex(index if index != -1 else 0)

        translation_layout.addWidget(self.lbl_target_lang)
        translation_layout.addWidget(self.combo_target_lang)
        translation_layout.addWidget(self.lbl_api_key)
        translation_layout.addWidget(self.txt_api_key)
        
        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)
        
        # Seção de Idioma
        lang_group = QGroupBox(get_text("grupo_idioma", self.idioma), self)
        lang_layout = QVBoxLayout()
        
        lang_layout.addWidget(QLabel(get_text("label_idioma", self.idioma), self))
        
        self.combo_idioma = QComboBox(self)
        self.combo_idioma.addItem("Português (BR)", "pt_BR")
        self.combo_idioma.addItem("English (US)", "en_US")
        self.combo_idioma.addItem("Español (ES)", "es_ES")
        self.combo_idioma.setCurrentText(
            "Português (BR)" if self.settings["language"] == "pt_BR" else
            "English (US)" if self.settings["language"] == "en_US" else
            "Español (ES)"
        )
        lang_layout.addWidget(self.combo_idioma)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Seção de Tema
        theme_group = QGroupBox(get_text("grupo_aparencia", self.idioma), self)
        theme_layout = QVBoxLayout()
        
        theme_layout.addWidget(QLabel(get_text("label_tema", self.idioma), self))
        
        theme_apply_layout = QHBoxLayout()
        self.combo_theme = QComboBox(self)
        self.combo_theme.addItems(THEMES.keys())
        self.combo_theme.setCurrentText(self.settings.get("theme", "Claro"))
        theme_apply_layout.addWidget(self.combo_theme)
        
        self.btn_apply = QPushButton(get_text("btn_aplicar", self.idioma), self)
        self.btn_apply.clicked.connect(self.apply_theme)
        theme_apply_layout.addWidget(self.btn_apply)
        theme_apply_layout.addStretch()
        
        theme_layout.addLayout(theme_apply_layout)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Indicador de status
        self.status_label = QLabel("Status: Verificando...", self)
        layout.addWidget(self.status_label)
        self.check_connection()
        
        # Botões
        btn_layout = QHBoxLayout()
        self.btn_salvar = QPushButton(get_text("btn_salvar", self.idioma), self)
        self.btn_cancelar = QPushButton(get_text("btn_cancelar", self.idioma), self)
        
        self.btn_salvar.clicked.connect(self.save_and_close)
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

    def save_and_close(self):
        """Salva configurações incluindo idioma e tema"""
        self.settings["translation_enabled"] = self.chk_translation.isChecked()
        self.settings["chatgpt_api_key"] = self.txt_api_key.text().strip()
        self.settings["translation_target_lang"] = self.combo_target_lang.currentData()
        
        lang_map = {
            "Português (BR)": "pt_BR",
            "English (US)": "en_US",
            "Español (ES)": "es_ES"
        }
        self.settings["language"] = lang_map.get(self.combo_idioma.currentText(), "pt_BR")
        
        self.settings["theme"] = self.combo_theme.currentText()
        
        save_settings(self.settings)
        self.accept()

    def apply_theme(self):
        """Aplica o tema sem fechar o diálogo"""
        app = QApplication.instance()
        if app:
            aplicar_tema(app, self.combo_theme.currentText())

    def check_connection(self):
        """Verifica o status da conexão com a internet"""
        try:
            requests.get("https://www.google.com", timeout=3)
            self.status_label.setText(get_text("status_online", self.idioma))
            self.status_label.setStyleSheet("color: green")
        except:
            self.status_label.setText(get_text("status_offline", self.idioma))
            self.status_label.setStyleSheet("color: red")

def translate_with_chatgpt(text, api_key, target_lang="pt"):
    """Translate using ChatGPT API"""
    try:
        if not api_key:
            print("ChatGPT: Nenhuma chave API fornecida.")
            return None
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        prompt = f"Translate the following text to {target_lang}: {text}"
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        print("ChatGPT: Enviando requisição para a API...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print("ChatGPT: Tradução bem-sucedida.")
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            print(f"ChatGPT: Erro na API - Status code: {response.status_code}, Mensagem: {response.text}")
            return None
    except Exception as e:
        print(f"ChatGPT: Falha na requisição - Erro: {str(e)}")
        return None

def translate_with_deepl(text, target_lang="pt"):
    """Translate using DeepL API with fixed key"""
    try:
        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}"}
        data = {
            "text": [text],
            "target_lang": target_lang.upper()
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['translations'][0]['text']
        elif response.status_code == 456:
            print("DeepL quota exceeded")
            return None
        else:
            print(f"DeepL error: Status code {response.status_code}")
    except Exception as e:
        print(f"DeepL error: {str(e)}")
    return None

def translate_with_google(text, target_lang="pt"):
    """Fallback using Google Translate"""
    try:
        from urllib.parse import quote
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={quote(text)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()[0][0][0]
        else:
            print(f"Google Translate error: Status code {response.status_code}")
    except Exception as e:
        print(f"Google Translate error: {str(e)}")
    return None

def get_active_translation_service():
    """Determina qual serviço de tradução está ativo com base na prioridade e disponibilidade"""
    settings = load_settings()
    if not settings.get("translation_enabled", False):
        return "None"

    # Texto de teste para verificar disponibilidade
    test_text = "Hello"
    target_lang = settings.get("translation_target_lang", "pt")

    # 1. Tenta ChatGPT se houver chave
    chatgpt_api_key = settings.get("chatgpt_api_key", "")
    if chatgpt_api_key:
        translated = translate_with_chatgpt(test_text, chatgpt_api_key, target_lang)
        if translated:
            return "ChatGPT"

    # 2. Tenta DeepL
    translated = translate_with_deepl(test_text, target_lang)
    if translated:
        return "DeepL"

    # 3. Tenta Google Translate
    translated = translate_with_google(test_text, target_lang)
    if translated:
        return "Google"

    return "None"

def traduzir_texto_automaticamente(texto_original: str, parent_window=None) -> tuple:
    """Main translation function with fallback, returns (translated_text, service)"""
    if not texto_original.strip():
        return texto_original, "None"
        
    settings = load_settings()
    if not settings.get("translation_enabled", False):
        if parent_window:
            QMessageBox.information(
                parent_window,
                get_text("msg_traducao_desativada", settings.get("language", "pt_BR")),
                get_text("msg_traducao_desativada", settings.get("language", "pt_BR"))
            )
        return texto_original, "None"
    
    target_lang = settings.get("translation_target_lang", "pt")
    translated = None
    service_used = "None"
    
    # 1. Tenta ChatGPT se houver chave
    chatgpt_api_key = settings.get("chatgpt_api_key", "")
    if chatgpt_api_key:
        translated = translate_with_chatgpt(texto_original, chatgpt_api_key, target_lang)
        if translated:
            service_used = "ChatGPT"
    
    # 2. Se ChatGPT falhar ou não houver chave, tenta DeepL
    if not translated:
        translated = translate_with_deepl(texto_original, target_lang)
        if translated:
            service_used = "DeepL"
    
    # 3. Se DeepL falhar ou atingir limite, usa Google Translate
    if not translated:
        translated = translate_with_google(texto_original, target_lang)
        if translated:
            service_used = "Google"
    
    if translated:
        return translated, service_used
    
    if parent_window:
        QMessageBox.warning(
            parent_window,
            get_text("msg_erro_traducao", settings.get("language", "pt_BR")),
            get_text("msg_erro_traducao", settings.get("language", "pt_BR"))
        )
    return texto_original, "None"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = load_settings()
    aplicar_tema(app, settings.get("theme", "Claro"))
    dialog = ConfigDialog()
    dialog.exec()