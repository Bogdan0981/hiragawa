import streamlit as st

def main_page():
    background_image_url = "https://img1.akspic.ru/crops/5/2/9/8/68925/68925-oblako-bassejn-nebo-palma-otel-1920x1080.jpg"
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{background_image_url}');
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.title('Weather app')
    st.caption('Navigate to the sidebar to see full project info as well as options to choose from, to get started!')

def weather_page():
    background_img = 'https://situr.ru/media/k2/items/cache/6f43b5263fbba79c5962514b85d34738_XL.webp'
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url('{background_img}');
        background-size: cover;
        background-position: center;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.title('Weather in Prague')
    st.caption('There is the weather in Prague')
    st.markdown('***Current temperature***')
    st.markdown('**24°C**')
    if st.button("Return to main page"):
        st.session_state.page = 'main'

if 'page' not in st.session_state:
    st.session_state.page = 'main'



with st.sidebar:
    st.title('Choose your city')
    city = st.text_input('Write your city here')
    if st.button('Show weather'):
        st.session_state.page = 'weather'

if st.session_state.page == 'main':
    main_page()
elif st.session_state.page == 'weather':
    weather_page()
