"""
Prompt management - templates and system prompts.
"""

from __future__ import annotations

from typing import Any


class PromptManager:
    """Manages system prompts and templates for the LLM."""

    SYSTEM_PROMPT = """You are an AI Data Analyst assistant integrated with an Excel analytics platform.
Your role is to help users understand and analyze their uploaded Excel data.

Capabilities:
- Answer questions about data in uploaded workbooks
- Generate SQL queries to analyze data
- Create charts and visualizations
- Provide statistical summaries
- Generate reports

Guidelines:
1. Always base answers on the actual data in the workbook
2. Do not invent or hallucinate data
3. If you're unsure, say so
4. Be concise and specific
5. Use numbers and statistics from the data
6. Suggest visualizations when appropriate
7. Reference specific column names and values"""

    @staticmethod
    def sql_generation_prompt(
        question: str,
        schema: str,
        view_name: str,
        history: str = "",
    ) -> str:
        """Build a prompt for SQL generation."""
        return f"""You are an expert SQL analyst. Generate a DuckDB SQL query.

Table: {view_name}
Schema:
{schema}

Previous conversation:
{history}

Question: {question}

Generate ONLY the SQL query. No explanation. No markdown."""

    @staticmethod
    def answer_prompt(
        question: str,
        sql: str,
        results: list[dict[str, Any]],
        row_count: int,
    ) -> str:
        """Build a prompt for generating answers from SQL results."""
        return f"""Question: {question}
SQL: {sql}
Results ({row_count} rows): {results[:10]}

Provide a clear, concise answer using the data above."""

    @staticmethod
    def chart_suggestion_prompt(
        question: str,
        columns: list[str],
        numeric_cols: list[str],
        categorical_cols: list[str],
    ) -> str:
        """Build a prompt for chart suggestions."""
        return f"""Based on this question: "{question}"

Available columns:
- All: {columns}
- Numeric: {numeric_cols}
- Categorical: {categorical_cols}

Suggest a chart configuration as JSON:
{{
    "chart_type": "bar|line|pie|scatter|histogram|box",
    "x_axis": "column_name",
    "y_axis": "column_name",
    "title": "Chart title"
}}"""