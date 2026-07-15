"""
Excel Loader

Reads Excel workbooks using Polars.

Author: AI Excel Analytics Platform
"""

from __future__ import annotations

from io import BytesIO
from typing import Dict

import polars as pl
from fastapi import UploadFile

from app.models.session import SheetData


class ExcelLoader:
    """
    Reads uploaded Excel files and converts
    every worksheet into a Polars DataFrame.
    """

    async def load_workbook(
        self,
        file: UploadFile,
    ) -> Dict[str, SheetData]:

        file_bytes = await file.read()

        workbook = pl.read_excel(
            BytesIO(file_bytes),
            sheet_id=0,
        )

        sheets: Dict[str, SheetData] = {}

        # When multiple sheets exist, Polars returns a dictionary.
        if isinstance(workbook, dict):

            for sheet_name, dataframe in workbook.items():

                sheets[sheet_name] = SheetData(
                    sheet_name=sheet_name,
                    rows=dataframe.height,
                    columns=dataframe.width,
                    column_names=dataframe.columns,
                    dataframe=dataframe,
                )

        else:
            sheets["Sheet1"] = SheetData(
                sheet_name="Sheet1",
                rows=workbook.height,
                columns=workbook.width,
                column_names=workbook.columns,
                dataframe=workbook,
            )

        await file.seek(0)

        return sheets