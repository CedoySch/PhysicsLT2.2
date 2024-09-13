import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QMessageBox, QVBoxLayout, QHBoxLayout, QSizePolicy
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.axes = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def resizeEvent(self, event):
        super(MplCanvas, self).resizeEvent(event)
        self.adjust_plot_elements()

    def adjust_plot_elements(self):
        width, height = self.fig.get_size_inches() * self.fig.dpi
        scaling_factor = min(width, height) / 500

        self.axes.title.set_fontsize(12 * scaling_factor)
        self.axes.xaxis.label.set_fontsize(10 * scaling_factor)
        self.axes.yaxis.label.set_fontsize(10 * scaling_factor)
        self.axes.tick_params(axis='both', which='major', labelsize=8 * scaling_factor)

        if self.axes.get_legend():
            self.axes.legend(fontsize=8 * scaling_factor, loc=(1.01, 0.5))

        self.fig.tight_layout()
        self.draw()


class ProjectileApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Визуализация Баллистического Движения')
        self.setGeometry(100, 0, 1200, 800)

        self.initUI()

    def initUI(self):
        label_h0 = QLabel('Начальная высота (м)')
        self.input_h0 = QLineEdit()
        self.input_h0.setPlaceholderText('Пример: 0')

        label_v0 = QLabel('Начальную скорость (м/с)')
        self.input_v0 = QLineEdit()
        self.input_v0.setPlaceholderText('Пример: 50')

        label_angle = QLabel('Угол запуска (°)')
        self.input_angle = QLineEdit()
        self.input_angle.setPlaceholderText('Пример: 45')

        self.button_plotting = QPushButton('Построить графики')
        self.button_plotting.clicked.connect(self.plot_graphs)

        grid = QGridLayout()
        grid.addWidget(label_h0, 0, 0)
        grid.addWidget(self.input_h0, 0, 1)
        grid.addWidget(label_v0, 1, 0)
        grid.addWidget(self.input_v0, 1, 1)
        grid.addWidget(label_angle, 2, 0)
        grid.addWidget(self.input_angle, 2, 1)
        grid.addWidget(self.button_plotting, 3, 0, 1, 2)

        self.canvas_trajectory = MplCanvas(self)
        self.canvas_speed = MplCanvas(self)
        self.canvas_coord = MplCanvas(self)

        layout_graphs = QVBoxLayout()
        layout_graphs.addWidget(QLabel('Траектория'))
        layout_graphs.addWidget(self.canvas_trajectory)

        layout_graphs.addWidget(QLabel('Скорость от времени'))
        layout_graphs.addWidget(self.canvas_speed)

        layout_graphs.addWidget(QLabel('Координаты от времени'))
        layout_graphs.addWidget(self.canvas_coord)

        layout_main = QHBoxLayout()
        layout_main.addLayout(grid, 1)
        layout_main.addLayout(layout_graphs, 3)

        self.setLayout(layout_main)

    def plot_graphs(self):
        try:
            h0 = float(self.input_h0.text())
            v0 = float(self.input_v0.text())
            angle = float(self.input_angle.text())
        except ValueError:
            QMessageBox.warning(self, 'Ввод данных', 'Введите корректные числовые значения')
            return

        theta = np.radians(angle)
        v0x = v0 * np.cos(theta)
        v0y = v0 * np.sin(theta)
        g = 9.81

        a = 0.5 * g
        b = -v0y
        c = -h0
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            QMessageBox.warning(self, "Вычисления", "Нет реальных решений для заданных параметров.")
            return

        t_flight = (-b + np.sqrt(discriminant)) / (2 * a)
        t = np.linspace(0, t_flight, num=500)
        x = v0x * t
        y = h0 + v0y * t - 0.5 * g * t ** 2
        vx = np.full_like(t, v0x)
        vy = v0y - g * t
        v = np.sqrt(vx ** 2 + vy ** 2)

        self.canvas_trajectory.axes.cla()
        self.canvas_speed.axes.cla()
        self.canvas_coord.axes.cla()

        self.canvas_trajectory.axes.plot(x, y, label='Траектория', color='blue')
        self.canvas_trajectory.axes.set_xlabel('X (м)')
        self.canvas_trajectory.axes.set_ylabel('Y (м)')
        self.canvas_trajectory.axes.legend(loc=(1.01, 0.5))
        self.canvas_trajectory.axes.grid(True)
        self.canvas_trajectory.fig.tight_layout()
        self.canvas_trajectory.draw()

        self.canvas_speed.axes.plot(t, v, label='Скорость', color='green')
        self.canvas_speed.axes.set_xlabel('Время (с)')
        self.canvas_speed.axes.set_ylabel('Скорость (м/с)')
        self.canvas_speed.axes.legend(loc=(1.01, 0.5))
        self.canvas_speed.axes.grid(True)
        self.canvas_speed.fig.tight_layout()
        self.canvas_speed.draw()

        self.canvas_coord.axes.plot(t, x, label='X (м)', color='red')
        self.canvas_coord.axes.plot(t, y, label='Y (м)', color='orange')
        self.canvas_coord.axes.set_xlabel('Время (с)')
        self.canvas_coord.axes.set_ylabel('Координаты (м)')
        self.canvas_coord.axes.legend(loc=(1.01, 0.5))
        self.canvas_coord.axes.grid(True)
        self.canvas_coord.fig.tight_layout()
        self.canvas_coord.draw()


def main():
    app = QApplication(sys.argv)
    window = ProjectileApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
