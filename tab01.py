import streamlit as st

with st.expander('Header and Contact'):
    st.text_input('Full Name')
    st.text_input('Address')
    st.text_input('Phone')
    st.text_input('Email')
    st.text_input('LinkedIn')
with st.expander('Objective/Summary'):
    st.text_area('A brief statement that defines your career goals.')
with st.expander('Education'):
    st.text_area('Outline your degrees and diplomas')
with st.expander('Work Experience'):
    st.text_area('')
with st.expander('Certifications and Licenses'):
    st.text_area('')
with st.expander('Skills'):
    st.text_area('')
with st.expander('Awards and Honors'):
    st.text_area('')
with st.expander('Projects'):
    st.text_area('')