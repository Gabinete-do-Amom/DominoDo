# streamlit_app.py
# ===============================================
# Dominó Duplas — Placar mobile-first (UMA tela, sem scroll)
# -----------------------------------------------
# 1) pip install -r requirements.txt
# 2) streamlit run streamlit_app.py
# -----------------------------------------------
# - Cabe inteiro numa tela de iPhone/Pixel (~390–412px de largura)
# - Times LADO A LADO (colunas não colapsam no mobile)
# - Histórico único da partida em expander recolhido
# - ➖5 vermelho via classe st-key (estável, sem hack de :last-child)
# ===============================================

from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Placar Do Dominó", layout="centered",
                   initial_sidebar_state="collapsed")


def init_state():
    st.session_state.setdefault("team_names", {"A": "Time A", "B": "Time B"})
    st.session_state.setdefault("totais", {"A": 0, "B": 0})
    st.session_state.setdefault("hist", {"A": [], "B": []})
    # Histórico único da partida: {timestamp, time_id, time, delta, total_resultante}
    st.session_state.setdefault("hist_all", [])


init_state()

st.markdown(
    """
    <style>
      /* Chrome do Streamlit fora — cada pixel vertical conta */
      header[data-testid="stHeader"], div[data-testid="stToolbar"],
      div[data-testid="stDecoration"], footer {display: none !important;}

      div[data-testid="stMainBlockContainer"], section.main .block-container {
        padding: 0.5rem 0.55rem 0.75rem !important;
        max-width: 520px !important;
      }
      div[data-testid="stVerticalBlock"] {gap: 0.4rem !important;}

      /* Times lado a lado SEMPRE (por padrão o Streamlit empilha colunas
         em viewport estreito via wrap + min-width) */
      div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
      }
      div[data-testid="stColumn"], div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
      }

      .titulo {font-size: 20px; font-weight: 700; text-align: center; margin: 0;}
      .placar {font-size: clamp(42px, 13vw, 60px); font-weight: 800;
               line-height: 1.05; text-align: center; margin: 0;}

      div[data-baseweb="input"] input {
        text-align: center; padding: 0.3rem 0.4rem !important;
        font-size: 15px !important;
      }

      /* Botões: alvo de dedo (≥44px) mas compactos */
      .stButton, .stButton > button {
        width: 100% !important;
        min-height: 46px !important;
        padding: 4px 6px !important;
        font-size: 18px !important;
        border-radius: 12px !important;
      }
      /* ➖5 em vermelho */
      .st-key-sub_A_5 button, .st-key-sub_B_5 button {
        background: #b00020 !important; color: #fff !important;
        border-color: #b00020 !important;
      }
      div[data-testid="stExpander"] summary {padding: 0.4rem 0.6rem !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def registrar(team: str, delta: int):
    """Registra a ação nos históricos (por time e único da partida)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.hist[team].append({
        "timestamp": ts,
        "delta": f"{'+' if delta > 0 else ''}{delta}",
        "total_resultante": st.session_state.totais[team],
    })
    st.session_state.hist_all.append({
        "timestamp": ts,
        "time_id": team,
        "time": st.session_state.team_names[team],
        "delta": f"{'+' if delta > 0 else ''}{delta}",
        "total_resultante": st.session_state.totais[team],
    })


def somar(team: str, valor: int):
    st.session_state.totais[team] += valor
    registrar(team, valor)


def subtrair5(team: str):
    if st.session_state.totais[team] - 5 < 0:
        st.toast("O placar não pode ficar negativo.", icon="⚠️")
        return
    st.session_state.totais[team] -= 5
    registrar(team, -5)


def zerar():
    st.session_state.totais = {"A": 0, "B": 0}
    st.session_state.hist = {"A": [], "B": []}
    st.session_state.hist_all = []


st.markdown("<div class='titulo'>Placar do Dominó</div>", unsafe_allow_html=True)

left, right = st.columns(2)


def painel_time(team: str, col):
    with col:
        name = st.text_input(f"Nome do {team}",
                             value=st.session_state.team_names[team],
                             key=f"name_{team}",
                             help="Edite o nome do time",
                             label_visibility="collapsed")
        st.session_state.team_names[team] = name.strip() or f"Time {team}"

        st.markdown(f"<div class='placar'>{st.session_state.totais[team]}</div>",
                    unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.button("➕5", key=f"add_{team}_5", on_click=somar, args=(team, 5))
        with r1c2:
            st.button("➕10", key=f"add_{team}_10", on_click=somar, args=(team, 10))
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.button("➕15", key=f"add_{team}_15", on_click=somar, args=(team, 15))
        with r2c2:
            st.button("➕20", key=f"add_{team}_20", on_click=somar, args=(team, 20))
        st.button("➖5", key=f"sub_{team}_5", on_click=subtrair5, args=(team,))


painel_time("A", left)
painel_time("B", right)

st.button("🧹 Zerar placares", key="zerar", on_click=zerar)

with st.expander(f"📜 Histórico da partida ({len(st.session_state.hist_all)})",
                 expanded=False):
    if not st.session_state.hist_all:
        st.caption("Sem ações registradas ainda.")
    else:
        df_all = pd.DataFrame(st.session_state.hist_all)
        cols = [c for c in ("timestamp", "time", "delta", "total_resultante")
                if c in df_all.columns]
        st.dataframe(df_all[cols], hide_index=True,
                     height=min(300, 60 + 35 * len(df_all)))
