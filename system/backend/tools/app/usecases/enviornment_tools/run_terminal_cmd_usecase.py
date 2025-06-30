import asyncio
import os
import re
import sys
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, project_root)


class RunTerminalCmdUsecase:
    def __init__(self):
        # Explicitly blocked commands
        self.BLOCKED_COMMANDS: Set[str] = {
            "rm -rf /",
            "rm -rf /*",
            "rm -rf --no-preserve-root /",
            ":(){ :|:& };:",
            "crontab -r",
        }

        # Dangerous command patterns to detect
        self.DANGEROUS_PATTERNS: List[Tuple[Pattern, str]] = [
            # Data destruction patterns
            (
                re.compile(r"rm\s+-r?f\s+(/|/\*|/\.\.|--no-preserve-root)"),
                "File system deletion",
            ),
            (
                re.compile(
                    r"dd\s+if=/dev/(zero|random|urandom)\s+of=/dev/([sh]d[a-z]|nvme|xvd)"
                ),
                "Disk overwrite",
            ),
            (
                re.compile(r"mkfs\.[a-z0-9]+\s+/dev/([sh]d[a-z]|nvme|xvd)"),
                "Disk formatting",
            ),
            (re.compile(r"mv\s+.*\s+/dev/null"), "Data deletion via /dev/null"),
            (re.compile(r">\s+/dev/([sh]d[a-z]|nvme|xvd)"), "Disk corruption"),
            (re.compile(r"shred\s+.*\s+-z"), "Secure data deletion"),
            # System destabilization patterns
            (re.compile(r":\(\)\s*{\s*:\|:"), "Fork bomb detection"),
            (re.compile(r"kill\s+-9\s+-1"), "Killing all processes"),
            (re.compile(r"shutdown\s+(-h|-r)\s+now"), "System shutdown"),
            (
                re.compile(r"systemctl\s+(poweroff|halt|reboot)"),
                "System power management",
            ),
            # Permission and security compromise
            (
                re.compile(r"chmod\s+-R\s+777\s+/"),
                "Recursive permission change",
            ),
            (
                re.compile(r"chmod\s+.*\s+/etc/sudoers"),
                "Sudoers file modification",
            ),
            (re.compile(r"passwd\s+root"), "Root password change"),
            # Remote execution vulnerabilities
            (
                re.compile(r"wget\s+.*\s+\|\s+([sb]a)?sh"),
                "Piping web content to shell",
            ),
            (
                re.compile(r"curl\s+.*\s+\|\s+([sb]a)?sh"),
                "Piping web content to shell",
            ),
            # File system manipulation
            (
                re.compile(r"find\s+/\s+-type\s+[fd]\s+-exec\s+.*\s+\{\}"),
                "Dangerous find command",
            ),
            (re.compile(r"find\s+/\s+.*\s+-delete"), "Dangerous find deletion"),
            # Disk usage filling
            (
                re.compile(r"fallocate\s+-l\s+\d+[GT]\s+"),
                "Large file allocation",
            ),
            (re.compile(r"base64\s+/dev/urandom"), "Random data generation"),
            # Network command abuse
            (
                re.compile(r"nc\s+-e\s+/bin/([sb]a)?sh"),
                "Netcat shell execution",
            ),
            (
                re.compile(r"telnet\s+.*\s+\|\s+/bin/([sb]a)?sh"),
                "Telnet shell piping",
            ),
        ]

        # Dangerous command names (for non-recursive checking)
        self.DANGEROUS_COMMAND_NAMES = {
            'rm', 'rmdir', 'dd', 'mkfs', 'format', 'fdisk', 'parted',
            'shutdown', 'poweroff', 'halt', 'reboot', 'kill', 'killall',
            'chmod', 'chown', 'passwd', 'su', 'sudo', 'wget', 'curl',
            'nc', 'netcat', 'telnet', 'ssh', 'scp', 'rsync'
        }

    def _modify_command_for_node_modules_exclusion(self, command: str) -> str:
        """
        Modify commands to exclude node_modules directory to prevent recursion issues.
        
        Args:
            command: The original command
            
        Returns:
            Modified command with node_modules exclusion where applicable
        """
        # Commands that commonly traverse directories and can benefit from node_modules exclusion
        directory_traversal_commands = ['find', 'grep', 'ls', 'tree', 'du', 'wc']
        
        # Check if this is a command that traverses directories
        first_word = command.strip().split()[0] if command.strip() else ""
        
        if first_word in directory_traversal_commands:
            # Add node_modules exclusion based on command type
            if first_word == 'find':
                # Add -not -path "*/node_modules/*" to find commands
                if 'node_modules' not in command and '-not -path' not in command:
                    # Insert the exclusion after the path but before other conditions
                    parts = command.split()
                    if len(parts) >= 2:
                        # Find where to insert the exclusion (after path, before conditions)
                        insert_pos = 2  # After 'find' and path
                        while insert_pos < len(parts) and not parts[insert_pos].startswith('-'):
                            insert_pos += 1
                        
                        exclusion = ['-not', '-path', '*/node_modules/*']
                        parts = parts[:insert_pos] + exclusion + parts[insert_pos:]
                        command = ' '.join(parts)
            
            elif first_word in ['grep', 'wc']:
                # Add --exclude-dir=node_modules to grep/wc commands with -r flag
                if '-r' in command and '--exclude-dir' not in command and 'node_modules' not in command:
                    command += ' --exclude-dir=node_modules'
            
            elif first_word == 'du':
                # Add --exclude=node_modules to du commands
                if '--exclude' not in command and 'node_modules' not in command:
                    command += ' --exclude=node_modules'
            
            elif first_word == 'tree':
                # Add -I node_modules to tree commands
                if '-I' not in command and 'node_modules' not in command:
                    command += ' -I node_modules'
        
        return command

    async def run_terminal_command(
        self,
        command: str,
        is_background: bool,
        explanation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a terminal command on the user's system with safety checks and node_modules exclusion.

        Args:
            command: The terminal command to execute
            is_background: Whether the command should be run in the background
            explanation: Explanation for why the command is needed

        Returns:
            A dictionary with the command output and execution status
        """
        import subprocess

        try:
            # Modify command to exclude node_modules if applicable
            original_command = command
            command = self._modify_command_for_node_modules_exclusion(command)
            
            if command != original_command:
                print(f"Modified command to exclude node_modules: {command}")

            # Security check for dangerous commands
            security_check = self._check_command_safety(command)
            if security_check["is_dangerous"]:
                return {
                    "output": "",
                    "error": f"SECURITY ALERT: Dangerous command detected. {security_check['reason']}",
                    "exit_code": 1,
                    "status": "blocked_dangerous_command",
                }

            # Log command and explanation if provided
            if explanation:
                print(f"Explanation: {explanation}")

            print(f"Executing command: {command}")
            print(f"Run in background: {is_background}")

            if is_background:
                # For background processes, use Popen and don't wait
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    start_new_session=True,
                    cwd=os.path.join(project_root, "codebase"),
                    shell=True,  # Use shell to expand wildcards, variables, etc.
                )
                return {
                    "output": f"Command started in background with PID {process.pid}",
                    "exit_code": None,
                    "status": "running_in_background",
                }
            else:
                # For foreground processes, capture output
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.join(project_root, "codebase"),
                )

                stdout, stderr = await process.communicate()
                stdout_str = stdout.decode("utf-8")
                stderr_str = stderr.decode("utf-8")

                return {
                    "output": stdout_str,
                    "error": stderr_str,
                    "exit_code": process.returncode,
                    "status": (
                        "completed" if process.returncode == 0 else "error"
                    ),
                }

        except subprocess.TimeoutExpired:
            return {
                "output": "Command timed out after 60 seconds",
                "exit_code": None,
                "status": "timeout",
            }
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            print(error_msg)
            return {
                "output": "",
                "error": error_msg,
                "exit_code": 1,
                "status": "error",
            }

    def _check_command_safety(self, command: str, _recursion_depth: int = 0) -> Dict[str, Any]:
        """
        Check if the command is potentially dangerous.
        
        Args:
            command: The command to check
            _recursion_depth: Internal parameter to prevent infinite recursion
            
        Returns:
            Dictionary with is_dangerous flag and reason if dangerous
        """
        # Prevent infinite recursion
        if _recursion_depth > 3:
            return {"is_dangerous": False, "reason": None}
        
        # Normalize command for better matching (lowercase, remove extra spaces)
        normalized_cmd = re.sub(r"\s+", " ", command.strip().lower())

        # Check against explicitly blocked commands
        for blocked_cmd in self.BLOCKED_COMMANDS:
            if blocked_cmd in normalized_cmd:
                return {
                    "is_dangerous": True,
                    "reason": f"Blocked command detected: '{blocked_cmd}'",
                }

        # Check against dangerous patterns
        for pattern, description in self.DANGEROUS_PATTERNS:
            if pattern.search(normalized_cmd):
                return {
                    "is_dangerous": True,
                    "reason": f"Dangerous operation detected: {description}",
                }

        # Look for sudo usages with dangerous commands (only check once to avoid recursion)
        if "sudo" in normalized_cmd and _recursion_depth == 0:
            cmd_without_sudo = re.sub(r"^sudo\s+", "", normalized_cmd)
            sudo_check = self._check_command_safety(cmd_without_sudo, _recursion_depth + 1)
            if sudo_check["is_dangerous"]:
                return {
                    "is_dangerous": True,
                    "reason": f"Privileged dangerous operation detected: {sudo_check['reason']}",
                }
                
        # Check for chained commands that might be dangerous (only if not too deep in recursion)
        if _recursion_depth < 2 and self._has_command_chaining(normalized_cmd):
            command_parts = self._split_chained_commands(normalized_cmd)
            
            for cmd_part in command_parts:
                cmd_part = cmd_part.strip()
                if cmd_part and len(cmd_part) > 2:
                    # Extract just the command name (first word) to check against known dangerous commands
                    first_word = cmd_part.split()[0] if cmd_part.split() else ""
                    if first_word and self._is_potentially_dangerous_command_name(first_word):
                        return {
                            "is_dangerous": True,
                            "reason": f"Dangerous command in chain: {first_word}",
                        }

        return {"is_dangerous": False, "reason": None}
        
    def _has_command_chaining(self, command: str) -> bool:
        """Check if command has actual command chaining (not just content with special chars)"""
        chaining_patterns = [
            r';\s*\w+',          # semicolon followed by word
            r'\w+\s*&&\s*\w+',   # word && word
            r'\w+\s*\|\|\s*\w+', # word || word
        ]
        
        for pattern in chaining_patterns:
            if re.search(pattern, command):
                return True
        return False
    
    def _split_chained_commands(self, command: str) -> List[str]:
        """Split chained commands safely"""
        # Split by major command separators
        parts = []
        
        # Split by semicolons first
        for part in re.split(r';\s*', command):
            # Then split by && and ||
            subparts = re.split(r'\s*(?:\|\||&&)\s*', part)
            parts.extend([p.strip() for p in subparts if p.strip()])
        
        return parts
    
    def _is_potentially_dangerous_command_name(self, command_name: str) -> bool:
        """Check if a command name is potentially dangerous (non-recursive check)"""
        return command_name.lower() in self.DANGEROUS_COMMAND_NAMES