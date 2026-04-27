import streamlit as st
import json

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'header': {},
        'objective': '',
        'education': [],
        'work_experience': [],
        'certifications': [],
        'skills': [],
        'awards': [],
        'projects': []
    }

def add_item(section, value):
    if value.strip():
        st.session_state.resume_data[section].append(value.strip())

def delete_item(section, index):
    st.session_state.resume_data[section].pop(index)

uploaded = st.file_uploader('Load saved resume data', type='json')
if uploaded:
    data = json.loads(uploaded.read())
    st.session_state.resume_data = data
    # Sync header values into widget keys
    for field in ['full_name', 'address', 'phone', 'email', 'linkedin']:
        st.session_state[f'header_{field}'] = data['header'].get(field, '')
    st.rerun()

with st.expander('Header and Contact'):
    for field in ['Full Name', 'Address', 'Phone', 'Email', 'LinkedIn']:
        key = field.lower().replace(' ', '_')
        st.text_input(field, key=f'header_{key}')
        st.session_state.resume_data['header'][key] = st.session_state.get(f'header_{key}', '')

with st.expander('Objective/Summary'):
    obj = st.text_area('A brief statement that defines your career goals.', 
                        value=st.session_state.resume_data['objective'], key='objective_input')
    st.session_state.resume_data['objective'] = obj


with st.expander('Education'):
    edu_degree = st.text_input('Degree', key='edu_degree')
    edu_school = st.text_input('School', key='edu_school')
    edu_dates = st.text_input('Dates', key='edu_dates')
    if st.button('Add', key='add_edu'):
        add_item('education', {'degree': edu_degree, 'school': edu_school, 'dates': edu_dates})
        st.rerun()

    for i, edu in enumerate(st.session_state.resume_data['education']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.markdown(f"**{edu['degree']}** — {edu['school']} ({edu['dates']})")
        if col2.button('✕', key=f'del_edu_{i}'):
            delete_item('education', i)
            st.rerun()

# --- Work Experience ---
with st.expander('Work Experience'):
    we_title = st.text_input('Job Title', key='we_title')
    we_company = st.text_input('Company', key='we_company')
    we_dates = st.text_input('Dates', key='we_dates')
    we_desc = st.text_area('Description', key='we_desc')
    if st.button('Add', key='add_we'):
        add_item('work_experience', {
            'title': we_title, 'company': we_company,
            'dates': we_dates, 'description': we_desc
        })
        st.rerun()

    for i, exp in enumerate(st.session_state.resume_data['work_experience']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.markdown(f"**{exp['title']}** at {exp['company']} ({exp['dates']})")
        col1.write(exp['description'])
        if col2.button('✕', key=f'del_we_{i}'):
            delete_item('work_experience', i)
            st.rerun()

# --- Certifications and Licenses ---
with st.expander('Certifications and Licenses'):
    col1, col2 = st.columns([0.90, 0.1])
    new_cert = col1.text_input('Add a certification', key='new_cert_input')
    if col2.button('Add', key='add_cert', width='stretch'):
        add_item('certifications', new_cert)
        st.rerun()

    for i, cert in enumerate(st.session_state.resume_data['certifications']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.write(cert)
        if col2.button('✕', key=f'del_cert_{i}'):
            delete_item('certifications', i)
            st.rerun()

# --- Skills ---
with st.expander('Skills'):
    col1, col2 = st.columns([0.90, 0.1])
    new_skill = col1.text_input('Add a skill', key='new_skill_input')
    if col2.button('Add', key='add_skill', width='stretch'):
        add_item('skills', new_skill)
        st.rerun()

    for i, skill in enumerate(st.session_state.resume_data['skills']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.write(skill)
        if col2.button('✕', key=f'del_skill_{i}'):
            delete_item('skills', i)
            st.rerun()

# --- Awards and Honors ---
with st.expander('Awards and Honors'):
    col1, col2 = st.columns([0.90, 0.1])
    new_award = col1.text_input('Add an award', key='new_award_input')
    if col2.button('Add', key='add_award', width='stretch'):
        add_item('awards', new_award)
        st.rerun()

    for i, award in enumerate(st.session_state.resume_data['awards']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.write(award)
        if col2.button('✕', key=f'del_award_{i}'):
            delete_item('awards', i)
            st.rerun()

# --- Projects ---
with st.expander('Projects'):
    proj_name = st.text_input('Project Name', key='proj_name')
    proj_desc = st.text_area('Description', key='proj_desc')
    if st.button('Add', key='add_proj'):
        add_item('projects', {'name': proj_name, 'description': proj_desc})
        st.rerun()

    for i, proj in enumerate(st.session_state.resume_data['projects']):
        col1, col2 = st.columns([0.95, 0.05])
        col1.markdown(f"**{proj['name']}**")
        col1.write(proj['description'])
        if col2.button('✕', key=f'del_proj_{i}'):
            delete_item('projects', i)
            st.rerun()

st.divider()
if any([
    st.session_state.resume_data['header'],
    st.session_state.resume_data['objective'],
    *[st.session_state.resume_data[k] for k in ['education', 'work_experience', 'certifications', 'skills', 'awards', 'projects']]
]):
    st.download_button(
        'Download Resume Data (JSON)',
        data=json.dumps(st.session_state.resume_data, indent=2),
        file_name='resume_data.json',
        mime='application/json'
    )