"""
Filter preset management - save and load filter configurations.
"""

import json
import os
from typing import List, Optional
from models import FilterRule, NumericFilter, TextFilter, DateFilter
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from styles import AppTheme


class FilterPreset:
    """Represents a saved filter configuration."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.filters: List[FilterRule] = []
    
    def add_filter(self, filter_rule: FilterRule):
        """Add a filter to this preset."""
        self.filters.append(filter_rule)
    
    def to_dict(self) -> dict:
        """Convert preset to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "filters": [f.to_dict() for f in self.filters]
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'FilterPreset':
        """Create preset from dictionary."""
        preset = FilterPreset(data["name"], data.get("description", ""))
        
        for filter_data in data.get("filters", []):
            filter_type = filter_data.get("type")
            
            if filter_type == "numeric":
                preset.add_filter(NumericFilter.from_dict(filter_data))
            elif filter_type == "text":
                preset.add_filter(TextFilter.from_dict(filter_data))
            elif filter_type == "date":
                preset.add_filter(DateFilter.from_dict(filter_data))
        
        return preset


class PresetManager:
    """Manages saving and loading filter presets."""
    
    def __init__(self, presets_dir: str = "presets"):
        self.presets_dir = presets_dir
        os.makedirs(presets_dir, exist_ok=True)
    
    def save_preset(self, preset: FilterPreset) -> str:
        """Save a preset to disk."""
        safe_name = "".join(c for c in preset.name if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_name}.json"
        filepath = os.path.join(self.presets_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(preset.to_dict(), f, indent=2)
        
        return filepath
    
    def load_preset(self, filepath: str) -> Optional[FilterPreset]:
        """Load a preset from disk."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return FilterPreset.from_dict(data)
        except Exception as e:
            print(f"Error loading preset: {e}")
            return None
    
    def list_presets(self) -> List[dict]:
        """List all available presets."""
        presets = []
        
        if not os.path.exists(self.presets_dir):
            return presets
        
        for filename in os.listdir(self.presets_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.presets_dir, filename)
                preset = self.load_preset(filepath)
                
                if preset:
                    presets.append({
                        'name': preset.name,
                        'description': preset.description,
                        'filepath': filepath,
                        'filter_count': len(preset.filters)
                    })
        
        return presets
    
    def delete_preset(self, filepath: str) -> bool:
        """Delete a preset file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting preset: {e}")
            return False


class SavePresetDialog(QDialog):
    """Dialog for saving a filter preset."""
    
    def __init__(self, current_filters: List[FilterRule], parent=None):
        super().__init__(parent)
        self.current_filters = current_filters
        self.preset_manager = PresetManager()
        self.result_preset = None
        
        self.setWindowTitle("Save Filter Preset")
        self.setMinimumWidth(550)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Name
        name_label = QLabel("Preset Name:")
        name_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., High Achievers")
        layout.addWidget(self.name_edit)
        
        # Description
        desc_label = QLabel("Description (optional):")
        desc_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        layout.addWidget(desc_label)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Describe what this preset filters for...")
        layout.addWidget(self.description_edit)
        
        # Show current filters
        filters_label = QLabel("Current Filters:")
        filters_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        layout.addWidget(filters_label)
        
        filter_list = QListWidget()
        filter_list.setMaximumHeight(150)
        filter_list.setStyleSheet("""
            QListWidget {
                background-color: #F9FAFB;
                color: #111827;
                border: 2px solid #D1D5DB;
            }
        """)
        
        for f in self.current_filters:
            filter_list.addItem(str(f))
        
        layout.addWidget(filter_list)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_save(self):
        """Validate and save preset."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a preset name.")
            return
        
        description = self.description_edit.toPlainText().strip()
        
        preset = FilterPreset(name, description)
        for f in self.current_filters:
            preset.add_filter(f)
        
        try:
            filepath = self.preset_manager.save_preset(preset)
            self.result_preset = preset
            QMessageBox.information(
                self,
                "Preset Saved",
                f"Preset '{name}' saved successfully!"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving",
                f"Failed to save preset:\n{str(e)}"
            )
    
    def get_preset(self) -> Optional[FilterPreset]:
        """Get the saved preset."""
        return self.result_preset


class LoadPresetDialog(QDialog):
    """Dialog for loading a filter preset."""
    
    presetSelected = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_manager = PresetManager()
        self.selected_preset = None
        
        self.setWindowTitle("Load Filter Preset")
        self.setMinimumSize(650, 550)
        self._setup_ui()
        self._load_presets()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Available Filter Presets")
        title.setStyleSheet(f"font-size: 12pt; font-weight: 600; color: {AppTheme.TEXT};")
        layout.addWidget(title)
        
        # Preset list
        self.preset_list = QListWidget()
        self.preset_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 2px solid {AppTheme.BORDER};
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
            QListWidget::item:hover {{
                background-color: {AppTheme.GRAY_100};
            }}
        """)
        self.preset_list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.preset_list)
        
        # Details panel
        self.details_label = QLabel("Select a preset to view details")
        self.details_label.setStyleSheet(f"""
            QLabel {{
                padding: 12px;
                background-color: {AppTheme.GRAY_50};
                border: 2px solid {AppTheme.BORDER};
                border-radius: 4px;
                color: {AppTheme.TEXT};
            }}
        """)
        self.details_label.setWordWrap(True)
        self.details_label.setMinimumHeight(100)
        layout.addWidget(self.details_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self._on_load)
        self.load_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.GRAY_600};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.GRAY_700};
            }}
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_presets(self):
        """Load available presets into list."""
        self.preset_list.clear()
        presets = self.preset_manager.list_presets()
        
        if not presets:
            item = QListWidgetItem("No presets saved yet")
            item.setFlags(Qt.NoItemFlags)
            self.preset_list.addItem(item)
            return
        
        for preset_info in presets:
            item_text = f"{preset_info['name']} ({preset_info['filter_count']} filters)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, preset_info['filepath'])
            self.preset_list.addItem(item)
    
    def _on_selection_changed(self, current, previous):
        """Handle preset selection."""
        if current is None or not current.flags() & Qt.ItemIsEnabled:
            self.details_label.setText("Select a preset to view details")
            self.load_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        filepath = current.data(Qt.UserRole)
        preset = self.preset_manager.load_preset(filepath)
        
        if preset:
            details = f"<b>Name:</b> {preset.name}<br>"
            if preset.description:
                details += f"<b>Description:</b> {preset.description}<br>"
            details += f"<b>Filters:</b><br><ul>"
            
            for f in preset.filters:
                details += f"<li>{str(f)}</li>"
            
            details += "</ul>"
            
            self.details_label.setText(details)
            self.selected_preset = preset
            self.load_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def _on_load(self):
        """Load selected preset."""
        if self.selected_preset:
            self.presetSelected.emit(self.selected_preset)
            self.accept()
    
    def _on_delete(self):
        """Delete selected preset."""
        current = self.preset_list.currentItem()
        if not current:
            return
        
        filepath = current.data(Qt.UserRole)
        preset = self.preset_manager.load_preset(filepath)
        
        if not preset:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the preset '{preset.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.preset_manager.delete_preset(filepath):
                QMessageBox.information(self, "Deleted", f"Preset '{preset.name}' deleted.")
                self._load_presets()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete preset.")
