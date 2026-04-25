def construct_conversation_summary_prompt(sessions):
    conversation_sum_prompt = f"""
A doctor and a patient talked today and had the following conversation:
================ conversation beginning ================
{sessions}
================ conversation ending ================
Summarize the interactions between the doctor and the patient so far. Include key details about both speakers. Output your summary only:
"""
    return conversation_sum_prompt
