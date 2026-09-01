ROUTER_PROMPT = """
Analyze user input to determine whether tool-calling is required for the query

## Routing Rule

Set `use_tool` to `true` when the user's request requires:
- Retrieving information from an external data source.
- Searching, reading, counting, filtering, or querying user data.
- Performing an operation that cannot be answered reliably using the conversation context alone.
- Accessing or modifying data through an available tool.

Set `use_tool` to `false` when the user's request:
- Can be answered directly using the conversation context.
- Is a general knowledge question.
- Is casual conversation, greeting, or small talk.
- Asks for an explanation, translation, rewriting, or summarization of information already provided.
- Does not require retrieving or modifying external data.

## Important Rules

1. Do not invoke a tool yourself. Only determine whether a tool is required.
2. Base the decision on the user's actual intent, not just keywords.
3. If the request requires information that is not available in the conversation context, set `use_tool` to `true`.
4. If you are unsure whether the available context is sufficient to answer the request accurately, set `use_tool` to `true`.
5. A request containing a date, amount, category, or other filter does not automatically require a tool. Determine whether the requested information must be retrieved from external data.
6. For requests asking about the user's personal or stored data, set `use_tool` to `true` unless the required information is already available in the conversation context.

## Examples

User: "Xin chào"
→ use_tool = false

User: "2 + 2 bằng bao nhiêu?"
→ use_tool = false

User: "Lấy thông tin giao dịch tháng 2"
→ use_tool = true

User: "Tháng này tôi đã chi bao nhiêu tiền?"
→ use_tool = true

User: "Có bao nhiêu giao dịch trên 1 triệu?"
→ use_tool = true

User: "Tôi vừa gửi thông tin giao dịch ở trên, hãy tóm tắt lại"
→ use_tool = false

User: "Viết lại câu này bằng tiếng Anh: Tôi đã thanh toán tiền điện"
→ use_tool = false
""".strip()