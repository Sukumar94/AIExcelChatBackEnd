"""
AI Agent - orchestrates the LLM, SQL generation, and tool usage.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.ai.llm import LLMService
from app.ai.rag import RAGService
from app.database.schema_manager import SchemaManager

logger = logging.getLogger(__name__)


class AIAgent:
    """
    AI Agent that processes natural language questions about Excel data.
    Uses a multi-step approach:
    1. Understand the question and schema
    2. Generate SQL if needed
    3. Execute SQL against DuckDB
    4. Generate natural language answer
    5. Optionally generate chart config
    """

    def __init__(self) -> None:
        self.llm = LLMService()
        self.rag = RAGService()
        self.schema_manager = SchemaManager()

    def process(
        self,
        question: str,
        schema_context: str,
        sheet_name: str,
        session_id: str,
        chat_history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Process a question and return the answer with optional SQL and chart.
        """
        # Get relevant context from RAG
        rag_context = self.rag.get_relevant_context(question, session_id)

        # Build chat history context
        history_context = ""
        if chat_history:
            history_parts = []
            for h in chat_history[-3:]:  # Last 3 messages
                history_parts.append(f"User: {h['question']}\nAssistant: {h['answer']}")
            history_context = "\n\n".join(history_parts)

        # Step 1: Determine if SQL is needed
        needs_sql = self._should_use_sql(question, schema_context)

        sql_query = None
        chart_config = None
        answer = ""

        if needs_sql:
            # Step 2: Generate SQL
            sql_query = self._generate_sql(question, schema_context, sheet_name, session_id, history_context, rag_context)

            if sql_query:
                # Step 3: Execute SQL
                try:
                    result_df = self.schema_manager.execute_query(session_id, sheet_name, sql_query)
                    result_preview = result_df.head(20).to_dicts() if result_df.height > 0 else []

                    # Step 4: Generate answer from results
                    answer = self._generate_answer_from_results(
                        question, sql_query, result_preview, result_df.height, schema_context
                    )

                    # Step 5: Check if chart is appropriate
                    if result_df.height > 0 and result_df.width >= 2:
                        chart_config = self._suggest_chart(question, result_df, sql_query)

                except Exception as e:
                    logger.warning("SQL execution failed: %s", e)
                    answer = self._generate_direct_answer(question, schema_context, history_context, rag_context)
            else:
                answer = self._generate_direct_answer(question, schema_context, history_context, rag_context)
        else:
            answer = self._generate_direct_answer(question, schema_context, history_context, rag_context)

        # Store in RAG for future context
        self.rag.add_query_history(session_id, question, answer, sql_query)

        return {
            "answer": answer,
            "sql_query": sql_query,
            "chart_config": chart_config,
            "sources": [sheet_name],
        }

    def _should_use_sql(self, question: str, schema_context: str) -> bool:
        """Determine if the question requires SQL query execution."""
        sql_indicators = [
            "how many", "count", "sum", "average", "total", "maximum", "minimum",
            "compare", "top", "bottom", "highest", "lowest", "most", "least",
            "group by", "filter", "where", "sort", "order", "percentage",
            "trend", "distribution", "correlation", "statistics",
            "calculate", "compute", "find", "list", "show me", "what is",
            "greater than", "less than", "between",
        ]
        q_lower = question.lower()
        return any(indicator in q_lower for indicator in sql_indicators)

    def _generate_sql(
        self,
        question: str,
        schema_context: str,
        sheet_name: str,
        session_id: str,
        history_context: str,
        rag_context: str,
    ) -> str | None:
        """Generate SQL query from natural language."""
        view_name = f"session_{session_id[:8]}_{sheet_name}"

        prompt = f"""You are an expert SQL analyst. Given a question about data and the table schema, generate a DuckDB-compatible SQL query.

TABLE SCHEMA:
{schema_context}

The table is available as a view named: {view_name}

PREVIOUS CONTEXT:
{history_context}

{rag_context}

USER QUESTION: {question}

RULES:
1. Use ONLY the columns shown in the schema above
2. Use DuckDB-compatible SQL syntax
3. Always use the view name: {view_name}
4. Limit results to 100 rows unless asked otherwise
5. Use proper aggregations (COUNT, SUM, AVG, MIN, MAX) when needed
6. Use GROUP BY with aggregations
7. Use ORDER BY for sorting
8. Return ONLY the SQL query, no explanation, no markdown formatting
9. The query must start with SELECT"""

        try:
            response = self.llm.ask(prompt)
            # Clean the response to extract just the SQL
            sql = response.strip()
            # Remove markdown code blocks if present
            sql = re.sub(r"```sql\s*", "", sql, flags=re.IGNORECASE)
            sql = re.sub(r"```\s*", "", sql)
            sql = sql.strip()

            if sql.upper().startswith("SELECT"):
                return sql
            logger.warning("Generated query doesn't start with SELECT: %s", sql[:100])
            return None
        except Exception as e:
            logger.error("SQL generation failed: %s", e)
            return None

    def _generate_answer_from_results(
        self,
        question: str,
        sql_query: str,
        results: list[dict[str, Any]],
        row_count: int,
        schema_context: str,
    ) -> str:
        """Generate a natural language answer from SQL results."""
        results_str = json.dumps(results[:10], indent=2, default=str)

        prompt = f"""You are a data analyst. Given a user question, the SQL query used, and the results, provide a clear, concise answer.

USER QUESTION: {question}

SQL QUERY: {sql_query}

RESULTS ({row_count} rows returned):
```json
{results_str}
```

Provide a helpful, natural language answer. Include specific numbers from the results. If there are many rows, summarize the key findings. Do not mention the SQL query unless asked."""
        try:
            return self.llm.ask(prompt)
        except Exception as e:
            logger.error("Answer generation failed: %s", e)
            return f"Found {row_count} results. Here's the data: {results_str[:500]}"

    def _generate_direct_answer(
        self,
        question: str,
        schema_context: str,
        history_context: str,
        rag_context: str,
    ) -> str:
        """Generate a direct answer without SQL (for general questions)."""
        prompt = f"""You are an AI data analyst assistant. You help users understand their Excel data.

WORKBOOK SCHEMA:
{schema_context}

PREVIOUS CONVERSATION:
{history_context}

{rag_context}

USER QUESTION: {question}

Provide a helpful answer based on the available data. If the question requires calculations or specific data lookups, explain what data would be needed. Be concise and specific."""
        try:
            return self.llm.ask(prompt)
        except Exception as e:
            logger.error("Direct answer failed: %s", e)
            return "I'm unable to process this question at the moment. Please try again."

    def _suggest_chart(self, question: str, df: Any, sql_query: str) -> dict[str, Any] | None:
        """Suggest a chart configuration based on the query results."""
        cols = df.columns
        numeric_cols = [c for c in cols if df[c].dtype in (
            "Float32", "Float64", "Int8", "Int16", "Int32", "Int64"
        )]
        categorical_cols = [c for c in cols if df[c].dtype == "Utf8"]

        if not numeric_cols:
            return None

        chart_type = "bar"
        x_axis = categorical_cols[0] if categorical_cols else cols[0]
        y_axis = numeric_cols[0]

        # Determine chart type from question
        q_lower = question.lower()
        if any(w in q_lower for w in ["trend", "over time", "change", "growth"]):
            chart_type = "line"
        elif any(w in q_lower for w in ["distribution", "histogram", "spread"]):
            chart_type = "histogram"
            x_axis = numeric_cols[0]
            y_axis = None
        elif any(w in q_lower for w in ["pie", "proportion", "share", "percentage"]):
            chart_type = "pie"
        elif any(w in q_lower for w in ["correlation", "relationship", "scatter"]):
            chart_type = "scatter"
            if len(numeric_cols) >= 2:
                x_axis = numeric_cols[0]
                y_axis = numeric_cols[1]

        return {
            "chart_type": chart_type,
            "title": f"Chart: {question[:50]}",
            "x_axis": x_axis,
            "y_axis": y_axis,
        }