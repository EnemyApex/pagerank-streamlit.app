import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time

st.set_page_config(page_title="PageRank - 10 Sites Web", layout="wide")
st.title("🚀 Implémentation et Expérimentation de PageRank")
st.caption("Ajoutez vos propres sites ou utilisez le mini-web de 10 sites par défaut")

# 1. GRAPHE DE BASE : 10 SITES
BASE_SITES = {
    'google.com': 'Moteur de recherche',
    'wikipedia.org': 'Encyclopédie',
    'youtube.com': 'Vidéos',
    'facebook.com': 'Réseau social',
    'github.com': 'Développement',
    'amazon.com': 'E-commerce',
    'news.bbc.com': 'Actualités',
    'stackoverflow.com': 'Q&A Dev',
    'instagram.com': 'Photos',
    'linkedin.com': 'Professionnel'
}

BASE_EDGES = [
    ('google.com', 'wikipedia.org'), ('google.com', 'youtube.com'), ('google.com', 'amazon.com'),
    ('wikipedia.org', 'github.com'), ('wikipedia.org', 'news.bbc.com'),
    ('youtube.com', 'google.com'), ('youtube.com', 'instagram.com'),
    ('facebook.com', 'instagram.com'), ('facebook.com', 'linkedin.com'),
    ('github.com', 'stackoverflow.com'), ('github.com', 'google.com'),
    ('amazon.com', 'facebook.com'),
    ('news.bbc.com', 'wikipedia.org'), ('news.bbc.com', 'google.com'),
    ('stackoverflow.com', 'github.com'), ('stackoverflow.com', 'google.com'),
    ('instagram.com', 'facebook.com'),
    ('linkedin.com', 'github.com'), ('linkedin.com', 'stackoverflow.com')
]

# 2. ONGLET
tab1, tab2 = st.tabs(["🌐 Web de 10 sites", "➕ Ajouter des sites manuellement"])

def build_graph(sites_dict, edges_list):
    G = nx.DiGraph()
    for site in sites_dict.keys():
        G.add_node(site)
    G.add_edges_from(edges_list)
    return G

def pagerank(G, d=0.85, max_iter=100, tol=1e-6):
    N = G.number_of_nodes()
    if N == 0: return {}, [], 0
    pr = {n: 1/N for n in G.nodes()}
    history = [pr.copy()]
    for i in range(max_iter):
        new_pr = {}
        for n in G.nodes():
            rank = (1-d)/N
            for pred in G.predecessors(n):
                rank += d * pr[pred] / max(1, G.out_degree(pred))
            new_pr[n] = rank
        history.append(new_pr.copy())
        if sum(abs(new_pr[n]-pr[n]) for n in G) < tol: break
        pr = new_pr
    return pr, history, i+1

def afficher_resultats(G, scores, iterations, temps):
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("🏆 Classement")
        df = pd.DataFrame(scores.items(), columns=['Site', 'Score PageRank'])
        df = df.sort_values('Score PageRank', ascending=False).reset_index(drop=True)
        df['Rang'] = df.index + 1
        df['Score PageRank'] = df['Score PageRank'].apply(lambda x: f"{x:.5f}")
        st.dataframe(df[['Rang', 'Site', 'Score PageRank']], use_container_width=True, hide_index=True)
        st.metric("Temps", f"{temps:.3f}s")
        st.metric("Itérations", iterations)
    with col2:
        st.subheader("🕸️ Graphe")
        fig, ax = plt.subplots(figsize=(7, 5))
        pos = nx.spring_layout(G, k=0.7, seed=42)
        sizes = [scores[n]*20000 if scores else 1000 for n in G.nodes()]
        nx.draw(G, pos, ax=ax, with_labels=True, node_size=sizes,
                node_color=list(scores.values()), cmap='plasma',
                font_size=7, arrows=True, arrowsize=10, edge_color='gray')
        st.pyplot(fig)

with tab1:
    st.write("Utilise le mini-web de 10 sites prédéfinis")
    G_base = build_graph(BASE_SITES, BASE_EDGES)
    d = st.slider("Facteur d", 0.1, 0.99, 0.85, 0.01, key="d1")
    if st.button("▶️ Lancer sur 10 sites", type="primary"):
        with st.spinner("Calcul..."):
            start = time.time()
            scores, history, it = pagerank(G_base, d)
            end = time.time()
        afficher_resultats(G_base, scores, it, end-start)

with tab2:
    st.write("Crée ton propre graphe ici")
    # Stockage dans session_state
    if 'sites_manuel' not in st.session_state:
        st.session_state.sites_manuel = {'siteA.com': 'Site A', 'siteB.com': 'Site B'}
    if 'edges_manuel' not in st.session_state:
        st.session_state.edges_manuel = [('siteA.com', 'siteB.com')]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Ajouter un Site")
        new_site = st.text_input("Nom du site ex: monsite.com")
        new_desc = st.text_input("Description")
        if st.button("Ajouter Site"):
            if new_site and new_site not in st.session_state.sites_manuel:
                st.session_state.sites_manuel[new_site] = new_desc
                st.rerun()

    with col2:
        st.subheader("2. Ajouter un Lien")
        sites_list = list(st.session_state.sites_manuel.keys())
        src = st.selectbox("De", sites_list)
        dst = st.selectbox("Vers", sites_list)
        if st.button("Ajouter Lien"):
            if (src, dst) not in st.session_state.edges_manuel:
                st.session_state.edges_manuel.append((src, dst))
                st.rerun()

    st.divider()
    st.write("**Sites actuels :**", list(st.session_state.sites_manuel.keys()))
    st.write("**Liens actuels :**", st.session_state.edges_manuel)

    d2 = st.slider("Facteur d", 0.1, 0.99, 0.85, 0.01, key="d2")
    if st.button("▶️ Lancer PageRank sur mes sites", type="primary"):
        G_custom = build_graph(st.session_state.sites_manuel, st.session_state.edges_manuel)
        with st.spinner("Calcul..."):
            start = time.time()
            scores, history, it = pagerank(G_custom, d2)
            end = time.time()
        afficher_resultats(G_custom, scores, it, end-start)

    if st.button("🗑️ Réinitialiser mes sites"):
        st.session_state.sites_manuel = {}
        st.session_state.edges_manuel = []
        st.rerun()
