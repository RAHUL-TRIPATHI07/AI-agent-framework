from typing import Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    """Categories of tools."""
    WEB = "web"
    FILE = "file"
    DATA = "data"
    CALCULATION = "calculation"
    COMMUNICATION = "communication"
    SYSTEM = "system"


@dataclass
class Tool:
    """A tool that can be executed."""
    name: str
    type: ToolType
    description: str
    handler: Callable
    keywords: list[str]  # Keywords that trigger this tool
    required_params: list[str] = None
    
    def __post_init__(self):
        if self.required_params is None:
            self.required_params = []


class ToolResult:
    """Result of a tool execution."""
    def __init__(self, tool_name: str, success: bool, output: Any = None, 
                 error: str = None):
        self.tool_name = tool_name
        self.success = success
        self.output = output
        self.error = error
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILURE"
        return f"ToolResult({self.tool_name}: {status})"


class ToolRegistry:
    """
    Registry for tools with rule-based selection and execution.
    
    Decides whether a task needs a tool based on keyword matching
    and task description analysis.
    """
    
    def __init__(self):
        self.tools: dict[str, Tool] = {}
        self.tool_usage_log: list[dict] = []
    
    def register(self, tool: Tool) -> 'ToolRegistry':
        """Register a tool (builder pattern)."""
        self.tools[tool.name] = tool
        return self
    
    def needs_tool(self, task_description: str) -> tuple[bool, Optional[str]]:
        """
        Determine if a task needs a tool based on rules.
        
        Args:
            task_description: Description of the task
            
        Returns:
            Tuple of (needs_tool: bool, tool_name: Optional[str])
        """
        task_lower = task_description.lower()
        
        # Rule 1: Check for exact keyword matches
        for tool_name, tool in self.tools.items():
            for keyword in tool.keywords:
                if keyword.lower() in task_lower:
                    return (True, tool_name)
        
        # Rule 2: Check for action patterns
        action_patterns = {
            'web': ['fetch', 'download', 'scrape', 'get url', 'http', 'api call'],
            'file': ['read file', 'write file', 'save to', 'load from', 'open file'],
            'data': ['parse', 'transform', 'filter', 'aggregate', 'sort'],
            'calculation': ['calculate', 'compute', 'sum', 'average', 'count'],
            'communication': ['send email', 'notify', 'message', 'alert'],
            'system': ['execute', 'run command', 'shell', 'process']
        }
        
        for tool_name, tool in self.tools.items():
            tool_type = tool.type.value
            if tool_type in action_patterns:
                for pattern in action_patterns[tool_type]:
                    if pattern in task_lower:
                        return (True, tool_name)
        
        # Rule 3: No tool needed
        return (False, None)
    
    def select_tool(self, task_description: str) -> Optional[Tool]:
        """
        Select the most appropriate tool for a task.
        
        Returns:
            The selected Tool or None if no tool is needed
        """
        needs_tool, tool_name = self.needs_tool(task_description)
        
        if needs_tool and tool_name:
            return self.tools.get(tool_name)
        
        return None
    
    def execute_tool(self, tool_name: str, params: dict) -> ToolResult:
        """
        Execute a specific tool with parameters.
        
        Args:
            tool_name: Name of the tool to execute
            params: Parameters to pass to the tool
            
        Returns:
            ToolResult with execution outcome
        """
        if tool_name not in self.tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        
        # Validate required parameters
        missing_params = [p for p in tool.required_params if p not in params]
        if missing_params:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Missing required parameters: {missing_params}"
            )
        
        # Execute tool
        try:
            output = tool.handler(params)
            
            # Log usage
            self.tool_usage_log.append({
                'tool': tool_name,
                'params': params,
                'success': True
            })
            
            return ToolResult(
                tool_name=tool_name,
                success=True,
                output=output
            )
        
        except Exception as e:
            # Log failure
            self.tool_usage_log.append({
                'tool': tool_name,
                'params': params,
                'success': False,
                'error': str(e)
            })
            
            return ToolResult(
                tool_name=tool_name,
                success=False,
                error=str(e)
            )
    
    def execute_if_needed(self, task_description: str, params: dict) -> Optional[ToolResult]:
        """
        Decide if a task needs a tool and execute it.
        
        Args:
            task_description: Description of the task
            params: Parameters for tool execution
            
        Returns:
            ToolResult if a tool was executed, None otherwise
        """
        tool = self.select_tool(task_description)
        
        if tool is None:
            return None
        
        return self.execute_tool(tool.name, params)
    
    def list_tools(self, tool_type: Optional[ToolType] = None) -> list[Tool]:
        """
        List registered tools, optionally filtered by type.
        
        Args:
            tool_type: Optional filter by tool type
            
        Returns:
            List of tools
        """
        if tool_type is None:
            return list(self.tools.values())
        
        return [t for t in self.tools.values() if t.type == tool_type]
    
    def get_usage_stats(self) -> dict:
        """Get statistics on tool usage."""
        total = len(self.tool_usage_log)
        if total == 0:
            return {'total': 0, 'success': 0, 'failure': 0, 'by_tool': {}}
        
        success_count = sum(1 for log in self.tool_usage_log if log['success'])
        
        by_tool = {}
        for log in self.tool_usage_log:
            tool = log['tool']
            if tool not in by_tool:
                by_tool[tool] = {'total': 0, 'success': 0, 'failure': 0}
            by_tool[tool]['total'] += 1
            if log['success']:
                by_tool[tool]['success'] += 1
            else:
                by_tool[tool]['failure'] += 1
        
        return {
            'total': total,
            'success': success_count,
            'failure': total - success_count,
            'by_tool': by_tool
        }


# Example tool handlers
def web_fetch_handler(params: dict) -> dict:
    """Simulated web fetch tool."""
    url = params.get('url', '')
    return {
        'status': 200,
        'content': f"Content from {url}",
        'size': 1024
    }


def file_read_handler(params: dict) -> dict:
    """Simulated file read tool."""
    filepath = params.get('filepath', '')
    return {
        'content': f"File content from {filepath}",
        'lines': 42
    }


def calculate_handler(params: dict) -> dict:
    """Simple calculation tool."""
    expression = params.get('expression', '')
    # Simple eval (in production, use a safe parser)
    try:
        result = eval(expression)
        return {'result': result, 'expression': expression}
    except:
        raise ValueError(f"Invalid expression: {expression}")


def data_transform_handler(params: dict) -> dict:
    """Simulated data transformation tool."""
    data = params.get('data', [])
    operation = params.get('operation', 'identity')
    
    if operation == 'filter':
        condition = params.get('condition', lambda x: True)
        return {'result': [x for x in data if condition(x)]}
    elif operation == 'map':
        func = params.get('func', lambda x: x)
        return {'result': [func(x) for x in data]}
    else:
        return {'result': data}


# Example usage
if __name__ == "__main__":
    # Create registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(Tool(
        name="web_fetch",
        type=ToolType.WEB,
        description="Fetch content from a URL",
        handler=web_fetch_handler,
        keywords=["fetch", "download", "url", "http", "api"],
        required_params=["url"]
    )).register(Tool(
        name="file_reader",
        type=ToolType.FILE,
        description="Read content from a file",
        handler=file_read_handler,
        keywords=["read file", "open file", "load file"],
        required_params=["filepath"]
    )).register(Tool(
        name="calculator",
        type=ToolType.CALCULATION,
        description="Perform calculations",
        handler=calculate_handler,
        keywords=["calculate", "compute", "math"],
        required_params=["expression"]
    )).register(Tool(
        name="data_transformer",
        type=ToolType.DATA,
        description="Transform data",
        handler=data_transform_handler,
        keywords=["transform", "filter", "map", "process data"],
        required_params=["data", "operation"]
    ))
    
    # Test tasks
    test_tasks = [
        ("Fetch data from https://api.example.com", {"url": "https://api.example.com"}),
        ("Calculate the sum of 10 and 20", {"expression": "10 + 20"}),
        ("Read file from /data/input.txt", {"filepath": "/data/input.txt"}),
        ("Transform data by filtering", {"data": [1, 2, 3, 4, 5], "operation": "filter", "condition": lambda x: x > 2}),
        ("Just analyze this text without tools", {})
    ]
    
    print("=== Tool Execution Tests ===\n")
    for task_desc, params in test_tasks:
        print(f"Task: {task_desc}")
        
        # Check if tool is needed
        needs_tool, tool_name = registry.needs_tool(task_desc)
        print(f"  Needs tool: {needs_tool}")
        if tool_name:
            print(f"  Selected tool: {tool_name}")
        
        # Execute if needed
        result = registry.execute_if_needed(task_desc, params)
        if result:
            print(f"  Result: {result}")
            if result.success:
                print(f"  Output: {result.output}")
            else:
                print(f"  Error: {result.error}")
        else:
            print("  No tool executed (none needed)")
        
        print()
    
    # Show usage statistics
    print("=== Tool Usage Statistics ===")
    stats = registry.get_usage_stats()
    print(f"Total executions: {stats['total']}")
    print(f"Successful: {stats['success']}")
    print(f"Failed: {stats['failure']}")
    print("\nBy tool:")
    for tool, data in stats['by_tool'].items():
        print(f"  {tool}: {data['success']}/{data['total']} successful")
