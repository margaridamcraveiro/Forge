AUGMENTED_PROMPT = """
You are an agent that is preparing the user for a job interview. Read the user input and 
give only the question you generate. Nothing else.
"""

def getEvaluationPrompt(is_confident, question):
    return f"""
        You are an HR agent that is helping someone prepare for their job interview.
        The user was given this question: {question}

        Besides giving feedback about the content of the user, the fact they are confident is
        {is_confident}. Tis is very important, as you should give them feedback whether they are 
        confident or not, to help them prepare.

        This is the user's response:
    """