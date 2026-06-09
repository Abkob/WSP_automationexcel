from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from services.excel_schema import EXPECTED_WSP_COLUMNS


@pytest.fixture
def sample_workbook_path(tmp_path: Path) -> Path:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Sheet1"
    worksheet.append(EXPECTED_WSP_COLUMNS)
    worksheet.append(
        [
            "1001",
            "Test Student",
            "Computer Science",
            "Senior",
            "student@example.com",
            "English",
            "English, Arabic",
            "Planning",
            "Python, Excel",
            "Teamwork",
            "Documentation",
            "Office assistant",
            "Admin",
            "Data analysis",
            "N",
            202610,
            "N",
            "70123456",
            "N",
            "2026-06-03",
            3.4,
            "Active",
            "R",
            "Regular",
            "Y",
            "Y",
            "UG",
            "AS",
            90,
            202610,
            None,
            None,
            None,
            "N",
            "N",
            "N",
            "N",
            "Y",
            "N",
        ]
    )
    path = tmp_path / "sample_wsp.xlsx"
    workbook.save(path)
    return path

