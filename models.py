"""
Core data models with REACTIVE OBSERVER PATTERN fully implemented.
All UI components auto-update when data changes.
"""

import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from typing import Dict, List, Optional, Any, Callable
import datetime


class FilterRule:
    """Base class for filter rules."""
    def __init__(self, column: str):
        self.column = column
        self.id = id(self)
    
    def matches(self, value: Any) -> bool:
        raise NotImplementedError
    
    def to_dict(self) -> dict:
        raise NotImplementedError
    
    @staticmethod
    def from_dict(data: dict) -> 'FilterRule':
        raise NotImplementedError


class NumericFilter(FilterRule):
    """Numeric threshold filter (>=, <=, ==, >, <, !=)."""
    
    OPERATORS = [">=", "<=", "==", ">", "<", "!="]
    COLORS = {
        ">=": QColor(255, 230, 230),
        "<=": QColor(230, 255, 230),
        "==": QColor(230, 230, 255),
        ">": QColor(255, 220, 220),
        "<": QColor(220, 255, 220),
        "!=": QColor(245, 245, 245),
    }
    
    def __init__(self, column: str, operator: str, value: float):
        super().__init__(column)
        self.operator = operator
        self.value = value
    
    def matches(self, value: Any) -> bool:
        try:
            val = float(value)
        except (TypeError, ValueError):
            return False
        
        if self.operator == ">=":
            return val >= self.value
        elif self.operator == "<=":
            return val <= self.value
        elif self.operator == "==":
            return val == self.value
        elif self.operator == ">":
            return val > self.value
        elif self.operator == "<":
            return val < self.value
        elif self.operator == "!=":
            return val != self.value
        return False
    
    def get_color(self) -> QColor:
        return self.COLORS.get(self.operator, QColor(255, 255, 255))
    
    def to_dict(self) -> dict:
        return {
            "type": "numeric",
            "column": self.column,
            "operator": self.operator,
            "value": self.value
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'NumericFilter':
        return NumericFilter(data["column"], data["operator"], data["value"])
    
    def __str__(self):
        return f"{self.column} {self.operator} {self.value}"
    
    def __eq__(self, other):
        if not isinstance(other, NumericFilter):
            return False
        return (self.column == other.column and 
                self.operator == other.operator and 
                self.value == other.value)
    
    def __hash__(self):
        return hash((self.column, self.operator, self.value))


class TextFilter(FilterRule):
    """Text contains filter with multiple tokens."""
    
    COLOR = QColor(255, 250, 205)
    
    def __init__(self, column: str, tokens: List[str], case_sensitive: bool = False):
        super().__init__(column)
        self.tokens = [t.strip() for t in tokens if t.strip()]
        self.case_sensitive = case_sensitive
        if not self.case_sensitive:
            self.tokens = [t.lower() for t in self.tokens]
    
    def matches(self, value: Any) -> bool:
        if not self.tokens:
            return False
        
        text = str(value)
        if not self.case_sensitive:
            text = text.lower()
        
        return any(token in text for token in self.tokens)
    
    def get_color(self) -> QColor:
        return self.COLOR
    
    def to_dict(self) -> dict:
        return {
            "type": "text",
            "column": self.column,
            "tokens": self.tokens,
            "case_sensitive": self.case_sensitive
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'TextFilter':
        return TextFilter(
            data["column"],
            data["tokens"],
            data.get("case_sensitive", False)
        )
    
    def __str__(self):
        tokens_str = ", ".join(self.tokens[:3])
        if len(self.tokens) > 3:
            tokens_str += "..."
        return f"{self.column} contains: {tokens_str}"
    
    def __eq__(self, other):
        if not isinstance(other, TextFilter):
            return False
        return (self.column == other.column and 
                set(self.tokens) == set(other.tokens) and
                self.case_sensitive == other.case_sensitive)
    
    def __hash__(self):
        return hash((self.column, tuple(sorted(self.tokens)), self.case_sensitive))


class DateFilter(FilterRule):
    """Date range filter."""
    
    COLOR = QColor(240, 230, 255)
    
    def __init__(self, column: str, start_date: Optional[datetime.date] = None,
                 end_date: Optional[datetime.date] = None):
        super().__init__(column)
        self.start_date = start_date
        self.end_date = end_date
    
    def matches(self, value: Any) -> bool:
        try:
            if isinstance(value, (pd.Timestamp, datetime.datetime)):
                date_val = value.date()
            elif isinstance(value, datetime.date):
                date_val = value
            else:
                date_val = pd.to_datetime(value).date()
        except Exception:
            return False
        
        if self.start_date and date_val < self.start_date:
            return False
        if self.end_date and date_val > self.end_date:
            return False
        return True
    
    def get_color(self) -> QColor:
        return self.COLOR
    
    def to_dict(self) -> dict:
        return {
            "type": "date",
            "column": self.column,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'DateFilter':
        start = datetime.date.fromisoformat(data["start_date"]) if data.get("start_date") else None
        end = datetime.date.fromisoformat(data["end_date"]) if data.get("end_date") else None
        return DateFilter(data["column"], start, end)
    
    def __str__(self):
        if self.start_date and self.end_date:
            return f"{self.column}: {self.start_date} to {self.end_date}"
        elif self.start_date:
            return f"{self.column}: from {self.start_date}"
        elif self.end_date:
            return f"{self.column}: until {self.end_date}"
        return f"{self.column}: date filter"
    
    def __eq__(self, other):
        if not isinstance(other, DateFilter):
            return False
        return (self.column == other.column and 
                self.start_date == other.start_date and
                self.end_date == other.end_date)
    
    def __hash__(self):
        return hash((self.column, self.start_date, self.end_date))


class FilterManager:
    """Manages all active filters with OBSERVER PATTERN."""
    
    def __init__(self):
        self.filters: Dict[str, List[FilterRule]] = {}
        self.observers: List[Callable] = []
    
    def add_observer(self, callback: Callable):
        """Register observer for filter changes."""
        if callback not in self.observers:
            self.observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Unregister observer."""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def notify_observers(self, event: str, data: dict):
        """Notify all observers of filter changes."""
        for observer in self.observers:
            try:
                observer(event, data)
            except Exception as e:
                print(f"Observer error: {e}")
    
    def add_filter(self, filter_rule: FilterRule):
        """Add a filter rule and notify observers."""
        col = filter_rule.column
        if col not in self.filters:
            self.filters[col] = []
        
        if filter_rule not in self.filters[col]:
            self.filters[col].append(filter_rule)
            self.notify_observers('filter_added', {'filter': filter_rule})
    
    def remove_filter(self, filter_rule: FilterRule):
        """Remove a specific filter rule and notify observers."""
        col = filter_rule.column
        if col in self.filters:
            if filter_rule in self.filters[col]:
                self.filters[col].remove(filter_rule)
                if not self.filters[col]:
                    del self.filters[col]
                self.notify_observers('filter_removed', {'filter': filter_rule})
    
    def clear_column_filters(self, column: str):
        """Remove all filters for a column and notify observers."""
        if column in self.filters:
            del self.filters[column]
            self.notify_observers('column_filters_cleared', {'column': column})
    
    def clear_all(self):
        """Remove all filters and notify observers."""
        self.filters.clear()
        self.notify_observers('filters_cleared', {})
    
    def get_filters_for_column(self, column: str) -> List[FilterRule]:
        """Get all filters for a specific column."""
        return self.filters.get(column, [])
    
    def get_all_filters(self) -> List[FilterRule]:
        """Get all filters as a flat list."""
        all_filters = []
        for filters in self.filters.values():
            all_filters.extend(filters)
        return all_filters
    
    def has_filters(self) -> bool:
        """Check if any filters are active."""
        return len(self.filters) > 0
    
    def matches_any_filter(self, row_data: pd.Series) -> bool:
        """Check if a row matches any filter."""
        for column, filters in self.filters.items():
            if column not in row_data.index:
                continue
            value = row_data[column]
            for filter_rule in filters:
                if filter_rule.matches(value):
                    return True
        return False

    def matches_all_filters(self, row_data: pd.Series) -> bool:
        """Check if a row matches all active filters (AND logic)."""
        if not self.filters:
            return True

        for column, filters in self.filters.items():
            if column not in row_data.index:
                return False
            value = row_data[column]
            for filter_rule in filters:
                if not filter_rule.matches(value):
                    return False
        return True
    
    def get_color_for_cell(self, column: str, value: Any) -> Optional[QColor]:
        """Get highlight color for a cell if it matches any filter."""
        if column not in self.filters:
            return None
        
        for filter_rule in self.filters[column]:
            if filter_rule.matches(value):
                return filter_rule.get_color()
        return None


class DataFrameModel(QAbstractTableModel):
    """Qt model for pandas DataFrame with REACTIVE OBSERVER PATTERN."""
    
    DATE_COL_NAME = "Date Added"
    
    dataLoaded = pyqtSignal(dict)
    dataChanged = pyqtSignal(QModelIndex, QModelIndex, list)
    filterChanged = pyqtSignal()
    
    def __init__(self, df: Optional[pd.DataFrame] = None, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else pd.DataFrame()
        self.filter_manager = FilterManager()
        self._highlight_mask: Optional[np.ndarray] = None
        self.observers: List[Callable] = []
        
        self.filter_manager.add_observer(self._on_filter_manager_change)
    
    def _on_filter_manager_change(self, event: str, data: dict):
        """React to filter manager changes."""
        self.filterChanged.emit()
        self.notify_observers(event, data)
        self.layoutChanged.emit()
    
    def add_observer(self, callback: Callable):
        """Register observer for data changes."""
        if callback not in self.observers:
            self.observers.append(callback)
    
    def remove_observer(self, callback: Callable):
        """Unregister observer."""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def notify_observers(self, event: str, data: dict):
        """Notify all observers of data changes."""
        for observer in self.observers:
            try:
                observer(event, data)
            except Exception as e:
                print(f"Observer error: {e}")
    
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._df)
    
    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._df.columns)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        
        if row < 0 or row >= len(self._df) or col < 0 or col >= len(self._df.columns):
            return QVariant()
        
        col_name = self._df.columns[col]
        value = self._df.iat[row, col]
        
        is_row_highlighted = self.is_row_highlighted(row)
        
        if role == Qt.DisplayRole:
            if pd.isna(value):
                return ""
            elif isinstance(value, float):
                return f"{value:.4g}"
            elif isinstance(value, (pd.Timestamp, datetime.datetime, datetime.date)):
                return str(value)
            else:
                return str(value)
        
        elif role == Qt.BackgroundRole:
            color = self.filter_manager.get_color_for_cell(col_name, value)
            if color:
                return color
            
            if row % 2 == 0:
                return QColor(255, 255, 255)
            return QColor(248, 248, 248)
        
        elif role == Qt.ForegroundRole:
            col_name_lower = col_name.lower()
            if is_row_highlighted and any(name_indicator in col_name_lower for name_indicator in ['name', 'student', 'applicant']):
                return QColor(204, 0, 0)
            return QColor(0, 0, 0)
        
        elif role == Qt.TextAlignmentRole:
            if isinstance(value, (int, float)) and not pd.isna(value):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if 0 <= section < len(self._df.columns):
                    col_name = str(self._df.columns[section])
                    if self.filter_manager.get_filters_for_column(col_name):
                        return f"[F] {col_name}"
                    return col_name
                return ""
            else:
                return str(section + 1)
        
        elif role == Qt.BackgroundRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self._df.columns):
                col_name = str(self._df.columns[section])
                if self.filter_manager.get_filters_for_column(col_name):
                    return QColor(204, 229, 255)
            return QColor(248, 248, 248)
        
        elif role == Qt.ForegroundRole:
            return QColor(0, 0, 0)
        
        elif role == Qt.FontRole and orientation == Qt.Horizontal:
            font = QFont()
            font.setBold(True)
            return font
        
        return QVariant()
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        # Keep editing via dialog/context menu; avoid inline edits unless explicitly enabled.
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        """Update a cell value with basic type coercion."""
        if role != Qt.EditRole or not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if row < 0 or row >= len(self._df) or col < 0 or col >= len(self._df.columns):
            return False

        col_name = self._df.columns[col]
        dtype = self._df[col_name].dtype

        # Treat empty strings as missing values
        if value is None or (isinstance(value, str) and value.strip() == ""):
            new_value = np.nan
        else:
            new_value = value

            try:
                if pd.api.types.is_numeric_dtype(dtype):
                    new_value = pd.to_numeric(value, errors="coerce")
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    new_value = pd.to_datetime(value, errors="coerce")
                else:
                    new_value = str(value)
            except Exception:
                # Fall back to raw input if coercion fails
                new_value = value

        self._df.iat[row, col] = new_value

        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.BackgroundRole, Qt.ForegroundRole])
        self.notify_observers("cell_updated", {"row": row, "column": col_name, "value": new_value})

        return True
    
    def sort(self, column, order):
        if self._df.empty:
            return
        
        self.layoutAboutToBeChanged.emit()
        col_name = self._df.columns[column]
        self._df.sort_values(
            by=col_name,
            ascending=(order == Qt.AscendingOrder),
            inplace=True,
            na_position='last'
        )
        self._df.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()
    
    def is_row_highlighted(self, row: int) -> bool:
        """Check if row is highlighted."""
        if self._df.empty or not self.filter_manager.has_filters():
            if self._highlight_mask is None:
                return False
        
        try:
            if self._highlight_mask is not None and row < len(self._highlight_mask):
                return bool(self._highlight_mask[row])
            row_data = self._df.iloc[row]
            return self.filter_manager.matches_all_filters(row_data)
        except Exception:
            return False

    def set_highlight_mask(self, mask: Optional[np.ndarray]):
        """Set per-row highlight mask for custom highlighting."""
        if mask is None:
            self._highlight_mask = None
        else:
            try:
                self._highlight_mask = np.asarray(mask, dtype=bool)
            except Exception:
                self._highlight_mask = None

        if not self._df.empty:
            top_left = self.index(0, 0)
            bottom_right = self.index(
                self.rowCount() - 1,
                self.columnCount() - 1
            )
            self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole, Qt.ForegroundRole])

    def get_raw_value(self, row: int, col: int):
        """Get raw dataframe value for a given row/column index."""
        try:
            return self._df.iat[row, col]
        except Exception:
            return None
    
    def set_dataframe(self, df: pd.DataFrame):
        """Replace the entire DataFrame and notify observers."""
        self.beginResetModel()
        self._df = df.copy()
        self.filter_manager.clear_all()
        self._highlight_mask = None
        self.endResetModel()
        
        self.notify_observers('data_loaded', {
            'rows': len(df),
            'columns': list(df.columns)
        })
        self.dataLoaded.emit({
            'rows': len(df),
            'columns': list(df.columns)
        })
    
    def dataframe(self) -> pd.DataFrame:
        """Get the underlying DataFrame."""
        return self._df.copy()
    
    def get_column_dtype(self, column: str) -> str:
        """Get the data type category of a column."""
        if column not in self._df.columns:
            return "unknown"
        
        dtype = self._df[column].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "date"
        else:
            return "text"
    
    def get_column_stats(self, column: str) -> dict:
        """Get statistics for a column."""
        if column not in self._df.columns:
            return {}
        
        col_data = self._df[column]
        stats = {
            "count": len(col_data),
            "non_null": col_data.notna().sum(),
            "null": col_data.isna().sum(),
            "unique": col_data.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(col_data.dtype):
            stats.update({
                "min": col_data.min(),
                "max": col_data.max(),
                "mean": col_data.mean(),
                "median": col_data.median()
            })
        
        return stats
