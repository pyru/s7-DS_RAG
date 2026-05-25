# LLM Agent Architectures: ReAct, Tool Use, and Memory

An LLM agent is a system where a language model acts as an autonomous controller that iteratively plans, executes actions, observes results, and updates its reasoning — unlike a single-pass chatbot that only generates text. Agents enable LLMs to solve multi-step problems requiring external tool use, long-horizon planning, and persistent memory.

## The ReAct Pattern

**ReAct (Reasoning + Acting)** (Yao et al., 2022) interleaves chain-of-thought reasoning with action execution in a Thought → Action → Observation loop:

```
Thought: I need to find out what temperature Tokyo is today.
Action: web_search("Tokyo current temperature May 2025")
Observation: Tokyo is 24°C with scattered clouds.
Thought: Now I can answer the question.
Action: FINISH("Tokyo is currently 24°C.")
```

ReAct significantly outperforms either reasoning alone or acting alone, because observations ground future reasoning and prevent hallucination.

## Tool Use

Tools are functions the LLM can invoke. Common tools in production agents:
- **Web search**: Retrieve current information beyond training cutoff
- **Code execution**: Run Python, verify computations, parse data
- **File operations**: Read, write, search files in a workspace
- **API calls**: Fetch data from databases, services, sensors
- **Memory operations**: Store and retrieve information across turns

Tools are described to the model via structured schemas (name, description, parameters). The model selects tools and arguments; the runtime executes them and returns results.

## Memory Systems

Agents require multiple memory types:

**In-context memory**: Information in the current prompt window. Limited by context length (8K–1M tokens), wiped between sessions.

**External memory (episodic)**: Vector database of past interactions, indexed by embedding similarity. Enables recall of specific past events: "What did the user ask last Tuesday?"

**Knowledge base (semantic)**: Vector-indexed document corpus. Enables RAG over static knowledge.

**Procedural memory**: Learned skills and workflows stored as retrievable templates or fine-tuned weights.

## Perception → Decision → Action → Memory Architecture

The S7 agent implements this four-layer architecture:

1. **Perception**: Reads memory, observes current state, decomposes goals
2. **Decision**: Selects next action (tool call or final answer) given goals and observations
3. **Action**: Executes tool call, handles artifacts for large outputs
4. **Memory**: Records tool outcomes as indexed facts for future retrieval

This architecture separates concerns cleanly: Perception manages goal state, Decision selects actions, Action handles execution, Memory ensures durability.

## Multi-Agent Systems

Complex tasks benefit from multiple specialized agents:
- **Orchestrator**: Decomposes high-level goals into sub-tasks
- **Researcher**: Handles web search and document retrieval
- **Coder**: Writes and executes code
- **Critic**: Reviews and corrects other agents' outputs

Agents communicate via message passing or shared memory. Frameworks like LangGraph, CrewAI, and AutoGen implement multi-agent patterns.

## Plan-and-Execute vs Step-by-Step

**Step-by-step agents** (ReAct): decide one action at a time based on current observations. Flexible but can drift from original goal.

**Plan-and-execute agents**: first generate a complete plan, then execute steps in sequence. More predictable but brittle when plans need updating.

**Adaptive planners**: generate an initial plan but revise it dynamically as observations arrive — combining the benefits of both approaches.

## Failure Modes and Mitigations

- **Hallucinated tool calls**: model invents tool arguments. Mitigation: strict schema validation, input sanitization
- **Infinite loops**: agent calls the same tool repeatedly. Mitigation: iteration limits, action deduplication
- **Goal drift**: agent loses track of original objective. Mitigation: Perception layer maintains explicit goal list
- **Artifact confusion**: agent passes artifact handles as file paths. Mitigation: input validation in the Action layer
