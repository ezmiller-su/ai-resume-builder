import streamlit as st
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title('Generate Tailored CV')

if jd := st.text_area('Paste Job Description'):
    st.session_state.url_response = client.chat.completions.create(
        model='gpt-5-nano',
        max_tokens = 1024,
        messages=[{"role": "user",
                "content": [
                    {"type": "text", "text": '''Generate a resume tailored to this particular job description:\n
                        {jd}\n
                        '''}]
                    }]
    )

    cv = []
    if st.session_state.url_response:
        st.pdf(cv)
        st.download_button('Download CV', cv)