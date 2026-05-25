# Reinforcement Learning: Fundamentals and Modern Approaches

Reinforcement learning (RL) is a machine learning paradigm where an agent learns to make decisions by interacting with an environment to maximize cumulative reward. Unlike supervised learning, RL receives no direct labels — only reward signals that may be delayed and sparse.

## Core Components

**Agent**: The learner and decision-maker
**Environment**: Everything the agent interacts with
**State (s)**: A representation of the current situation
**Action (a)**: What the agent can do
**Reward (r)**: Scalar feedback signal from the environment
**Policy (π)**: The agent's strategy mapping states to actions
**Value function (V)**: Expected cumulative future reward from a state

The **Markov Decision Process (MDP)** formalizes RL: (S, A, P, R, γ)
- S: state space
- A: action space
- P(s'|s,a): transition probability
- R(s,a): reward function
- γ: discount factor (0–1), weighting future rewards

## Model-Free Methods

### Q-Learning

Q-learning learns the action-value function Q(s,a) — expected reward for taking action a in state s, then following optimal policy:

```
Q(s,a) ← Q(s,a) + α[r + γ max_{a'} Q(s',a') - Q(s,a)]
```

**Deep Q-Network (DQN)**: Approximates Q with a neural network. Key innovations:
- Experience replay: store and sample past transitions
- Target network: separate frozen network for TD targets (stability)
- Achieved superhuman Atari performance (Mnih et al., 2015)

### Policy Gradient Methods

Instead of learning a value function, directly optimize the policy:

```
∇J(θ) = E[∇ log π_θ(a|s) · Q^π(s,a)]
```

**REINFORCE**: Monte Carlo estimate — accumulate full trajectory, then update.

**Actor-Critic**: Combine policy gradient (actor) with value function baseline (critic) to reduce variance.

**PPO (Proximal Policy Optimization)**: Most widely used RL algorithm. Clips the policy update ratio to prevent destructive large updates:
```
L^CLIP = E[min(r_t(θ)·Â_t, clip(r_t(θ), 1-ε, 1+ε)·Â_t)]
```

## Model-Based RL

Model-based methods learn a model of the environment P(s'|s,a) and use it for planning:
- **Dyna-Q**: Learn model from real experience; generate synthetic experience from model
- **AlphaZero**: Monte Carlo tree search guided by neural network for chess, Go, shogi
- **World models**: Learn compact latent representations of the environment for imagination-based planning

## Exploration vs Exploitation

The fundamental tradeoff:
- **ε-greedy**: With probability ε, take random action; otherwise take greedy action
- **UCB (Upper Confidence Bound)**: Select action with highest upper confidence estimate
- **Thompson Sampling**: Sample from posterior over action value distributions
- **Intrinsic motivation**: Reward novelty (count-based, prediction error) to drive exploration in sparse reward environments

## RL from Human Feedback (RLHF)

RLHF adapts RL to train language models:
1. Collect human preference comparisons (A preferred to B)
2. Train reward model to predict human preferences
3. Fine-tune LM with PPO to maximize learned reward minus KL divergence from base model

Used in InstructGPT, Claude, Gemini. DPO provides an alternative without explicit RL.

## Multi-Agent RL

Multiple agents interact simultaneously, creating non-stationary environments from each agent's perspective. Applications include game-playing (OpenAI Five for Dota 2), robotic swarms, and mechanism design.
