import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import requests
from openai import OpenAI

st.set_page_config(page_title="Agent de Veille IA")

def fetch_rss(url):
    return feedparser.parse(url)

def classify_article(text, openai_client):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "Analyse si cet article est pertinent pour une veille IA. Réponds uniquement par 'Pertinent' ou 'Non pertinent'."
        }, {
            "role": "user",
            "content": text
        }]
    )
    return response.choices[0].message.content

def main():
    st.title("Agent de Veille IA")
    
    # Configuration
    with st.sidebar:
        st.header("Configuration")
        openai_key = st.text_input("OpenAI API Key", type="password")
        sources = st.text_area("Sources RSS (une par ligne)", 
            """https://www.lemonde.fr/rss/une.xml
https://www.lesechos.fr/rss/rss_tech.xml""")
        
        if st.button("Lancer la veille"):
            if not openai_key:
                st.error("Clé API OpenAI requise")
                return
                
            client = OpenAI(api_key=openai_key)
            articles = []
            
            for source in sources.split('\n'):
                feed = fetch_rss(source)
                for entry in feed.entries:
                    relevance = classify_article(entry.description, client)
                    if relevance == 'Pertinent':
                        articles.append({
                            'titre': entry.title,
                            'description': entry.description,
                            'date': entry.published,
                            'lien': entry.link
                        })
            
            if articles:
                df = pd.DataFrame(articles)
                st.dataframe(df)
                
                # Export
                st.download_button(
                    "Télécharger en CSV",
                    df.to_csv(index=False).encode('utf-8'),
                    "veille_ia.csv"
                )
            else:
                st.info("Aucun article IA pertinent trouvé")

if __name__ == "__main__":
    main()
