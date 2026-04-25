def construct_gpt_eval_prompt_simplified(extracted, gt):
       
    prompt = """
Your task is to rate the semantically equivalence between two events.

Evaluation Criteria:

Here's the revised prompt focusing on assessing the relevance of the extracted event to the document:

Relevance (0/1): Assess the relevance of the extracted event to the original user response on the following two-point scalea:
- 0: Irrelevant: The extracted event does not relate to the user's response or significantly deviates from the main themes and points. It may include unrelated information or fail to capture the essence of the user's message.
- 1: Relevant: The extracted event is connected to the user's response and reflects the key themes or points. It may include minor details that do not detract from the overall relevance.

Now, I will provide you with a user query and the model's response to that instruction. Please review the model's response in light of the evaluation criteria:
Extracted Event: \"%s\"
User Response: \"%s\"

Evaluation Form (scores ONLY):

#thescore: your score here    
"""

    return prompt % (extracted, gt)



def construct_gpt_eval_prompt(extracted, gt):
       
    prompt = """
Your task is to rate the semantically equivalence between two events.

Evaluation Criteria:

Here's the revised prompt focusing on assessing the relevance of the extracted event to the document:

Relevance (1-5): Assess the relevance of the extracted event to the original user response on a scale of 1 to 5, considering the following criteria:
- 1: Barely Relevant - The extracted event has little to no connection to the user's response, and does not reflect the main ideas or themes discussed.
- 2: Somewhat Relevant - The extracted event touches upon the user's response but lacks depth or misses out on several key elements, possibly including some tangential or unrelated details.
- 3: Moderately Relevant - The extracted event is largely in line with the user's response, capturing the general theme and most of the main points, though it may include a few minor irrelevant details.
- 4: Highly Relevant - The extracted event closely mirrors the user's response, effectively capturing the essential aspects and themes with only a few, if any, minor details out of place.
- 5: Completely Relevant - The extracted event is a precise reflection of the user's response, encapsulating all the key points and themes without any extraneous information.

Now, I will provide you with a user query and the model's response to that instruction. Please review the model's response in light of the evaluation criteria:
    Extracted Event: \"%s\"
    User Response: \"%s\"

Evaluation Form (scores ONLY):

#thescore: your score here
    """

    return prompt % (extracted, gt)

def construct_event_summarization_prompt(autobiography, ):
    summary_prompt = """
You are tasked with summarizing the key events from an autobiography chapter. 

A key event is a significant occurrence that has a substantial impact on the author's life or mental health. This includes but is not limited to:
- Career achievements or changes
- Personal challenges or turning points
- Significant relationships and their development
- Moments of crisis or epiphany

Specific Instructions on Extracting Event:
- Identify Event Time: Determine the time frame of each key event. This can be done by looking for explicit time markers (e.g., dates, ages, years) and then converted to YYYY-MM-DD format.
- Extract Event Content: Focus on the "who," "what," "where," and "why" of each event. Summarize the event in a way that conveys its significance without unnecessary detail.
- Chronological Order: Organize the extracted events in chronological order to maintain the narrative flow.
- Brevity and Clarity: for each event the summary should be no longer than 3 sentences, ensuring that each sentence contributes to the overall understanding of the key events.
- Objectivity: Maintain an objective tone, avoiding any personal interpretations or opinions unless they are explicitly stated by the author.

Now, I will provide you with the autobiography content.
================ autobiography beginning ================
%s
================ autobiography ending ================

Your output should resemble the following structure:

Event Time: [Time or Age]
Summary: [Brief description of the event and its significance]

Event Time: [Time or Age]
Summary: [Brief description of the event and its significance]

Output your summary only:
"""
    return summary_prompt % autobiography