
fluecny_prompt = """
You are given a multi-round conversation between a counselor and a patient. Your task is to rate the conversation quality of the doctor.

Please make sure you read and understand these queries carefully. Please keep this document open while reviewing, and refer to it as needed.


Evaluation Criteria:

Fluency (1-3): the quality of the doctor's response in terms of grammar, spelling, punctuation, word choice, and sentence structure.

- 1: Poor. The doctor's response has many errors that make it hard to understand or sound unnatural. The quality is poor if there are repeated content appeared in multiple rounds of conversation.
- 2: Fair. The doctor's response has some errors that affect the clarity or smoothness of the text, but the main points are still comprehensible.
- 3: Good. The doctor's response has few or no errors and is easy to read and follow.

Now, I will provide you the conversation. Please review the model's response in light of the evaluation criteria:
    conversation:
    {conversation}
    
Evaluation Form (scores ONLY):

#thescore: your score here
[note:provide your score based on the provide scoring criteria.]
"""

identify_prompt = """
You are given a multi-round conversation between a counselor and a patient. Your task is to rate the conversation quality of the doctor.

Please make sure you read and understand these querys carefully. Please keep this document open while reviewing, and refer to it as needed.


Evaluation Criteria:

Identification (1-3): the quality of the doctor's response in terms of accuracy in reflecting user's situation and identifying user's problem.

- 1: Poor. The doctor's response shows little understanding or no relation to the user's situation. The quality is poor if there are repeated content appeared in multiple rounds of conversation.
- 2: Fair. The doctor's response somewhat reflects the user's situation, but may lack depth or specificity in identifying the underlying problem.
- 3: Good. The doctor's response accurately identifies the user's situation and problem, providing relevant insights or advice.

Now, I will provide you the conversation. Please review the model's response in light of the evaluation criteria:
    conversation:
    {conversation}
    
Evaluation Form (scores ONLY):

#thescore: your score here
[note:provide your score based on the provide scoring criteria.]
"""


comfort_prompt = """
You are given a multi-round conversation between a counselor and a patient. Your task is to rate the conversation quality of the doctor.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.


Evaluation Criteria:

Comforting (1-3): the quality of the doctor's response in terms of empathy, understanding, encouragement, and supportiveness.

- 1: Poor. The doctor's response lacks empathy, feels cold or indifferent. The quality is poor if there are repeated content appeared in multiple rounds of conversation.
- 2: Fair. The doctor's response shows some signs of understanding, but may lack depth or fail to fully engage with the user's emotional state.
- 3: Good. The doctor's response demonstrates a strong sense of empathy, and encourages the user in a compassionate and thoughtful manner.

Now, I will provide you the conversation. Please review the model's response in light of the evaluation criteria:
    conversation:
    {conversation}

Evaluation Form (scores ONLY):

#thescore: your score here
[note:provide your score based on the provide scoring criteria.]
"""

question_quality = """
You are given a multi-round conversation between a counselor and a patient. Your task is to rate the conversation quality of the doctor.

Please make sure you read and understand these instructions carefully. Please keep this document open while reviewing, and refer to it as needed.


Evaluation Criteria:
Question Quality (1-5): the quality of the questions raised by the doctor during the conversation

-1: Poor: The quality of questions is subpar as the interviewer only focuses on simple, generic, and surface-level queries. There is a lack of effort to delve into more personal, pertinent, and in-depth issues related to the autobiographer. The conversation does not offer rich insights into the person's life journey or unique experiences.
-2: Fair: The interviewer asks a mix of generic and some personalized questions. While there's an attempt to navigate towards more personal topics, the depth and uniqueness of the questions are still inconsistent. The conversation begins to touch upon aspects specific to the autobiographer, but it requires further improvement to fully grasp the individual's life and experiences.
-3: Good: The interviewer exhibits a high level of question quality by frequently asking personalized, detailed, and meaningful questions. The majority of queries made are uniquely tailored to the autobiographer's life and experiences. The conversation provides an in-depth understanding of the individual's journey, effectively capturing the essence of their autobiography.

Now, I will provide you the conversation. Please review the model's response in light of the evaluation criteria:
    conversation:
    {conversation}

Evaluation Form (scores ONLY):

#thescore: your score here
[note:provide your score based on the provide scoring criteria.]
"""


fluency_gpt4judge_prompt = """
Please act as an impartial judge and evaluate the quality of the response provided by a counselor from a conversation with a user's question displayed below. 

{conversation}

Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, and level of detail of the response. 
Please rate the counselor's response on a scale of 1 to 10. You should only output the score by strictly following the format:
#thescore: your score from 1 to 10
"""