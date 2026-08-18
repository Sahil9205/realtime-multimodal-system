"""
Built-in tools for the agent system.
"""

from __future__ import annotations

import math
from datetime import datetime

from app.agents.tools import BaseTool, ToolDefinition, ToolParameter, ToolResult

from app.core.logging import get_logger


logger = get_logger(__name__)


class CalculatorTool(BaseTool):
    """
    Calculator tool for mathematical operations.
    """

    def get_definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="calculator",
            description="Perform mathematical calculations. Supports +, -, *, /, %, **, sqrt, sin, cos, tan, log, exp.",
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="Mathematical expression to evaluate (e.g., '2 + 2' or 'sqrt(16)' or 'sin(3.14)').",
                    required=True,
                )
            ],
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute calculator."""
        try:
            expression = kwargs.get("expression", "")

            if not expression:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Expression is required.",
                )

            # Safe evaluation with limited scope
            safe_dict = {
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
            }

            result = eval(expression, {"__builtins__": {}}, safe_dict)

            logger.info(
                "Calculator evaluated: %s = %s",
                expression,
                result,
            )

            return ToolResult(
                success=True,
                result=result,
            )

        except Exception as exc:
            error_msg = f"Calculation failed: {str(exc)}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
            )


class CurrentTimeTool(BaseTool):
    """
    Tool to get current date and time.
    """

    def get_definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="current_time",
            description="Get the current date and time.",
            parameters=[],
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute time tool."""
        try:
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

            logger.info("Current time retrieved: %s", formatted_time)

            return ToolResult(
                success=True,
                result={
                    "time": formatted_time,
                    "timestamp": now.isoformat(),
                },
            )

        except Exception as exc:
            error_msg = f"Time retrieval failed: {str(exc)}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
            )


class StringToolsTool(BaseTool):
    """
    Tool for string operations.
    """

    def get_definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="string_tools",
            description="Perform string operations like uppercase, lowercase, reverse, length.",
            parameters=[
                ToolParameter(
                    name="operation",
                    type="string",
                    description="Operation to perform: uppercase, lowercase, reverse, length.",
                    required=True,
                ),
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text to operate on.",
                    required=True,
                ),
            ],
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute string tools."""
        try:
            operation = kwargs.get("operation", "").lower()
            text = kwargs.get("text", "")

            if not operation or not text:
                return ToolResult(
                    success=False,
                    result=None,
                    error="Both operation and text are required.",
                )

            if operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            elif operation == "reverse":
                result = text[::-1]
            elif operation == "length":
                result = len(text)
            else:
                return ToolResult(
                    success=False,
                    result=None,
                    error=f"Unknown operation: {operation}",
                )

            logger.info(
                "String operation executed: %s on %r",
                operation,
                text[:50],
            )

            return ToolResult(
                success=True,
                result=result,
            )

        except Exception as exc:
            error_msg = f"String operation failed: {str(exc)}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
            )
