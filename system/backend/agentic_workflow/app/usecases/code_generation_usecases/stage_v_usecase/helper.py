import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional


class StageVHelper:
    def __init__(self):
        # Set up a logger for stage V validation
        self.logger = logging.getLogger("code_generation_stage_v")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def get_validation_commands(
        self, platform_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get validation commands based on platform type

        Args:
            platform_type: The platform type (web, mobile, etc.)

        Returns:
            List of command configurations to run
        """
        if platform_type.lower() == "web":
            return await self._get_web_validation_commands()
        elif platform_type.lower() == "mobile":
            return await self._get_mobile_validation_commands()
        else:
            # Default to web commands for unknown platforms
            return await self._get_web_validation_commands()

    async def _get_web_validation_commands(self) -> List[Dict[str, Any]]:
        """Get validation commands for web/React projects"""
        return [
            {
                "command": "npm run build",
                "description": "Build the project",
                "timeout": 300,
                "required": True,
                "error_patterns": [
                    r"ERROR",
                    r"Build failed",
                    r"Module not found",
                    r"Cannot resolve",
                    r"Syntax error",
                    r"Type error",
                    r"Property .* does not exist",
                    r"Expected .* but got",
                    r"Unexpected token",
                ],
            },
            # {
            #     "command": "npx eslint src --ext .js,.jsx,.ts,.tsx",
            #     "description": "Run ESLint for code quality",
            #     "timeout": 30,
            #     "required": False,
            #     "error_patterns": [
            #         r"error",
            #         r"✖",
            #         r"problems \(",
            #         r"Parsing error"
            #     ]
            # },
        ]

    async def _get_mobile_validation_commands(self) -> List[Dict[str, Any]]:
        """Get validation commands for mobile (Flutter) projects"""
        return [
            {
                "command": "flutter pub get",
                "description": "Get Flutter dependencies",
                "timeout": 180,
                "required": True,
                "error_patterns": [
                    r"Error:",
                    r"Failed to",
                    r"Could not resolve",
                    r"version solving failed",
                    r"pub get failed",
                ],
            },
            {
                "command": "flutter build web",
                "description": "Build Flutter web app",
                "timeout": 300,
                "required": True,
                "error_patterns": [
                    r"Error:",
                    r"Failed to build",
                    r"Build failed",
                    r"Exception:",
                    r"Compiler message",
                    r"Target dart2js failed",
                    r"Compilation failed",
                    r"lib/.*\.dart:\d+:\d+:",
                    r"Error when reading",
                    r"No such file or directory",
                    r"Expected .* after",
                    r"missing implementations",
                    r"Couldn't find constructor",
                    r"ProcessException",
                ],
            },
        ]

    async def execute_validation_command(
        self, command_info: Dict[str, Any], codebase_path: str
    ) -> Dict[str, Any]:
        """
        Execute a validation command and parse its output

        Args:
            command_info: Configuration for the command to run
            codebase_path: Path to the codebase directory

        Returns:
            Dict containing execution results and parsed errors
        """
        start_time = time.time()

        try:
            self.logger.info(f"Executing command: {command_info['command']}")

            # Run the command
            process = await asyncio.create_subprocess_shell(
                command_info["command"],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=codebase_path,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=command_info.get("timeout", 300),
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "command": command_info["command"],
                    "description": command_info["description"],
                    "status": "timeout",
                    "has_errors": True,
                    "error_details": {
                        "type": "timeout",
                        "message": f"Command timed out after {command_info.get('timeout', 300)} seconds",
                        "raw_output": "",
                        "parsed_errors": [],
                    },
                    "execution_time": time.time() - start_time,
                }

            # Decode output
            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")
            combined_output = stdout_text + "\n" + stderr_text

            # Parse errors from output
            parsed_errors = await self._parse_command_errors(
                combined_output, command_info.get("error_patterns", [])
            )

            # Determine if command has errors
            has_errors = (
                process.returncode != 0
                or len(parsed_errors) > 0
                or await self._has_critical_errors(
                    combined_output, command_info["command"]
                )
            )

            execution_time = time.time() - start_time

            return {
                "command": command_info["command"],
                "description": command_info["description"],
                "status": "error" if has_errors else "success",
                "has_errors": has_errors,
                "exit_code": process.returncode,
                "error_details": {
                    "type": "command_errors" if has_errors else "none",
                    "message": self._extract_error_message(
                        combined_output, parsed_errors
                    ),
                    "raw_output": combined_output,
                    "parsed_errors": parsed_errors,
                },
                "execution_time": execution_time,
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "command": command_info["command"],
                "description": command_info["description"],
                "status": "failed",
                "has_errors": True,
                "error_details": {
                    "type": "execution_error",
                    "message": str(e),
                    "raw_output": "",
                    "parsed_errors": [],
                },
                "execution_time": execution_time,
            }

    async def _parse_command_errors(
        self, output: str, error_patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Parse errors from command output using regex patterns

        Args:
            output: Command output text
            error_patterns: List of regex patterns to match errors

        Returns:
            List of parsed error objects
        """
        parsed_errors = []

        for pattern in error_patterns:
            matches = re.finditer(pattern, output, re.MULTILINE | re.IGNORECASE)

            for match in matches:
                # Find the line containing the error
                lines = output.split("\n")
                line_number = None
                error_line = match.group(0)

                # Try to find line number and context
                for i, line in enumerate(lines):
                    if match.group(0) in line:
                        line_number = i + 1
                        error_line = line.strip()
                        break

                # Extract additional context (file path, column, etc.)
                file_path = self._extract_file_path(error_line)
                column = self._extract_column_number(error_line)

                parsed_errors.append(
                    {
                        "pattern": pattern,
                        "matched_text": match.group(0),
                        "line_number": line_number,
                        "error_line": error_line,
                        "file_path": file_path,
                        "column": column,
                        "context": (
                            self._get_error_context(lines, line_number)
                            if line_number
                            else None
                        ),
                    }
                )

        return parsed_errors

    def _extract_file_path(self, error_line: str) -> Optional[str]:
        """Extract file path from error line"""
        # Common patterns for file paths in error messages
        patterns = [
            r"([a-zA-Z0-9_\-./]+\.[a-zA-Z]{1,4}):?\d*:?\d*",
            r"at ([a-zA-Z0-9_\-./]+\.[a-zA-Z]{1,4})",
            r"in ([a-zA-Z0-9_\-./]+\.[a-zA-Z]{1,4})",
            r"file://([a-zA-Z0-9_\-./]+\.[a-zA-Z]{1,4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_line)
            if match:
                return match.group(1)

        return None

    def _extract_column_number(self, error_line: str) -> Optional[int]:
        """Extract column number from error line"""
        # Look for patterns like ":line:column" or "line:column"
        pattern = r":(\d+):(\d+)"
        match = re.search(pattern, error_line)
        if match:
            return int(match.group(2))

        return None

    def _get_error_context(
        self, lines: List[str], line_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get context around error line"""
        if not line_number or line_number < 1:
            return None

        start_line = max(0, line_number - 3)
        end_line = min(len(lines), line_number + 2)

        return {
            "before": lines[start_line : line_number - 1],
            "error_line": (
                lines[line_number - 1] if line_number - 1 < len(lines) else ""
            ),
            "after": lines[line_number:end_line],
        }

    async def _has_critical_errors(self, output: str, command: str) -> bool:
        """Check for critical errors that should fail validation"""
        critical_patterns = [
            r"Build failed",
            r"Compilation failed",
            r"Fatal error",
            r"Cannot resolve module",
            r"Module not found",
            r"Syntax error",
            r"Type error",
            r"ReferenceError",
            r"TypeError",
            r"ERR_MODULE_NOT_FOUND",
            r"Cannot find package",
            r"Oops! Something went wrong",
            r"Missing script:",
            r"npm ERR!",
            # Flutter-specific patterns
            r"Target dart2js failed",
            r"Error: Compilation failed",
            r"ProcessException",
            r"Error when reading",
            r"No such file or directory",
            r"Expected .* after",
            r"missing implementations",
            r"Couldn't find constructor",
            r"lib/.*\.dart:\d+:\d+:.*Error:",
        ]

        for pattern in critical_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True

        return False

    def _extract_error_message(
        self, output: str, parsed_errors: List[Dict[str, Any]]
    ) -> str:
        """Extract a detailed error message from output"""
        # Check if this is Flutter output with compilation errors
        if "Target dart2js failed" in output or "Error: Compilation failed" in output:
            return self._extract_flutter_compilation_errors(output)
        
        # First, try to use parsed errors if they contain meaningful information
        if parsed_errors:
            for error in parsed_errors:
                error_line = error.get("error_line", "")
                if error_line and error_line != "error during build:" and len(error_line.strip()) > 10:
                    return error_line.strip()
        
        # If no good parsed errors, extract from raw output
        lines = output.split("\n")
        error_lines = []
        
        # Look for specific error patterns with more context
        error_patterns = [
            r"Error: \[vite\].*",
            r"Error: .*",
            r"Failed to resolve.*",
            r"Cannot resolve.*",
            r"Module not found.*",
            r"Compilation failed.*",
            r"Build failed.*",
            r"TypeError.*",
            r"ReferenceError.*",
            r"SyntaxError.*",
            r"npm ERR!.*"
        ]
        
        # Find lines matching error patterns
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for specific error patterns
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    error_lines.append(line)
                    # Include next few lines for context if they seem relevant
                    for j in range(i + 1, min(i + 4, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("at ") and len(next_line) < 200:
                            # Include lines that provide context but aren't stack traces
                            if any(keyword in next_line.lower() for keyword in [
                                "this is most likely", "unintended", "because", 
                                "runtime", "application", "module", "import", "file"
                            ]):
                                error_lines.append(next_line)
                            elif re.match(r".*\.(js|jsx|ts|tsx|dart).*", next_line):
                                error_lines.append(next_line)
                    break
        
        if error_lines:
            return "\n".join(error_lines)
        
        # Fallback: look for any line with error-related keywords
        for line in lines:
            line = line.strip()
            if line and any(keyword in line.lower() for keyword in ["error", "fail", "exception"]):
                if len(line) > 10 and line != "error during build:":
                    # Get a few lines of context
                    line_index = lines.index(line)
                    context_lines = [line]
                    for j in range(line_index + 1, min(line_index + 3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 5:
                            context_lines.append(next_line)
                    return "\n".join(context_lines)
        
        return "No specific error message found"

    def _extract_flutter_compilation_errors(self, output: str) -> str:
        """Extract and format Flutter compilation errors"""
        lines = output.split("\n")
        compilation_errors = []
        current_error = []
        
        # Look for lines that start with file paths (Flutter error format)
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Flutter errors typically start with a file path and line/column numbers
            if re.match(r"lib/.*\.dart:\d+:\d+:", line):
                # If we have a previous error, save it
                if current_error:
                    compilation_errors.append("\n".join(current_error))
                    current_error = []
                
                # Start new error with the file path line
                current_error.append(line)
                
                # Look for the "Error:" line that follows
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith("Error:"):
                        current_error.append(next_line)
                        break
                        
            # Also capture standalone error messages
            elif line.startswith("Error:") and not any("Error:" in err for err in current_error):
                if current_error:
                    compilation_errors.append("\n".join(current_error))
                    current_error = []
                current_error.append(line)
                
                # Look for additional context lines
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith("Error:") and not next_line.startswith("lib/"):
                        # Add context if it's meaningful
                        if any(keyword in next_line.lower() for keyword in [
                            "missing", "expected", "found", "implementation", "constructor"
                        ]):
                            current_error.append(next_line)
        
        # Don't forget the last error
        if current_error:
            compilation_errors.append("\n".join(current_error))
        
        # If we found specific compilation errors, return them
        if compilation_errors:
            return "\n\n".join(compilation_errors)
        
        # Fallback: try to extract the main error block
        error_start = -1
        error_end = -1
        
        for i, line in enumerate(lines):
            if "Target dart2js failed" in line or "Error: Compilation failed" in line:
                error_start = max(0, i - 1)
                break
        
        if error_start >= 0:
            # Find the end of the error block (before stack trace)
            for i in range(error_start, len(lines)):
                line = lines[i].strip()
                if line.startswith("#0") or line.startswith("Error: Failed to compile"):
                    error_end = i
                    break
            
            if error_end > error_start:
                error_block = lines[error_start:error_end]
                # Filter out empty lines and stack trace entries
                filtered_errors = []
                for line in error_block:
                    line = line.strip()
                    if line and not line.startswith("at ") and not line.startswith("#"):
                        filtered_errors.append(line)
                
                if filtered_errors:
                    return "\n".join(filtered_errors)
        
        # Ultimate fallback
        return "Flutter compilation failed with multiple errors"

    async def create_validation_summary(
        self, validation_results: List[Dict[str, Any]], has_errors: bool
    ) -> Dict[str, Any]:
        """
        Create a summary of validation results

        Args:
            validation_results: List of validation command results
            has_errors: Whether any errors were found

        Returns:
            Summary dictionary
        """
        total_commands = len(validation_results)
        successful_commands = sum(
            1 for r in validation_results if r["status"] == "success"
        )
        failed_commands = sum(
            1 for r in validation_results if r["status"] == "error"
        )
        timeout_commands = sum(
            1 for r in validation_results if r["status"] == "timeout"
        )

        total_errors = sum(
            len(r["error_details"]["parsed_errors"]) for r in validation_results
        )
        total_execution_time = sum(
            r["execution_time"] for r in validation_results
        )

        summary = {
            "overall_status": "failed" if has_errors else "passed",
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "failed_commands": failed_commands,
            "timeout_commands": timeout_commands,
            "total_errors": total_errors,
            "total_execution_time": round(total_execution_time, 2),
            "timestamp": self._get_timestamp(),
            "command_details": [],
        }

        # Add command details
        for result in validation_results:
            summary["command_details"].append(
                {
                    "command": result["command"],
                    "description": result["description"],
                    "status": result["status"],
                    "has_errors": result["has_errors"],
                    "error_count": len(
                        result["error_details"]["parsed_errors"]
                    ),
                    "execution_time": round(result["execution_time"], 2),
                }
            )

        return summary

    async def update_scratchpads(
        self,
        session_id: str,
        validation_results: List[Dict[str, Any]],
        summary: Dict[str, Any],
    ):
        """
        Update scratchpad files with validation results

        Args:
            session_id: The session ID for file paths
            validation_results: List of validation command results
            summary: Summary of validation results
        """
        scratchpads_dir = f"artifacts/{session_id}/scratchpads"
        os.makedirs(scratchpads_dir, exist_ok=True)

        # Create detailed validation report
        validation_report = f"""
<STAGE_V_CODE_VALIDATION>
<TIMESTAMP>{self._get_timestamp()}</TIMESTAMP>
<OVERALL_STATUS>{summary['overall_status']}</OVERALL_STATUS>
<SUMMARY>
Total Commands: {summary['total_commands']}
Successful: {summary['successful_commands']}
Failed: {summary['failed_commands']}
Timeout: {summary['timeout_commands']}
Total Errors: {summary['total_errors']}
Total Execution Time: {summary['total_execution_time']}s
</SUMMARY>

<COMMAND_RESULTS>
"""

        for result in validation_results:
            validation_report += f"""
<COMMAND>
<COMMAND_TEXT>{result['command']}</COMMAND_TEXT>
<DESCRIPTION>{result['description']}</DESCRIPTION>
<STATUS>{result['status']}</STATUS>
<HAS_ERRORS>{result['has_errors']}</HAS_ERRORS>
<EXECUTION_TIME>{result['execution_time']:.2f}s</EXECUTION_TIME>
"""

            if result["has_errors"]:
                validation_report += f"""
<ERROR_DETAILS>
<ERROR_TYPE>{result['error_details']['type']}</ERROR_TYPE>
<ERROR_MESSAGE>{result['error_details']['message']}</ERROR_MESSAGE>
<PARSED_ERRORS_COUNT>{len(result['error_details']['parsed_errors'])}</PARSED_ERRORS_COUNT>
"""

                for i, error in enumerate(
                    result["error_details"]["parsed_errors"]
                ):
                    validation_report += f"""
<ERROR_{i+1}>
<FILE_PATH>{error.get('file_path', 'unknown')}</FILE_PATH>
<LINE_NUMBER>{error.get('line_number', 'unknown')}</LINE_NUMBER>
<ERROR_LINE>{error.get('error_line', 'unknown')}</ERROR_LINE>
</ERROR_{i+1}>
"""

                validation_report += "</ERROR_DETAILS>\n"

            validation_report += "</COMMAND>\n"

        validation_report += """
</COMMAND_RESULTS>
</STAGE_V_CODE_VALIDATION>

"""

        # Append to global scratchpad
        global_scratchpad_path = os.path.join(
            scratchpads_dir, "global_scratchpad.txt"
        )
        with open(global_scratchpad_path, "a", encoding="utf-8") as f:
            f.write(validation_report)

        # Create dedicated validation results file
        validation_results_path = os.path.join(
            scratchpads_dir, "validation_results.json"
        )
        with open(validation_results_path, "w", encoding="utf-8") as f:
            json.dump(
                {"summary": summary, "validation_results": validation_results},
                f,
                indent=2,
            )

        self.logger.info(
            f"Updated validation results at {validation_results_path}"
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
