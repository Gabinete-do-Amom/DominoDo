# streamlit_app.py
# ===============================================
# Dominó Duplas — Placar mobile-first (UMA tela, sem scroll)
# -----------------------------------------------
# 1) pip install -r requirements.txt
# 2) streamlit run streamlit_app.py
# -----------------------------------------------
# Design "pedra de dominó": o board dos dois times é uma peça deitada —
# divisória central com pip losango, 1 pip no canto do Time A e 2 no do
# Time B. Numerais Anton (placar), Archivo no resto. Cabe inteiro em
# iPhone/Pixel (~390–412px) sem scroll; histórico em expander recolhido.
# ➖5 vermelho via classe st-key (melhor que :last-child, mas a Streamlit
# não garante o prefixo entre versões — conferir em upgrades).
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
      @import url('https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@500;600;700&display=swap');

      :root {
        --bg: #0c0e11;
        --tile: #171a20;
        --edge: #262c38;
        --bone: #e9e4d6;
        --bone-dim: #98938a;
        --red: #c22333;
      }

      /* Chrome do Streamlit fora — cada pixel vertical conta */
      header[data-testid="stHeader"], div[data-testid="stToolbar"],
      div[data-testid="stDecoration"], footer {display: none !important;}

      /* Mesa: vinheta + textura de pips bem sutil */
      div[data-testid="stAppViewContainer"] {
        background:
          radial-gradient(circle at 12px 12px,
            rgba(233,228,214,.022) 1.2px, transparent 1.7px),
          radial-gradient(120% 90% at 50% 0%, #13161c 0%, var(--bg) 60%);
        background-size: 26px 26px, auto;
      }

      div[data-testid="stMainBlockContainer"], section.main .block-container {
        padding: 0.65rem 0.6rem 0.85rem !important;
        max-width: 520px !important;
      }
      div[data-testid="stVerticalBlock"] {gap: 0.5rem !important;}

      /* Colunas lado a lado SEMPRE (o Streamlit empilha em viewport
         estreito via wrap + min-width) */
      div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.55rem !important;
      }
      div[data-testid="stColumn"], div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
        position: relative;
      }
      div[data-testid="stElementContainer"], .stButton {width: 100% !important;}

      /* ── A PEDRA: só o bloco horizontal que contém os placares ── */
      div[data-testid="stHorizontalBlock"]:has(.placar) {
        position: relative;
        background: linear-gradient(180deg, #1a1e26 0%, var(--tile) 100%);
        border: 1px solid var(--edge);
        border-radius: 18px;
        padding: 14px 12px 12px;
        box-shadow:
          inset 0 1px 0 rgba(255,255,255,.05),
          0 10px 28px rgba(0,0,0,.45);
      }
      /* divisória central da peça */
      div[data-testid="stHorizontalBlock"]:has(.placar)::before {
        content: ''; position: absolute; left: 50%; top: 12%; bottom: 12%;
        width: 1px;
        background: linear-gradient(180deg, transparent,
          var(--edge) 22%, var(--edge) 78%, transparent);
      }
      /* pip losango no centro da divisória */
      div[data-testid="stHorizontalBlock"]:has(.placar)::after {
        content: ''; position: absolute; left: 50%; top: 50%;
        width: 7px; height: 7px;
        transform: translate(-50%, -50%) rotate(45deg);
        background: var(--edge); border-radius: 1px;
      }
      /* pips de canto: 1 no Time A, 2 no Time B */
      div[data-testid="stHorizontalBlock"]:has(.placar)
        > div[data-testid="stColumn"]:first-child::before {
        content: ''; position: absolute; top: 2px; left: 6px;
        width: 5px; height: 5px; border-radius: 50%;
        background: rgba(233,228,214,.30);
      }
      div[data-testid="stHorizontalBlock"]:has(.placar)
        > div[data-testid="stColumn"]:last-child::before {
        content: ''; position: absolute; top: 2px; right: 6px;
        width: 5px; height: 5px; border-radius: 50%;
        background: rgba(233,228,214,.30);
        box-shadow: -9px 0 0 rgba(233,228,214,.30);
      }

      .titulo {
        font-family: 'Archivo', sans-serif; font-weight: 700;
        font-size: 12px; letter-spacing: .30em; text-transform: uppercase;
        color: var(--bone-dim); text-align: center; margin: 0;
      }

      .placar {
        font-family: 'Anton', sans-serif;
        font-size: clamp(54px, 16vw, 74px);
        font-variant-numeric: tabular-nums;
        color: var(--bone); line-height: 1.04; text-align: center;
        margin: 0; text-shadow: 0 3px 14px rgba(0,0,0,.55);
        animation: pop .22s ease;
      }
      @keyframes pop {
        from {transform: scale(.93); opacity: .55;}
        to   {transform: scale(1);   opacity: 1;}
      }

      /* nomes dos times */
      div[data-baseweb="input"] {
        background: #10141a !important;
        border-radius: 10px !important;
      }
      div[data-baseweb="input"] input {
        text-align: center; padding: .32rem .4rem !important;
        font-family: 'Archivo', sans-serif !important;
        font-weight: 600 !important; font-size: 14px !important;
        color: var(--bone-dim) !important;
      }

      /* chips de pontuação */
      .stButton > button {
        width: 100% !important;
        min-height: 46px !important;
        padding: 4px 6px !important;
        font-family: 'Archivo', sans-serif !important;
        font-weight: 600 !important; font-size: 17px !important;
        color: var(--bone) !important;
        background: #1d232d !important;
        border: 1px solid var(--edge) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.045),
                    0 2px 6px rgba(0,0,0,.35);
        transition: transform .08s ease, background .15s ease;
      }
      .stButton > button:active {transform: scale(.96); background: #242b37 !important;}

      /* ➖5: chip de perigo */
      .st-key-sub_A_5 button, .st-key-sub_B_5 button {
        background: linear-gradient(180deg, #c22333, #9d1424) !important;
        border-color: rgba(255,120,130,.25) !important;
        color: #fff !important;
        text-shadow: 0 1px 2px rgba(0,0,0,.35);
      }

      /* zerar: fantasma */
      .st-key-zerar button {
        background: transparent !important;
        border: 1px dashed var(--edge) !important;
        color: var(--bone-dim) !important;
        font-weight: 500 !important; font-size: 14px !important;
        min-height: 40px !important;
        box-shadow: none;
      }

      /* histórico */
      div[data-testid="stExpander"] {
        border: 1px solid var(--edge); border-radius: 12px;
        background: #12151b; overflow: hidden;
      }
      div[data-testid="stExpander"] summary {
        padding: .45rem .7rem !important;
        font-family: 'Archivo', sans-serif;
        color: var(--bone-dim) !important; font-size: 14px;
      }

      /* toast embaixo, nunca por cima do placar */
      div[data-testid="stToast"] {
        top: auto !important; bottom: 14px !important;
      }
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
                             label_visibility="collapsed")
        st.session_state.team_names[team] = name.strip() or f"Time {team}"

        st.markdown(f"<div class='placar'>{st.session_state.totais[team]}</div>",
                    unsafe_allow_html=True)

        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.button("+5", key=f"add_{team}_5", on_click=somar, args=(team, 5))
        with r1c2:
            st.button("+10", key=f"add_{team}_10", on_click=somar, args=(team, 10))
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.button("+15", key=f"add_{team}_15", on_click=somar, args=(team, 15))
        with r2c2:
            st.button("+20", key=f"add_{team}_20", on_click=somar, args=(team, 20))
        st.button("−5", key=f"sub_{team}_5", on_click=subtrair5, args=(team,))


painel_time("A", left)
painel_time("B", right)

st.button("Zerar placares", key="zerar", on_click=zerar)

with st.expander(f"Histórico da partida ({len(st.session_state.hist_all)})",
                 expanded=False, key="hist_expander"):
    if not st.session_state.hist_all:
        st.caption("Sem ações registradas ainda.")
    else:
        df_all = pd.DataFrame(st.session_state.hist_all)
        cols = [c for c in ("timestamp", "time", "delta", "total_resultante")
                if c in df_all.columns]
        st.dataframe(df_all[cols], hide_index=True,
                     height=min(300, 60 + 35 * len(df_all)))
