from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
)

import config
from core.system_monitor import SystemMonitor


class MonitorWidget(QWidget):
    def __init__(self, monitor: SystemMonitor, parent=None):
        super().__init__(parent)
        self.monitor = monitor
        self._setup_ui()
        self.monitor.stats_updated.connect(self._update_stats)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("System Monitor")
        title.setStyleSheet(f"color: {config.COLORS['text']}; font-size: 16px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedWidth(80)
        self.refresh_btn.clicked.connect(self.monitor.update)
        header.addWidget(self.refresh_btn)
        layout.addLayout(header)

        self.cpu_label = QLabel("CPU")
        self.cpu_label.setStyleSheet(f"color: {config.COLORS['text']};")
        layout.addWidget(self.cpu_label)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(True)
        self.cpu_bar.setFormat("%p%")
        layout.addWidget(self.cpu_bar)

        self.ram_label = QLabel("RAM")
        self.ram_label.setStyleSheet(f"color: {config.COLORS['text']};")
        layout.addWidget(self.ram_label)

        self.ram_bar = QProgressBar()
        self.ram_bar.setTextVisible(True)
        self.ram_bar.setFormat("%p%")
        layout.addWidget(self.ram_bar)

        self.ram_detail = QLabel("")
        self.ram_detail.setStyleSheet(f"color: {config.COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.ram_detail)

        self.disk_label = QLabel("Disk C:")
        self.disk_label.setStyleSheet(f"color: {config.COLORS['text']};")
        layout.addWidget(self.disk_label)

        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(True)
        self.disk_bar.setFormat("%p%")
        layout.addWidget(self.disk_bar)

        self.battery_label = QLabel("Battery")
        self.battery_label.setStyleSheet(f"color: {config.COLORS['text']};")
        layout.addWidget(self.battery_label)

        self.battery_bar = QProgressBar()
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat("%p%")
        layout.addWidget(self.battery_bar)

        self.battery_detail = QLabel("")
        self.battery_detail.setStyleSheet(f"color: {config.COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.battery_detail)

        net_header = QLabel("Network")
        net_header.setStyleSheet(f"color: {config.COLORS['text']}; font-weight: bold; margin-top: 8px;")
        layout.addWidget(net_header)

        self.net_label = QLabel("Up: 0 B/s  |  Down: 0 B/s")
        self.net_label.setStyleSheet(f"color: {config.COLORS['text_secondary']};")
        layout.addWidget(self.net_label)

        proc_header = QLabel("Top Processes")
        proc_header.setStyleSheet(f"color: {config.COLORS['text']}; font-weight: bold; margin-top: 8px;")
        layout.addWidget(proc_header)

        self.proc_table = QTableWidget(0, 4)
        self.proc_table.setHorizontalHeaderLabels(["PID", "Name", "CPU%", "RAM MB"])
        self.proc_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.proc_table.verticalHeader().setVisible(False)
        self.proc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.proc_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.proc_table.setMaximumHeight(150)
        self.proc_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {config.COLORS['surface']};
                color: {config.COLORS['text']};
                border: none;
                gridline-color: rgba(255, 255, 255, 0.1);
            }}
            QHeaderView::section {{
                background-color: {config.COLORS['surface']};
                color: {config.COLORS['text_secondary']};
                border: none;
                padding: 4px;
            }}
        """)
        layout.addWidget(self.proc_table)

        layout.addStretch()

    def _update_stats(self, stats: dict):
        cpu = stats.get("cpu", {})
        cpu_pct = cpu.get("percent", 0)
        self.cpu_bar.setValue(int(cpu_pct))
        self._color_bar(self.cpu_bar, cpu_pct, [50, 80])
        self.cpu_label.setText(f"CPU ({cpu.get('count', 0)} cores)")

        mem = stats.get("memory", {})
        mem_pct = mem.get("percent", 0)
        self.ram_bar.setValue(int(mem_pct))
        self._color_bar(self.ram_bar, mem_pct, [60, 85])
        self.ram_label.setText("RAM")
        self.ram_detail.setText(f"{mem.get('used_gb', 0)} / {mem.get('total_gb', 0)} GB")

        disk = stats.get("disk", {})
        disk_pct = disk.get("percent", 0)
        self.disk_bar.setValue(int(disk_pct))
        self._color_bar(self.disk_bar, disk_pct, [70, 90])
        self.disk_label.setText(f"Disk C: ({disk.get('free_gb', 0)} GB free)")

        bat = stats.get("battery", {})
        bat_pct = bat.get("percent", 0)
        self.battery_bar.setValue(int(bat_pct))
        self._color_bar(self.battery_bar, bat_pct, [50, 20])
        if bat.get("power_plugged"):
            self.battery_detail.setText("Charging")
        else:
            self.battery_detail.setText("On battery")

        net = stats.get("network", {})
        up = self._format_bytes(net.get("speed_up", 0))
        down = self._format_bytes(net.get("speed_down", 0))
        self.net_label.setText(f"Up: {up}/s  |  Down: {down}/s")

        procs = stats.get("processes", [])
        self.proc_table.setRowCount(len(procs))
        for i, proc in enumerate(procs):
            self.proc_table.setItem(i, 0, QTableWidgetItem(str(proc["pid"])))
            self.proc_table.setItem(i, 1, QTableWidgetItem(proc["name"]))
            self.proc_table.setItem(i, 2, QTableWidgetItem(f"{proc['cpu']:.1f}"))
            self.proc_table.setItem(i, 3, QTableWidgetItem(f"{proc['memory']:.0f}"))

    def _color_bar(self, bar: QProgressBar, value: float, thresholds: list):
        if value > thresholds[1]:
            color = config.COLORS["error"]
        elif value > thresholds[0]:
            color = config.COLORS["warning"]
        else:
            color = config.COLORS["success"]
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {config.COLORS['surface']};
                border: none;
                border-radius: 4px;
                height: 16px;
                text-align: center;
                color: white;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    def _format_bytes(self, b: float) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"
