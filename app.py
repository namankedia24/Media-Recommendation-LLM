import time
import streamlit as st
from system import RAGSystem


if "rag_system" not in st.session_state:
    st.session_state.rag_system = RAGSystem() 
# rag_system = RAGSystem()

# print("Loaded...")

# Streamlit app title

st.set_page_config(page_title="Media Search Assistant", page_icon="🎬")

st.title("Mallika's Personal Assistant ❤️")

media_name = st.text_input(f"🔍 Enter media name:", placeholder="e.g., Severence")

# st.markdown('####')
# st.image("https://media.giphy.com/media/3ohhwsP9qFzhQwaGRS/giphy.gif")

year_input = st.text_input("📅 Enter Year (Optional):", placeholder="e.g., 2015")

query = st.text_input(f"🔍 Enter your query/what do you want to search:", placeholder="e.g., Give me 3 similar recommendations with the same writer")

st.text(" ")
with st.container():
    st.write("Check the boxes below to include different media types in your search response:")
    col1, col2, col3 = st.columns(3)

    with col1:
        search_books = st.checkbox("📚 Books", value=True)
    with col2:
        search_movies = st.checkbox("🎬 Movies", value=True)
    with col3:
        search_shows = st.checkbox("📺 Shows", value=True)

search_options = []
if search_books:
    search_options.append("Books")
if search_movies:
    search_options.append("Movies")
if search_shows:
    search_options.append("Shows")


if st.button("🎬 Search"):
    if not media_name or not query:
        st.warning(f"⚠️ Please enter a media name/query to search.")
    else:
        try:
            with st.spinner("Searching... 🔍"):
                begin = time.time()
                response, relevant_node = st.session_state.rag_system.searchmedia(query, search_options, year_input, media_name)
                end = time.time()
                st.subheader("Response:")
                st.write(response)
                st.subheader(f"Approx Response Time: {end - begin:.2f} seconds")
                # st.success(f"✅ Found {search_type}: **{media_name} ({year_input if year_input else 'Year Unknown'})**")
                # st.info("ℹ️ Additional details will be fetched here...")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")