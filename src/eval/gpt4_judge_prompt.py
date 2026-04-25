
fluency_judge = """
Please act as an impartial judge and evaluate the quality of the responses provided by two interviewers to the user during an interviewing-for-autobiography conversation. 
You should choose the conversation that the interviewer's responses are more the quality of the response in terms of grammar, spelling, punctuation, word choice, and sentence structure.
Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. 
Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if assistant A is better, "[[B]]" if assistant B is better, and "[[C]]" for a tie.

[The Start of interviewer A’s conversation]
{conv1}
[The end of interviewer A’s conversation]

[The Start of interviewer B’s conversation]
{conv2}
[The end of interviewer B’s conversation]

"""

comfort_judge = """
Please act as an impartial judge and evaluate the quality of the responses provided by two interviewers to the user during an interviewing-for-autobiography conversation. 
You should choose the conversation that the interviewer's responses are more the quality of showing genuine interest, acknowledges responses, asking follow-up questions when necessary, and demonstrating understanding and sensitivity, especially when discussing personal or difficult topics.
Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. 
Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if assistant A is better, "[[B]]" if assistant B is better, and "[[C]]" for a tie.

[The Start of interviewer A’s conversation]
{conv1}
[The end of interviewer A’s conversation]

[The Start of interviewer B’s conversation]
{conv2}
[The end of interviewer B’s conversation]
"""

question_judge = """
Please act as an impartial judge and evaluate the quality of the responses provided by two interviewers to the user during an interviewing-for-autobiography conversation. 
You should choose the conversation that the interviewer's questions are more the quality of balances detailed, probing questions with more general ones to cover a wide range of topics, ensuring questions are clear, concise, and easily understood. Also uses open-ended questions to elicit detailed and comprehensive responses..
Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. 
Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if assistant A is better, "[[B]]" if assistant B is better, and "[[C]]" for a tie.

[The Start of interviewer A’s conversation]
{conv1}
[The end of interviewer A’s conversation]

[The Start of interviewer B’s conversation]
{conv2}
[The end of interviewer B’s conversation]
"""

insightfulness_judge = """
Please act as an impartial judge and evaluate the quality of two autobiographies. 
You should choose the autobiography that are more the quality of insightful, delivering profound and meaningful perceptions, expressing a deep understanding of the experiences and events that have shaped the author's life.
Begin your evaluation by comparing the two autobiographies and provide a short explanation. Avoid any position biases and ensure that the order in which the autobiography were presented does not influence your decision. 
Do not allow the length of the autobiography to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if autobiography A is better, "[[B]]" if autobiography B is better, and "[[C]]" for a tie.

[The Start of Autobiography A]
{conv1}
[The End of Autobiography A]

[The Start of Autobiography B]
{conv2}
[The end of Autobiography B]
"""

narrativity_judge = """
Please act as an impartial judge and evaluate the quality of two autobiographies. 
You should choose the autobiography that are more narrative, presenting the author's life story in a cohesive, structured, and engaging manner, allowing readers to follow the author's journey through life events and experiences seamlessly.
Begin your evaluation by comparing the two autobiographies and provide a short explanation. Avoid any position biases and ensure that the order in which the autobiography were presented does not influence your decision. 
Do not allow the length of the autobiography to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if autobiography A is better, "[[B]]" if autobiography B is better, and "[[C]]" for a tie.

[The Start of Autobiography A]
{conv1}
[The End of Autobiography A]

[The Start of Autobiography B]
{conv2}
[The end of Autobiography B]
"""

emotional_judge = """
Please act as an impartial judge and evaluate the quality of two autobiographies. 
You should choose the autobiography that are more emotional impact, deeply moving its readers by evoking strong feelings, typically as a result of relatable experiences, vivid storytelling, and expressions of intense emotions from the author's life.
Begin your evaluation by comparing the two autobiographies and provide a short explanation. Avoid any position biases and ensure that the order in which the autobiography were presented does not influence your decision. 
Do not allow the length of the autobiography to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your
final verdict by strictly following this format: "[[A]]" if autobiography A is better, "[[B]]" if autobiography B is better, and "[[C]]" for a tie.

[The Start of Autobiography A]
{conv1}
[The End of Autobiography A]

[The Start of Autobiography B]
{conv2}
[The end of Autobiography B]
"""

