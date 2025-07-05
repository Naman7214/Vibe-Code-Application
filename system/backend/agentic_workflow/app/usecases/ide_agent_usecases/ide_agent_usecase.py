import glob
import os
from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.ide_agent_schema import (
    IDEAgentRequest,
)
from system.backend.agentic_workflow.app.prompts.ide_agent_prompts.ide_agent_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.ide_agent_tools import (
    IDEAgentTools,
)
from system.backend.agentic_workflow.app.utils.logger import loggers
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class IDEAgentUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo
        self.ide_tools = IDEAgentTools()
        self.max_tool_calls = 25

    def _get_absolute_path(self, relative_path: str) -> str:
        """Convert relative path to absolute path"""
        return os.path.abspath(relative_path)



    def _read_file_structure_content(self, session_id: str) -> str:
        """Read and return file structure content"""
        file_structure_path = (
            f"artifacts/{session_id}/scratchpads/file_structure.txt"
        )
        file_structure_content = ""

        try:
            if os.path.exists(file_structure_path):
                with open(file_structure_path, "r", encoding="utf-8") as f:
                    file_structure_content = f.read()
            else:
                file_structure_content = "File structure not available"
        except Exception as e:
            loggers["ide_agent"].warning(
                f"Failed to read file structure: {str(e)}"
            )
            file_structure_content = f"Error reading file structure: {str(e)}"

        return file_structure_content

    def _read_global_scratch_pad_content(self, session_id: str) -> str:
        """Read and return global scratch pad content"""
        global_scratch_pad_path = f"artifacts/{session_id}/scratchpads/global_scratchpad.txt"
        global_scratch_pad_content = ""

        try:
            if os.path.exists(global_scratch_pad_path):
                with open(global_scratch_pad_path, "r", encoding="utf-8") as f:
                    global_scratch_pad_content = f.read()
            else:
                global_scratch_pad_content = "Global scratch pad not available"
        except Exception as e:
            loggers["ide_agent"].warning(
                f"Failed to read global scratch pad: {str(e)}"
            )
            global_scratch_pad_content = f"Error reading global scratch pad: {str(e)}"

        return global_scratch_pad_content

    def _read_screen_scratch_pads_content(self, session_id: str) -> str:
        """Read and return all screen scratch pads content"""
        screen_scratch_pads_dir = f"artifacts/{session_id}/scratchpads/screen_scratchpads"
        screen_scratch_pads_content = ""

        try:
            if os.path.exists(screen_scratch_pads_dir):
                # Get all .txt files in the screen_scratchpads directory
                pattern = os.path.join(screen_scratch_pads_dir, "*.txt")
                screen_files = glob.glob(pattern)
                screen_files.sort()  # Sort for consistent ordering

                if screen_files:
                    screen_contents = []
                    for file_path in screen_files:
                        file_name = os.path.basename(file_path)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_content = f.read()
                                screen_contents.append(f"=== {file_name} ===\n{file_content}")
                        except Exception as e:
                            loggers["ide_agent"].warning(
                                f"Failed to read screen scratch pad {file_name}: {str(e)}"
                            )
                            screen_contents.append(f"=== {file_name} ===\nError reading file: {str(e)}")
                    
                    screen_scratch_pads_content = "\n\n".join(screen_contents)
                else:
                    screen_scratch_pads_content = "No screen scratch pads found"
            else:
                screen_scratch_pads_content = "Screen scratch pads directory not available"
        except Exception as e:
            loggers["ide_agent"].warning(
                f"Failed to read screen scratch pads: {str(e)}"
            )
            screen_scratch_pads_content = f"Error reading screen scratch pads: {str(e)}"

        return screen_scratch_pads_content

    def _extract_summary_from_exit_tool_result(
        self, tool_result: Dict[str, Any], tool_input: Dict[str, Any]
    ) -> str:
        """Extract summary from exit tool result and input"""
        try:
            # First try to get the summary directly from the tool input
            if tool_input and "summary" in tool_input:
                summary = tool_input["summary"]
                if summary and summary.strip():
                    return summary.strip()

            # Fallback: try to extract from the file if it was written
            if tool_result.get("success") and "data" in tool_result:
                data = tool_result["data"]
                if isinstance(data, dict) and "details" in data:
                    file_path = data["details"].get("file_path")
                    if file_path and os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            # Extract the last summary from the file
                            lines = content.strip().split("\n")
                            summary_start = -1
                            for i in range(len(lines) - 1, -1, -1):
                                if "Summary:" in lines[i]:
                                    summary_start = i + 1
                                    break

                            if summary_start > 0:
                                summary_lines = []
                                for i in range(summary_start, len(lines)):
                                    if lines[i].startswith("="):
                                        break
                                    summary_lines.append(lines[i])
                                return "\n".join(summary_lines).strip()

            return "Agent completed the task using exit tool."
        except Exception as e:
            loggers["ide_agent"].warning(
                f"Failed to extract summary from exit tool: {str(e)}"
            )
            return "Agent completed the task using exit tool."

    async def execute(self, request: IDEAgentRequest) -> Dict[str, Any]:
        """
        Execute IDE agent processing with tool calling loop

        :param request: IDEAgentRequest containing user query
        :return: Dict with success status, final message, and metadata
        """
        try:
            # Get session_id from context (set by middleware)
            session_id = session_state.get()
            if not session_id:
                raise ValueError("No session_id available in context")

            loggers["ide_agent"].info(
                f"Starting IDE agent for session: {session_id}"
            )
            print(f"🤖 IDE Agent started for session: {session_id}")

            # Get the codebase path for the session
            codebase_path = f"artifacts/{session_id}/codebase"
            if not os.path.exists(codebase_path):
                raise ValueError(
                    f"No codebase found for session {session_id}. Please run code generation first."
                )

            # Get context paths and content
            file_structure_content = self._read_file_structure_content(
                session_id
            )
            global_scratch_pad_content = self._read_global_scratch_pad_content(
                session_id
            )
            screen_scratch_pads_content = self._read_screen_scratch_pads_content(
                session_id
            )

            print(f"📁 Codebase found at: {codebase_path}")
            print(
                f"🗂️  File structure loaded: {len(file_structure_content)} characters"
            )
            print(
                f"📝 Global scratch pad content: {len(global_scratch_pad_content)} characters"
            )
            print(
                f"📋 Screen scratch pads content: {len(screen_scratch_pads_content)} characters"
            )

            # Initialize conversation tracking
            tool_call_count = 0
            final_message = ""
            exit_summary = ""
            completion_reason = "completed"

            # Get tool definitions and system prompt
            tools = self.ide_tools.get_tool_definitions()
            system_prompt_with_context = SYSTEM_PROMPT.format(
                global_scratch_pad_content=global_scratch_pad_content,
                screen_scratch_pads_content=screen_scratch_pads_content,
            )

            print(f"🛠️  Available tools: {len(tools)}")

            # Initialize messages list for the conversation with enhanced context
            user_prompt = USER_PROMPT.format(
                user_query=request.user_query,
                codebase_path=self._get_absolute_path(codebase_path),
                file_structure_content=file_structure_content,
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt,
                        }
                    ],
                }
            ]

            # Tool calling loop
            while tool_call_count < self.max_tool_calls:
                print(
                    f"\n💭 Making request to LLM (iteration {tool_call_count + 1})..."
                )

                # Make request to LLM with tools
                response = (
                    await self.anthropic_service.generate_text_with_tools(
                        messages=messages,
                        system_prompt=system_prompt_with_context,
                        tools=tools,
                    )
                )

                # Store the current response content as potential final message
                if response["content"] and response["content"].strip():
                    final_message = response["content"]
                    print(
                        f"🤖 Agent says: {response['content'][:200]}{'...' if len(response['content']) > 200 else ''}"
                    )

                # If no tool calls, we're done
                if not response["tool_calls"]:
                    print("✅ Agent completed - no more tool calls needed")
                    completion_reason = "natural_completion"
                    loggers["ide_agent"].info(
                        f"IDE agent completed without tool calls. Total tool calls used: {tool_call_count}"
                    )
                    break

                print(
                    f"🔧 Received {len(response['tool_calls'])} tool call(s) to execute"
                )

                # Execute tool calls
                tool_results = []
                exit_tool_called = False

                for tool_call in response["tool_calls"]:
                    if tool_call_count >= self.max_tool_calls:
                        loggers["ide_agent"].warning(
                            f"Maximum tool calls ({self.max_tool_calls}) reached"
                        )
                        completion_reason = "max_tool_calls"
                        break

                    tool_call_count += 1
                    tool_name = tool_call["name"]
                    tool_input = tool_call["input"]

                    print(f"  ⚡ Executing: {tool_name} (#{tool_call_count})")

                    loggers["ide_agent"].info(
                        f"Calling tool: {tool_name} (call #{tool_call_count})"
                    )

                    try:
                        # Call the tool
                        tool_result = await self.ide_tools.call_tool(
                            tool_name, tool_input
                        )
                        formatted_result = self.ide_tools.format_tool_result(
                            tool_name, tool_result
                        )

                        # Check if exit_tool was called
                        if tool_name == "exit_tool":
                            exit_tool_called = True
                            completion_reason = "exit_tool"
                            exit_summary = (
                                self._extract_summary_from_exit_tool_result(
                                    tool_result, tool_input
                                )
                            )
                            print(f"🚪 Exit tool called - stopping execution")
                            loggers["ide_agent"].info(
                                "Exit tool called - stopping agent loop"
                            )

                        # Show tool result (truncated for readability)
                        result_preview = (
                            formatted_result[:300]
                            if formatted_result
                            else "No result"
                        )
                        print(
                            f"    ✅ Result: {result_preview}{'...' if len(formatted_result) > 300 else ''}"
                        )

                        tool_results.append(
                            {
                                "tool_call_id": tool_call["id"],
                                "result": formatted_result,
                            }
                        )

                    except Exception as e:
                        error_msg = f"Error calling tool {tool_name}: {str(e)}"
                        loggers["ide_agent"].error(error_msg)

                        print(f"    ❌ Tool failed: {error_msg}")

                        tool_results.append(
                            {
                                "tool_call_id": tool_call["id"],
                                "result": f"❌ Error: {error_msg}",
                            }
                        )

                    # Break if exit tool was called
                    if exit_tool_called:
                        break

                # Add assistant message with tool calls to messages
                assistant_message = {"role": "assistant", "content": []}

                # Add text content if any
                if response["content"] and response["content"].strip():
                    assistant_message["content"].append(
                        {"type": "text", "text": response["content"]}
                    )

                # Add tool use blocks if any
                if response["tool_calls"]:
                    for tool_call in response["tool_calls"]:
                        assistant_message["content"].append(
                            {
                                "type": "tool_use",
                                "id": tool_call["id"],
                                "name": tool_call["name"],
                                "input": tool_call["input"],
                            }
                        )

                messages.append(assistant_message)

                # Add tool results to messages
                for tool_result in tool_results:
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_result["tool_call_id"],
                                    "content": tool_result["result"],
                                }
                            ],
                        }
                    )

                # Break if exit tool was called or max tool calls reached
                if exit_tool_called:
                    break

                if tool_call_count >= self.max_tool_calls:
                    print(
                        f"⚠️  Maximum tool calls ({self.max_tool_calls}) reached - stopping execution"
                    )
                    completion_reason = "max_tool_calls"
                    loggers["ide_agent"].warning(
                        f"Maximum tool calls ({self.max_tool_calls}) reached"
                    )
                    break

            # Handle final response based on completion reason
            if completion_reason == "max_tool_calls":
                print("📝 Generating final summary due to tool limit...")
                # Add a final message asking for summary
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please provide a summary of what has been accomplished and any remaining tasks.",
                            }
                        ],
                    }
                )

                final_response = (
                    await self.anthropic_service.generate_text_with_tools(
                        messages=messages,
                        system_prompt=system_prompt_with_context,
                        tools=[],  # No tools for final summary
                    )
                )

                if final_response["content"]:
                    final_message = final_response["content"]
                    print(
                        f"📋 Summary: {final_response['content'][:400]}{'...' if len(final_response['content']) > 400 else ''}"
                    )

            elif completion_reason == "exit_tool":
                # Use the exit summary as the final message
                if exit_summary:
                    final_message = exit_summary
                elif not final_message:
                    final_message = (
                        "Task completed successfully using exit tool."
                    )

            # Ensure we have a final message
            if not final_message:
                final_message = "IDE agent completed successfully."

            print(
                f"🎯 IDE Agent completed! Total tool calls: {tool_call_count}"
            )

            return {
                "success": True,
                "message": final_message,
                "tool_calls_used": tool_call_count,
                "completion_reason": completion_reason,
                "session_id": session_id,
                "error": None,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="ide_agent",
                    error_message=f"HTTP error in IDE agent usecase: {str(e.detail)}",
                    stack_trace=str(e),
                )
            )

            return {
                "success": False,
                "message": f"HTTP error in IDE agent usecase: {str(e.detail)}",
                "error": e.detail,
                "tool_calls_used": 0,
                "completion_reason": "error",
            }

        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="ide_agent",
                    error_message=f"Error in IDE agent usecase: {str(e)}",
                    stack_trace=str(e),
                )
            )

            return {
                "success": False,
                "message": f"Error in IDE agent usecase: {str(e)}",
                "error": str(e),
                "tool_calls_used": 0,
                "completion_reason": "error",
            }
