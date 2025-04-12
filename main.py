import sys
import json
import multiprocessing
import os
import shutil
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QGroupBox, QWidget, QToolBar, QMenu, QLabel, QTextEdit, QPushButton,
    QMessageBox, QHBoxLayout, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt, QRect, QPoint

from grid_widget import GridWidget
from config.config import ConfigDialog, traduzir_texto_automaticamente, load_settings, aplicar_tema, get_text, get_active_translation_service
from preview_renderer import render_preview, criar_preview_widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.idioma = self.settings["language"]
        self.setWindowTitle(get_text("main_title", self.idioma))
        self.setGeometry(100, 100, 1025, 655)

        self.traducao_ativa = self.settings["translation_enabled"]
        self.dados_json = {}
        self.scene_items = []
        self.current_item_index = 0
        self.current_appear_time = 0
        self.current_duration = 0

        self.total_items = 0
        self.translated_items = 0
        self.input_file = None

        self.initUI()
        aplicar_tema(QApplication.instance(), self.settings["theme"])

    def initUI(self):
        self.setStyleSheet("QWidget { font-size: 14px; }")

        self.toolbar = QToolBar(get_text("menu_arquivo", self.idioma), self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.open_action = QAction(get_text("menu_abrir", self.idioma), self)
        self.open_action.triggered.connect(self.load_json_file)
        self.toolbar.addAction(self.open_action)

        self.options_menu = QMenu(get_text("menu_opcoes", self.idioma), self)
        self.config_action = QAction(get_text("config_title", self.idioma), self)
        self.config_action.triggered.connect(self.open_config)
        self.options_menu.addAction(self.config_action)

        self.options_button = QAction(get_text("menu_opcoes", self.idioma), self)
        self.options_button.triggered.connect(self.show_options_menu)
        self.toolbar.addAction(self.options_button)

        self.status = self.statusBar()

        self.position_label = QLabel("Posição: 0,0")
        self.progress_label = QLabel("Progresso: 0% (0/0)")
        self.translation_status_label = QLabel("Tradutor automático: Off")
        self.dimensions_label = QLabel("Dimensões: 1025x655")
        
        self.status.addWidget(self.position_label)
        self.status.addWidget(self.progress_label)
        self.status.addPermanentWidget(self.translation_status_label)
        self.status.addPermanentWidget(self.dimensions_label)


        self.grid = GridWidget(self)
        self.setCentralWidget(self.grid)

        self.groupbox = QGroupBox(get_text("grupo_textos", self.idioma), self.grid)
        self.groupbox.setGeometry(QRect(11, 7, 200, 450))
        self.groupbox.setObjectName("BlocosDeTexto")
        layout = QVBoxLayout(self.groupbox)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(4)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree_widget)

        self.frame_original = QGroupBox(get_text("texto_original", self.idioma), self.grid)
        self.frame_original.setGeometry(QRect(230, 7, 450, 210))
        self.frame_original.setObjectName("TextoOriginal")
        layout_original = QVBoxLayout(self.frame_original)
        self.txt_original = QTextEdit()
        self.txt_original.setReadOnly(True)
        layout_original.addWidget(self.txt_original)

        self.frame_editavel = QGroupBox(get_text("texto_editavel", self.idioma), self.grid)
        self.frame_editavel.setGeometry(QRect(230, 223, 450, 210))
        self.frame_editavel.setObjectName("TextoEditavel")
        layout_editavel = QVBoxLayout(self.frame_editavel)
        self.txt_editavel = QTextEdit()
        self.txt_editavel.textChanged.connect(self.on_text_changed)
        self.txt_editavel.cursorPositionChanged.connect(self.update_position_status)
        layout_editavel.addWidget(self.txt_editavel)

        self.frame_preview = QGroupBox("Prévia da Tradução", self.grid)
        self.frame_preview.setGeometry(QRect(692, 10, 320, 240))
        self.frame_preview.setObjectName("PreviaDaTraducao")
        layout_preview = QVBoxLayout(self.frame_preview)
        layout_preview.setContentsMargins(3, 3, 3, 3)
        self.txtboxpreview = criar_preview_widget()
        layout_preview.addWidget(self.txtboxpreview)

        button_width = 120
        button_height = 30
        spacing = 10
        start_x = 230
        start_y = 433

        self.btn_voltar = QPushButton(get_text("btn_voltar", self.idioma), self.grid)
        self.btn_voltar.setGeometry(QRect(start_x, start_y, button_width, button_height))
        self.btn_voltar.clicked.connect(self.voltar_texto)

        self.btn_avancar = QPushButton(get_text("btn_avancar", self.idioma), self.grid)
        self.btn_avancar.setGeometry(QRect(start_x + button_width + spacing, start_y, button_width, button_height))
        self.btn_avancar.clicked.connect(self.avancar_texto)

        self.btn_limpar = QPushButton(get_text("btn_limpar", self.idioma), self.grid)
        self.btn_limpar.setGeometry(QRect(start_x + 2 * (button_width + spacing), start_y, button_width, button_height))
        self.btn_limpar.clicked.connect(self.limpar_texto)

        self.btn_traduzir = QPushButton(get_text("btn_traducao_automatica", self.idioma), self.grid)
        self.btn_traduzir.setGeometry(QRect(start_x + 3 * (button_width + spacing), start_y, button_width, button_height))
        self.btn_traduzir.clicked.connect(self.traduzir_automaticamente)

        button_style = """
            QPushButton {
                border-radius: 10px;
                border: 1px solid #555;
                padding: 5px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #777777;
            }
        """
        for btn in [self.btn_voltar, self.btn_avancar, self.btn_limpar, self.btn_traduzir]:
            btn.setStyleSheet(button_style)

        self.frame_timing = QGroupBox("Controle de Tempo", self.grid)
        self.frame_timing.setGeometry(QRect(692, 260, 320, 150))
        layout_timing = QVBoxLayout(self.frame_timing)
        layout_timing.setContentsMargins(10, 10, 10, 10)
        layout_timing.setSpacing(5)

        appear_layout = QHBoxLayout()
        self.label_appear = QLabel("Appear Time: 0 ms", self.frame_timing)
        self.slider_appear = QSlider(Qt.Orientation.Horizontal, self.frame_timing)
        self.slider_appear.setMinimum(0)
        self.slider_appear.setMaximum(1000)
        self.slider_appear.setTickInterval(100)
        self.slider_appear.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_appear.setFixedWidth(150)
        self.slider_appear.valueChanged.connect(self.on_slider_appear_changed)
        self.slider_appear.setEnabled(False)
        self.checkbox_appear = QCheckBox("", self.frame_timing)
        self.checkbox_appear.toggled.connect(self.toggle_appear_slider)
        appear_layout.addWidget(self.label_appear)
        appear_layout.addWidget(self.slider_appear)
        appear_layout.addWidget(self.checkbox_appear)
        layout_timing.addLayout(appear_layout)

        duration_layout = QHBoxLayout()
        self.label_duration = QLabel("Duration: 0 ms", self.frame_timing)
        self.slider_duration = QSlider(Qt.Orientation.Horizontal, self.frame_timing)
        self.slider_duration.setMinimum(0)
        self.slider_duration.setMaximum(1000)
        self.slider_duration.setTickInterval(100)
        self.slider_duration.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_duration.setFixedWidth(150)
        self.slider_duration.valueChanged.connect(self.on_slider_duration_changed)
        self.slider_duration.setEnabled(False)
        self.checkbox_duration = QCheckBox("", self.frame_timing)
        self.checkbox_duration.toggled.connect(self.toggle_duration_slider)
        duration_layout.addWidget(self.label_duration)
        duration_layout.addWidget(self.slider_duration)
        duration_layout.addWidget(self.checkbox_duration)
        layout_timing.addLayout(duration_layout)

        self.grid.load_widget_positions()
        self.update_button_states()
        self.update_translation_status()

    def on_text_changed(self):
        render_preview(self.txt_editavel, self.txtboxpreview)
        self.update_json_text()
        self.update_progress()
        if self.translated_items == self.total_items:
            self.save_file()

    def update_json_text(self):
        if not self.scene_items or not self.dados_json:
            return

        item = self.scene_items[self.current_item_index]
        bloco, cena_id = item.data(0, Qt.ItemDataRole.UserRole)
        if bloco in self.dados_json and cena_id in self.dados_json[bloco]:
            self.dados_json[bloco][cena_id]["text"] = self.txt_editavel.toPlainText()
            if "original_text" not in self.dados_json[bloco][cena_id]:
                self.dados_json[bloco][cena_id]["original_text"] = self.dados_json[bloco][cena_id].get("text", "")

    def update_progress(self):
        if not self.scene_items or not self.dados_json:
            self.progress_label.setText("Progresso: 0% (0/0)")
            return

        self.translated_items = 0
        for item in self.scene_items:
            bloco, cena_id = item.data(0, Qt.ItemDataRole.UserRole)
            if bloco in self.dados_json and cena_id in self.dados_json[bloco]:
                original_text = self.dados_json[bloco][cena_id].get("original_text", "")
                current_text = self.dados_json[bloco][cena_id].get("text", "")
                if current_text and current_text != original_text:
                    self.translated_items += 1

        percentage = (self.translated_items / self.total_items) * 100 if self.total_items > 0 else 0
        self.progress_label.setText(f"Progresso: {percentage:.1f}% ({self.translated_items}/{self.total_items})")

    def save_file(self):
        if not self.input_file or not self.dados_json:
            return

        if os.path.exists(self.input_file):
            backup_file = self.input_file + ".bkp"
            shutil.copy2(self.input_file, backup_file)

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(self.dados_json, f, ensure_ascii=False, indent=2)

    def toggle_appear_slider(self, checked):
        self.slider_appear.setEnabled(checked)
        if not checked:
            self.slider_appear.setValue(self.current_appear_time)
            self.update_json_timing("appear_time", self.current_appear_time)

    def toggle_duration_slider(self, checked):
        self.slider_duration.setEnabled(checked)
        if not checked:
            self.slider_duration.setValue(self.current_duration)
            self.update_json_timing("duration", self.current_duration)

    def on_slider_appear_changed(self, value):
        if self.checkbox_appear.isChecked():
            self.current_appear_time = value
            self.label_appear.setText(f"Appear Time: {value} ms")
            self.update_json_timing("appear_time", value)

    def on_slider_duration_changed(self, value):
        if self.checkbox_duration.isChecked():
            self.current_duration = value
            self.label_duration.setText(f"Duration: {value} ms")
            self.update_json_timing("duration", value)

    def update_timing_display(self):
        self.slider_appear.setValue(self.current_appear_time)
        self.label_appear.setText(f"Appear Time: {self.current_appear_time} ms")
        self.slider_duration.setValue(self.current_duration)
        self.label_duration.setText(f"Duration: {self.current_duration} ms")

    def update_json_timing(self, key, value):
        if not self.scene_items or not self.dados_json:
            return

        item = self.scene_items[self.current_item_index]
        bloco, cena_id = item.data(0, Qt.ItemDataRole.UserRole)
        if bloco in self.dados_json and cena_id in self.dados_json[bloco]:
            self.dados_json[bloco][cena_id][key] = value

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.width()
        height = self.height()
        self.dimensions_label.setText(f"Dimensões: {width}x{height}")

    def show_options_menu(self):
        self.options_menu.exec(self.mapToGlobal(QPoint(0, self.toolbar.height())))

    def update_ui_texts(self):
        self.setWindowTitle(get_text("main_title", self.idioma))
        self.toolbar.setWindowTitle(get_text("menu_arquivo", self.idioma))
        self.open_action.setText(get_text("menu_abrir", self.idioma))
        self.options_menu.setTitle(get_text("menu_opcoes", self.idioma))
        self.config_action.setText(get_text("config_title", self.idioma))
        self.options_button.setText(get_text("menu_opcoes", self.idioma))
        self.groupbox.setTitle(get_text("grupo_textos", self.idioma))
        self.frame_original.setTitle(get_text("texto_original", self.idioma))
        self.frame_editavel.setTitle(get_text("texto_editavel", self.idioma))
        self.btn_voltar.setText(get_text("btn_voltar", self.idioma))
        self.btn_avancar.setText(get_text("btn_avancar", self.idioma))
        self.btn_limpar.setText(get_text("btn_limpar", self.idioma))
        self.btn_traduzir.setText(get_text("btn_traducao_automatica", self.idioma))
        self.frame_preview.setTitle("Prévia da Tradução")

    def update_translation_status(self):
        settings = load_settings()
        if not settings.get("translation_enabled", False):
            self.translation_status_label.setText("Tradutor automático: Off")
        else:
            active_service = get_active_translation_service()
            self.translation_status_label.setText(f"Tradutor automático: On ({active_service})")

    def update_position_status(self):
        cursor = self.txt_editavel.textCursor()
        x = cursor.blockNumber() + 1
        y = cursor.columnNumber() + 1
        self.position_label.setText(f"Posição: {x},{y}")

    def update_status_conexao(self, online):
        pass

    def update_button_states(self):
        self.btn_voltar.setEnabled(self.current_item_index > 0)
        self.btn_avancar.setEnabled(self.current_item_index < len(self.scene_items) - 1)

    def open_config(self):
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.settings = load_settings()
            self.idioma = self.settings.get("language", "pt_BR")
            aplicar_tema(QApplication.instance(), self.settings.get("theme", "Claro"))
            self.traducao_ativa = self.settings.get("translation_enabled", False)
            self.update_translation_status()
            self.update_ui_texts()
            render_preview(self.txt_editavel, self.txtboxpreview)

    def load_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo JSON", "", "Arquivos JSON (*.json)")
        if file_path:
            self.input_file = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                self.dados_json = json.load(f)

            for bloco, cenas in self.dados_json.items():
                if isinstance(cenas, dict):
                    for cena_id, cena_conteudo in cenas.items():
                        if "original_text" not in cena_conteudo:
                            cena_conteudo["original_text"] = cena_conteudo.get("text", "")

            self.populate_tree_widget(self.dados_json)

    def populate_tree_widget(self, data):
        self.tree_widget.clear()
        self.scene_items = []
        self.tree_widget.setStyleSheet("QTreeWidget { font-size: 14px; }")

        for bloco, cenas in data.items():
            bloco_item = QTreeWidgetItem([bloco])
            if isinstance(cenas, dict):
                for cena_id, cena_conteudo in cenas.items():
                    item = QTreeWidgetItem([f"Cena {cena_id}"])
                    item.setData(0, Qt.ItemDataRole.UserRole, (bloco, cena_id))
                    bloco_item.addChild(item)
                    self.scene_items.append(item)
            self.tree_widget.addTopLevelItem(bloco_item)

        self.total_items = len(self.scene_items)
        self.translated_items = 0
        self.update_progress()

        if self.scene_items:
            self.exibir_texto(0)

    def exibir_texto(self, index):
        if not self.scene_items:
            return

        for i in range(self.tree_widget.topLevelItemCount()):
            top_item = self.tree_widget.topLevelItem(i)
            for j in range(top_item.childCount()):
                child = top_item.child(j)
                font = child.font(0)
                font.setBold(False)
                child.setFont(0, font)

        self.current_item_index = max(0, min(index, len(self.scene_items) - 1))
        item = self.scene_items[self.current_item_index]

        font = item.font(0)
        font.setBold(True)
        item.setFont(0, font)

        self.tree_widget.setCurrentItem(item)
        self.tree_widget.scrollToItem(item)

        bloco, cena_id = item.data(0, Qt.ItemDataRole.UserRole)
        texto_obj = self.dados_json.get(bloco, {}).get(cena_id, {})
        texto = texto_obj.get("original_text", "")
        self.current_appear_time = texto_obj.get("appear_time", 0)
        self.current_duration = texto_obj.get("duration", 0)

        self.txt_original.setText(texto)
        self.txt_editavel.setText(texto_obj.get("text", texto))
        render_preview(self.txt_editavel, self.txtboxpreview)
        self.update_button_states()
        self.update_timing_display()
        self.update_progress()

    def on_item_clicked(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            bloco, cena_id = data
            texto_obj = self.dados_json.get(bloco, {}).get(cena_id, {})
            texto = texto_obj.get("original_text", "")
            self.current_appear_time = texto_obj.get("appear_time", 0)
            self.current_duration = texto_obj.get("duration", 0)

            self.txt_original.setText(texto)
            self.txt_editavel.setText(texto_obj.get("text", texto))
            render_preview(self.txt_editavel, self.txtboxpreview)

            for i, it in enumerate(self.scene_items):
                if it == item:
                    self.current_item_index = i
                    font = it.font(0)
                    font.setBold(True)
                    it.setFont(0, font)
                    break
            self.update_button_states()
            self.update_timing_display()
            self.update_progress()

    def voltar_texto(self):
        if self.current_item_index > 0:
            self.save_file()
            self.exibir_texto(self.current_item_index - 1)

    def avancar_texto(self):
        if self.current_item_index < len(self.scene_items) - 1:
            self.save_file()
            self.exibir_texto(self.current_item_index + 1)

    def limpar_texto(self):
        texto_atual = self.txt_original.toPlainText()
        self.txt_editavel.setText(texto_atual)
        render_preview(self.txt_editavel, self.txtboxpreview)
        self.update_progress()

    def traduzir_automaticamente(self):
        current_settings = load_settings()
        if not current_settings.get("translation_enabled", False):
            self.status.showMessage(get_text("msg_traducao_desativada", self.idioma))
            QMessageBox.information(self, get_text("msg_traducao_desativada", self.idioma), get_text("msg_traducao_desativada", self.idioma))
            return

        texto = self.txt_original.toPlainText()
        if not texto.strip():
            return

        try:
            traducao, service = traduzir_texto_automaticamente(texto, self)
            if traducao:
                self.txt_editavel.setText(traducao)
                render_preview(self.txt_editavel, self.txtboxpreview)
                self.update_progress()
        except Exception as e:
            msg = f"{get_text('msg_erro_traducao', self.idioma)}: {str(e)}"
            self.status.showMessage(msg)
            QMessageBox.warning(self, get_text("msg_erro_traducao", self.idioma), msg)


def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    process = multiprocessing.Process(target=run_app)
    process.start()