# Student Admissions Manager - Web Version

A modern, web-based alternative to the PyQt desktop application with all the same functionality.

## 🚀 Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements_web.txt
```

2. Run the application:
```bash
streamlit run web_app.py
```

3. Open your browser to the URL shown (typically `http://localhost:8501`)

## ✨ Features

### All PyQt Functionality - Now in Your Browser!

#### 📁 File Operations
- **Load Files**: Upload Excel (.xlsx, .xls), CSV, TSV, or JSON files
- **Export Data**: Download filtered results as Excel or CSV
- **No Installation Required**: Runs in any modern web browser

#### 🔍 Smart Search
- **Global Search**: Search across all columns simultaneously
- **Column-Specific Search**: Target specific fields for precise results
- **Real-time Filtering**: See results update as you type

#### ⚙️ Advanced Filtering
- **Multiple Filter Rules**: Create complex filter combinations
- **AND/OR Logic**: Combine rules with ALL (AND) or ANY (OR)
- **Filter Types**:
  - **Numeric**: >, >=, <, <=, ==, !=, range
  - **Text**: contains, starts with, ends with, exact match
  - **Date**: before, after, between (for datetime columns)
- **Visual Filter Chips**: See all active filters at a glance
- **Easy Management**: Add or remove filters with one click

#### ⚡ Quick Filters (One-Click)
- **GPA ≥ 3.5**: High performers
- **GPA 2.5-3.5**: Average range
- **GPA < 2.5**: At-risk students
- **Active**: Currently enrolled
- **Probation**: Academic probation status

#### 📊 Data Visualization
- **Interactive Table**: Sort, search, and explore your data
- **Real-time Stats**:
  - Total rows
  - Filtered rows
  - Active filters count
  - Column count
- **Column Statistics**: View statistical summary of all columns

## 🎨 Modern UI Features

### Design Improvements Over PyQt

1. **Responsive Layout**: Automatically adapts to screen size
2. **No Installation**: Runs in browser, no Qt dependencies
3. **Cloud Ready**: Can be deployed to web servers
4. **Better Variability**: Easy to customize colors, layouts, and components
5. **Modern Aesthetics**: Clean, gradient headers and smooth animations
6. **Cross-Platform**: Works on Windows, Mac, Linux, tablets, phones

### Visual Design
- Gradient header with modern color scheme
- Clean stat cards with highlighted values
- Filter chips with emoji icons
- Smooth hover effects and transitions
- Professional color palette (blue primary, green success, red error)

## 📖 How to Use

### Basic Workflow

1. **Load Data**
   - Click "Browse files" in the sidebar
   - Select your Excel/CSV file
   - Data loads automatically

2. **Search Data**
   - Use the search bar to find specific records
   - Select "Global" to search all columns, or pick a specific column

3. **Apply Filters**
   - Click "➕ Add New Rule" in the sidebar
   - Select column, operator, and value
   - Click "Add Rule"
   - Repeat for multiple filters
   - Choose AND/ALL or OR/ANY mode

4. **Quick Filter Shortcuts**
   - Click any quick filter button (GPA ranges, Status)
   - Filter applies immediately

5. **Export Results**
   - Click "📊 Excel" or "📋 CSV" in the sidebar
   - Exports current filtered view
   - Downloads automatically to your browser

6. **View Statistics**
   - Expand "📈 Column Statistics" to see data summary
   - View mean, std, min, max, quartiles for numeric columns

### Managing Filters

- **Add Filter**: Expand "➕ Add New Rule" → select options → click "Add Rule"
- **Remove Filter**: Click 🗑️ next to any filter chip
- **Clear All**: Click "✕ Clear All" button
- **Change Mode**: Toggle between ALL (AND) and ANY (OR) radio buttons

## 🆚 Comparison: Web vs PyQt Desktop

| Feature | PyQt Desktop | Web Version |
|---------|--------------|-------------|
| Installation | Requires Python + PyQt5 | Just Python + Streamlit |
| Platform | Windows/Mac/Linux desktop | Any device with browser |
| Deployment | Local only | Can deploy to cloud |
| UI Framework | Qt (C++) | HTML/CSS/JavaScript |
| Customization | Requires Qt knowledge | Standard web technologies |
| File Handling | Native file dialogs | Browser upload/download |
| Performance | Fast, native | Fast, browser-based |
| Tabs | Multiple custom tabs | Single view (simpler) |
| State Management | Qt signals/slots | Streamlit session state |
| Updates | Manual recompile | Hot reload |

## 🔧 Technical Details

### Architecture

```
web_app.py
├── Streamlit UI Components
├── Session State Management
│   ├── df (original data)
│   ├── filtered_df (current view)
│   ├── filters (active rules)
│   └── search state
├── Data Processing
│   ├── load_data_file() - File loading
│   ├── apply_filters() - Filter logic
│   └── apply_search() - Search logic
└── Export Functions
    ├── export_to_excel()
    └── export_to_csv()
```

### Session State Variables

- `df`: Original loaded DataFrame
- `filtered_df`: Current filtered/searched view
- `filters`: List of active filter rules
- `filter_mode`: 'all' (AND) or 'any' (OR)
- `search_text`: Current search query
- `search_column`: Target column for search
- `current_file`: Loaded filename

### Filter Rule Format

```python
{
    'column': 'GPA',
    'operator': '>=',
    'value': 3.5
}
```

## 🚀 Deployment Options

### Local Use
```bash
streamlit run web_app.py
```

### Deploy to Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to share.streamlit.io
3. Connect repository
4. Deploy in one click

### Deploy to Other Platforms
- **Heroku**: Use Procfile with streamlit
- **AWS/Azure/GCP**: Use Docker container
- **Replit**: Direct import and run

## 🎯 Advantages of Web Version

1. **No Installation Hassles**: Users just need a browser
2. **Better Collaboration**: Share URL instead of installing software
3. **Cloud Storage**: Easy integration with cloud databases
4. **Mobile Friendly**: Works on tablets and phones
5. **Easier Updates**: Push to server, everyone gets update
6. **Modern Stack**: Leverage web ecosystem (React, Vue later if needed)
7. **Better Accessibility**: Screen readers, keyboard navigation
8. **Easier Customization**: CSS is easier than Qt stylesheets

## 🛠️ Customization

### Change Colors
Edit the CSS in the `st.markdown()` section at the top of `web_app.py`:
```css
--primary: #3B82F6;  /* Change to your brand color */
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
```

### Add New Features
- **Charts**: Use `st.line_chart()`, `st.bar_chart()`, etc.
- **Maps**: Use `st.map()` for geographic data
- **Custom Components**: Use Streamlit components library

### Modify Layout
- Change `layout="wide"` to `layout="centered"` in `st.set_page_config()`
- Adjust column ratios in `st.columns([3, 1])`
- Modify sidebar with `st.sidebar` elements

## 📝 Future Enhancements

Potential additions to match PyQt version completely:

1. **Multiple Tabs**: Use `st.tabs()` for different views
2. **Archives**: Add archive management with file uploads
3. **Custom Views**: Save filter combinations as presets
4. **User Authentication**: Add login/user management
5. **Database Integration**: Connect to SQL databases
6. **Real-time Collaboration**: Multiple users simultaneously
7. **Advanced Charts**: Add Plotly/Altair visualizations
8. **PDF Export**: Generate PDF reports
9. **Email Integration**: Send filtered results via email
10. **Scheduled Reports**: Automated daily/weekly exports

## 🐛 Troubleshooting

### Port Already in Use
```bash
streamlit run web_app.py --server.port 8502
```

### File Upload Size Limit
Increase in `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200
```

### Memory Issues with Large Files
Use chunked reading or database backend for large datasets (>100MB)

### Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

## 💡 Tips

1. **Large Files**: For files >50MB, consider using Parquet format
2. **Performance**: Use `@st.cache_data` decorator for expensive operations
3. **Debugging**: Add `st.write()` to inspect variables during development
4. **State**: Clear session state with browser refresh (Ctrl+F5)
5. **Hot Reload**: Edit code and save - page auto-refreshes

## 🎓 Example Usage

```python
# Load sample data
# 1. Run: streamlit run web_app.py
# 2. Upload: students.xlsx
# 3. Quick filter: Click "GPA ≥ 3.5"
# 4. Search: Type "Computer Science" in search box
# 5. Export: Click "📊 Excel" button
```

## ✅ Feature Parity Checklist

- ✅ File loading (Excel, CSV, TSV, JSON)
- ✅ Search (global + column-specific)
- ✅ Advanced filtering (numeric, text, date)
- ✅ AND/OR filter logic
- ✅ Quick filters (one-click)
- ✅ Export to Excel
- ✅ Export to CSV
- ✅ Real-time statistics
- ✅ Column statistics
- ✅ Modern UI design
- ✅ Filter management (add/remove)
- ✅ Interactive data table
- ⚠️ Multiple tabs (can be added with `st.tabs()`)
- ⚠️ Archives (can be added with file management)
- ⚠️ Rule-based tabs (can be added)
- ⚠️ Custom tab naming (can be added)

## 🎉 Conclusion

This web version provides all the core functionality of the PyQt desktop app with these key improvements:

- **Easier to use**: No installation required
- **More accessible**: Works on any device
- **Easier to customize**: Standard web technologies
- **Cloud-ready**: Deploy anywhere
- **Modern design**: Clean, professional interface

Start exploring your data today - just run `streamlit run web_app.py`! 🚀
