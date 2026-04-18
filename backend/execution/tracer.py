"""
Execution Tracer Module
Captures real Python code execution with line-by-line tracing
and variable state capture using sys.settrace
"""
import sys
import types
from typing import Dict, Any, List, Optional


class ExecutionTracer:
    """Real Python code execution tracer with security sandboxing"""
    
    def __init__(self, timeout: int = 5, max_lines: int = 1000):
        self.timeout = timeout
        self.max_lines = max_lines
        self.execution_steps: List[Dict[str, Any]] = []
        self.output: List[str] = []
        self.error: Optional[str] = None
        self.line_count = 0
        self._captured_locals: Dict[str, Any] = {}
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create restricted globals for sandboxed execution"""
        safe_builtins = {
            'print': self._safe_print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'sorted': sorted,
            'reversed': reversed,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'type': type,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'input': self._blocked,
            'open': self._blocked,
            'eval': self._blocked,
            'exec': self._blocked,
            '__import__': self._blocked,
            'compile': self._blocked,
        }
        
        return {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            '__doc__': None,
            '__package__': None,
        }
    
    def _safe_print(self, *args, **kwargs):
        """Safe print that captures output"""
        output = ' '.join(str(arg) for arg in args)
        self.output.append(output)
    
    def _blocked(self, *args, **kwargs):
        """Blocked function for security"""
        raise RuntimeError("This operation is not allowed in sandboxed execution")
    
    def _trace_function(self, frame: types.FrameType, event: str, arg: Any) -> Optional[callable]:
        """Trace function for sys.settrace"""
        if event == 'line':
            self._handle_line(frame)
        elif event == 'exception':
            self._handle_exception(frame, arg)
        return self._trace_function
    
    def _handle_line(self, frame: types.FrameType):
        """Handle each line execution"""
        code = frame.f_code
        filename = code.co_filename
        
        if filename != '<string>':
            return
            
        self.line_count += 1
        
        if self.line_count > self.max_lines:
            raise RuntimeError(f"Execution exceeded {self.max_lines} lines. Possible infinite loop?")
        
        try:
            local_vars = {}
            for key, value in frame.f_locals.items():
                if key not in ['__builtins__', '__loader__', '__spec__', '__doc__']:
                    try:
                        local_vars[key] = self._serialize_value(value)
                    except:
                        local_vars[key] = f"<{type(value).__name__}>"
            
            self._captured_locals = local_vars
            
            code_info = {
                'line_number': frame.f_lineno,
                'code': self._get_line_code(frame),
                'variables': local_vars.copy()
            }
            
            self.execution_steps.append(code_info)
            
        except Exception as e:
            pass
    
    def _handle_exception(self, frame: types.FrameType, arg: tuple):
        """Handle exception during execution"""
        exc_type, exc_value, _ = arg
        self.error = f"{exc_type.__name__}: {exc_value}"
    
    def _get_line_code(self, frame: types.FrameType) -> str:
        """Get the source line being executed"""
        try:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            if filename == '<string>':
                lines = frame.f_globals.get('_source_lines', [])
                if 0 <= lineno - 1 < len(lines):
                    return lines[lineno - 1]
            return f"Line {lineno}"
        except:
            return "Unknown"
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize values for JSON output"""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {str(k): self._serialize_value(v) for k, v in value.items() if k != '_source_lines'}
        elif isinstance(value, set):
            return list(value)
        elif isinstance(value, (types.FunctionType, types.LambdaType)):
            return f"<function {value.__name__}>"
        else:
            return f"<{type(value).__name__}>"
    
    def execute(self, code: str) -> Dict[str, Any]:
        """Execute code and return execution trace"""
        self.execution_steps = []
        self.output = []
        self.error = None
        self.line_count = 0
        self._captured_locals = {}
        
        safe_globals = self._create_safe_globals()
        safe_globals['_source_lines'] = code.split('\n')
        
        import threading
        import time
        
        def execute_with_timeout():
            old_trace = sys.gettrace()
            try:
                compiled = compile(code, '<string>', 'exec')
                sys.settrace(self._trace_function)
                exec(compiled, safe_globals)
            except Exception as e:
                if not self.error:
                    self.error = f"{type(e).__name__}: {str(e)}"
            finally:
                sys.settrace(old_trace)
        
        executor = threading.Thread(target=execute_with_timeout, daemon=True)
        executor.start()
        executor.join(timeout=self.timeout)
        
        if executor.is_alive():
            self.error = f"Execution timeout after {self.timeout} seconds. Possible infinite loop?"
        
        return self._build_result()
    
    def _build_result(self) -> Dict[str, Any]:
        """Build execution result"""
        filtered_steps = []
        seen_lines = set()
        
        for step in self.execution_steps:
            if step['line_number'] not in seen_lines:
                seen_lines.add(step['line_number'])
                filtered_steps.append(step)
        
        return {
            'execution': filtered_steps,
            'output': self.output,
            'error': self.error
        }


def execute_python_code(code: str, timeout: int = 5) -> Dict[str, Any]:
    """Main function to execute Python code and return execution trace"""
    tracer = ExecutionTracer(timeout=timeout)
    return tracer.execute(code)