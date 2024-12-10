import google.generativeai as genai

genai.configure(api_key="")

model = genai.GenerativeModel("gemini-1.5-flash")


def prompt_construct(question, data):
    prompt = (
        "I am studying for an exam which requires me to answer the questions in utmost detail. "
        + "Each question is for 8 marks. "
        + "Answer the question using the same wordings as provided in the data. "
        + "It is essential that you use the keywords and explain the concept in depth. "
        + "Answer the question that has been asked. "
        + f"QUESTION - {question} \n\n"
        + f"DATA - {data}"
    )
    return prompt


def get_response_from_api(prompt):
    response = model.generate_content(prompt)
    return response._result.candidates[0].content.parts[0].text


def ai_api_functionality_wrapper(question, data):
    prompt = prompt_construct(question, data)
    response = get_response_from_api(prompt)
    return response
