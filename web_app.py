"""
Student Admissions Manager - Web Version
Streamlit-based web UI with all PyQt functionality
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import io

# Page configuration
st.set_page_config(
    page_title="Student Admissions Manager",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary: #3B82F6;
        --primary-dark: #2563EB;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
        --info: #06B6D4;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }

    .app-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }

    .app-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
    }

    /* Stats card */
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #3B82F6;
    }

    .stat-label {
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Filter chip */
    .filter-chip {
        display: inline-block;
        background: #EFF6FF;
        color: #3B82F6;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 2px solid #3B82F6;
        margin: 0.25rem;
        font-weight: 600;
        font-size: 0.875rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f9fafb;
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* Button styling */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* File uploader */
    .uploadedFile {
        border: 2px dashed #3B82F6;
        border-radius: 8px;
    }

    /* Dataframe styling */
    .dataframe {
        font-size: 0.875rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = None
if 'filters' not in st.session_state:
    st.session_state.filters = []
if 'tabs' not in st.session_state:
    st.session_state.tabs = []
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'filter_mode' not in st.session_state:
    st.session_state.filter_mode = 'all'
if 'search_text' not in st.session_state:
    st.session_state.search_text = ''
if 'search_column' not in st.session_state:
    st.session_state.search_column = 'Global'


def load_data_file(uploaded_file) -> pd.DataFrame:
    """Load data from uploaded file."""
    try:
        file_extension = Path(uploaded_file.name).suffix.lower()

        if file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension == '.tsv':
            df = pd.read_csv(uploaded_file, sep='\t')
        elif file_extension == '.json':
            df = pd.read_json(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None

        st.session_state.current_file = uploaded_file.name
        return df

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


def apply_filters(df: pd.DataFrame, filters: List[Dict], mode: str = 'all') -> pd.DataFrame:
    """Apply filters to dataframe."""
    if not filters or df is None:
        return df

    masks = []

    for filter_rule in filters:
        column = filter_rule['column']
        operator = filter_rule['operator']
        value = filter_rule['value']

        if column not in df.columns:
            continue

        # Numeric filters
        if operator == '>':
            mask = df[column] > value
        elif operator == '>=':
            mask = df[column] >= value
        elif operator == '<':
            mask = df[column] < value
        elif operator == '<=':
            mask = df[column] <= value
        elif operator == '==':
            mask = df[column] == value
        elif operator == '!=':
            mask = df[column] != value
        elif operator == 'range':
            mask = (df[column] >= value[0]) & (df[column] <= value[1])

        # Text filters
        elif operator == 'contains':
            mask = df[column].astype(str).str.contains(str(value), case=False, na=False)
        elif operator == 'startswith':
            mask = df[column].astype(str).str.startswith(str(value), na=False)
        elif operator == 'endswith':
            mask = df[column].astype(str).str.endswith(str(value), na=False)
        elif operator == 'exact':
            mask = df[column].astype(str) == str(value)

        # Date filters (assuming datetime columns)
        elif operator == 'before':
            mask = pd.to_datetime(df[column]) < pd.to_datetime(value)
        elif operator == 'after':
            mask = pd.to_datetime(df[column]) > pd.to_datetime(value)
        elif operator == 'between':
            mask = (pd.to_datetime(df[column]) >= pd.to_datetime(value[0])) & \
                   (pd.to_datetime(df[column]) <= pd.to_datetime(value[1]))
        else:
            continue

        masks.append(mask)

    if not masks:
        return df

    # Combine masks based on mode
    if mode == 'all':
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask & mask
    else:  # any
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask | mask

    return df[combined_mask]


def apply_search(df: pd.DataFrame, search_text: str, search_column: str) -> pd.DataFrame:
    """Apply search filter to dataframe."""
    if not search_text or df is None:
        return df

    if search_column == 'Global':
        # Search across all columns
        mask = df.astype(str).apply(lambda x: x.str.contains(search_text, case=False, na=False)).any(axis=1)
    else:
        # Search in specific column
        mask = df[search_column].astype(str).str.contains(search_text, case=False, na=False)

    return df[mask]


def export_to_excel(df: pd.DataFrame, filename: str = "export.xlsx") -> bytes:
    """Export dataframe to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()


def export_to_csv(df: pd.DataFrame) -> str:
    """Export dataframe to CSV string."""
    return df.to_csv(index=False)


# ============================================================================
# MAIN APP LAYOUT
# ============================================================================

# Header
st.markdown("""
<div class="app-header">
    <h1>🎓 Student Admissions Manager</h1>
    <p>Filter, analyze, and export student data with ease</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - File Operations & Filters
with st.sidebar:
    st.header("📁 File Operations")

    # File upload
    uploaded_file = st.file_uploader(
        "Load Data File",
        type=['xlsx', 'xls', 'csv', 'tsv', 'json'],
        help="Upload Excel, CSV, TSV, or JSON file"
    )

    if uploaded_file is not None:
        if st.session_state.df is None or st.session_state.current_file != uploaded_file.name:
            with st.spinner("Loading file..."):
                st.session_state.df = load_data_file(uploaded_file)
                if st.session_state.df is not None:
                    st.success(f"✓ Loaded {uploaded_file.name}")

    # Export options
    if st.session_state.df is not None:
        st.divider()
        st.header("📤 Export Data")

        export_df = st.session_state.filtered_df if st.session_state.filtered_df is not None else st.session_state.df

        col1, col2 = st.columns(2)

        with col1:
            excel_data = export_to_excel(export_df)
            st.download_button(
                label="📊 Excel",
                data=excel_data,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            csv_data = export_to_csv(export_df)
            st.download_button(
                label="📋 CSV",
                data=csv_data,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # Filter Panel
    st.divider()
    st.header("⚙️ Filter Rules")

    if st.session_state.df is not None:
        # Filter mode
        filter_mode = st.radio(
            "Combine rules:",
            options=['all', 'any'],
            format_func=lambda x: 'ALL (AND)' if x == 'all' else 'ANY (OR)',
            horizontal=True
        )
        st.session_state.filter_mode = filter_mode

        # Add new filter
        with st.expander("➕ Add New Rule", expanded=False):
            columns = list(st.session_state.df.columns)

            filter_column = st.selectbox("Column", columns, key="new_filter_column")

            # Determine column type
            col_dtype = st.session_state.df[filter_column].dtype

            if pd.api.types.is_numeric_dtype(col_dtype):
                # Numeric filter
                filter_operator = st.selectbox(
                    "Operator",
                    options=['>', '>=', '<', '<=', '==', '!=', 'range'],
                    key="new_filter_operator"
                )

                if filter_operator == 'range':
                    col1, col2 = st.columns(2)
                    with col1:
                        min_val = st.number_input("Min", value=float(st.session_state.df[filter_column].min()))
                    with col2:
                        max_val = st.number_input("Max", value=float(st.session_state.df[filter_column].max()))
                    filter_value = (min_val, max_val)
                else:
                    filter_value = st.number_input("Value", value=0.0)

            else:
                # Text filter
                filter_operator = st.selectbox(
                    "Operator",
                    options=['contains', 'startswith', 'endswith', 'exact'],
                    key="new_filter_operator"
                )
                filter_value = st.text_input("Value", key="new_filter_value")

            if st.button("Add Rule", type="primary", use_container_width=True):
                new_filter = {
                    'column': filter_column,
                    'operator': filter_operator,
                    'value': filter_value
                }
                st.session_state.filters.append(new_filter)
                st.rerun()

        # Display active filters
        if st.session_state.filters:
            st.subheader(f"{len(st.session_state.filters)} Active Rules")

            for idx, filter_rule in enumerate(st.session_state.filters):
                col1, col2 = st.columns([4, 1])

                with col1:
                    # Display filter as chip
                    if filter_rule['operator'] == 'range':
                        filter_text = f"{filter_rule['column']} {filter_rule['operator']} ({filter_rule['value'][0]}, {filter_rule['value'][1]})"
                    else:
                        filter_text = f"{filter_rule['column']} {filter_rule['operator']} {filter_rule['value']}"

                    st.markdown(f"<div class='filter-chip'>{filter_text}</div>", unsafe_allow_html=True)

                with col2:
                    if st.button("🗑️", key=f"remove_filter_{idx}", help="Remove rule"):
                        st.session_state.filters.pop(idx)
                        st.rerun()

            if st.button("✕ Clear All", use_container_width=True):
                st.session_state.filters = []
                st.rerun()

# Main Content Area
if st.session_state.df is None:
    # Welcome screen
    st.info("👈 Upload a data file to get started")
    st.markdown("""
    ### Getting Started

    1. **Upload** your data file (Excel, CSV, TSV, or JSON)
    2. **Filter** your data using the sidebar
    3. **Search** for specific records
    4. **Export** filtered results

    ### Features

    - 🔍 **Smart Search**: Search across all columns or specific fields
    - ⚙️ **Advanced Filtering**: Create complex filter rules with AND/OR logic
    - 📊 **Multiple Export Formats**: Export to Excel or CSV
    - 📈 **Real-time Stats**: See row counts and filter statistics
    - 🎯 **Quick Filters**: One-click GPA and status filters
    """)

else:
    # Apply filters and search
    working_df = st.session_state.df.copy()

    if st.session_state.filters:
        working_df = apply_filters(working_df, st.session_state.filters, st.session_state.filter_mode)

    if st.session_state.search_text:
        working_df = apply_search(working_df, st.session_state.search_text, st.session_state.search_column)

    st.session_state.filtered_df = working_df

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(st.session_state.df):,}</div>
            <div class="stat-label">Total Rows</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(working_df):,}</div>
            <div class="stat-label">Filtered Rows</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(st.session_state.filters)}</div>
            <div class="stat-label">Active Filters</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(st.session_state.df.columns)}</div>
            <div class="stat-label">Columns</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Search bar
    col1, col2 = st.columns([3, 1])

    with col1:
        search_text = st.text_input(
            "🔍 Search",
            value=st.session_state.search_text,
            placeholder="Search students by name, ID, status...",
            label_visibility="collapsed"
        )
        st.session_state.search_text = search_text

    with col2:
        search_options = ['Global'] + list(st.session_state.df.columns)
        search_column = st.selectbox(
            "Search in",
            options=search_options,
            index=search_options.index(st.session_state.search_column) if st.session_state.search_column in search_options else 0,
            label_visibility="collapsed"
        )
        st.session_state.search_column = search_column

    # Quick filters
    st.subheader("⚡ Quick Filters")
    qf_col1, qf_col2, qf_col3, qf_col4, qf_col5 = st.columns(5)

    with qf_col1:
        if st.button("GPA ≥ 3.5", use_container_width=True):
            if 'GPA' in st.session_state.df.columns:
                st.session_state.filters.append({'column': 'GPA', 'operator': '>=', 'value': 3.5})
                st.rerun()

    with qf_col2:
        if st.button("GPA 2.5-3.5", use_container_width=True):
            if 'GPA' in st.session_state.df.columns:
                st.session_state.filters.append({'column': 'GPA', 'operator': 'range', 'value': (2.5, 3.5)})
                st.rerun()

    with qf_col3:
        if st.button("GPA < 2.5", use_container_width=True):
            if 'GPA' in st.session_state.df.columns:
                st.session_state.filters.append({'column': 'GPA', 'operator': '<', 'value': 2.5})
                st.rerun()

    with qf_col4:
        if st.button("Active", use_container_width=True):
            if 'Status' in st.session_state.df.columns:
                st.session_state.filters.append({'column': 'Status', 'operator': 'contains', 'value': 'Active'})
                st.rerun()

    with qf_col5:
        if st.button("Probation", use_container_width=True):
            if 'Status' in st.session_state.df.columns:
                st.session_state.filters.append({'column': 'Status', 'operator': 'contains', 'value': 'Probation'})
                st.rerun()

    st.divider()

    # Data table
    st.subheader(f"📊 Data View ({len(working_df):,} rows)")

    # Display dataframe with interactive features
    st.dataframe(
        working_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )

    # Column statistics
    with st.expander("📈 Column Statistics"):
        st.write(working_df.describe())
