"""
Helper functions for creating agent tools
"""

from agents.tool import FunctionTool
from typing import Callable, Any, List, Dict
import asyncio
import inspect


def create_function_tool(
    name: str,
    description: str,
    func: Callable
) -> FunctionTool:
    """
    Create a FunctionTool from a regular Python function.
    
    Args:
        name: Tool name
        description: Tool description
        func: Python function to wrap
    
    Returns:
        FunctionTool instance
    """
    # Check if function is async
    is_async = inspect.iscoroutinefunction(func)
    
    # Create params schema from function signature
    sig = inspect.signature(func)
    params = {}
    required = []
    
    for param_name, param in sig.parameters.items():
        param_info = {}
        
        # Get type annotation
        if param.annotation != inspect.Parameter.empty:
            param_type = param.annotation
            if param_type == str:
                param_info["type"] = "string"
            elif param_type == int:
                param_info["type"] = "integer"
            elif param_type == float:
                param_info["type"] = "number"
            elif param_type == bool:
                param_info["type"] = "boolean"
            elif param_type == list or param_type == List:
                param_info["type"] = "array"
            elif param_type == dict or param_type == Dict:
                param_info["type"] = "object"
            else:
                param_info["type"] = "string"
        else:
            param_info["type"] = "string"
        
        # Default value
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default
        else:
            required.append(param_name)
        
        params[param_name] = param_info
    
    params_schema = {
        "type": "object",
        "properties": params,
        "required": required
    }
    
    # Create async wrapper
    async def on_invoke_tool(context, arguments_json: str):
        import json
        args = json.loads(arguments_json)
        
        # Call function with unpacked args
        if is_async:
            result = await func(**args)
        else:
            result = func(**args)
        
        return result
    
    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=params_schema,
        on_invoke_tool=on_invoke_tool
    )

