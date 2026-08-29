"""Package for ADK agent implementation in browser_agent."""

import warnings

from google.adk.agents import Agent

# Suppress experimental UserWarnings emitted by ADK framework
warnings.filterwarnings("ignore", category=UserWarning, module=r".*google\.adk.*")
warnings.filterwarnings("ignore", category=UserWarning, message=r".*\[EXPERIMENTAL\].*")

root_agent = Agent(
  name="browser_agent",
  model="gemini-3.5-flash",
  description="Browser automation and web data agent.",
  instruction=(
    "You are a helpful browser assistant capable of navigating web pages, "
    "retrieving online content, and extracting structured web data."
  ),
  tools=[],
)

__all__ = ["root_agent"]
