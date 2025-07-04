import json
import os
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

from system.backend.agentic_workflow.app.config.settings import settings
from system.backend.agentic_workflow.app.utils.logger import loggers
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class IDEAgentTools:
    def __init__(self):
        self.tools_base_url = (
            settings.TOOLS_API_BASE_URL or "http://localhost:8001/api/v1"
        )
        self.timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,
            write=60.0,
            pool=30.0,
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in Anthropic format for the IDE agent
        """
        return [
            {
                "name": "read_file",
                "description": "Reads the contents of a specified file. You may choose to read the entire file or a specific range of lines by providing optional start and end line numbers. The tool returns the file content.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The absolute path to the file to read",
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "The line number to start reading from",
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "The line number to stop reading at",
                        },
                    },
                    "required": ["file_path"],
                },
            },
            {
                "name": "edit_file",
                "description": """Use this tool to propose an edit to an existing file or write the content in a new file. This will be read by a less intelligent model, which will quickly apply the edit. You should make it clear what the edit is, while also minimizing the unchanged code you write. You should still bias towards repeating as few lines of the original file as possible to convey the change. But, each edit should contain sufficient context of unchanged lines around the code you're editing to resolve ambiguity. Make sure it is clear what the edit should be, and where it should be applied.

                IMPORTANT: If you need to make multiple changes to the same file, COMBINE ALL CHANGES into a SINGLE tool call. Do NOT use this tool multiple times for the same file - consolidate all modifications, additions, and deletions into one comprehensive edit by following the below formatting requirements.

                CRITICAL FORMATTING REQUIREMENTS:
                - For ADDITIONS/MODIFICATIONS: Include 3 lines of UNCHANGED code above and below your new/modified code to provide precise context for placement
                - For DELETIONS: Show the code block WITH the target lines already removed, including 3 unchanged context lines around the deletion area
                - The FastApply model needs this context to accurately locate where changes should be applied
                """,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_file_path": {
                            "type": "string",
                            "description": "The absolute path to the file to edit",
                        },
                        "code_snippet": {
                            "type": "string",
                            "description": "The new code content to write to the file",
                        },
                    },
                    "required": [
                        "target_file_path",
                        "code_snippet",
                    ],
                },
            },
            {
                "name": "search_replace",
                "description": "A tool for searching pattern in files and replace it with new text. this tool allows you to perform search and replace operation across files in codebase.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The text or regex pattern to search for",
                        },
                        "replacement": {
                            "type": "string",
                            "description": "The text to replace the matched content with",
                        },
                        "options": {
                            "type": "object",
                            "properties": {
                                "case_sensitive": {
                                    "type": "boolean",
                                    "description": "Whether the search should be case sensitive",
                                },
                                "include_pattern": {
                                    "type": "string",
                                    "description": "Glob pattern for files to include",
                                },
                                "exclude_pattern": {
                                    "type": "string",
                                    "description": "Glob pattern for files to exclude",
                                },
                                "search_paths": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Paths to search in",
                                },
                            },
                        },
                    },
                    "required": ["query", "replacement"],
                },
            },
            {
                "name": "run_terminal_cmd",
                "description": "Execute terminal commands to run builds, tests, install packages, or perform system operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "cmd": {
                            "type": "string",
                            "description": "The terminal command to execute",
                        },
                        "is_background": {
                            "type": "boolean",
                            "description": "Whether to run the command in the background",
                        },
                    },
                    "required": ["cmd", "is_background"],
                },
            },
            {
                "name": "list_directory",
                "description": "List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "The path to the directory to list, If not provided, the default path is the codebase path",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list subdirectories recursively",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "search_files",
                "description": "Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The fuzzy filename pattern to search for in the current directory.",
                        }
                    },
                    "required": ["pattern"],
                },
            },
            {
                "name": "delete_file",
                "description": "Deletes a file or directory at the specified path with strict safety checks. Protected system or project-critical paths (e.g., node_modules, .env, src) and hidden/system files cannot be deleted. The tool returns the deletion status and an error message if the deletion is rejected or fails",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The absolute path to the file that should be deleted. ",
                        }
                    },
                    "required": ["path"],
                },
            },
            {
                "name": "grep_search",
                "description": "This is best for finding exact text matches or regex patterns. This is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types. Use this tool to run fast, exact regex searches over text files using the `ripgrep` engine. To avoid overwhelming output, the results are capped at 50 matches. Use the include or exclude patterns to filter the search scope by file type or specific paths.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The regex pattern or text to search for",
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether to search case-sensitively",
                        },
                        "include_pattern": {
                            "type": "string",
                            "description": "The pattern to include in the search",
                        },
                        "exclude_pattern": {
                            "type": "string",
                            "description": "The pattern to exclude in the search",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "exit_tool",
                "description": "Use this tool to exit the agent loop. This is useful when you have completed your task and want to exit the agent loop.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "What things you have done so far",
                        }
                    },
                    "required": ["summary"],
                },
            },
        ]

    async def call_tool(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a specific tool with the given input parameters
        """
        # Get the current session's codebase path from session context
        session_id = session_state.get()
        codebase_path = (
            f"artifacts/{session_id}/codebase" if session_id else None
        )

        # For directory/search tools, send default codebase path (can be overridden)
        directory_search_tools = {
            "list_directory",
            "grep_search",
            "run_terminal_cmd",
            "search_replace",
            "search_files",
        }

        # For file-specific tools, IDE agent sends absolute paths directly
        file_specific_tools = {"read_file", "edit_file", "delete_file"}

        if tool_name in directory_search_tools and codebase_path:
            # Set default working directory for directory/search operations
            tool_input["default_path"] = codebase_path

        if tool_name == "exit_tool":
            # Keep the original summary from the agent, just set the file path
            tool_input["file_path"] = os.path.join(
                codebase_path, "scratchpads/global_scratchpad.txt"
            )
            tool_input["explanation"] = "IDE Agent task completion summary"

        try:
            endpoint_map = {
                "read_file": "/read-file",
                "edit_file": "/edit-file",
                "search_replace": "/search-replace",
                "run_terminal_cmd": "/run-terminal-cmd",
                "list_directory": "/list-directory",
                "search_files": "/search-files",
                "delete_file": "/delete-file",
                "code_base_search": "/code-base-search",
                "grep_search": "/grep-search",
                "web_search": "/web-search",
                "exit_tool": "/exit-tool",
            }

            if tool_name not in endpoint_map:
                raise ValueError(f"Unknown tool: {tool_name}")

            endpoint = endpoint_map[tool_name]
            url = f"{self.tools_base_url}{endpoint}"

            # Map tool input to the expected request format for each endpoint
            request_payload = self._map_tool_input_to_request(
                tool_name, tool_input
            )

            async with httpx.AsyncClient(
                timeout=self.timeout, verify=False
            ) as client:
                response = await client.post(url, json=request_payload)
                response.raise_for_status()

                result = response.json()
                loggers["ide_agent"].info(
                    f"Tool {tool_name} called successfully"
                )
                return result

        except httpx.RequestError as exc:
            error_msg = f"Error calling tool {tool_name}: {str(exc)}"
            loggers["ide_agent"].error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        except httpx.HTTPStatusError as exc:
            error_msg = f"HTTP error calling tool {tool_name}: {exc.response.status_code}"
            loggers["ide_agent"].error(error_msg)
            raise HTTPException(
                status_code=exc.response.status_code, detail=error_msg
            )
        except Exception as exc:
            error_msg = f"Unexpected error calling tool {tool_name}: {str(exc)}"
            loggers["ide_agent"].error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

    def _map_tool_input_to_request(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map the tool input to the expected request format for each tool endpoint
        """
        if tool_name == "run_terminal_cmd":
            return {
                "cmd": tool_input.get("cmd"),
                "is_background": tool_input.get("is_background"),
                "default_path": tool_input.get("default_path"),
            }
        elif tool_name == "web_search":
            return {
                "search_query": tool_input.get("query"),
            }
        elif tool_name == "code_base_search":
            return {"search_query": tool_input.get("query")}
        elif tool_name == "grep_search":
            return {
                "query": tool_input.get("query"),
                "case_sensitive": tool_input.get("case_sensitive"),
                "include_pattern": tool_input.get("include_pattern"),
                "exclude_pattern": tool_input.get("exclude_pattern"),
                "default_path": tool_input.get("default_path"),
            }
        elif tool_name == "exit_tool":
            return {
                "file_path": tool_input.get("file_path"),
                "summary": tool_input.get("summary"),
                "explanation": tool_input.get("explanation"),
            }
        else:
            # For most tools, the input can be passed directly
            return tool_input

    def format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """
        Format tool results for display to the LLM
        """
        if result.get("success"):
            if tool_name in ["read_file", "edit_file", "search_replace"]:
                return f"✅ {tool_name} completed successfully.\n\nResult:\n{result.get('data', '')}"
            elif tool_name == "run_terminal_cmd":
                output = result.get("data", {})
                return f"✅ Command executed successfully.\n\nOutput:\n{output.get('output', '')}\nReturn code: {output.get('return_code', 0)}"
            elif tool_name == "list_directory":
                files = result.get("data", [])
                file_list = "\n".join([f"  {file}" for file in files])
                return f"✅ Directory listed successfully.\n\nContents:\n{file_list}"
            elif tool_name in ["code_base_search", "grep_search"]:
                matches = result.get("data", [])
                if matches:
                    formatted_matches = []
                    for match in matches[:10]:  # Limit to first 10 matches
                        formatted_matches.append(
                            f"📁 {match.get('file', 'Unknown file')}\n   {match.get('content', '')}"
                        )
                    return (
                        f"✅ Search completed successfully. Found {len(matches)} matches.\n\n"
                        + "\n\n".join(formatted_matches)
                    )
                else:
                    return "✅ Search completed successfully. No matches found."
            elif tool_name == "web_search":
                search_results = result.get("data", [])
                if search_results:
                    formatted_results = []
                    for result_item in search_results[
                        :5
                    ]:  # Limit to first 5 results
                        formatted_results.append(
                            f"🔗 {result_item.get('title', 'No title')}\n   {result_item.get('snippet', '')}"
                        )
                    return (
                        f"✅ Web search completed successfully.\n\n"
                        + "\n\n".join(formatted_results)
                    )
                else:
                    return "✅ Web search completed successfully. No results found."
            elif tool_name == "exit_tool":
                return f"✅ Exit tool executed successfully. Summary saved to file."
            else:
                return f"✅ {tool_name} completed successfully.\n\nResult:\n{json.dumps(result.get('data', {}), indent=2)}"
        else:
            error_msg = result.get("error", "Unknown error")
            return f"❌ {tool_name} failed: {error_msg}"
