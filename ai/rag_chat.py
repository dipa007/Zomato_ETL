import os
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Using Gemini's cloud embedding model instead of hefty local files
EMBEDDING_MODEL = "gemini-embedding-2"
CHAT_MODEL = "gemini-3-flash-preview"
NEW_REVIEWS = 100
TOK_K = 5
# Renamed cache file to match the new 768-dimension Gemini embeddings
CACHE_FILE = "review_embeddings_gemini.parquet"

# A single lightweight client handles both embeddings and chat
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def read_reviews_from_snowflake():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = f"""
        SELECT REVIEW_ID, CITY, RATING, COMMENT
        FROM ZOMATO.STAGING.STG_REVIEWS
        SAMPLE ({NEW_REVIEWS} ROWS)
    """
    df = conn.cursor().execute(query).fetch_pandas_all()
    conn.close()

    df.columns = [col.lower() for col in df.columns]
    return df

def embed(texts):
    all_embeddings = []
    batch_size = 100  # Maximum allowed by the Gemini API
    
    # Process the reviews in chunks of 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Explicitly wrap each string so the multimodal SDK treats them as separate documents
        formatted_batch = [
            types.Content(parts=[types.Part(text=t)]) for t in batch
        ]
        
        response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=formatted_batch
        )
        
        # Extract and append the numeric vectors from this batch
        batch_embeddings = [e.values for e in response.embeddings]
        all_embeddings.extend(batch_embeddings)
        
    return all_embeddings
    
@st.cache_data()
def load_reviews():
    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)

    df = read_reviews_from_snowflake()
    df['embedding'] = embed(df['comment'].tolist())
    df.to_parquet(CACHE_FILE)
    return df

st.title("Chat with your Zomato Reviews")
st.caption(f"Searching {NEW_REVIEWS} reviews, answering with {CHAT_MODEL} model")

def consine_simiarity(vec_a, vec_b):
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))

def find_similar_reviews(question, df):
    # Generate the vector for the user's search query
    question_vector = embed([question])[0]

    scores = []
    for review_vector in df['embedding']:
        scores.append(consine_simiarity(question_vector, review_vector))

    df = df.copy()
    df['score'] = scores
    return df.nlargest(TOK_K, 'score')

def ask_llm(question, top_reviews):
    context = ""

    for _, row in top_reviews.iterrows():
        context += f" ({row['city']}, {row['rating']} stars) {row['comment']}\n"

    system_prompt = (
        "Answer ONLY using the customer reviews provided. "
        "Be concise. If the reviews don't cover it, say so."
    )

    user_prompt = f"Question: {question}\n\nReviews:\n{context}"

    response = gemini_client.models.generate_content(
        model=CHAT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2
        )
    )
    return response.text
    
review_df = load_reviews()

question = st.text_input("Ask a question about your reviews:",
                         placeholder="e.g. What are the most common complaints about delivery?")

if question:
    top_reviews = find_similar_reviews(question, review_df)
    answer = ask_llm(question, top_reviews)

    st.markdown(f"**Answer:**")
    st.write(answer)

    with st.expander("Reviews used to build this answer"):
        st.dataframe(top_reviews[['city', 'rating', 'comment']], hide_index=True)