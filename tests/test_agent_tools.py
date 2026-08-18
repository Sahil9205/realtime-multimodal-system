"""
Tests for the agent/tool system.
"""

import pytest

from app.agents import (
    ToolRegistry,
    ToolExecutor,
    CalculatorTool,
    CurrentTimeTool,
    StringToolsTool,
)


@pytest.mark.anyio
async def test_calculator_tool() -> None:
    """Test calculator tool."""
    tool = CalculatorTool()
    
    # Test addition
    result = await tool.execute(expression="2 + 2")
    assert result.success
    assert result.result == 4
    
    # Test square root
    result = await tool.execute(expression="sqrt(16)")
    assert result.success
    assert result.result == 4.0
    
    # Test exponentiation
    result = await tool.execute(expression="2 ** 3")
    assert result.success
    assert result.result == 8


@pytest.mark.anyio
async def test_calculator_tool_invalid_expression() -> None:
    """Test calculator with invalid expression."""
    tool = CalculatorTool()
    
    result = await tool.execute(expression="invalid @@@ expression")
    assert not result.success
    assert result.error is not None


@pytest.mark.anyio
async def test_current_time_tool() -> None:
    """Test current time tool."""
    tool = CurrentTimeTool()
    
    result = await tool.execute()
    assert result.success
    assert "time" in result.result
    assert "timestamp" in result.result


@pytest.mark.anyio
async def test_string_tools_uppercase() -> None:
    """Test string tools with uppercase operation."""
    tool = StringToolsTool()
    
    result = await tool.execute(operation="uppercase", text="hello")
    assert result.success
    assert result.result == "HELLO"


@pytest.mark.anyio
async def test_string_tools_reverse() -> None:
    """Test string tools with reverse operation."""
    tool = StringToolsTool()
    
    result = await tool.execute(operation="reverse", text="hello")
    assert result.success
    assert result.result == "olleh"


@pytest.mark.anyio
async def test_string_tools_length() -> None:
    """Test string tools with length operation."""
    tool = StringToolsTool()
    
    result = await tool.execute(operation="length", text="hello")
    assert result.success
    assert result.result == 5


def test_tool_registry_register() -> None:
    """Test registering tools."""
    registry = ToolRegistry()
    
    calculator = CalculatorTool()
    registry.register(calculator)
    
    retrieved = registry.get_tool("calculator")
    assert retrieved is not None
    assert retrieved == calculator


def test_tool_registry_list_definitions() -> None:
    """Test listing tool definitions."""
    registry = ToolRegistry()
    
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(StringToolsTool())
    
    definitions = registry.list_definitions()
    assert len(definitions) == 3
    
    names = [d.name for d in definitions]
    assert "calculator" in names
    assert "current_time" in names
    assert "string_tools" in names


def test_tool_registry_get_nonexistent() -> None:
    """Test getting a tool that doesn't exist."""
    registry = ToolRegistry()
    
    tool = registry.get_tool("nonexistent")
    assert tool is None


def test_tool_registry_clear() -> None:
    """Test clearing the registry."""
    registry = ToolRegistry()
    
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    
    assert len(registry.get_all_tools()) == 2
    
    registry.clear()
    assert len(registry.get_all_tools()) == 0


@pytest.mark.anyio
async def test_tool_executor_execute_valid_tool() -> None:
    """Test executor with valid tool."""
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    
    executor = ToolExecutor(registry)
    
    result = await executor.execute("calculator", expression="3 + 3")
    assert result.success
    assert result.result == 6


@pytest.mark.anyio
async def test_tool_executor_execute_invalid_tool() -> None:
    """Test executor with invalid tool."""
    registry = ToolRegistry()
    executor = ToolExecutor(registry)
    
    result = await executor.execute("nonexistent", param="value")
    assert not result.success
    assert result.error is not None


def test_tool_definition() -> None:
    """Test ToolDefinition model."""
    from app.agents.tools import ToolDefinition, ToolParameter
    
    definition = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters=[
            ToolParameter(
                name="param1",
                type="string",
                description="First parameter",
            )
        ]
    )
    
    assert definition.name == "test_tool"
    assert len(definition.parameters) == 1
    assert definition.parameters[0].name == "param1"
