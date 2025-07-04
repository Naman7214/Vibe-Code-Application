import os
from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.ide_agent_schema import (
    IDEAgentRequest,
)
from system.backend.agentic_workflow.app.prompts.ide_agent_prompts.ide_agent_prompt import (
    SYSTEM_PROMPT,
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

    async def execute(self, request: IDEAgentRequest) -> Dict[str, Any]:
        """
        Execute IDE agent processing with tool calling loop

        :param request: IDEAgentRequest containing user query
        :return: Dict with success status, message, and conversation history
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

            # Initialize conversation with system context
            conversation_history = []
            tool_call_count = 0

            # Get tool definitions and system prompt
            tools = self.ide_tools.get_tool_definitions()
            system_prompt_with_context = f"{SYSTEM_PROMPT}\n\n**Session Context:**\n- Session ID: {session_id}\n- Codebase location: {codebase_path}\n- You are working on the codebase generated for this session."

            print(f"📁 Codebase found at: {codebase_path}")
            print(f"🛠️  Available tools: {len(tools)}")

            # Initialize messages list for the conversation
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"<USER_QUERY>\n{request.user_query}\n</USER_QUERY>\n\nPlease help me with this request. The codebase is located at {codebase_path}.",
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

                # Add assistant's response to conversation history
                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": response["content"],
                        "tool_calls": response["tool_calls"],
                    }
                )

                # Show agent's response if there's text content
                if response["content"] and response["content"].strip():
                    print(
                        f"🤖 Agent says: {response['content'][:200]}{'...' if len(response['content']) > 200 else ''}"
                    )

                # If no tool calls, we're done
                if not response["tool_calls"]:
                    print("✅ Agent completed - no more tool calls needed")
                    loggers["ide_agent"].info(
                        f"IDE agent completed without tool calls. Total tool calls used: {tool_call_count}"
                    )
                    break

                print(
                    f"🔧 Received {len(response['tool_calls'])} tool call(s) to execute"
                )

                # Execute tool calls
                tool_results = []
                for tool_call in response["tool_calls"]:
                    if tool_call_count >= self.max_tool_calls:
                        loggers["ide_agent"].warning(
                            f"Maximum tool calls ({self.max_tool_calls}) reached"
                        )
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

                        # Add tool result to conversation history
                        conversation_history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": formatted_result,
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

                        # Add error to conversation history
                        conversation_history.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": tool_name,
                                "content": f"❌ Error: {error_msg}",
                            }
                        )

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

                # If we've reached the maximum tool calls, break
                if tool_call_count >= self.max_tool_calls:
                    print(
                        f"⚠️  Maximum tool calls ({self.max_tool_calls}) reached - stopping execution"
                    )
                    loggers["ide_agent"].warning(
                        f"Maximum tool calls ({self.max_tool_calls}) reached"
                    )
                    break

            # Get final response if we stopped due to tool limit
            if tool_call_count >= self.max_tool_calls:
                print("📝 Generating final summary...")
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

                # Show final summary
                if final_response["content"]:
                    print(
                        f"📋 Summary: {final_response['content'][:400]}{'...' if len(final_response['content']) > 400 else ''}"
                    )

                conversation_history.append(
                    {
                        "role": "assistant",
                        "content": final_response["content"],
                        "tool_calls": [],
                    }
                )

            print(
                f"🎯 IDE Agent completed! Total tool calls: {tool_call_count}"
            )

            return {
                "success": True,
                "message": f"IDE agent completed successfully. Used {tool_call_count} tool calls.",
                "conversation_history": conversation_history,
                "tool_calls_used": tool_call_count,
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
                "conversation_history": [],
                "tool_calls_used": 0,
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
                "conversation_history": [],
                "tool_calls_used": 0,
            }
