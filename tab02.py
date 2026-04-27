import time
import streamlit as st
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
import json

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
                        "description": "",
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
                        Using the following user's profile:\n
                        {json.dumps(st.session_state.user_data)}
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

st.title("Generate Tailored CV")

# Pull name from tab01 session state if the user filled it in
resume_data = st.session_state.get("resume_data", {})
user_name = resume_data.get("header", {}).get("full_name", "") or "Your Name"
user_email = resume_data.get("header", {}).get("email", "") or "email@example.com"
user_phone = resume_data.get("header", {}).get("phone", "") or "(555) 555-5555"
user_linkedin = resume_data.get("header", {}).get("linkedin", "") or "linkedin.com/in/yourprofile"

jd = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="Paste the full job posting...",
)

if st.button("Generate Tailored CV", type="primary", disabled=not jd):
    with st.status("Building your tailored CV...", expanded=True) as status:
        st.write("Analyzing job requirements...")
        time.sleep(1.1)
        st.write("Retrieving relevant experience and projects...")
        time.sleep(1.3)
        st.write("Ranking content by relevance...")
        time.sleep(0.9)
        st.write("Generating tailored sections...")
        time.sleep(1.4)
        st.write("Validating output...")
        time.sleep(0.7)
        status.update(label="CV ready!", state="complete", expanded=False)

    st.divider()

    # Header
    st.markdown(f"# {user_name}")
    st.markdown(
        f"{user_email} &nbsp;|&nbsp; {user_phone} &nbsp;|&nbsp; {user_linkedin}",
        unsafe_allow_html=True,
    )
    st.divider()

    # Summary
    st.markdown("## Professional Summary")
    st.markdown(
        "Results-driven professional with a strong foundation in software development "
        "and data-driven problem solving. Demonstrated ability to deliver scalable solutions "
        "in collaborative, fast-paced environments. Passionate about applying modern AI "
        "techniques to real-world challenges."
    )

    # Experience
    st.markdown("## Experience")
    col1, col2 = st.columns([3, 1])
    col1.markdown("**Software Engineering Intern** — TechCorp Solutions")
    col2.markdown("Jun 2024 – Aug 2024")
    st.markdown(
        "- Developed and maintained RESTful APIs serving 50,000+ daily requests using Python and FastAPI\n"
        "- Reduced query latency by 30% through database indexing and query optimization\n"
        "- Collaborated with cross-functional teams to design and ship two major product features\n"
        "- Wrote unit and integration tests achieving 90% code coverage"
    )

    col1, col2 = st.columns([3, 1])
    col1.markdown("**Research Assistant** — University AI Lab")
    col2.markdown("Jan 2024 – May 2024")
    st.markdown(
        "- Implemented NLP pipelines using transformer models (BERT, GPT) for text classification tasks\n"
        "- Processed and analyzed datasets of 500K+ records using Pandas and NumPy\n"
        "- Contributed to a published paper on retrieval-augmented generation systems\n"
        "- Presented findings to faculty and graduate researchers in weekly lab meetings"
    )

    # Projects
    st.markdown("## Projects")
    st.markdown("**AI Resume Builder** *(current project)*")
    st.markdown(
        "- Built the application generator module for an AI-powered job application tool\n"
        "- Designed a modular pipeline supporting both CV and cover letter generation\n"
        "- Implemented preference management, prompt templates, and retrieval integration\n"
        "- Developed 25 automated tests covering the full generation pipeline"
    )
    st.markdown("**Sentiment Analysis Dashboard**")
    st.markdown(
        "- Built an end-to-end sentiment analysis tool using Python, HuggingFace, and Streamlit\n"
        "- Ingested and processed live Twitter data via API with real-time chart updates\n"
        "- Deployed on AWS with a CI/CD pipeline via GitHub Actions"
    )

    # Education
    st.markdown("## Education")
    col1, col2 = st.columns([3, 1])
    col1.markdown("**B.S. Computer Science** — State University")
    col2.markdown("Expected May 2026")
    st.markdown("GPA: 3.7 &nbsp;|&nbsp; Relevant coursework: Machine Learning, Databases, Software Engineering, Algorithms", unsafe_allow_html=True)

    # Skills
    st.markdown("## Skills")
    col1, col2, col3 = st.columns(3)
    col1.markdown("**Languages**\n\nPython, JavaScript, SQL, Java")
    col2.markdown("**Frameworks & Tools**\n\nFastAPI, Streamlit, React, Docker, Git")
    col3.markdown("**AI / ML**\n\nOpenAI API, ChromaDB, LangChain, HuggingFace, PyTorch")

    st.divider()

    # Download
    cv_text = f"""{user_name}
{user_email} | {user_phone} | {user_linkedin}

PROFESSIONAL SUMMARY
Results-driven professional with a strong foundation in software development and data-driven problem solving. Demonstrated ability to deliver scalable solutions in collaborative, fast-paced environments. Passionate about applying modern AI techniques to real-world challenges.

EXPERIENCE
Software Engineering Intern — TechCorp Solutions (Jun 2024 – Aug 2024)
- Developed and maintained RESTful APIs serving 50,000+ daily requests using Python and FastAPI
- Reduced query latency by 30% through database indexing and query optimization
- Collaborated with cross-functional teams to design and ship two major product features
- Wrote unit and integration tests achieving 90% code coverage

Research Assistant — University AI Lab (Jan 2024 – May 2024)
- Implemented NLP pipelines using transformer models (BERT, GPT) for text classification tasks
- Processed and analyzed datasets of 500K+ records using Pandas and NumPy
- Contributed to a published paper on retrieval-augmented generation systems

PROJECTS
AI Resume Builder
- Built the application generator module for an AI-powered job application tool
- Designed a modular pipeline supporting both CV and cover letter generation
- Implemented preference management, prompt templates, and retrieval integration

Sentiment Analysis Dashboard
- Built an end-to-end sentiment analysis tool using Python, HuggingFace, and Streamlit
- Ingested and processed live Twitter data via API with real-time chart updates

EDUCATION
B.S. Computer Science — State University (Expected May 2026)
GPA: 3.7

SKILLS
Languages: Python, JavaScript, SQL, Java
Frameworks & Tools: FastAPI, Streamlit, React, Docker, Git
AI / ML: OpenAI API, ChromaDB, LangChain, HuggingFace, PyTorch
"""
    st.download_button(
        "Download CV (.txt)",
        data=cv_text,
        file_name="tailored_cv.txt",
        mime="text/plain",
    )
