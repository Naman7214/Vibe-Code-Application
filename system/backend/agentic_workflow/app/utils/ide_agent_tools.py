import json
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

from system.backend.agentic_workflow.app.config.settings import settings
from system.backend.agentic_workflow.app.utils.logger import loggers


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
                "description": "Read the contents of a file. Use this to examine code, configuration files, or any text-based file in the codebase.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        },
                        "start_line": {
                            "type": "integer",
                            "description": "Optional: The line number to start reading from",
                        },
                        "end_line": {
                            "type": "integer",
                            "description": "Optional: The line number to stop reading at",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Brief explanation of why you're reading this file",
                        },
                    },
                    "required": ["file_path", "explanation"],
                },
            },
            {
                "name": "edit_file",
                "description": "Edit a file by providing new code content. Use this to fix bugs, add features, or modify existing code.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_file_path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "code_snippet": {
                            "type": "string",
                            "description": "The new code content to write to the file",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what changes you're making and why",
                        },
                    },
                    "required": [
                        "target_file_path",
                        "code_snippet",
                        "explanation",
                    ],
                },
            },
            {
                "name": "search_replace",
                "description": "Search for specific text patterns and replace them. Use this for precise text replacements across files.",
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
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what you're searching and replacing",
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
                    "required": ["query", "replacement", "explanation"],
                },
            },
            {
                "name": "run_terminal_cmd",
                "description": "Execute terminal commands to run builds, tests, install packages, or perform system operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The terminal command to execute",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what this command does and why you're running it",
                        },
                    },
                    "required": ["command", "explanation"],
                },
            },
            {
                "name": "list_directory",
                "description": "List the contents of a directory to understand the project structure.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "The path to the directory to list",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to list subdirectories recursively",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of why you're listing this directory",
                        },
                    },
                    "required": ["explanation"],
                },
            },
            {
                "name": "search_files",
                "description": "Search for files by name pattern in the codebase.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "The pattern to search for in file names",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what files you're looking for",
                        },
                    },
                    "required": ["pattern", "explanation"],
                },
            },
            {
                "name": "delete_file",
                "description": "Delete a file from the filesystem. Use with caution.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to delete",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of why you're deleting this file",
                        },
                    },
                    "required": ["path", "explanation"],
                },
            },
            {
                "name": "code_base_search",
                "description": "Perform semantic search across the codebase to find relevant code, functions, or patterns.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query describing what you're looking for",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what you're searching for and why",
                        },
                    },
                    "required": ["query", "explanation"],
                },
            },
            {
                "name": "grep_search",
                "description": "Search for exact text patterns or regex in files using grep-like functionality.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The regex pattern or text to search for",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what pattern you're searching for",
                        },
                    },
                    "required": ["query", "explanation"],
                },
            },
            {
                "name": "web_search",
                "description": "Search the web for information, documentation, or solutions to coding problems.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for web search",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what information you're looking for",
                        },
                    },
                    "required": ["query", "explanation"],
                },
            },
        ]

    async def call_tool(
        self, tool_name: str, tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a specific tool with the given input parameters
        """
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
                "command": tool_input.get("command"),
                "explanation": tool_input.get("explanation"),
            }
        elif tool_name == "web_search":
            return {
                "search_query": tool_input.get("query"),
                "explanation": tool_input.get("explanation"),
            }
        elif tool_name == "code_base_search":
            return {
                "search_query": tool_input.get("query"),
                "explanation": tool_input.get("explanation"),
            }
        elif tool_name == "grep_search":
            return {
                "query": tool_input.get("query"),
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
            else:
                return f"✅ {tool_name} completed successfully.\n\nResult:\n{json.dumps(result.get('data', {}), indent=2)}"
        else:
            error_msg = result.get("error", "Unknown error")
            return f"❌ {tool_name} failed: {error_msg}"
