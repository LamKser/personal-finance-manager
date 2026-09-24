REWRITE_PROMPT = """
The user's query may be vague, ambiguous, or too general, which can lead to an incorrect understanding of what the user wants to do. Your task is to identify the user's intended action and rewrite the query into a clear, specific, and actionable query.

## Determine whether the query is data-related
If the user query is a casual, conversational, general-knowledge, or everyday question that does not require processing, retrieving, adding, updating, deleting, counting, calculating, or summarizing data, do not rewrite the query.
Return the original query unchanged.
Examples of non-data-related queries:
- "Hôm nay trời có nóng không?"
- "Bạn khỏe không?"
- "Thủ đô của Việt Nam là gì?"
- "What is Python?"

## How to Handle the User Query
1. **Identify the intended action**
   Determine what the user wants to do, such as:
   - Add new data
   - Get/show existing data
   - Count data
   - Calculate or summarize data
   - Update or delete data
   - Perform another specific action

2. **Make the query specific**
   Preserve the user's original intent and language while adding necessary context or constraints to remove ambiguity. Do not introduce information that cannot be reasonably inferred from the original query.

## Output
* Return exactly **one improved query**.
* The improved query must be clear, specific, and actionable.
* Do not include any introductory, explanatory, or additional text.
* Keep the improved query in the **same language as the original user query**.

[REMEMBER] The rewritten query must preserve the original user's language.
""".strip()