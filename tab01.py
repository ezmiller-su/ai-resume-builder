import streamlit as st
import json
from openai import OpenAI
import chromadb
import pdfplumber

st.title('User Profile')

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'header': {
            'name': '',
            'contact_lines': []
        },
        'sections': []
    }

if 'section_bullets' not in st.session_state:
    st.session_state.section_bullets = []

openai_client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

def read_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
        return text

schema_dict = {"type":"object","properties":{"header":{"type":"object","properties":{"name":{"type":"string"},"subheader":{"type":"array","items":{"type":"string"},"description":"Contact lines such as citizenship, LinkedIn, phone, email."},"summary":{"type":"string"}},"required":["name","subheader"]},"sections":{"type":"array","items":{"type":"object","properties":{"title":{"type":"string"},"type":{"type":"string","enum":["education","experience","projects","skills"]},"entries":{"type":"array","items":{"oneOf":[{"type":"object","description":"Education entry.","properties":{"institution":{"type":"string"},"institution_detail":{"type":"array","items":{"type":"string"}},"date":{"type":"string"},"degree":{"type":"array","items":{"type":"string"}},"coursework":{"type":"array","items":{"type":"string"}}},"required":["institution","date","degree"]},{"type":"object","description":"Experience entry (used for both professional and leadership experience).","properties":{"role":{"type":"string"},"org":{"type":"string"},"date":{"type":"string"},"bullets":{"type":"array","items":{"type":"string"}}},"required":["role","org","date","bullets"]},{"type":"object","description":"Project entry.","properties":{"name":{"type":"string"},"date":{"type":"string"},"bullets":{"type":"array","items":{"type":"string"}}},"required":["name","date","bullets"]},{"type":"object","description":"Skills entry — one per category row.","properties":{"label":{"type":"string"},"items":{"type":"array","items":{"type":"string"}}},"required":["label","items"]}]}}},"required":["title","type","entries"]}}},"required":["header","sections"]}

with st.container(horizontal=True):
    uploaded = st.file_uploader('Load saved user profile', type='json')
    if uploaded:
        data = json.loads(uploaded.read())
        st.session_state.user_data = data
        if 'sections' not in st.session_state.user_data:
            st.session_state.user_data['sections'] = []
        st.success('Profile loaded successfully')
        st.rerun()
    aiuploaded = st.file_uploader('Import resume with AI', type='pdf')
if aiuploaded and st.session_state.get('last_ai_file_id') != aiuploaded.file_id:
    st.session_state.last_ai_file_id = aiuploaded.file_id   # ← mark as processed first

    document = read_pdf(aiuploaded).encode("utf-8", errors="ignore").decode("utf-8")

    response = openai_client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You extract resume content into structured JSON matching the provided schema."},
            {"role": "user", "content": f"Convert this document into JSON in the specified format:\n\n{document}"}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "resume", "strict": False, "schema": schema_dict}
        }
    )

    st.session_state.user_data = json.loads(response.choices[0].message.content)
    if 'sections' not in st.session_state.user_data:
        st.session_state.user_data['sections'] = []
    st.success('Profile loaded successfully')
    st.rerun()

st.divider()
st.text('Manually input information below:')

with st.expander('Header and Contact Information', expanded=True):
    st.session_state.user_data['header']['name'] = st.text_input(
        'Full Name',
        value=st.session_state.user_data['header'].get('name', ''),
        key='header_name'
    )
    
    st.write('**Contact Lines** (one per line)')
    contact_text = st.text_area(
        'Enter contact information (e.g., location, LinkedIn, phone, email)',
        value='\n'.join(st.session_state.user_data['header'].get('contact_lines', [])),
        height=100,
        key='contact_lines_input',
        label_visibility='collapsed'
    )
    st.session_state.user_data['header']['contact_lines'] = [
        line.strip() for line in contact_text.split('\n') if line.strip()
    ]


def render_section_editor(section_type):
    if 'sections' not in st.session_state.user_data:
        st.session_state.user_data['sections'] = []
    
    section_title_map = {
        'education': 'Education',
        'experience': 'Professional Experience',
        'projects': 'Projects',
        'skills': 'Technical Skills'
    }
    
    section_title = section_title_map.get(section_type, section_type.upper())
    
    with st.expander(section_title):
        section_idx = None
        for i, sec in enumerate(st.session_state.user_data['sections']):
            if sec['type'] == section_type:
                section_idx = i
                break
        
        if section_idx is None:
            st.session_state.user_data['sections'].append({
                'title': section_title,
                'type': section_type,
                'entries': []
            })
            section_idx = len(st.session_state.user_data['sections']) - 1
        
        section = st.session_state.user_data['sections'][section_idx]
        
        if section_type == 'education':
            st.write('**Add Education Entry**')
            col1, col2 = st.columns(2)
            inst_bold = col1.text_input('Institution (bold part)', key=f'{section_type}_inst_bold')
            inst_detail = col2.text_input('Institution Detail', key=f'{section_type}_inst_detail')
            col3, col4 = st.columns(2)
            degree = col3.text_area('Degree', key=f'{section_type}_degree')
            date_val = col4.text_input('Date', key=f'{section_type}_date')
            coursework = st.text_area('Relevant Coursework (comma-separated)', key=f'{section_type}_coursework')
            
            if st.button('+ Add Education Entry', key=f'add_{section_type}'):
                if inst_bold and degree and date_val:
                    section['entries'].append({
                        'institution': inst_bold,
                        'institution_detail': inst_detail,
                        'degree': degree,
                        'date': date_val,
                        'coursework_label': 'Relevant Coursework: ',
                        'coursework': [c.strip() for c in coursework.split(',') if c.strip()]
                    })
                    st.rerun()
                else:
                    st.warning('Please fill in institution, degree, and date')
        
        elif section_type == 'experience':
            st.write('**Add Experience Entry**')
            col1, col2 = st.columns(2)
            role = col1.text_input('Job Title', key=f'{section_type}_role')
            org = col2.text_input('Organization/Company', key=f'{section_type}_org')
            date_val = st.text_input('Dates', key=f'{section_type}_date')
            
            if f'{section_type}_bullets' not in st.session_state:
                st.session_state[f'{section_type}_bullets'] = []
            
            st.write('**Add bullet points:**')
            bullet = st.text_area('New bullet', key=f'{section_type}_bullet_input', height=60)
            if st.button('+ Add Bullet', key=f'add_{section_type}_bullet'):
                if bullet.strip():
                    st.session_state[f'{section_type}_bullets'].append(bullet.strip())
                    st.rerun()
            
            for j, b in enumerate(st.session_state.get(f'{section_type}_bullets', [])):
                col_a, col_b = st.columns([0.95, 0.05])
                col_a.caption(f"• {b}")
                if col_b.button('✕', key=f'del_{section_type}_bullet_{j}'):
                    st.session_state[f'{section_type}_bullets'].pop(j)
                    st.rerun()
            
            if st.button('Save Experience Entry', key=f'save_{section_type}'):
                if role and org and date_val and st.session_state.get(f'{section_type}_bullets'):
                    section['entries'].append({
                        'role': role + ', ',
                        'org': org,
                        'date': date_val,
                        'bullets': list(st.session_state[f'{section_type}_bullets'])
                    })
                    st.session_state[f'{section_type}_bullets'] = []
                    st.rerun()
                else:
                    st.warning('Please fill in all fields and add at least one bullet point')
        
        elif section_type == 'projects':
            st.write('**Add Project Entry**')
            proj_name = st.text_input('Project Name', key=f'{section_type}_name')
            date_val = st.text_input('Date', key=f'{section_type}_date')
            
            if f'{section_type}_bullets' not in st.session_state:
                st.session_state[f'{section_type}_bullets'] = []
            
            st.write('**Add bullet points:**')
            bullet = st.text_area('New bullet', key=f'{section_type}_bullet_input', height=60)
            if st.button('+ Add Bullet', key=f'add_{section_type}_bullet'):
                if bullet.strip():
                    st.session_state[f'{section_type}_bullets'].append(bullet.strip())
                    st.rerun()
            
            for j, b in enumerate(st.session_state.get(f'{section_type}_bullets', [])):
                col_a, col_b = st.columns([0.95, 0.05])
                col_a.caption(f"• {b}")
                if col_b.button('✕', key=f'del_{section_type}_bullet_{j}'):
                    st.session_state[f'{section_type}_bullets'].pop(j)
                    st.rerun()
            
            if st.button('Save Project Entry', key=f'save_{section_type}'):
                if proj_name and date_val and st.session_state.get(f'{section_type}_bullets'):
                    section['entries'].append({
                        'name': proj_name,
                        'date': date_val,
                        'bullets': list(st.session_state[f'{section_type}_bullets'])
                    })
                    st.session_state[f'{section_type}_bullets'] = []
                    st.rerun()
                else:
                    st.warning('Please fill in all fields and add at least one bullet point')
        
        elif section_type == 'skills':
            st.write('**Add Skill Category**')
            label = st.text_input('Category Label (e.g., "Languages: ")', key=f'{section_type}_label')
            items_text = st.text_area('Skills (comma-separated)', key=f'{section_type}_items')
            
            if st.button('+ Add Skill Category', key=f'add_{section_type}'):
                if label and items_text:
                    items = [i.strip() for i in items_text.split(',') if i.strip()]
                    section['entries'].append({
                        'label': label,
                        'items': items
                    })
                    st.rerun()
                else:
                    st.warning('Please fill in label and skills')
        
        st.write('---')
        st.write('**Existing Entries:**')
        for i, entry in enumerate(section['entries']):
            col1, col2 = st.columns([0.95, 0.05])
            
            if section_type == 'education':
                col1.markdown(f"**{entry['institution']}** {entry['institution_detail']}")
                col1.write(f"{entry['degree']} ({entry['date']})")
            elif section_type in ['experience', 'projects']:
                if section_type == 'experience':
                    col1.markdown(f"**{entry['role']}** {entry['org']} ({entry['date']})")
                else:
                    col1.markdown(f"**{entry['name']}** ({entry['date']})")
                for bullet in entry.get('bullets', []):
                    col1.write(f"• {bullet}")
            elif section_type == 'skills':
                col1.markdown(f"**{entry['label']}** {', '.join(entry['items'])}")
            
            if col2.button('✕', key=f'del_entry_{section_type}_{i}'):
                section['entries'].pop(i)
                st.rerun()

render_section_editor('education')
render_section_editor('experience')
render_section_editor('projects')
render_section_editor('skills')

st.divider()

if openai_client:
    try:
        chroma_client = chromadb.PersistentClient(path='./ChromaDB')
        collection = chroma_client.get_or_create_collection('ResumAI_collection')
    except:
        collection = None
else:
    collection = None
 
if any([
    st.session_state.user_data['header']['name'],
    st.session_state.user_data.get('sections', [])
]):
    with st.container(horizontal=True, horizontal_alignment='center'):
        if save := st.button('Save Profile', icon=":material/save:", type='primary'):
            if collection and openai_client:
                with st.spinner(text='Encoding user profile to Vector Database', show_time=False):
                    try:
                        for section in st.session_state.user_data['sections']:
                            section_text = f"Section: {section['title']}\n"
                            for entry in section['entries']:
                                if section['type'] == 'education':
                                    section_text += f"{entry['institution']} {entry['institution_detail']} - {entry['degree']} ({entry['date']})\n"
                                elif section['type'] in ['experience', 'projects']:
                                    name = entry.get('role', entry.get('name', ''))
                                    section_text += f"{name} - {entry.get('org', '')} ({entry['date']})\n"
                                    for bullet in entry.get('bullets', []):
                                        section_text += f"  {bullet}\n"
                            
                            response = openai_client.embeddings.create(
                                input=section_text,
                                model='text-embedding-3-small'
                            )
                            embedding = response.data[0].embedding
                            
                            collection.add(
                                documents=[section_text],
                                ids=[f"{st.session_state.user_data['header']['name']}_{section['type']}"],
                                embeddings=[embedding]
                            )
                        
                        st.success('Profile saved to vector database!')
                    except Exception as e:
                        st.error(f'Error saving to database: {e}')
            else:
                st.info('Vector database not available. Download your profile instead.')
        
        st.download_button(
            'Download Profile (.json)',
            data=json.dumps(st.session_state.user_data, indent=2),
            file_name=f"{st.session_state.user_data['header']['name'].replace(' ', '_')}_profile.json",
            mime='application/json',
            icon=":material/download:"
        )
