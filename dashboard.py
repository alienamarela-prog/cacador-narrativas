import json
from pathlib import Path

import pandas as pd
import streamlit as st

HISTORY_PATH = Path("data/narrative_history.json")
SNAPSHOT_PATH = Path("data/latest_snapshot.json")

st.set_page_config(
    page_title="Caçador de Narrativas",
    page_icon="🛸",
    layout="wide",
)

st.title("🛸 Caçador de Narrativas")
st.caption("Radar de narrativas cripto da Alien Amarela")

if not SNAPSHOT_PATH.exists():
    st.warning("Ainda não existe data/latest_snapshot.json. Rode o coletor pelo menos uma vez.")
    st.stop()

snapshot = json.loads(SNAPSHOT_PATH.read_text())
ranking = snapshot.get("ranking", [])
alpha = snapshot.get("alpha_hunter", [])
research = snapshot.get("alien_research", [])
dex = snapshot.get("narrative_dex", [])
content = snapshot.get("content_hunter", [])
explosoes = snapshot.get("explosoes", [])
wallet_discovery = snapshot.get("wallet_discovery", [])

st.caption(f"Última atualização: {snapshot.get('gerado_em')}")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔥 Radar",
    "⚡ Alpha Hunter",
    "🧠 Alien Research",
    "🧬 Narrative Dex",
    "✍️ Content Hunter",
    "📈 Histórico",
    "🕵️ Wallet Discovery",
])

with tab1:
    st.subheader("🔥 Ranking atual de narrativas")

    if ranking:
        df = pd.DataFrame(ranking)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Narrativas", len(df))
        col2.metric("Maior score", df["score"].max())
        col3.metric("Explosivas", len(df[df["nivel"] == "Explosiva"]))
        col4.metric("Com influenciadores", len(df[df["infl_mencoes"] > 0]))

        cols = [
            "nome", "score", "nivel", "fontes",
            "infl_mencoes", "reddit_mencoes", "rss_mencoes"
        ]
        st.dataframe(df[cols], use_container_width=True)

        st.subheader("🚨 Explosões detectadas")
        if explosoes:
            exp_df = pd.DataFrame(explosoes)
            st.dataframe(exp_df, use_container_width=True)
        else:
            st.info("Nenhuma explosão detectada no snapshot atual.")
    else:
        st.warning("Ranking vazio.")

with tab2:
    st.subheader("⚡ Alpha Hunter — pré-explosão")

    if alpha:
        for item in alpha:
            with st.container(border=True):
                st.markdown(f"### {item['nome']} — {item['score']}/100 ({item['nivel']})")
                c1, c2, c3 = st.columns(3)
                c1.metric("KOLs", item.get("infl_mencoes", 0))
                c2.metric("Reddit", item.get("reddit_mencoes", 0))
                c3.metric("Notícias", item.get("rss_mencoes", 0))

                infls = item.get("influenciadores", [])
                if infls:
                    st.write("**Influenciadores:** " + ", ".join(infls[:10]))

                st.caption("Leitura: possível narrativa ganhando força antes da mídia.")
    else:
        st.info("Nenhuma pré-explosão detectada no snapshot atual.")

with tab3:
    st.subheader("🧠 Alien Research")

    if research:
        nomes = [item["nome"] for item in research]
        selecionada = st.selectbox("Escolha uma narrativa", nomes)

        item = next(x for x in research if x["nome"] == selecionada)

        st.markdown(f"## {item['nome']} — {item['score']}/100 ({item['nivel']})")

        c1, c2, c3 = st.columns(3)
        c1.metric("KOLs", item.get("infl_mencoes", 0))
        c2.metric("Reddit", item.get("reddit_mencoes", 0))
        c3.metric("Notícias", item.get("rss_mencoes", 0))

        st.markdown("### 👽 O que é")
        st.write(item.get("o_que_e"))

        st.markdown("### 📡 Por que entrou no radar")
        st.write("Fontes: " + " + ".join(item.get("fontes", [])))
        infls = item.get("influenciadores", [])
        st.write("KOLs: " + (", ".join(infls) if infls else "Sem KOLs detectados"))

        st.markdown("### 🪙 Tokens relacionados")
        tokens = item.get("tokens", [])
        st.write(", ".join(tokens) if tokens else "Ainda sem tokens mapeados")

        st.markdown("### ⚠️ Risco")
        st.write(item.get("risco"))

        st.markdown("### 💡 Ideia de conteúdo")
        st.success(item.get("conteudo"))
    else:
        st.info("Alien Research ainda vazio.")

with tab4:
    st.subheader("🧬 Narrative Dex")

    if dex:
        for item in dex:
            with st.container(border=True):
                st.markdown(
                    f"### {item['narrativa']} — Score narrativo {item['score_narrativa']}/100 ({item['nivel']})"
                )

                tokens = item.get("tokens", [])
                if tokens:
                    token_df = pd.DataFrame(tokens)
                    st.dataframe(token_df, use_container_width=True)
                else:
                    st.info("Sem tokens mapeados.")
    else:
        st.info("Narrative Dex vazio no snapshot atual.")

with tab5:
    st.subheader("✍️ Content Hunter")

    if content:
        for item in content:
            with st.container(border=True):
                st.markdown(f"### 🚀 {item['narrativa']}")

                st.markdown("#### 🧵 Ideia de thread")
                st.write(item.get("thread"))

                st.markdown("#### 😂 Ideia de meme")
                st.write(item.get("meme"))

                st.markdown("#### ⚡ Post curto")
                st.success(item.get("post_curto"))
    else:
        st.info("Content Hunter vazio no snapshot atual.")

with tab6:
    st.subheader("📈 Histórico de narrativas")

    if not HISTORY_PATH.exists():
        st.warning("Sem narrative_history.json.")
        st.stop()

    history = json.loads(HISTORY_PATH.read_text())

    rows = []
    for narrativa, pontos in history.items():
        if not pontos:
            continue

        scores = [p.get("score", 0) for p in pontos]
        rows.append({
            "Narrativa": narrativa,
            "Score atual": scores[-1],
            "Score médio": round(sum(scores) / len(scores), 1),
            "Score máximo": max(scores),
            "Leituras": len(scores),
            "Variação": round(scores[-1] - scores[0], 1),
        })

 with tab7:

    st.subheader("🕵️ Wallet Discovery")

    if wallet_discovery:
        st.dataframe(
            pd.DataFrame(wallet_discovery),
            use_container_width=True
        )
    else:
        st.info("Nenhuma carteira descoberta ainda.")   df_hist = pd.DataFrame(rows)

    if df_hist.empty:
        st.warning("Histórico vazio.")
        st.stop()

    df_hist = df_hist.sort_values("Score atual", ascending=False)
    st.dataframe(df_hist, use_container_width=True)

    narrativa_escolhida = st.selectbox(
        "Escolha uma narrativa para ver evolução",
        df_hist["Narrativa"].tolist()
    )

    pontos = history[narrativa_escolhida]

    chart_df = pd.DataFrame([
        {"data": p.get("data"), "score": p.get("score", 0)}
        for p in pontos
    ])

    chart_df["data"] = pd.to_datetime(chart_df["data"])
    st.line_chart(chart_df, x="data", y="score")
