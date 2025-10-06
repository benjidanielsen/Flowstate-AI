from typing import Dict, List, Optional
from threading import Lock


class Skill:
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Skill(name={self.name}, description={self.description})"


class Agent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.skills: Dict[str, Skill] = {}
        self.available: bool = True

    def add_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def remove_skill(self, skill_name: str):
        if skill_name in self.skills:
            del self.skills[skill_name]

    def has_skill(self, skill_name: str) -> bool:
        return skill_name in self.skills

    def set_availability(self, available: bool):
        self.available = available

    def __repr__(self):
        return f"Agent(agent_id={self.agent_id}, skills={list(self.skills.keys())}, available={self.available})"


class AgentSkillRegistry:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._lock = Lock()

    def register_agent(self, agent_id: str) -> Agent:
        with self._lock:
            if agent_id not in self._agents:
                self._agents[agent_id] = Agent(agent_id)
            return self._agents[agent_id]

    def unregister_agent(self, agent_id: str):
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]

    def add_skill_to_agent(self, agent_id: str, skill_name: str, description: Optional[str] = None):
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent '{agent_id}' not registered.")
            skill = Skill(skill_name, description)
            agent.add_skill(skill)

    def remove_skill_from_agent(self, agent_id: str, skill_name: str):
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent '{agent_id}' not registered.")
            agent.remove_skill(skill_name)

    def set_agent_availability(self, agent_id: str, available: bool):
        with self._lock:
            agent = self._agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent '{agent_id}' not registered.")
            agent.set_availability(available)

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        with self._lock:
            return self._agents.get(agent_id)

    def find_agents_with_skill(self, skill_name: str, only_available: bool = True) -> List[Agent]:
        with self._lock:
            agents = [agent for agent in self._agents.values()
                      if agent.has_skill(skill_name) and (agent.available or not only_available)]
            return agents

    def list_all_agents(self) -> List[Agent]:
        with self._lock:
            return list(self._agents.values())


# Example usage:
# registry = AgentSkillRegistry()
# agent = registry.register_agent('agent_1')
# registry.add_skill_to_agent('agent_1', 'nlp', 'Natural Language Processing')
# registry.set_agent_availability('agent_1', True)
# print(registry.find_agents_with_skill('nlp'))
