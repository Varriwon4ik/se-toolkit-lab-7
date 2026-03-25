"""LLM API client for intent routing with tool calling."""

import json
import sys
from typing import Any

import httpx


# Tool schemas for all 9 backend endpoints
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get the list of all labs and tasks available in the LMS",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get the list of enrolled students and their groups",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average pass rates and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day timeline for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return, e.g. 5, 10",
                        "default": 5,
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a specific lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync to refresh data from autochecker",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS). 
Your job is to help users get information about labs, tasks, scores, and students.

You have access to tools (API endpoints) that can fetch real data from the backend.
When a user asks a question, you should:
1. Think about what data you need to answer the question
2. Call the appropriate tool(s) to get that data
3. Use the tool results to formulate a helpful, accurate response

Available tools:
- get_items: List all labs and tasks
- get_learners: List enrolled students and groups
- get_scores: Score distribution for a lab (4 buckets)
- get_pass_rates: Per-task pass rates and attempts for a lab
- get_timeline: Submissions per day for a lab
- get_groups: Per-group performance for a lab
- get_top_learners: Top N students for a lab
- get_completion_rate: Completion percentage for a lab
- trigger_sync: Refresh data from autochecker

For multi-step questions (e.g., "which lab has the lowest pass rate?"), 
you may need to call multiple tools:
1. First call get_items to get all labs
2. Then call get_pass_rates for each lab
3. Compare the results and provide an answer

If the user's message is a greeting (hello, hi, etc.), respond warmly and mention what you can help with.
If the user's message is unclear or gibberish, politely ask for clarification and suggest what you can do.
If the user mentions a specific lab (e.g., "lab 4" or "lab-04"), ask what they want to know about it 
(scores, pass rates, completion rate, etc.) unless their intent is clear.

Always be helpful, concise, and use the actual data from tool calls in your responses."""


class LLMClient:
    """Client for the LLM API with tool calling support."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        """Initialize the LLM client.

        Args:
            base_url: The LLM API base URL.
            api_key: The LLM API authentication key.
            model: The model name to use.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: httpx.AsyncClient | None = None
        self._lms_client = None

    def set_lms_client(self, lms_client: Any) -> None:
        """Set the LMS client for tool execution.

        Args:
            lms_client: The LMSClient instance for API calls.
        """
        self._lms_client = lms_client

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=60.0,
            )
        return self._client

    def _debug(self, message: str) -> None:
        """Print debug message to stderr.

        Args:
            message: The debug message to print.
        """
        print(message, file=sys.stderr)

    async def _execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool by calling the appropriate LMS API endpoint.

        Args:
            name: The tool/function name.
            arguments: The tool arguments.

        Returns:
            The tool result.
        """
        if self._lms_client is None:
            return {"error": "LMS client not initialized"}

        try:
            if name == "get_items":
                labs, error = await self._lms_client.get_labs()
                if error:
                    return {"error": error}
                return {"items": labs, "count": len(labs)}

            elif name == "get_learners":
                # Call the learners endpoint
                client = await self._get_client()
                # We need to call LMS API, not LLM API
                # Use the lms_client's internal client
                lms_client = await self._lms_client._get_client()
                response = await lms_client.get("/learners")
                response.raise_for_status()
                learners = response.json()
                return {"learners": learners, "count": len(learners) if isinstance(learners, list) else 0}

            elif name == "get_scores":
                lab = arguments.get("lab", "")
                client = await self._lms_client._get_client()
                response = await client.get("/analytics/scores", params={"lab": lab})
                response.raise_for_status()
                return response.json()

            elif name == "get_pass_rates":
                lab = arguments.get("lab", "")
                pass_rates, error = await self._lms_client.get_pass_rates(lab)
                if error:
                    return {"error": error}
                return [
                    {"task_name": pr.task_name, "pass_rate": pr.pass_rate, "attempts": pr.attempts}
                    for pr in pass_rates
                ]

            elif name == "get_timeline":
                lab = arguments.get("lab", "")
                client = await self._lms_client._get_client()
                response = await client.get("/analytics/timeline", params={"lab": lab})
                response.raise_for_status()
                return response.json()

            elif name == "get_groups":
                lab = arguments.get("lab", "")
                client = await self._lms_client._get_client()
                response = await client.get("/analytics/groups", params={"lab": lab})
                response.raise_for_status()
                return response.json()

            elif name == "get_top_learners":
                lab = arguments.get("lab", "")
                limit = arguments.get("limit", 5)
                client = await self._lms_client._get_client()
                response = await client.get(
                    "/analytics/top-learners",
                    params={"lab": lab, "limit": limit},
                )
                response.raise_for_status()
                return response.json()

            elif name == "get_completion_rate":
                lab = arguments.get("lab", "")
                client = await self._lms_client._get_client()
                response = await client.get("/analytics/completion-rate", params={"lab": lab})
                response.raise_for_status()
                return response.json()

            elif name == "trigger_sync":
                client = await self._lms_client._get_client()
                response = await client.post("/pipeline/sync", json={})
                response.raise_for_status()
                return response.json()

            else:
                return {"error": f"Unknown tool: {name}"}

        except httpx.HTTPStatusError as exc:
            return {"error": f"HTTP {exc.response.status_code}: {exc.response.reason_phrase}"}
        except Exception as exc:
            return {"error": str(exc)}

    async def chat_with_tools(
        self,
        user_message: str,
        max_iterations: int = 5,
    ) -> str:
        """Chat with the LLM using tool calling.

        Args:
            user_message: The user's message text.
            max_iterations: Maximum tool calling iterations.

        Returns:
            The final response text.
        """
        client = await self._get_client()

        # Build conversation history
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        for iteration in range(max_iterations):
            # Call LLM with tools
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": TOOL_SCHEMAS,
                    "tool_choice": "auto",
                },
            )

            if response.status_code == 401:
                return "LLM error: HTTP 401 Unauthorized. The OAuth token may have expired."

            response.raise_for_status()
            data = response.json()

            if not data.get("choices") or not data["choices"]:
                return "LLM returned empty response"

            choice = data["choices"][0]
            assistant_message = choice.get("message", {})

            # Check if LLM wants to call tools
            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                # LLM returned final answer
                content = assistant_message.get("content", "")
                return content if content else "I don't have enough information to answer that."

            # Add assistant message with tool calls to history
            messages.append(assistant_message)

            # Execute each tool call
            for tool_call in tool_calls:
                tool_id = tool_call.get("id", "")
                function = tool_call.get("function", {})
                tool_name = function.get("name", "")
                tool_args_str = function.get("arguments", "{}")

                try:
                    tool_args = json.loads(tool_args_str) if tool_args_str else {}
                except json.JSONDecodeError:
                    tool_args = {}

                self._debug(f"[tool] LLM called: {tool_name}({tool_args})")

                # Execute the tool
                result = await self._execute_tool(tool_name, tool_args)
                result_str = json.dumps(result, ensure_ascii=False, default=str)

                self._debug(f"[tool] Result: {result_str[:200]}..." if len(result_str) > 200 else f"[tool] Result: {result_str}")

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": result_str,
                })

            self._debug(f"[summary] Feeding {len(tool_calls)} tool result(s) back to LLM")

        return "I couldn't complete the request after multiple attempts."

    async def route_intent(self, message: str) -> str:
        """Route a user message using LLM with tool calling.

        Args:
            message: The user's message text.

        Returns:
            The response text from the LLM.
        """
        try:
            return await self.chat_with_tools(message)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                return "LLM error: HTTP 401 Unauthorized. The OAuth token may have expired."
            return f"LLM error: HTTP {exc.response.status_code}"
        except Exception as exc:
            return f"LLM error: {str(exc)}"

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
