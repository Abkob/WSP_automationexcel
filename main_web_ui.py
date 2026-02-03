"""
MODERN WEB-BASED STUDENT ADMISSIONS MANAGER
Using PyQt5 QWebEngineView with HTML/CSS/JavaScript

Architecture:
- PyQt5 QWebEngineView hosts the web interface
- HTML/CSS/JavaScript for modern, responsive UI
- QWebChannel for Python ↔ JavaScript communication
- Reactive data updates
- Beautiful Material Design interface
"""

import os
import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QUrl, QTimer
import pandas as pd
import numpy as np
from typing import Optional, List, Dict

from models import DataFrameModel, NumericFilter, TextFilter, DateFilter
from utils import (
    load_dataframe_from_file, add_date_column, merge_dataframes,
    export_to_excel_formatted, create_archive_snapshot,
    save_last_loaded_file, get_last_loaded_file
)


class PythonBridge(QObject):
    """
    Bridge between Python backend and JavaScript frontend.
    Exposes Python functions to JavaScript.
    """
    
    # Signals to send data to JavaScript
    dataUpdated = pyqtSignal(str)  # JSON data
    filterUpdated = pyqtSignal(str)  # JSON filters
    statsUpdated = pyqtSignal(str)  # JSON stats
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    
    @pyqtSlot(str)
    def search(self, query):
        """Handle search from JavaScript."""
        self.main_window.perform_search(query)
    
    @pyqtSlot()
    def loadFile(self):
        """Open file dialog to load data."""
        self.main_window.load_file_dialog()
    
    @pyqtSlot()
    def exportData(self):
        """Export current data."""
        self.main_window.export_dialog()
    
    @pyqtSlot(str)
    def addFilter(self, filter_json):
        """Add a new filter from JavaScript."""
        filter_data = json.loads(filter_json)
        self.main_window.add_filter_from_web(filter_data)
    
    @pyqtSlot(int)
    def removeFilter(self, filter_id):
        """Remove a filter."""
        self.main_window.remove_filter_by_id(filter_id)
    
    @pyqtSlot()
    def clearAllFilters(self):
        """Clear all active filters."""
        self.main_window.clear_all_filters()
    
    @pyqtSlot(int)
    def selectTab(self, tab_id):
        """Switch to a specific tab."""
        self.main_window.switch_tab(tab_id)
    
    @pyqtSlot()
    def createNewTab(self):
        """Create a new custom tab."""
        self.main_window.create_new_tab()
    
    @pyqtSlot(str, bool)
    def sortColumn(self, column, ascending):
        """Sort by column."""
        self.main_window.sort_by_column(column, ascending)
    
    @pyqtSlot(int)
    def openStudentDetail(self, student_id):
        """Open student detail view."""
        self.main_window.show_student_detail(student_id)
    
    @pyqtSlot(int, int)
    def loadPage(self, page, page_size):
        """Load a specific page of data."""
        self.main_window.load_data_page(page, page_size)


class ModernWebMainWindow(QMainWindow):
    """Modern web-based main window using QWebEngineView."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Student Admissions Manager - Modern Web UI")
        self.resize(1800, 1000)
        
        # Data
        self.df = pd.DataFrame()
        self.current_file_path = None
        self.model = DataFrameModel(self.df)
        self.active_filters = []
        self.filter_id_counter = 0
        
        # Setup UI
        self._setup_web_view()
        self._setup_bridge()
        
        # Load interface
        QTimer.singleShot(100, self._load_interface)
        
        # Auto-load last file
        QTimer.singleShot(500, self._autoload_last_file)
    
    def _setup_web_view(self):
        """Setup QWebEngineView."""
        self.web_view = QWebEngineView()
        self.setCentralWidget(self.web_view)
        
        # Enable developer tools (for debugging)
        self.web_view.page().settings().setAttribute(
            self.web_view.page().settings().LocalContentCanAccessRemoteUrls, True
        )
    
    def _setup_bridge(self):
        """Setup Python-JavaScript bridge."""
        self.channel = QWebChannel()
        self.bridge = PythonBridge(self)
        self.channel.registerObject('pybridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)
    
    def _load_interface(self):
        """Load the HTML/CSS/JS interface."""
        html_content = self._get_html_template()
        
        # Save to temp file or load directly
        base_url = QUrl.fromLocalFile(os.getcwd() + "/")
        self.web_view.setHtml(html_content, base_url)
    
    def _get_html_template(self):
        """Get the complete HTML template with embedded CSS/JS."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Admissions Manager</title>
    
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .slide-in { animation: slideIn 0.3s ease-out; }
        .fade-in { animation: fadeIn 0.2s ease-out; }
        .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        
        .card-hover {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .card-hover:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .filter-chip {
            transition: all 0.2s ease;
        }
        
        .filter-chip:hover {
            transform: scale(1.05);
        }
        
        .table-row {
            transition: background-color 0.15s ease;
        }
        
        .table-row:hover {
            background-color: #f3f4f6;
            cursor: pointer;
        }
        
        * {
            scroll-behavior: smooth;
        }
        
        .gradient-bg {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .glass-effect {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
        }
        
        .btn-primary {
            @apply bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-200 font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5;
        }
        
        .btn-secondary {
            @apply bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-all duration-200 font-medium;
        }
        
        .data-card {
            @apply bg-white rounded-xl shadow-md p-6 border border-gray-100;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
    <div id="app" class="min-h-screen">
        <!-- Top Navigation -->
        <nav class="glass-effect sticky top-0 z-50 border-b border-gray-200 shadow-sm">
            <div class="max-w-7xl mx-auto px-6">
                <div class="flex justify-between items-center h-16">
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                <i class="fas fa-graduation-cap text-white text-xl"></i>
                            </div>
                            <div>
                                <h1 class="text-lg font-bold text-gray-900">Student Admissions</h1>
                                <p class="text-xs text-gray-500">Modern Dashboard</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex items-center space-x-3">
                        <div class="relative">
                            <input 
                                type="text" 
                                v-model="searchQuery"
                                @input="onSearch"
                                placeholder="Search students..."
                                class="pl-10 pr-4 py-2 w-80 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            >
                            <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
                        </div>
                        
                        <button @click="openLoadDialog" class="btn-primary flex items-center">
                            <i class="fas fa-folder-open mr-2"></i>
                            Load Data
                        </button>
                        
                        <button @click="exportData" class="btn-secondary flex items-center">
                            <i class="fas fa-download mr-2"></i>
                            Export
                        </button>
                    </div>
                </div>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="max-w-7xl mx-auto px-6 py-8">
            
            <!-- Stats Dashboard -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="data-card card-hover">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                                <i class="fas fa-users text-blue-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-500">Total Students</p>
                            <p class="text-3xl font-bold text-gray-900">{{ formatNumber(totalStudents) }}</p>
                            <p class="text-xs text-gray-400 mt-1">All records</p>
                        </div>
                    </div>
                </div>
                
                <div class="data-card card-hover">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                                <i class="fas fa-filter text-green-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-500">Filtered</p>
                            <p class="text-3xl font-bold text-gray-900">{{ formatNumber(filteredCount) }}</p>
                            <p class="text-xs text-gray-400 mt-1">Active filters: {{ filters.length }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="data-card card-hover">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
                                <i class="fas fa-star text-purple-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-500">High Performers</p>
                            <p class="text-3xl font-bold text-gray-900">{{ formatNumber(highGPACount) }}</p>
                            <p class="text-xs text-gray-400 mt-1">GPA >= 3.5</p>
                        </div>
                    </div>
                </div>
                
                <div class="data-card card-hover">
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <div class="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
                                <i class="fas fa-clock text-yellow-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-500">Pending Review</p>
                            <p class="text-3xl font-bold text-gray-900">{{ formatNumber(pendingCount) }}</p>
                            <p class="text-xs text-gray-400 mt-1">Needs attention</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Active Filters Section -->
            <div v-if="filters.length > 0" class="mb-6">
                <div class="data-card">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center">
                            <i class="fas fa-filter text-blue-600 mr-3 text-lg"></i>
                            <h2 class="text-lg font-semibold text-gray-900">Active Filters</h2>
                        </div>
                        <button @click="clearAllFilters" class="text-sm text-red-600 hover:text-red-700 font-medium transition-colors">
                            <i class="fas fa-times-circle mr-1"></i>
                            Clear All
                        </button>
                    </div>
                    
                    <div class="flex flex-wrap gap-3">
                        <div 
                            v-for="filter in filters" 
                            :key="filter.id"
                            class="filter-chip bg-gradient-to-r from-blue-100 to-blue-50 border border-blue-200 text-blue-800 px-4 py-2 rounded-full flex items-center space-x-3 fade-in"
                        >
                            <i :class="getFilterIcon(filter.type)" class="text-blue-600"></i>
                            <span class="font-medium">{{ filter.label }}</span>
                            <span class="text-blue-600 bg-blue-200 px-2 py-0.5 rounded-full text-xs font-bold">{{ filter.count }}</span>
                            <button @click="removeFilter(filter)" class="ml-2 text-blue-600 hover:text-red-600 transition-colors">
                                <i class="fas fa-times-circle"></i>
                            </button>
                        </div>
                        
                        <button @click="openFilterDialog" class="filter-chip bg-gradient-to-r from-gray-100 to-gray-50 border border-gray-300 text-gray-700 px-4 py-2 rounded-full hover:from-gray-200 hover:to-gray-100 flex items-center">
                            <i class="fas fa-plus-circle mr-2"></i>
                            Add Filter
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Empty State -->
            <div v-if="totalStudents === 0" class="data-card text-center py-16 fade-in">
                <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-inbox text-gray-400 text-4xl"></i>
                </div>
                <h3 class="text-2xl font-bold text-gray-900 mb-2">No Data Loaded</h3>
                <p class="text-gray-500 mb-6">Load a data file to get started with managing student admissions</p>
                <button @click="openLoadDialog" class="btn-primary inline-flex items-center">
                    <i class="fas fa-folder-open mr-2"></i>
                    Load Data File
                </button>
            </div>
            
            <!-- Data Table -->
            <div v-if="totalStudents > 0" class="data-card">
                <!-- Table Controls -->
                <div class="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
                    <div class="flex items-center space-x-4">
                        <button class="text-sm text-gray-600 hover:text-gray-900 transition-colors font-medium">
                            <i class="fas fa-check-square mr-2"></i>
                            Select All
                        </button>
                        <span class="text-sm text-gray-500">
                            Showing <span class="font-semibold text-gray-700">{{ visibleRows.length }}</span> of <span class="font-semibold text-gray-700">{{ totalRows }}</span> students
                        </span>
                    </div>
                    
                    <div class="flex items-center space-x-2">
                        <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Column Settings">
                            <i class="fas fa-columns text-gray-600"></i>
                        </button>
                        <button @click="exportData" class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Export">
                            <i class="fas fa-download text-gray-600"></i>
                        </button>
                        <button class="p-2 hover:bg-gray-100 rounded-lg transition-colors" title="Refresh">
                            <i class="fas fa-sync-alt text-gray-600"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Table -->
                <div class="overflow-x-auto -mx-6">
                    <table class="min-w-full">
                        <thead class="bg-gray-50 border-y border-gray-200">
                            <tr>
                                <th class="px-6 py-4 text-left">
                                    <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                                </th>
                                <th 
                                    v-for="col in columns" 
                                    :key="col.key"
                                    class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                                    @click="sortBy(col.key)"
                                >
                                    <div class="flex items-center space-x-2">
                                        <span>{{ col.label }}</span>
                                        <i v-if="sortColumn === col.key" :class="sortAsc ? 'fas fa-sort-up' : 'fas fa-sort-down'" class="text-blue-600"></i>
                                        <i v-else class="fas fa-sort text-gray-300"></i>
                                    </div>
                                </th>
                                <th class="px-6 py-4"></th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-100">
                            <tr 
                                v-for="row in visibleRows" 
                                :key="row.id"
                                class="table-row"
                                @click="openStudentDetail(row)"
                            >
                                <td class="px-6 py-4">
                                    <input type="checkbox" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500" @click.stop>
                                </td>
                                <td 
                                    v-for="col in columns" 
                                    :key="col.key"
                                    class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                >
                                    {{ row[col.key] }}
                                </td>
                                <td class="px-6 py-4 text-right">
                                    <button @click.stop="openRowMenu(row)" class="text-gray-400 hover:text-gray-600 transition-colors">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- Pagination -->
                <div class="mt-6 pt-4 border-t border-gray-200 flex items-center justify-between">
                    <div class="text-sm text-gray-600">
                        Showing <span class="font-semibold">{{ paginationStart }}</span> to <span class="font-semibold">{{ paginationEnd }}</span> of <span class="font-semibold">{{ totalRows }}</span> results
                    </div>
                    <div class="flex items-center space-x-2">
                        <button @click="prevPage" :disabled="currentPage === 1" class="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <button 
                            v-for="page in visiblePages" 
                            :key="page"
                            @click="goToPage(page)"
                            :class="page === currentPage ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
                            class="px-4 py-2 border rounded-lg transition-colors font-medium"
                        >
                            {{ page }}
                        </button>
                        <button @click="nextPage" :disabled="currentPage === totalPages" class="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Filter Dialog Modal -->
        <div v-if="showFilterDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md fade-in">
                <div class="p-6 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <h3 class="text-xl font-bold text-gray-900">Create Filter</h3>
                        <button @click="closeFilterDialog" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                </div>
                
                <div class="p-6 space-y-4">
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Column</label>
                        <select v-model="newFilter.column" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                            <option value="">Select column...</option>
                            <option v-for="col in columns" :key="col.key" :value="col.key">
                                {{ col.label }}
                            </option>
                        </select>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Operator</label>
                        <select v-model="newFilter.operator" class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                            <option value=">=">Greater than or equal (>=)</option>
                            <option value="<=">Less than or equal (<=)</option>
                            <option value="==">Equals (==)</option>
                            <option value="contains">Contains</option>
                        </select>
                    </div>
                    
                    <div>
                        <label class="block text-sm font-semibold text-gray-700 mb-2">Value</label>
                        <input v-model="newFilter.value" type="text" placeholder="Enter value..." class="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                    </div>
                    
                    <div class="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                        <div class="flex items-start">
                            <i class="fas fa-info-circle text-blue-600 mr-3 mt-1"></i>
                            <div>
                                <p class="text-sm font-medium text-blue-900 mb-1">Filter Preview</p>
                                <p class="text-sm text-blue-700">
                                    <strong>{{ previewCount }}</strong> students match this filter
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="p-6 bg-gray-50 rounded-b-2xl flex justify-end space-x-3">
                    <button @click="closeFilterDialog" class="btn-secondary">
                        Cancel
                    </button>
                    <button @click="createFilter" class="btn-primary">
                        <i class="fas fa-check mr-2"></i>
                        Create Filter
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue;
        
        let pybridge = null;
        
        new QWebChannel(qt.webChannelTransport, function(channel) {
            pybridge = channel.objects.pybridge;
            
            createApp({
                data() {
                    return {
                        searchQuery: '',
                        totalStudents: 0,
                        filteredCount: 0,
                        highGPACount: 0,
                        pendingCount: 0,
                        filters: [],
                        columns: [],
                        visibleRows: [],
                        totalRows: 0,
                        currentPage: 1,
                        pageSize: 50,
                        sortColumn: null,
                        sortAsc: true,
                        showFilterDialog: false,
                        newFilter: {
                            column: '',
                            operator: '>=',
                            value: ''
                        },
                        previewCount: 0
                    }
                },
                computed: {
                    totalPages() {
                        return Math.ceil(this.totalRows / this.pageSize);
                    },
                    paginationStart() {
                        return (this.currentPage - 1) * this.pageSize + 1;
                    },
                    paginationEnd() {
                        return Math.min(this.currentPage * this.pageSize, this.totalRows);
                    },
                    visiblePages() {
                        const pages = [];
                        for (let i = Math.max(1, this.currentPage - 2); i <= Math.min(this.totalPages, this.currentPage + 2); i++) {
                            pages.push(i);
                        }
                        return pages;
                    }
                },
                methods: {
                    formatNumber(num) {
                        return num.toLocaleString();
                    },
                    onSearch() {
                        if (pybridge) {
                            pybridge.search(this.searchQuery);
                        }
                    },
                    openLoadDialog() {
                        if (pybridge) {
                            pybridge.loadFile();
                        }
                    },
                    exportData() {
                        if (pybridge) {
                            pybridge.exportData();
                        }
                    },
                    openFilterDialog() {
                        this.showFilterDialog = true;
                    },
                    closeFilterDialog() {
                        this.showFilterDialog = false;
                        this.newFilter = { column: '', operator: '>=', value: '' };
                    },
                    createFilter() {
                        if (pybridge) {
                            pybridge.addFilter(JSON.stringify(this.newFilter));
                        }
                        this.closeFilterDialog();
                    },
                    removeFilter(filter) {
                        if (pybridge) {
                            pybridge.removeFilter(filter.id);
                        }
                    },
                    clearAllFilters() {
                        if (pybridge) {
                            pybridge.clearAllFilters();
                        }
                    },
                    sortBy(column) {
                        if (this.sortColumn === column) {
                            this.sortAsc = !this.sortAsc;
                        } else {
                            this.sortColumn = column;
                            this.sortAsc = true;
                        }
                        if (pybridge) {
                            pybridge.sortColumn(column, this.sortAsc);
                        }
                    },
                    openStudentDetail(row) {
                        if (pybridge) {
                            pybridge.openStudentDetail(row.id);
                        }
                    },
                    openRowMenu(row) {
                        console.log('Row menu:', row);
                    },
                    prevPage() {
                        if (this.currentPage > 1) {
                            this.currentPage--;
                            this.loadPage();
                        }
                    },
                    nextPage() {
                        if (this.currentPage < this.totalPages) {
                            this.currentPage++;
                            this.loadPage();
                        }
                    },
                    goToPage(page) {
                        this.currentPage = page;
                        this.loadPage();
                    },
                    loadPage() {
                        if (pybridge) {
                            pybridge.loadPage(this.currentPage, this.pageSize);
                        }
                    },
                    getFilterIcon(type) {
                        const icons = {
                            'numeric': 'fas fa-hashtag',
                            'text': 'fas fa-font',
                            'date': 'fas fa-calendar'
                        };
                        return icons[type] || 'fas fa-filter';
                    },
                    updateData(data) {
                        const parsed = JSON.parse(data);
                        this.visibleRows = parsed.rows || [];
                        this.columns = parsed.columns || [];
                        this.totalRows = parsed.total || 0;
                        this.totalStudents = parsed.total || 0;
                    },
                    updateFilters(data) {
                        const parsed = JSON.parse(data);
                        this.filters = parsed;
                        this.filteredCount = parsed.reduce((sum, f) => sum + (f.count || 0), 0);
                    },
                    updateStats(data) {
                        const parsed = JSON.parse(data);
                        this.totalStudents = parsed.total || 0;
                        this.filteredCount = parsed.filtered || 0;
                        this.highGPACount = parsed.highGPA || 0;
                        this.pendingCount = parsed.pending || 0;
                    }
                },
                mounted() {
                    // Listen for updates from Python
                    if (pybridge) {
                        pybridge.dataUpdated.connect(this.updateData);
                        pybridge.filterUpdated.connect(this.updateFilters);
                        pybridge.statsUpdated.connect(this.updateStats);
                        
                        this.loadPage();
                    }
                }
            }).mount('#app');
        });
    </script>
</body>
</html>
        """
    
    def load_file_dialog(self):
        """Show file dialog and load data."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.xlsx *.xls *.csv *.tsv *.json);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;TSV Files (*.tsv);;JSON Files (*.json)"
        )
        
        if filepath:
            self.load_file(filepath)
    
    def load_file(self, filepath: str, sheet_name: Optional[str] = None):
        """Load data file."""
        try:
            new_df, needs_sheet, sheets = load_dataframe_from_file(filepath, sheet_name)
            
            if needs_sheet:
                # Show sheet selection (implement dialog)
                sheet = sheets[0]  # Default to first sheet for now
                self.load_file(filepath, sheet)
                return
            
            new_df = add_date_column(new_df)
            
            self.df = new_df
            self.current_file_path = filepath
            self.model.set_dataframe(self.df)
            
            save_last_loaded_file(filepath)
            
            # Update UI
            self._send_data_to_web()
            self._send_stats_to_web()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"Failed to load file:\n\n{str(e)}")
    
    def _send_data_to_web(self, page=1, page_size=50):
        """Send data to JavaScript."""
        if self.df.empty:
            return
        
        start = (page - 1) * page_size
        end = start + page_size
        
        page_df = self.df.iloc[start:end].copy()
        
        # Convert timestamps and other non-serializable types to strings
        for col in page_df.columns:
            if pd.api.types.is_datetime64_any_dtype(page_df[col]):
                page_df[col] = page_df[col].astype(str)
            elif page_df[col].dtype == 'object':
                # Convert any remaining objects to strings
                page_df[col] = page_df[col].apply(lambda x: str(x) if pd.notna(x) else '')
        
        # Replace NaN with None for proper JSON serialization
        page_df = page_df.where(pd.notna(page_df), None)
        
        data = {
            'rows': page_df.to_dict('records'),
            'columns': [{'key': col, 'label': col} for col in self.df.columns],
            'total': len(self.df)
        }
        
        # Use default=str to handle any remaining non-serializable objects
        self.bridge.dataUpdated.emit(json.dumps(data, default=str))
    
    def _send_filters_to_web(self):
        """Send filters to JavaScript."""
        filters_data = []
        for i, filter_rule in enumerate(self.active_filters):
            filters_data.append({
                'id': id(filter_rule),
                'label': str(filter_rule),
                'type': filter_rule.__class__.__name__.replace('Filter', '').lower(),
                'count': 0  # Calculate actual count
            })
        
        self.bridge.filterUpdated.emit(json.dumps(filters_data, default=str))
    
    def _send_stats_to_web(self):
        """Send statistics to JavaScript."""
        stats = {
            'total': len(self.df),
            'filtered': 0,  # Calculate
            'highGPA': 0,   # Calculate
            'pending': 0    # Calculate
        }
        
        if not self.df.empty and 'GPA' in self.df.columns:
            stats['highGPA'] = len(self.df[self.df['GPA'] >= 3.5])
        
        self.bridge.statsUpdated.emit(json.dumps(stats, default=str))
    
    def perform_search(self, query):
        """Perform search."""
        # Implement search logic
        pass
    
    def export_dialog(self):
        """Show export dialog."""
        # Implement export
        pass
    
    def add_filter_from_web(self, filter_data):
        """Add filter from web UI."""
        # Implement filter creation
        pass
    
    def remove_filter_by_id(self, filter_id):
        """Remove filter by ID."""
        # Implement filter removal
        pass
    
    def clear_all_filters(self):
        """Clear all filters."""
        self.active_filters.clear()
        self._send_filters_to_web()
        self._send_data_to_web()
    
    def switch_tab(self, tab_id):
        """Switch active tab."""
        # Implement tab switching
        pass
    
    def create_new_tab(self):
        """Create new tab."""
        # Implement tab creation
        pass
    
    def sort_by_column(self, column, ascending):
        """Sort data by column."""
        if not self.df.empty and column in self.df.columns:
            self.df = self.df.sort_values(by=column, ascending=ascending)
            self._send_data_to_web()
    
    def show_student_detail(self, student_id):
        """Show student detail view."""
        # Implement detail view
        pass
    
    def load_data_page(self, page, page_size):
        """Load specific page of data."""
        self._send_data_to_web(page, page_size)
    
    def _autoload_last_file(self):
        """Auto-load last file."""
        last_file = get_last_loaded_file()
        if last_file and os.path.exists(last_file):
            self.load_file(last_file)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Student Admissions Manager - Modern Web UI")
    
    window = ModernWebMainWindow()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())