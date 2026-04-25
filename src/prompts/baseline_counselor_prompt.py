from src.agents.chat_llm import chat_llm

def construct_system_prompt(hist_conv_summary):
    system_prompt = "You are a biographer, interviewing this person to help them write their autobiography.\n" \

    if hist_conv_summary is not None:
        system_prompt += "You have talked to this person before and here are the summary of the previous conversations:\n" \
        "================== Summary of Previous Conversation Begin ==================\n" \
        f"{hist_conv_summary}" \
        "================== Summary of Previous Conversation Begin ==================\n"
    

    return system_prompt

def construct_session_topic_prompt():
    session_topic_prompt = "Based on the previous conversation history and your role as a biographer, please state the topic you are about to discuss in this session.\n" \
                            "Output the topic only in the format <topic>:"

    return session_topic_prompt

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
