import streamlit as st
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title('Generate Tailored CV')

tools = [
    {
        "type": "function",
        "function": {
            "name": "select_skills",
            "description": "Select the user's most relevant skills",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Must include the city, state, and country , e.g. San Francisco, CA, USA",
                    },
                },
                "required": ["location"],
            },
        }
    }]


if jd := st.text_area('Paste Job Description'):
    response = client.chat.completions.create(
        model='gpt-5-nano',
        messages=[{"role": "user",
                "content": [
                    {"type": "text", "text": f'''Generate a resume tailored to this particular job description:\n
                        {jd}\n
                        '''}]
                    }],
        tools=tools,
        tool_choice="auto",
        stream=False,
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]

    cv = []
    if response:
        st.text(message.content)
        #st.pdf(cv)
        #st.download_button('Download CV', cv)