"""
Proxy models for filtering, searching, and view management.
"""

from PyQt5.QtCore import QSortFilterProxyModel, Qt, QModelIndex
from typing import Optional, List


class SmartSearchProxy(QSortFilterProxyModel):
    """
    Advanced proxy model with:
    - Global or column-specific search
    - Filter mode (all/highlighted/unhighlighted)
    - Optional per-view extra filters (used by the Tab-First system)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text: str = ""
        self.search_column: Optional[str] = None
        self.filter_mode: str = "all"
        # Extra filter rules that belong only to this view / tab.
        self.extra_filters: List[object] = []
        self.extra_filter_mode: str = "all"  # "all" (AND) or "any" (OR)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
    
    def setSearchText(self, text: str):
        self.search_text = text.strip()
        self.invalidateFilter()
    
    def setSearchColumn(self, column_name: Optional[str]):
        self.search_column = column_name
        self.invalidateFilter()
    
    def setFilterMode(self, mode: str):
        if mode in ["all", "highlighted", "unhighlighted"]:
            self.filter_mode = mode
            self.invalidateFilter()
    
    def setExtraFilters(self, filters: Optional[list]):
        self.extra_filters = list(filters) if filters else []
        self.invalidateFilter()

    def setExtraFilterMode(self, mode: str):
        if mode in ["all", "any"]:
            self.extra_filter_mode = mode
            self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        if model is None:
            return True
        
        # 1) SEARCH FILTER
        if self.search_text:
            if self.search_column is None:
                matched = False
                for col in range(model.columnCount()):
                    index = model.index(source_row, col, source_parent)
                    value = model.data(index, Qt.DisplayRole)
                    if value and self.search_text.lower() in str(value).lower():
                        matched = True
                        break
                if not matched:
                    return False
            else:
                col_index = self._get_column_index(self.search_column)
                if col_index is not None:
                    index = model.index(source_row, col_index, source_parent)
                    value = model.data(index, Qt.DisplayRole)
                    if not (value and self.search_text.lower() in str(value).lower()):
                        return False
                else:
                    return False
        
        # 2) HIGHLIGHT FILTER
        if hasattr(model, 'is_row_highlighted'):
            if self.filter_mode != "all" and hasattr(model, "filter_manager"):
                if model.filter_manager.has_filters():
                    is_highlighted = model.is_row_highlighted(source_row)
                    if self.filter_mode == "highlighted" and not is_highlighted:
                        return False
                    if self.filter_mode == "unhighlighted" and is_highlighted:
                        return False
                    # (mode == "all" means pass)
        
        # 3) EXTRA PER-TAB FILTERS
        if self.extra_filters:
            if self.extra_filter_mode == "any":
                matched_any = False
                for filter_rule in self.extra_filters:
                    column_name = getattr(filter_rule, "column", None)
                    if not column_name:
                        continue
                    col_index = self._get_column_index(column_name)
                    if col_index is None:
                        continue
                    if hasattr(model, "get_raw_value"):
                        value = model.get_raw_value(source_row, col_index)
                    else:
                        index = model.index(source_row, col_index, source_parent)
                        value = model.data(index, Qt.DisplayRole)
                    if hasattr(filter_rule, "matches") and filter_rule.matches(value):
                        matched_any = True
                        break
                if not matched_any:
                    return False
            else:
                for filter_rule in self.extra_filters:
                    column_name = getattr(filter_rule, "column", None)
                    if not column_name:
                        continue
                    col_index = self._get_column_index(column_name)
                    if col_index is None:
                        return False
                    if hasattr(model, "get_raw_value"):
                        value = model.get_raw_value(source_row, col_index)
                    else:
                        index = model.index(source_row, col_index, source_parent)
                        value = model.data(index, Qt.DisplayRole)
                    if not hasattr(filter_rule, "matches") or not filter_rule.matches(value):
                        return False
        
        return True
    
    def _get_column_index(self, column_name: str) -> Optional[int]:
        model = self.sourceModel()
        if model is None:
            return None
        
        for col in range(model.columnCount()):
            header = model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            header_str = str(header).replace("[F] ", "")
            if header_str == column_name:
                return col
        return None
    
    def get_visible_row_count(self) -> int:
        return self.rowCount()
    
    def get_highlighted_count(self) -> int:
        model = self.sourceModel()
        if not hasattr(model, 'is_row_highlighted'):
            return 0
        
        count = 0
        for row in range(self.rowCount()):
            source_index = self.mapToSource(self.index(row, 0))
            if model.is_row_highlighted(source_index.row()):
                count += 1
        return count
