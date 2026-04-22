import streamlit as st

tab01 = st.Page('tab01.py', title='Upload Information')
tab02 = st.Page('tab02.py', title='Generate Tailored CV')


pg = st.navigation(pages = [tab01, tab02], position="sidebar", expanded=False)
st.set_page_config(page_title="AI Resume Builder", page_icon=None, layout="wide", initial_sidebar_state="expanded", menu_items=None)
pg.run()