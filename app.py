import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import time

st.set_page_config(page_title="PageRank - 10 Sites Web", layout="wide")
st.title("🚀 Implémentation et Expérimentation de PageRank")
st.caption("Simulation d'un mini-web de 10 sites. Déployé sur Streamlit Cloud")

# 1. DEFINITION DES 10 SITES
SITES = {
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

# 2. CREATION DU GRAPHE AVEC DES LIENS REALISTES
@st.cache_data
def build_graph():
    G = nx.DiGraph()
    for site in SITES.keys():
        G.add_node(site)

    edges = [
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
    G.add_edges_from(edges)
    return G

G = build_graph()

# 3. BARRE LATERALE PARAMETRES
st.sidebar.header("⚙️ Paramètres")
d = st.sidebar.slider("Facteur d'amortissement d", 0.1, 0.99, 0.85, 0.01)
max_iter = st.sidebar.slider("Nombre max d'itérations", 10, 200, 100, 10)

# 4. FONCTION PAGERANK FROM SCRATCH
def pagerank(G, d=0.85, max_iter=100, tol=1e-6):
    N = G.number_of_nodes()
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
        if sum(abs(new_pr[n]-pr[n]) for n in G) < tol:
            break
        pr = new_pr
    return pr, history, i+1

# 5. BOUTON ET AFFICHAGE
if st.button("▶️ Lancer le calcul PageRank", type="primary"):
    with st.spinner("Calcul en cours..."):
        start = time.time()
        scores, history, iterations = pagerank(G, d, max_iter)
        end = time.time()

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🏆 Classement des Sites")
        df = pd.DataFrame(scores.items(), columns=['Site', 'Score PageRank'])
        df = df.sort_values('Score PageRank', ascending=False).reset_index(drop=True)
        df['Rang'] = df.index + 1
        df['Score PageRank'] = df['Score PageRank'].apply(lambda x: f"{x:.4f}")
        df['Description'] = df['Site'].map(SITES)
        st.dataframe(df[['Rang', 'Site', 'Score PageRank', 'Description']], use_container_width=True, hide_index=True)
        st.metric("Temps de calcul", f"{end-start:.3f}s")
        st.metric("Itérations", iterations)

    with col2:
        st.subheader("🕸️ Visualisation du Graphe")
        fig, ax = plt.subplots(figsize=(7, 5))
        pos = nx.spring_layout(G, k=0.6, seed=42)
        sizes = [scores[n]*20000 for n in G.nodes()]
        nx.draw(G, pos, ax=ax, with_labels=True,
                node_size=sizes,
                node_color=list(scores.values()),
                cmap='plasma',
                font_size=7,
                font_weight='bold',
                arrows=True, arrowsize=12, edge_color='gray', alpha=0.7)
        sm = plt.cm.ScalarMappable(cmap='plasma', norm=plt.Normalize(vmin=min(scores.values()), vmax=max(scores.values())))
        sm._A = []
        fig.colorbar(sm, ax=ax, label="Score PageRank")
        st.pyplot(fig)

st.sidebar.info("Projet PageRank | FakevertoRJ | Toamasina MG")
