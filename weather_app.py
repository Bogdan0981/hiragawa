import streamlit as st


def main_page():
    background_image_url = "https://img1.akspic.ru/crops/5/2/9/8/68925/68925-oblako-bassejn-nebo-palma-otel-1920x1080.jpg"  

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url({background_image_url});
        background-size: cover;
        background-position: center;
    }}

    .ezrtsby2 {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.title('Weather app')
    st.caption('Navigate to side bar to see full project info as well as options to choose from, to get started!')

    with st.sidebar:
        st.title('Chose your city')
        st.text_input('Write your city here')
        if st.button('Show weather'):
            weather_page()
main_page()


def weather_page():
    st.title('Weather in Prague')
    st.caption('There is a weather in Prague')
    background_img = 'https://situr.ru/media/k2/items/cache/6f43b5263fbba79c5962514b85d34738_XL.webp'

    st.markdown(f"""
    .stApp{{
            background-img: url({background_img})
            background-size: cover;
            background-position: center;
    }}
    """, unsafe_allow_html=True)

    st.markdown('***Current temperatue***')
    st.markdown('**24C**')
    if st.button("Вернуться на главную страницу"):
        main_page()



