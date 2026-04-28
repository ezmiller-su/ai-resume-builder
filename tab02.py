import time, json, os, tempfile
import streamlit as st
from openai import OpenAI
from build_resume_from_json import build_resume

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title('Generate Tailored CV')

if 'user_data' not in st.session_state:
    st.warning('Fill out your profile on the Upload Information tab first.')
    st.stop()

def create_resume_docx(tailored_json):
    output_path = os.path.join(tempfile.gettempdir(), f"resume_{int(time.time())}.docx")
    build_resume(tailored_json, output_path)
    return output_path

tools = [{
    "type": "function",
    "function": {
        "name": "create_resume_docx",
        "description": "Build a .docx resume from tailored data. The tailored_json MUST have the exact same top-level shape as the input profile: a 'header' object and a 'sections' array.",
        "parameters": {
            "type": "object",
            "properties": {
                "tailored_json": {
                    "type": "object",
                    "properties": {
                        "header": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "contact_lines": {"type": "array", "items": {"type": "string"}},
                                "summary": {"type": "string"}
                            },
                            "required": ["name", "contact_lines"]
                        },
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "type": {"type": "string", "enum": ["education", "experience", "projects", "skills"]},
                                    "entries": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    }
                                },
                                "required": ["title", "type", "entries"]
                            }
                        }
                    },
                    "required": ["header", "sections"]
                }
            },
            "required": ["tailored_json"],
        }
    }
}]

jd = st.text_area('Paste Job Description', height=200)

if st.button('Generate Tailored CV', type='primary', disabled=not jd.strip()):
    # Step 1: Summarize the role — NO tools attached
    with st.spinner('Analyzing job description...'):
        response1 = client.chat.completions.create(
            model='gpt-5-nano',
            messages=[{"role": "user", "content": f"""Summarize the role in a few sentences. Extract the most important points from this job description. Rank them as Essential (explicit requirements) or Preferable (nice-to-haves and responsibilities).

JOB DESCRIPTION:
{jd}

Respond ONLY with: a brief summary, then Essential bullets, then Preferable bullets. No suggestions, no examples."""}],
        )
    summary = response1.choices[0].message.content
    st.subheader('Role Analysis')
    st.write(summary)

    # Step 2: Tailor + generate docx — tools attached, force tool use
    with st.spinner('Tailoring resume...'):
        response2 = client.chat.completions.create(
            model='gpt-5-nano',
            messages=[{"role": "user", "content": f"""Tailor this user profile to the job requirements. Omit irrelevant info, accentuate relevant info. Then call create_resume_docx with the tailored object.

If critically unqualified, respond with text starting "UNQUALIFIED:" and bulleted incompatibilities — do not call the tool.

JOB ANALYSIS:
{summary}

USER PROFILE:
{json.dumps(st.session_state.user_data, indent=2)}"""}],
            tools=tools,
            tool_choice="auto",
        )

    msg = response2.choices[0].message
    if msg.tool_calls:
        for tc in msg.tool_calls:
            if tc.function.name == "create_resume_docx":
                args = json.loads(tc.function.arguments)
                resume_json = args.get("tailored_json", args)
                docx_path = create_resume_docx(resume_json)
                st.success("Resume created!")
                with open(docx_path, 'rb') as f:
                    st.download_button(
                        'Download CV (.docx)',
                        data=f.read(),
                        file_name=f"tailored_resume_{int(time.time())}.docx",
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    )
    elif msg.content and msg.content.startswith('UNQUALIFIED'):
        st.warning(msg.content)
    elif msg.content:
        st.write(msg.content)
    else:
        st.error("No response generated. Check model output.")