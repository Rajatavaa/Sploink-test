from intent_parser import parse_intent, load_registry


async def route(intent: dict, agents: list = None) -> dict:
    """
    Routes intent to the appropriate agent.
    Supports evolution demo: chooses agent with highest quality_score.
    """
    if agents is None:
        agents = load_registry()

    task_type = intent.get("task_type")

    matching_agents = [
        agent for agent in agents if agent.get("capability") == task_type
    ]

    if not matching_agents:
        return None

    if len(matching_agents) == 1:
        selected = matching_agents[0]
    else:
        for agent in matching_agents:
            quality_score = agent.get("quality_score", 1)
            agent["quality_score"] = quality_score

        selected = max(matching_agents, key=lambda a: a.get("quality_score", 1))

    return selected


async def route_with_logging(intent: dict, agents: list = None) -> dict:
    """Routes intent with logging output."""
    selected = await route(intent, agents)

    if selected:
        print(
            f"[Router] Selected agent: {selected.get('name')} (capability: {selected.get('capability')})"
        )
    else:
        print(f"[Router] No agent found for intent: {intent.get('task_type')}")

    return selected
