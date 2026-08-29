from browser_agent import __authors__, __version__, root_agent


def test_package_metadata():
  assert __version__ == "0.1.0"
  assert __authors__ == "John K. Lee"


def test_root_agent():
  assert root_agent is not None
  assert root_agent.name == "browser_agent"
