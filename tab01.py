import streamlit as st
import json
from openai import OpenAI
import chromadb

st.title('User Profile')

# Initialize session state with proper structure
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

# Load OpenAI client if API key is available
try:
    openai_client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
except:
    openai_client = None

# File upload handler
uploaded = st.file_uploader('Load saved resume data', type='json')
if uploaded:
    data = json.loads(uploaded.read())
    st.session_state.user_data = data
    # Ensure sections exists after loading
    if 'sections' not in st.session_state.user_data:
        st.session_state.user_data['sections'] = []
    st.success('Profile loaded successfully!')
    st.rerun()

st.divider()
st.text('Manually input information below:')

# ============================================================================
# HEADER SECTION
# ============================================================================
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

# ============================================================================
# EDUCATION SECTION
# ============================================================================
st.subheader('Sections')

def render_section_editor(section_type):
    """Render editor for a specific section type."""
    # Ensure sections exist
    if 'sections' not in st.session_state.user_data:
        st.session_state.user_data['sections'] = []
    
    section_title_map = {
        'education': 'EDUCATION',
        'experience': 'PROFESSIONAL EXPERIENCE',
        'projects': 'PROJECTS',
        'skills': 'TECHNICAL SKILLS'
    }
    
    section_title = section_title_map.get(section_type, section_type.upper())
    
    with st.expander(section_title):
        # Find or create section in data
        section_idx = None
        for i, sec in enumerate(st.session_state.user_data['sections']):
            if sec['type'] == section_type:
                section_idx = i
                break
        
        if section_idx is None:
            # Create new section
            st.session_state.user_data['sections'].append({
                'title': section_title,
                'type': section_type,
                'entries': []
            })
            section_idx = len(st.session_state.user_data['sections']) - 1
        
        section = st.session_state.user_data['sections'][section_idx]
        
        # Section-specific input logic
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
                        'institution_bold': inst_bold,
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
            
            # Bullet collection
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
        
        # Display existing entries
        st.write('---')
        st.write('**Existing Entries:**')
        for i, entry in enumerate(section['entries']):
            col1, col2 = st.columns([0.95, 0.05])
            
            if section_type == 'education':
                col1.markdown(f"**{entry['institution_bold']}** {entry['institution_detail']}")
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

# Render all section types
render_section_editor('education')
render_section_editor('experience')
render_section_editor('projects')
render_section_editor('skills')

# ============================================================================
# SAVE & DOWNLOAD
# ============================================================================
st.divider()

# Vector database integration (optional)
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
                        # Create document chunks from sections
                        for section in st.session_state.user_data['sections']:
                            section_text = f"Section: {section['title']}\n"
                            for entry in section['entries']:
                                if section['type'] == 'education':
                                    section_text += f"{entry['institution_bold']} {entry['institution_detail']} - {entry['degree']} ({entry['date']})\n"
                                elif section['type'] in ['experience', 'projects']:
                                    name = entry.get('role', entry.get('name', ''))
                                    section_text += f"{name} - {entry.get('org', '')} ({entry['date']})\n"
                                    for bullet in entry.get('bullets', []):
                                        section_text += f"  {bullet}\n"
                            
                            # Create embedding
                            response = openai_client.embeddings.create(
                                input=section_text,
                                model='text-embedding-3-small'
                            )
                            embedding = response.data[0].embedding
                            
                            # Add to collection
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
