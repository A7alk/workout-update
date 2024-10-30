from astrapy import DataAPIClient
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()


os.environ["ASTRA_ENDPOINT"] =  "https://65d57f4b-7859-4de5-b03e-49a4a2df901c-us-east-2.apps.astra.datastax.com"
os.environ["ASTRA_DB_APPLICATION_TOKEN"] = "AstraCS:WWyBcesTMHMkdjbvyFRzlNQj:a6942c077116610d183d3a16dff02be22985bdda44c8378c71d9ffed0fce2192"

# Now attempt to load them with os.getenv to see if the error persists
ENDPOINT = os.getenv("ASTRA_ENDPOINT")
TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")

if not ENDPOINT or not TOKEN:
    raise ValueError("Missing ASTRA_ENDPOINT or ASTRA_DB_APPLICATION_TOKEN environment variables.")


# Fetch endpoint and token, ensuring they are set


@st.cache_resource
def get_db():
    client = DataAPIClient(TOKEN)
    db = client.get_database_by_api_endpoint(ENDPOINT)
    return db

db = get_db()
collection_names = ["personal_data", "notes"]

for collection in collection_names:
    try:
        db.create_collection(collection)
    except Exception as e:
        st.warning(f"Collection '{collection}' might already exist or failed to create: {e}")

personal_data_collection = db.get_collection("personal_data")
notes_collection = db.get_collection("notes")
