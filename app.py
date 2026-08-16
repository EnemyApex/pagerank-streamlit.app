import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time
from io import BytesIO

st.set_page_config(page_title="PageRank - 10 Sites Web", layout="wide")
st.title("🚀 Implémentation et Expérimentation de l'algorithme PageRank(mbola teste😂)")

# 1. GRAPHE DE BASE : 10 SITES
BASE_SITES = {
    'google.com': 'Moteur de recherche', 'wikipedia.org': 'Encyclopédie',
    'youtube.com': 'Vidéos', 'facebook.com': 'Réseau social', 'github.com': 'Développement',
    'amazon.com': 'E-commerce', 'news.bbc.com': 'Actualités', 'stackoverflow.com': 'Q&A Dev',
    'instagram.com': 'Photos', 'linkedin.com': 'Professionnel'
}
BASE_EDGES = [
    ('google.com', 'wikipedia.org'), ('google.com', 'youtube.com'), ('google.com', 'amazon.com'),
    ('wikipedia.org', 'github.com'), ('wikipedia.org', 'news.bbc.com'),
    ('youtube.com', 'google.com'), ('youtube.com', 'instagram.com'),
    ('facebook.com', 'instagram.com'), ('facebook.com', 'linkedin.com'),
    ('github.com', 'stackoverflow.com'), ('github.com', 'google.com'),
    ('amazon.com', 'facebook.com'), ('news.bbc.com', 'wikipedia.org'), ('news.bbc.com', 'google.com'),
    ('stackoverflow.com', 'github.com'), ('stackoverflow.com', 'google.com'),
    ('instagram.com', 'facebook.com'), ('linkedin.com', 'github.com'), ('linkedin.com', 'stackoverflow.com')
]

# 2. FONCTIONS
def build_graph(sites_dict, edges_list):
    G = nx.DiGraph()
    for site in sites_dict.keys(): G.add_node(site)
    G.add_edges_from(edges_list)
    return G

def pagerank(G, d=0.85, max_iter=100, tol=1e-6):
    N = G.number_of_nodes()
    if N == 0: return {}, [], 0
    pr = {n: 1/N for n in G.nodes()}
    for i in range(max_iter):
        new_pr = {}
        for n in G.nodes():
            rank = (1-d)/N
            for pred in G.predecessors(n):
                rank += d * pr[pred] / max(1, G.out_degree(pred))
            new_pr[n] = rank
        if sum(abs(new_pr[n]-pr[n]) for n in G) < tol: break
        pr = new_pr
    return pr, i+1

def draw_graph(G, scores):
    fig, ax = plt.subplots(figsize=(9, 6))
    pos = nx.spring_layout(G, k=0.7, seed=42)
    sizes = [scores[n]*20000 if scores else 1000 for n in G.nodes()]
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=sizes,
            node_color=list(scores.values()), cmap='plasma',
            font_size=8, font_weight='bold', arrows=True, arrowsize=12, edge_color='gray', alpha=0.8)
    sm = plt.cm.ScalarMappable(cmap='plasma', norm=plt.Normalize(vmin=min(scores.values()), vmax=max(scores.values())))
    sm._A = []
    fig.colorbar(sm, ax=ax, label="Score PageRank")
    plt.tight_layout()
    return fig

def get_file_download(fig, format):
    buf = BytesIO()
    fig.savefig(buf, format=format, dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

# 3. ONGLET
tab1, tab2 = st.tabs(["🌐 Web de 10 sites", "➕ Ajouter des sites manuellement"])

with tab1:
    st.write("Utilise le mini-web de 10 sites prédéfinis")
    G_base = build_graph(BASE_SITES, BASE_EDGES)
    d = st.slider("Facteur d'amortissement d", 0.1, 0.99, 0.85, 0.01, key="d1")
    if st.button("▶️ Lancer sur 10 sites", type="primary"):
        with st.spinner("Calcul..."):
            start = time.time()
            scores, it = pagerank(G_base, d)
            end = time.time()
            fig = draw_graph(G_base, scores)

        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("🏆 Classement")
            df = pd.DataFrame(scores.items(), columns=['Site', 'Score PageRank']).sort_values('Score PageRank', ascending=False)
            df['Rang'] = df.index + 1
            df['Score PageRank'] = df['Score PageRank'].apply(lambda x: f"{x:.5f}")
            st.dataframe(df[['Rang', 'Site', 'Score PageRank']], use_container_width=True, hide_index=True)
            st.metric("Temps", f"{end-start:.3f}s")
            st.metric("Itérations", it)

            # BOUTONS EXPORT
            st.divider()
            st.subheader("📥 Exporter le graphe")
            png_file = get_file_download(fig, 'png')
            st.download_button("Télécharger PNG", png_file, "graphe_pagerank.png", "image/png")
            pdf_file = get_file_download(fig, 'pdf')
            st.download_button("Télécharger PDF", pdf_file, "graphe_pagerank.pdf", "application/pdf")

        with col2:
            st.subheader("🕸️ Visualisation du Graphe")
            st.pyplot(fig)

with tab2:
    st.write("Crée ton propre graphe ici")
    if 'sites_manuel' not in st.session_state: st.session_state.sites_manuel = {'siteA.com': 'Site A'}
    if 'edges_manuel' not in st.session_state: st.session_state.edges_manuel = []

    col1, col2 = st.columns(2)
    with col1:
        new_site = st.text_input("Nom du site ex: monsite.com")
        if st.button("Ajouter Site") and new_site:
            st.session_state.sites_manuel[new_site] = "Custom"
            st.rerun()
    with col2:
        sites_list = list(st.session_state.sites_manuel.keys())
        if len(sites_list) > 1:
            src = st.selectbox("De", sites_list)
            dst = st.selectbox("Vers", sites_list)
            if st.button("Ajouter Lien"):
                st.session_state.edges_manuel.append((src, dst))
                st.rerun()

    st.write("**Sites :**", list(st.session_state.sites_manuel.keys()))
    st.write("**Liens :**", st.session_state.edges_manuel)

    d2 = st.slider("Facteur d", 0.1, 0.99, 0.85, 0.01, key="d2")
    if st.button("▶️ Lancer PageRank sur mes sites", type="primary"):
        G_custom = build_graph(st.session_state.sites_manuel, st.session_state.edges_manuel)
        with st.spinner("Calcul..."):
            start = time.time()
            scores, it = pagerank(G_custom, d2)
            end = time.time()
            fig = draw_graph(G_custom, scores)

        col1, col2 = st.columns([1, 1.5])
        with col1:
            df = pd.DataFrame(scores.items(), columns=['Site', 'Score PageRank']).sort_values('Score PageRank', ascending=False)
            st.dataframe(df, use_container_width=True)
            # BOUTONS EXPORT
            png_file = get_file_download(fig, 'png')
            st.download_button("Télécharger PNG", png_file, "graphe_custom.png", "image/png")
            pdf_file = get_file_download(fig, 'pdf')
            st.download_button("Télécharger PDF", pdf_file, "graphe_custom.pdf", "application/pdf")
        with col2:
            st.pyplot(fig)
