import streamlit as st
import feedparser
import pandas as pd
import re

def is_ai_related(text):
    keywords = ['intelligence artificielle', 'IA', 'AI', 'machine learning',
                'deep learning', 'ChatGPT', 'OpenAI', 'LLM']
    return any(keyword.lower() in text.lower() for keyword in keywords)

def fetch_articles(sources):
    articles = []
    for source in sources.split('\n'):
        if not source.strip():
            continue
        try:
            feed = feedparser.parse(source)
            for entry in feed.entries:
                if is_ai_related(entry.title + entry.description):
                    articles.append({
                        'titre': entry.title,
                        'description': entry.description,
                        'date': entry.published,
                        'lien': entry.link
                    })
        except Exception as e:
            st.error(f"Erreur avec {source}: {str(e)}")
    return articles

def main():
    st.title("Agent de Veille IA")

    with st.sidebar:
        st.header("Configuration")
        use_openai = st.checkbox("Utiliser OpenAI (optionnel)", value=False)
        if use_openai:
            openai_key = st.text_input("OpenAI API Key", type="password")

        sources = st.text_area("Sources RSS",
            """https://www.lemonde.fr/rss/une.xml
https://www.lesechos.fr/rss/rss_tech.xml""")

    if st.button("Lancer la veille"):
        articles = fetch_articles(sources)
        if articles:
            df = pd.DataFrame(articles)
            st.dataframe(df)
            st.download_button("Télécharger CSV", df.to_csv(index=False), "veille_ia.csv")
        else:
            st.info("Aucun article IA trouvé")

if __name__ == "__main__":
    main()
