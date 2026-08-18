"""
Tool/Agent system for LLM function calling.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from app.core.logging import get_logger


logger = get_logger(__name__)


class ToolParameter(BaseModel):
    """
    Represents a tool parameter definition.
    """

    name: str = Field(
        ...,
        description="Parameter name.",
    )

    type: str = Field(
        ...,
        description="Parameter type (string|number|boolean|array|object).",
    )

    description: str = Field(
        ...,
        description="Parameter description.",
    )

    required: bool = Field(
        default=True,
        description="Whether this parameter is required.",
    )


class ToolDefinition(BaseModel):
    """
    Represents the definition of a tool/function.
    """

    name: str = Field(
        ...,
        description="Tool name.",
    )

    description: str = Field(
        ...,
        description="Tool description.",
    )

    parameters: list[ToolParameter] = Field(
        default_factory=list,
        description="Tool parameters.",
    )


class ToolResult(BaseModel):
    """
    Result returned from tool execution.
    """

    success: bool = Field(
        default=True,
        description="Whether tool execution was successful.",
    )

    result: Any = Field(
        ...,
        description="Tool execution result.",
    )

    error: str | None = Field(
        default=None,
        description="Error message if execution failed.",
    )


class BaseTool(ABC):
    """
    Abstract base class for tools/functions callable by LLM.
    """

    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """
        Get the tool definition for LLM.

        Returns:
            ToolDefinition describing this tool.
        """
        raise NotImplementedError

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with provided arguments.

        Args:
            **kwargs: Tool-specific arguments.

        Returns:
            ToolResult with execution result.
        """
        raise NotImplementedError


class ToolRegistry:
    """
    Registry for managing available tools.
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._tools: dict[str, BaseTool] = {}
        logger.info("ToolRegistry initialized.")

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool instance to register.
        """
        definition = tool.get_definition()
        self._tools[definition.name] = tool

        logger.info(
            "Tool registered: %s",
            definition.name,
        )

    def get_tool(self, name: str) -> BaseTool | None:
        """
        Get a tool by name.

        Args:
            name: Tool name.

        Returns:
            Tool instance or None if not found.
        """
        return self._tools.get(name)

    def list_definitions(self) -> list[ToolDefinition]:
        """
        Get definitions of all registered tools.

        Returns:
            List of ToolDefinition objects.
        """
        return [
            tool.get_definition()
            for tool in self._tools.values()
        ]

    def get_all_tools(self) -> dict[str, BaseTool]:
        """
        Get all registered tools.

        Returns:
            Dictionary of tool name to tool instance.
        """
        return dict(self._tools)

    def clear(self) -> None:
        """Clear all registered tools."""
        cleared_count = len(self._tools)
        self._tools.clear()

        logger.info(
            "Tool registry cleared. Removed %d tools.",
            cleared_count,
        )


class ToolExecutor:
    """
    Executes tool calls from LLM.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        """
        Initialize the executor.

        Args:
            registry: Tool registry to use.
        """
        self._registry = registry
        logger.info("ToolExecutor initialized.")

    async def execute(
        self,
        tool_name: str,
        **arguments,
    ) -> ToolResult:
        """
        Execute a tool.

        Args:
            tool_name: Name of the tool to execute.
            **arguments: Tool arguments.

        Returns:
            ToolResult from execution.
        """
        tool = self._registry.get_tool(tool_name)

        if tool is None:
            error_msg = f"Tool not found: {tool_name}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
            )

        try:
            logger.info(
                "Executing tool: %s with args: %s",
                tool_name,
                list(arguments.keys()),
            )

            result = await tool.execute(**arguments)

            logger.info(
                "Tool execution succeeded: %s",
                tool_name,
            )

            return result

        except Exception as exc:
            error_msg = f"Tool execution failed: {str(exc)}"
            logger.error(error_msg, exc_info=True)
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
            )
