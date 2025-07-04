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
        ]

        for pattern in critical_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True

        return False

    def _extract_error_message(
        self, output: str, parsed_errors: List[Dict[str, Any]]
    ) -> str:
        """Extract a concise error message from output"""
        if not parsed_errors:
            # Try to extract first error-like line
            lines = output.split("\n")
            for line in lines:
                if any(
                    keyword in line.lower()
                    for keyword in ["error", "fail", "exception"]
                ):
                    return line.strip()
            return "No specific error message found"

        # Use the first parsed error
        return parsed_errors[0].get("error_line", "Unknown error")

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
