import streamlit as st
import feedparser
import pandas as pd
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

def classify_article(text, client):
    messages = [
        ChatMessage(role="system", content="Analyse si cet article est pertinent pour une veille IA. Réponds uniquement par 'Pertinent' ou 'Non pertinent'."),
        ChatMessage(role="user", content=text)
    ]
    response = client.chat(
        model="mistral-tiny",
        messages=messages
    )
    return response.messages[0].content

def main():
    st.title("Agent de Veille IA avec Mistral")

    with st.sidebar:
        st.header("Configuration")
        mistral_key = st.text_input("Mistral API Key", type="password")
        sources = st.text_area("Sources RSS",
            """https://www.lemonde.fr/rss/une.xml
https://www.lesechos.fr/rss/rss_tech.xml""")

    if st.button("Lancer la veille"):
        if not mistral_key:
            st.error("Clé API Mistral requise")
            return

        client = MistralClient(api_key=mistral_key)
        articles = []

        for source in sources.split('\n'):
            if not source.strip():
                continue
            try:
                feed = feedparser.parse(source)
                for entry in feed.entries:
                    relevance = classify_article(entry.description, client)
                    if relevance == 'Pertinent':
                        articles.append({
                            'titre': entry.title,
                            'description': entry.description,
                            'date': entry.published,
                            'lien': entry.link
                        })
            except Exception as e:
                st.error(f"Erreur avec {source}: {str(e)}")

        if articles:
            df = pd.DataFrame(articles)
            st.dataframe(df)
            st.download_button("Télécharger CSV", df.to_csv(index=False), "veille_ia.csv")
        else:
            st.info("Aucun article IA trouvé")

if __name__ == "__main__":
    main()
