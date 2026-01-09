"""Main GUI window for XDF Streamer."""

import threading
from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.lsl_streamer import LslStreamer
from ..core.stream_worker import StreamWorker
from ..core.xdf_loader import XdfLoader
from ..models.xdf_data import XdfData
from ..utils.validators import validate_stream


class MainWindow(QWidget):
    """Main application window."""

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize main window."""
        super().__init__(parent)
        self.setWindowTitle("XDF Streamer")
        self.setGeometry(100, 100, 1031, 647)

        # Core components
        self.xdf_loader = XdfLoader()
        self.lsl_streamer = LslStreamer()
        self.xdf_data: Optional[XdfData] = None

        # Threading
        self.stream_threads: List[threading.Thread] = []
        self.stop_event = threading.Event()
        self.outlets: List = []  # Keep references to outlets

        # State
        self.stream_ready = False
        self.is_streaming = False

        self._init_ui()

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Configuration group
        config_group = self._create_config_group()
        layout.addWidget(config_group)

        # Synthetic signal parameters group (initially hidden)
        self.synthetic_group = self._create_synthetic_group()
        layout.addWidget(self.synthetic_group)
        self.synthetic_group.hide()

        # Stream tree widgets
        self.xdf_tree = QTreeWidget()
        self.xdf_tree.setHeaderLabels(["Property", "Value"])
        self.xdf_tree.header().hide()
        self.xdf_tree.setColumnCount(2)
        self.xdf_tree.itemClicked.connect(self._on_tree_item_clicked)
        layout.addWidget(self.xdf_tree)

        self.random_tree = QTreeWidget()
        self.random_tree.setHeaderLabels(["Property", "Value"])
        self.random_tree.header().hide()
        self.random_tree.setColumnCount(2)
        self.random_tree.hide()
        layout.addWidget(self.random_tree)

        # Stream button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.stream_button = QPushButton("Stream")
        self.stream_button.setEnabled(False)
        self.stream_button.clicked.connect(self._on_stream_clicked)
        button_layout.addWidget(self.stream_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_config_group(self) -> QGroupBox:
        """Create configuration group box."""
        group = QGroupBox("Configuration")
        layout = QVBoxLayout()

        # File path row
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("File Path"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.textChanged.connect(self._on_file_path_changed)
        file_layout.addWidget(self.file_path_edit)
        self.browse_button = QPushButton("...")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        file_layout.addWidget(self.browse_button)
        self.load_button = QPushButton("Load")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._on_load_clicked)
        file_layout.addWidget(self.load_button)
        layout.addLayout(file_layout)

        # Sampling rate and random signal row
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Sampling Rate (Hz)"))
        self.sampling_rate_spin = QSpinBox()
        self.sampling_rate_spin.setMaximum(100000)
        self.sampling_rate_spin.setValue(10000)
        rate_layout.addWidget(self.sampling_rate_spin)
        rate_layout.addStretch()
        self.random_checkbox = QCheckBox("Generate Random Signals")
        self.random_checkbox.stateChanged.connect(self._on_random_checkbox_changed)
        rate_layout.addWidget(self.random_checkbox)
        layout.addLayout(rate_layout)

        group.setLayout(layout)
        return group

    def _create_synthetic_group(self) -> QGroupBox:
        """Create synthetic signal parameters group."""
        group = QGroupBox("Synthetic Signal Parameters")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Channel Count"))
        self.channel_count_spin = QSpinBox()
        self.channel_count_spin.setValue(32)
        self.channel_count_spin.setMaximum(1000)
        layout.addWidget(self.channel_count_spin)

        layout.addStretch()

        layout.addWidget(QLabel("Stream Name"))
        self.stream_name_edit = QLineEdit()
        self.stream_name_edit.setText("ActiChamp-0")
        layout.addWidget(self.stream_name_edit)

        layout.addStretch()

        layout.addWidget(QLabel("Stream Type"))
        self.stream_type_edit = QLineEdit()
        self.stream_type_edit.setText("EEG")
        layout.addWidget(self.stream_type_edit)

        layout.addStretch()

        layout.addWidget(QLabel("Channel Format"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["cf_float32", "cf_double64", "cf_string", "cf_int32", "cf_int16", "cf_int8", "cf_int64"])
        self.format_combo.setCurrentIndex(1)  # double64
        layout.addWidget(self.format_combo)

        group.setLayout(layout)
        return group

    def _on_file_path_changed(self, text: str):
        """Handle file path text change."""
        self.load_button.setEnabled(bool(text) and not self.is_streaming)

    def _on_browse_clicked(self):
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open XDF File", "", "XDF Files (*.xdf)")
        if file_path:
            self._clear_cache()
            self.file_path_edit.setText(file_path)
            self._on_load_clicked()

    def _on_load_clicked(self):
        """Handle load button click."""
        if self.load_button.text() == "Load":
            file_path = self.file_path_edit.text()
            if not file_path:
                return

            try:
                self.xdf_data = self.xdf_loader.load_xdf(file_path)
                self._populate_xdf_tree()
                self.load_button.setText("Unload")
                self.stream_button.setEnabled(True)
                self.stream_ready = False
            except FileNotFoundError:
                QMessageBox.warning(self, "XDF Streamer", f"Unable to find {file_path}\nPlease check your path")
            except Exception as e:
                QMessageBox.warning(self, "XDF Streamer", f"Error loading XDF file: {e}")
        else:
            self._clear_cache()

    def _on_random_checkbox_changed(self, state: int):
        """Handle random signal checkbox change."""
        is_checked = state == Qt.CheckState.Checked.value

        if is_checked:
            self.stream_button.setEnabled(True)
            self.synthetic_group.show()
            self.xdf_tree.hide()
            self.random_tree.show()
            self.random_tree.header().show()
            self._populate_random_tree()
            # Disable file controls
            self.file_path_edit.setEnabled(False)
            self.browse_button.setEnabled(False)
            self.load_button.setEnabled(False)
        else:
            self.stream_button.setEnabled(self.stream_ready)
            self.synthetic_group.hide()
            self.random_tree.hide()
            self.random_tree.header().hide()
            self.random_tree.clear()
            self.xdf_tree.show()
            # Enable file controls
            self.file_path_edit.setEnabled(True)
            self.browse_button.setEnabled(True)
            self.load_button.setEnabled(bool(self.file_path_edit.text()))

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree widget item click."""
        if column != 0:
            return

        # Find the top-level item
        top_item = item
        while top_item.parent() is not None:
            top_item = top_item.parent()

        # Update stream_ready based on checked items
        self.stream_ready = False
        for i in range(self.xdf_tree.topLevelItemCount()):
            item = self.xdf_tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                if self.xdf_data:
                    stream_info = self.xdf_data.streams[i]
                    is_valid, error_msg = validate_stream(stream_info)
                    if not is_valid:
                        QMessageBox.information(self, "Status", f"You selected a stream with irregular rate!\nThe app will ignore that stream!\n{error_msg}")
                        item.setCheckState(0, Qt.CheckState.Unchecked)
                        continue
                self.stream_ready = True

        self.stream_button.setEnabled(self.stream_ready)

    def _on_stream_clicked(self):
        """Handle stream button click."""
        if self.stream_button.text() == "Stream":
            self._start_streaming()
        else:
            self._stop_streaming()

    def _start_streaming(self):
        """Start streaming."""
        self.stop_event.clear()
        self.is_streaming = True
        self.stream_button.setText("Stop")
        self._enable_controls(False)

        if self.random_checkbox.isChecked():
            self._start_synthetic_streaming()
        else:
            self._start_xdf_streaming()

        QMessageBox.information(
            self,
            "Status",
            "Lab Streaming Layer stream initialized.\nPlease start LabRecorder and refresh the streams\nand/or RT_Receiver_GUI to run simulations.",
        )

    def _start_synthetic_streaming(self):
        """Start synthetic signal streaming."""
        sampling_rate = self.sampling_rate_spin.value()
        channel_count = self.channel_count_spin.value()
        stream_name = self.stream_name_edit.text()
        stream_type = self.stream_type_edit.text()

        # Create synthetic stream info
        from ..models.stream_info import StreamInfo
        format_map = {"cf_float32": "float32", "cf_double64": "double64", "cf_int8": "int8", "cf_int16": "int16", "cf_int32": "int32", "cf_int64": "int64", "cf_string": "string"}
        channel_format = format_map.get(self.format_combo.currentText(), "double64")

        stream_info = StreamInfo(
            name=stream_name,
            type=stream_type,
            channel_count=channel_count,
            sampling_rate=float(sampling_rate),
            channel_format=channel_format,
            channels=[],
            stream_id=0,
        )

        outlet = self.lsl_streamer.create_outlet(stream_info)
        self.outlets.append(outlet)

        worker = StreamWorker(self.stop_event)
        thread = threading.Thread(target=worker.stream_synthetic_data, args=(outlet, sampling_rate, channel_count), daemon=True)
        thread.start()
        self.stream_threads.append(thread)

    def _start_xdf_streaming(self):
        """Start XDF file streaming."""
        if not self.xdf_data or not self.stream_ready:
            QMessageBox.information(self, "Status", "Please select a stream!\nAt least one stream needs to be selected...")
            self.stop_event.set()
            return

        # Find checked streams
        for i in range(self.xdf_tree.topLevelItemCount()):
            item = self.xdf_tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                stream_info = self.xdf_data.streams[i]
                is_valid, _ = validate_stream(stream_info)
                if not is_valid:
                    continue

                outlet = self.lsl_streamer.create_outlet(stream_info)
                self.outlets.append(outlet)

                worker = StreamWorker(self.stop_event)

                def create_complete_callback():
                    def callback():
                        self._on_stream_complete()

                    return callback

                thread = threading.Thread(
                    target=worker.stream_xdf_data,
                    args=(i, outlet, self.xdf_data, create_complete_callback()),
                    daemon=True,
                )
                thread.start()
                self.stream_threads.append(thread)

    def _stop_streaming(self):
        """Stop streaming."""
        self.stop_event.set()
        self.xdf_tree.setEnabled(True)
        self.random_tree.setEnabled(True)

        # Wait for threads to finish
        for thread in self.stream_threads:
            thread.join(timeout=2.0)

        self.stream_threads.clear()
        self.outlets.clear()

        self.stream_button.setText("Stream")
        self._enable_controls(True)
        self.is_streaming = False

    def _on_stream_complete(self):
        """Handle stream completion."""
        # Auto-stop when XDF streaming completes
        if not self.random_checkbox.isChecked():
            self._stop_streaming()

    def _enable_controls(self, enabled: bool):
        """Enable/disable controls."""
        if not self.random_checkbox.isChecked():
            self.file_path_edit.setEnabled(enabled)
            self.browse_button.setEnabled(enabled)
            self.load_button.setEnabled(enabled and bool(self.file_path_edit.text()))

        self.sampling_rate_spin.setEnabled(enabled)
        self.random_checkbox.setEnabled(enabled)
        self.synthetic_group.setEnabled(enabled)
        self.xdf_tree.setEnabled(enabled)
        self.random_tree.setEnabled(enabled)

    def _populate_xdf_tree(self):
        """Populate XDF stream tree."""
        self.xdf_tree.clear()
        if not self.xdf_data:
            return

        self.xdf_tree.header().show()
        tree_width = self.xdf_tree.width()
        self.xdf_tree.setColumnWidth(0, int(0.5 * tree_width) if tree_width > 0 else 200)

        # Set sampling rate from first non-string stream
        for stream_info in self.xdf_data.streams:
            if stream_info.channel_format != "string":
                self.sampling_rate_spin.setValue(int(stream_info.sampling_rate))
                break

        for i, stream_info in enumerate(self.xdf_data.streams):
            item = QTreeWidgetItem(self.xdf_tree)
            item.setText(0, f"Stream-{i + 1}")
            item.setCheckState(0, Qt.CheckState.Unchecked)
            is_disabled = stream_info.channel_format == "string"
            item.setDisabled(is_disabled)

            # Add stream properties
            props = [
                ("Stream Name", stream_info.name),
                ("Channel Format", stream_info.channel_format),
                ("Sampling Rate", str(stream_info.sampling_rate)),
                ("Channel Count", str(stream_info.channel_count)),
                ("Stream Type", stream_info.type),
            ]

            for prop_name, prop_value in props:
                sub_item = QTreeWidgetItem(item)
                sub_item.setText(0, prop_name)
                sub_item.setText(1, prop_value)
                sub_item.setDisabled(is_disabled)
                item.addChild(sub_item)

            self.xdf_tree.addTopLevelItem(item)

        self.xdf_tree.expandAll()

    def _populate_random_tree(self):
        """Populate random signal tree."""
        self.random_tree.clear()
        self.random_tree.header().show()
        tree_width = self.random_tree.width()
        self.random_tree.setColumnWidth(0, int(0.5 * tree_width) if tree_width > 0 else 200)

        item = QTreeWidgetItem(self.random_tree)
        item.setText(0, "Stream-1")

        props = [
            ("Stream Name", self.stream_name_edit.text()),
            ("Channel Format", "Double"),
            ("Samplign Rate", str(self.sampling_rate_spin.value())),
            ("Channel Count", str(self.channel_count_spin.value())),
            ("Stream Type", self.stream_type_edit.text()),
        ]

        for prop_name, prop_value in props:
            sub_item = QTreeWidgetItem(item)
            sub_item.setText(0, prop_name)
            sub_item.setText(1, prop_value)
            item.addChild(sub_item)

        self.random_tree.addTopLevelItem(item)
        self.random_tree.expandAll()

    def _clear_cache(self):
        """Clear loaded data."""
        self.xdf_data = None
        self.stream_button.setEnabled(False)
        self.load_button.setText("Load")
        self.xdf_tree.header().hide()
        self.xdf_tree.clear()
        self.stream_ready = False
