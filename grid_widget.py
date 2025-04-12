from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QWheelEvent, QMouseEvent


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.cell_size = 20
        self.scale_factor = 1.0
        self.offset = QPoint(0, 0)
        self.dragging_widget = None
        self.drag_offset = QPoint()
        self.snap_to_grid = False  # Desativado para movimento pixel a pixel
        self.parent_window = parent
        self.alignment_lines = []  # Lista para armazenar linhas de alinhamento temporárias

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Desenha a grade
        pen = QPen(QColor(220, 220, 220))
        painter.setPen(pen)
        grid_size = int(self.cell_size * self.scale_factor)
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)

        # Desenha as linhas de alinhamento (se houver)
        if self.alignment_lines:
            pen = QPen(QColor(255, 0, 0, 150))  # Vermelho com transparência
            pen.setWidth(2)
            painter.setPen(pen)
            for line in self.alignment_lines:
                if line["type"] == "horizontal":
                    y = line["position"]
                    painter.drawLine(0, y, self.width(), y)
                elif line["type"] == "vertical":
                    x = line["position"]
                    painter.drawLine(x, 0, x, self.height())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging_widget:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            local_pos = self.mapFromGlobal(new_pos)
            if self.snap_to_grid:
                grid_size = int(self.cell_size * self.scale_factor)
                local_pos.setX((local_pos.x() // grid_size) * grid_size)
                local_pos.setY((local_pos.y() // grid_size) * grid_size)
            self.dragging_widget.move(local_pos)
            self.update_status_from_widget(self.dragging_widget)
            self.update_alignment_lines()  # Atualiza as linhas de alinhamento
        else:
            x = int(event.position().x())
            y = int(event.position().y())
            if self.parent() and hasattr(self.parent(), 'statusBar'):
                self.parent().statusBar().showMessage(f"Mouse: X={x} Y={y}")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.scale_factor = 1.0
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            child = self.childAt(event.position().toPoint())
            if child and child != self:
                self.dragging_widget = child
                self.drag_offset = event.globalPosition().toPoint() - child.mapToGlobal(QPoint(0, 0))
                child.raise_()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging_widget:
            self.save_widget_position(self.dragging_widget)
            self.update_status_from_widget(self.dragging_widget)
            self.dragging_widget = None
            self.alignment_lines = []  # Limpa as linhas de alinhamento
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.1
        else:
            self.scale_factor /= 1.1
        self.scale_factor = max(0.2, min(5.0, self.scale_factor))
        self.update()

    def save_widget_position(self, widget):
        if hasattr(self.parent_window, 'save_settings'):
            name = widget.objectName()
            if name:
                settings = self.parent_window.load_settings()
                if "widget_positions" not in settings:
                    settings["widget_positions"] = {}
                settings["widget_positions"][name] = {
                    "x": widget.pos().x(),
                    "y": widget.pos().y()
                }
                self.parent_window.save_settings(settings)

    def load_widget_positions(self):
        if hasattr(self.parent_window, 'load_settings'):
            settings = self.parent_window.load_settings()
            positions = settings.get("widget_positions", {})
            for name, pos in positions.items():
                widget = self.findChild(QWidget, name)
                if widget:
                    widget.move(pos["x"], pos["y"])

    def update_status_from_widget(self, widget):
        name = widget.objectName() if widget.objectName() else "Desconhecido"
        pos = widget.pos()
        if self.parent() and hasattr(self.parent(), 'statusBar'):
            self.parent().statusBar().showMessage(f"Objeto: {name}, Posição {pos.x()}/{pos.y()}")

    def update_alignment_lines(self):
        """Detecta alinhamento com outros widgets e atualiza as linhas de alinhamento"""
        self.alignment_lines = []
        if not self.dragging_widget:
            return

        # Posição e dimensões do widget sendo movido
        moving_rect = self.dragging_widget.geometry()
        moving_x = moving_rect.x()
        moving_y = moving_rect.y()
        moving_right = moving_rect.right()
        moving_bottom = moving_rect.bottom()
        moving_center_x = moving_rect.center().x()
        moving_center_y = moving_rect.center().y()

        # Tolerância para considerar alinhamento (em pixels)
        tolerance = 5

        # Verifica alinhamento com outros widgets
        for child in self.children():
            if child == self or child == self.dragging_widget or not isinstance(child, QWidget):
                continue

            if not child.isVisible():
                continue

            rect = child.geometry()
            x = rect.x()
            y = rect.y()
            right = rect.right()
            bottom = rect.bottom()
            center_x = rect.center().x()
            center_y = rect.center().y()

            # Alinhamento vertical (esquerda, centro, direita)
            if abs(moving_x - x) <= tolerance:
                self.alignment_lines.append({"type": "vertical", "position": x})
                self.dragging_widget.move(x, moving_y)
            elif abs(moving_center_x - center_x) <= tolerance:
                self.alignment_lines.append({"type": "vertical", "position": center_x})
                self.dragging_widget.move(center_x - moving_rect.width() // 2, moving_y)
            elif abs(moving_right - right) <= tolerance:
                self.alignment_lines.append({"type": "vertical", "position": right})
                self.dragging_widget.move(right - moving_rect.width(), moving_y)

            # Alinhamento horizontal (topo, centro, base)
            if abs(moving_y - y) <= tolerance:
                self.alignment_lines.append({"type": "horizontal", "position": y})
                self.dragging_widget.move(moving_x, y)
            elif abs(moving_center_y - center_y) <= tolerance:
                self.alignment_lines.append({"type": "horizontal", "position": center_y})
                self.dragging_widget.move(moving_x, center_y - moving_rect.height() // 2)
            elif abs(moving_bottom - bottom) <= tolerance:
                self.alignment_lines.append({"type": "horizontal", "position": bottom})
                self.dragging_widget.move(moving_x, bottom - moving_rect.height())

        self.update()  # Redesenha as linhas de alinhamento