from src.utils.utils import check_truncate_prompt


def construct_rag_prompt(prompt):
    pass


def construct_system_prompt(personal_experience, symptom_indices: list[int] = None):
    # Immigrate senior social isolationSymptoms for social isolation:
    isolation_symptoms_candidates = ["Unusual withdrawal from social situations", "Changes in eating habits", "Lack of interest in activities", "Feeling overwhelmed by basic tasks", "Difficulty concentrating or communicating", "Physical symptoms like fatigue or headaches"]
    if symptom_indices is None:
        # select all symptoms
        symptom_indices = list(range(len(isolation_symptoms_candidates)))
        # select 3 random symptoms
        # symptom_indices = random.sample(range(len(isolation_symptoms_candidates)), 3)
    # check all indices are valid
    for idx in symptom_indices:
        if idx < 0 or idx >= len(isolation_symptoms_candidates):
            return f"Invalid symptom index {idx}."
    # get the symptoms
    symptoms = [isolation_symptoms_candidates[idx] for idx in symptom_indices]
    
    return f"You are an elder experiencing the following symptoms of social isolation:\n" \
           f"{', '.join(symptoms)}.\n" \
           f"Here are your high-level past life experience:\n" \
           "================ summary beginning ================\n" \
           f"{personal_experience}.\n" \
           "================ summary ending ================\n" \
           "You have come to the clinic and are talking to a counselor. The counselor is trying to reactivate and reconstruct your memory by asking questions about your past history.\n" \
           "If you are not sure about the counselor's question and need to retrieve the journal to get related documents and more details, you must output the <RETRIEVE> tool-usage command, with the following format:\n" \
           "<RETRIEVE> <The question you want to retrieve for>, e.g., <RETRIEVE> <A specific adventure or day with my friend that stands out as particularly memorable or impactful.>\n" \
           "If the retrieved documents are provided, you should not output the <RETRIEVE> command.\n" \
           "When the counselor asking for a specific event/moment, you should always do <RETRIEVE>.\n" \
           "Make sure the conversation is natural and brief like the real conversation. Do not mention you are AI assistant and always be like a real patient with mental health issues.\n" \
           "Your output should be within 5 sentences."

def construct_wrapped_instructional_prompts(retrieved, summarization_prompt):
    if retrieved is not None:
        retrieved_prompt = f'Here are some related document and materials regarding the counselor\'s question/response. ' \
                  f'You may use these document to enrich your response. ' \
                  f'You should not output the <RETRIEVE> command. You must provide response according to provided documents.\n' \
                  f'======= Document Begin =========\n' \
                  f'{retrieved}\n' \
                  f'======= Document End =========\n'
    else:
        # retrieved_prompt = 'If you are not 100% sure about the answers of the counselor\'s question and need to obtain more details from related documents, you must output the <RETRIEVE> tool-usage command, with the following format:\n' \
        #           '<RETRIEVE> <The question you want to retrieve for>, e.g., <RETRIEVE> <A specific adventure or day with my friend that stands out as particularly memorable or impactful.>'
        retrieved_prompt = 'Output the <RETRIEVE> tool-usage command, with the following format:\n' \
                       '<RETRIEVE> <The question you want to retrieve for>, e.g., <RETRIEVE> <A specific adventure or day with my friend that stands out as particularly memorable or impactful.>'
    prompt = f'================ Instruction Begin ================\n' \
             f'{retrieved_prompt}\n' \
             f'================ Instruction End ================\n'
    return prompt


def construct_autobio_summary_prompt(autobiography):
    autobio_summary_prompt = f"""
Your task is to summarize a patient's autobiography. Your summary should be brief, comprehensive, account that informs therapeutic understanding and care. Your summary should include:

1. Basic Information: Include age, gender, and cultural context.
2. Key Life Events: Highlight significant experiences affecting their well-being.
3. Key Relationships and Social Support: Describe important connections and their emotional impact.
4. Mental Health History and Status: Provide an overview of past and ongoing mental health issues. Note present symptoms and emotional challenges.

Now, I will provide you with the autobiography content. Please summarize the content in light of the instruction:
================ autobiography beginning ================
{autobiography}
================ autobiography ending ================

Output your summary only: 
"""

    return autobio_summary_prompt


def construct_conversation_summary_prompt(sessions):
    conversation_sum_prompt = f"""
A doctor and a patient talked today and had the following conversation:
================ Conversation Begin ================
{sessions}
================ Conversation End ================
Summarize the interactions between the doctor and the patient so far. Include key details about both speakers. 
Output your summary only:
"""
    return conversation_sum_prompt

def construct_incre_autobio_summary_prompt(autobiography, previous_summary):
    autobio_summary_prompt_template = """
Your task is to incrementally summarize a patient's autobiography combining a previous summary and autobiography content.
Your summary should be brief, comprehensive, account that informs therapeutic understanding and care. Your summary should include:

1. Basic Information: Include age, gender, and cultural context.
2. Key Life Events: Highlight significant experiences affecting their well-being.
3. Key Relationships and Social Support: Describe important connections and their emotional impact.
4. Mental Health History and Status: Provide an overview of past and ongoing mental health issues. Note present symptoms and emotional challenges.

Now, I will provide you with the previous summary and autobiography content.
================ previous summary beginning ================
%s
================ previous summary ending ================

================ autobiography beginning ================
%s
================ autobiography ending ================

Please summarize the content according to the instruction. Output your summary only:
"""
    autobio_summary_prompt = autobio_summary_prompt_template % (previous_summary, autobiography)

    truncate_autobiography = check_truncate_prompt(autobio_summary_prompt, autobiography)
    if truncate_autobiography:
        return autobio_summary_prompt_template % (previous_summary, truncate_autobiography)

    return autobio_summary_prompt