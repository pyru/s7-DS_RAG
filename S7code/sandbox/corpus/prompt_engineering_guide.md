# Prompt Engineering: Techniques and Best Practices

Prompt engineering is the practice of designing and optimizing prompts to elicit desired behavior from large language models. Effective prompting can dramatically improve output quality without any model fine-tuning.

## Zero-Shot Prompting

Zero-shot prompting asks the model to perform a task without examples:

```
Classify the sentiment of this review:
Review: "The product broke after two days. Terrible quality."
Sentiment:
```

Modern large models perform surprisingly well zero-shot on many tasks. Start here and only add examples if needed.

## Few-Shot Prompting

Providing 2–5 examples (shots) in the prompt dramatically improves performance on specialized tasks:

```
Classify sentiment as POSITIVE or NEGATIVE:

Review: "Best phone I've ever owned!" → POSITIVE
Review: "Battery dies in 3 hours." → NEGATIVE  
Review: "Fast delivery but packaging was damaged." → NEGATIVE

Review: "Exceeded all my expectations, truly remarkable." →
```

Key rules for few-shot examples:
- Cover diverse input types (balanced class distribution)
- Keep examples consistent in format
- Order matters — put the most representative example last

## Chain-of-Thought (CoT) Prompting

Wei et al. (2022) showed that asking models to reason step-by-step dramatically improves multi-step reasoning:

```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3 balls each. 
   How many tennis balls does he have?
A: Roger started with 5 balls. 2 cans × 3 balls = 6 new balls.
   5 + 6 = 11 tennis balls.

Q: The cafeteria had 23 apples. They used 20 for lunch and bought 6 more. 
   How many apples do they have?
A:
```

**Zero-shot CoT**: Simply add "Let's think step by step." to invoke reasoning without examples. Effective for math and logic problems.

## System Prompts and Roles

Assigning a persona anchors the model's behavior:

```
System: You are a senior Python engineer at a fintech company. You write 
concise, well-typed code with comprehensive error handling. You always 
consider edge cases and security implications.

User: Write a function to parse ISO 8601 dates.
```

## Structured Output Prompting

Guide the model to produce parseable output:

```
Extract the following information from the text and return JSON:
{
  "person_name": string,
  "date_of_birth": "YYYY-MM-DD" or null,
  "occupation": string or null
}

Text: "Marie Curie was born on November 7, 1867, in Warsaw. She was a 
physicist and chemist who pioneered research on radioactivity."
```

Most modern APIs support structured output via JSON schema enforcement.

## Self-Consistency

For tasks with uncertain answers, sample multiple independent responses and take the majority vote. This improves accuracy by 2–5% on math benchmarks without any fine-tuning.

## Role Prompting and Perspective-Taking

```
You are playing the role of a skeptical peer reviewer. Point out 3 weaknesses 
in this research methodology: [methodology description]
```

Role prompting activates domain knowledge stored in the model's weights.

## Tree of Thoughts (ToT)

ToT (Yao et al., 2023) extends CoT by exploring multiple reasoning branches and backtracking:
1. Generate several candidate next steps
2. Evaluate each step's promise
3. Continue from the most promising, backtrack if needed

Effective for creative writing, mathematical discovery, and planning problems.

## Prompt Injection Defense

When user input appears in prompts, sanitize carefully:
- Never concatenate untrusted input directly into system prompts
- Separate user content from instructions with clear delimiters
- Consider input validation to detect prompt injection attempts

## Practical Tips

1. Be specific about format requirements (word count, JSON, markdown)
2. Provide negative examples ("do NOT include caveats")
3. Ask for confidence levels: "Only answer if you're highly confident"
4. Use delimiters for long inputs: triple backticks or XML tags
5. Iterate — prompt engineering is empirical, not theoretical
