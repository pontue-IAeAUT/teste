import streamlit as st
import sqlite3
import uuid
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Automação & IA – ROI-ômetro",
    page_icon="📈",
    layout="wide",
)

# ── Custom CSS (Pontue brand colours) ────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;600;700&family=JetBrains+Mono:wght@700;800&display=swap');

  :root {
    --purple: #38017b;
    --magenta: #cf007f;
    --bg: #fbfbfb;
  }

  html, body, [class*="css"] { font-family: 'Roboto Slab', sans-serif; }

  /* Header */
  .roi-header {
    background: var(--purple);
    color: white;
    padding: 1.25rem 2rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .roi-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
  .roi-header p  { margin: 0; opacity: .7; font-size: .85rem; }

  /* Ticker cards */
  .ticker-card {
    background: white;
    border: 1px solid rgba(56,1,123,.12);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    border-top: 4px solid var(--magenta);
    margin-bottom: 1rem;
  }
  .ticker-label { font-size: .75rem; text-transform: uppercase; letter-spacing: .08em; color: rgba(56,1,123,.7); font-weight: 600; margin-bottom: .5rem; }
  .ticker-value { font-family: 'JetBrains Mono', monospace; font-size: 2.8rem; font-weight: 800; color: var(--magenta); line-height: 1; }
  .ticker-prefix { font-size: 1.4rem; color: rgba(56,1,123,.5); font-weight: 700; }

  /* Section cards */
  .section-card {
    background: white;
    border: 1px solid rgba(56,1,123,.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  .section-title { font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--purple); margin-bottom: 1rem; }

  /* Area row */
  .area-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: .6rem 0;
    border-bottom: 1px solid rgba(56,1,123,.07);
  }
  .area-badge { width: 36px; height: 36px; border-radius: 50%; background: #fbfbfb; border: 1px solid rgba(56,1,123,.12);
                display: inline-flex; align-items: center; justify-content: center; font-size: .7rem; font-weight: 700; color: var(--purple); }
  .area-name  { font-weight: 600; font-size: .9rem; color: var(--purple); }
  .area-count { font-size: .75rem; color: rgba(56,1,123,.6); }
  .area-roi   { font-family: 'JetBrains Mono', monospace; font-weight: 800; color: var(--magenta); font-size: 1rem; }
  .area-return{ font-family: 'JetBrains Mono', monospace; font-size: .75rem; color: var(--magenta); }

  /* Project card */
  .proj-card {
    background: white;
    border: 1px solid rgba(56,1,123,.1);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: .9rem;
  }
  .proj-badge {
    display: inline-block;
    padding: .2rem .65rem;
    border-radius: 999px;
    font-size: .72rem;
    font-weight: 600;
    background: rgba(56,1,123,.07);
    color: var(--purple);
    margin-right: .4rem;
    margin-bottom: .5rem;
  }
  .proj-badge.magenta { background: rgba(207,0,127,.1); color: var(--magenta); }
  .proj-name  { font-size: 1.05rem; font-weight: 700; color: var(--purple); margin: .2rem 0 .5rem; }
  .proj-summary { font-size: .85rem; color: rgba(56,1,123,.75); margin-bottom: 1rem; }
  .proj-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .5rem; border-top: 1px solid rgba(56,1,123,.08); padding-top: .9rem; }
  .stat-label { font-size: .72rem; color: rgba(56,1,123,.65); margin-bottom: .2rem; }
  .stat-value { font-family: 'JetBrains Mono', monospace; font-weight: 700; color: var(--magenta); font-size: .95rem; }

  /* Streamlit tweaks */
  div[data-testid="stForm"] { background: white; border: 1px solid rgba(56,1,123,.12); border-radius: 16px; padding: 1.5rem; }
  .stButton > button { background: var(--purple) !important; color: white !important; border-radius: 10px !important; font-weight: 600 !important; border: none !important; }
  .stButton > button:hover { background: #4a0299 !important; }
  label { font-weight: 600 !important; color: var(--purple) !important; }
  .stSelectbox > div > div, .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea {
    border-color: rgba(56,1,123,.25) !important;
    border-radius: 8px !important;
  }
  .stRadio > label { font-size: .9rem !important; }
  h2, h3 { color: var(--purple) !important; }
</style>
""", unsafe_allow_html=True)

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = "roi.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area TEXT NOT NULL,
                summary TEXT NOT NULL,
                resultType TEXT NOT NULL,
                previousHours REAL,
                previousHourlyRate REAL,
                currentHours REAL,
                currentHourlyRate REAL,
                profit REAL,
                implementationHours REAL NOT NULL,
                implementationHourlyRate REAL NOT NULL,
                extraCosts REAL NOT NULL,
                returnAmount REAL NOT NULL,
                costAmount REAL NOT NULL,
                roi REAL NOT NULL,
                createdAt INTEGER NOT NULL
            )
        """)

def load_projects():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY createdAt DESC").fetchall()
    return [dict(r) for r in rows]

def save_project(p: dict, project_id: str | None = None):
    with get_db() as conn:
        if project_id:
            conn.execute("""
                UPDATE projects SET
                  name=:name, area=:area, summary=:summary, resultType=:resultType,
                  previousHours=:previousHours, previousHourlyRate=:previousHourlyRate,
                  currentHours=:currentHours, currentHourlyRate=:currentHourlyRate,
                  profit=:profit, implementationHours=:implementationHours,
                  implementationHourlyRate=:implementationHourlyRate, extraCosts=:extraCosts,
                  returnAmount=:returnAmount, costAmount=:costAmount, roi=:roi
                WHERE id=:id
            """, {**p, "id": project_id})
        else:
            pid = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO projects VALUES (
                  :id,:name,:area,:summary,:resultType,:previousHours,:previousHourlyRate,
                  :currentHours,:currentHourlyRate,:profit,:implementationHours,
                  :implementationHourlyRate,:extraCosts,:returnAmount,:costAmount,:roi,:createdAt
                )
            """, {**p, "id": pid, "createdAt": int(datetime.now().timestamp() * 1000)})

def delete_project(project_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (project_id,))

# ── ROI calculation ────────────────────────────────────────────────────────────
def calculate_roi(data: dict) -> dict:
    ENCARGOS = 1.7
    if data["resultType"] == "Economia":
        prev_spend = data["previousHours"] * (data["previousHourlyRate"] * ENCARGOS)
        curr_spend = data["currentHours"] * (data["currentHourlyRate"] * ENCARGOS)
        monthly_return = prev_spend - curr_spend
    else:
        monthly_return = data["profit"]

    return_amount = monthly_return * 12
    cost_amount = (data["implementationHours"] * data["implementationHourlyRate"] * ENCARGOS) + (data["extraCosts"] * 12)
    roi = ((return_amount - cost_amount) / cost_amount * 100) if cost_amount > 0 else (100 if return_amount > 0 else 0)

    return {**data, "returnAmount": return_amount, "costAmount": cost_amount, "roi": roi}

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_brl(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(val: float) -> str:
    return f"{val:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")

AREAS = ["Tech", "Relacional", "Pedagógico", "RH", "Financeiro"]

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()

if "editing" not in st.session_state:
    st.session_state.editing = None
if "show_form" not in st.session_state:
    st.session_state.show_form = False

projects = load_projects()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="roi-header">
  <div style="background:rgba(255,255,255,.15);padding:.6rem;border-radius:10px;font-size:1.4rem">📈</div>
  <div>
    <h1>Automação &amp; IA – ROI-ômetro</h1>
    <p>Acompanhamento de Retorno sobre Investimento</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Global stats ──────────────────────────────────────────────────────────────
total_return = sum(p["returnAmount"] for p in projects)
total_cost   = sum(p["costAmount"]   for p in projects)
global_roi   = ((total_return - total_cost) / total_cost * 100) if total_cost > 0 else (100 if total_return > 0 else 0)

left_col, right_col = st.columns([5, 7], gap="large")

# ── LEFT COLUMN ───────────────────────────────────────────────────────────────
with left_col:
    # Tickers
    st.markdown(f"""
    <div class="ticker-card">
      <div class="ticker-label">Valor Total Gerado ao Ano (Economia + Lucro)</div>
      <div><span class="ticker-prefix">R$</span>
           <span class="ticker-value"> {total_return:,.2f}".replace(",","X").replace(".","," ).replace("X",".")</span>
      </div>
    </div>
    """.replace(
        f' {total_return:,.2f}".replace(",","X").replace(".","," ).replace("X",".")',
        f' {fmt_brl(total_return).replace("R$ ","")}'
    ), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ticker-card">
      <div class="ticker-label">ROI Global Anual da Empresa</div>
      <div><span class="ticker-value">{fmt_pct(global_roi)}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Area breakdown
    stats_by_area = []
    for area in AREAS:
        ap = [p for p in projects if p["area"] == area]
        ar = sum(p["returnAmount"] for p in ap)
        ac = sum(p["costAmount"]   for p in ap)
        roi_a = ((ar - ac) / ac * 100) if ac > 0 else (100 if ar > 0 else 0)
        stats_by_area.append({"area": area, "count": len(ap), "totalReturn": ar, "roi": roi_a})

    stats_by_area.sort(key=lambda x: x["roi"], reverse=True)

    rows_html = ""
    for s in stats_by_area:
        abbr = s["area"][:2].upper()
        rows_html += f"""
        <div class="area-row">
          <div style="display:flex;align-items:center;gap:.75rem">
            <span class="area-badge">{abbr}</span>
            <div>
              <div class="area-name">{s['area']}</div>
              <div class="area-count">{s['count']} projeto{'s' if s['count'] != 1 else ''}</div>
            </div>
          </div>
          <div style="text-align:right">
            <div class="area-roi">{fmt_pct(s['roi'])}</div>
            <div class="area-return">{fmt_brl(s['totalReturn'])}</div>
          </div>
        </div>"""

    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">ROI Anual por Área</div>
      {rows_html}
    </div>
    """, unsafe_allow_html=True)

    # Share button (Outlook mailto)
    if projects:
        body_lines = [
            "Olá equipe,\n\nAqui estão os resultados atualizados do ROI-ômetro da Pontue:\n",
            f"💰 Valor Total Gerado ao Ano: {fmt_brl(total_return)}",
            f"📈 ROI Global Anual da Empresa: {fmt_pct(global_roi)}\n",
            "Resumo Anual por Área:",
        ]
        for s in stats_by_area:
            body_lines.append(f"- {s['area']}: {fmt_pct(s['roi'])} ({fmt_brl(s['totalReturn'])} em {s['count']} projetos)")

        import urllib.parse
        emails = "fernandocandiani@pontue.com.br;brunaleal@pontue.com.br;liviatoledo@pontue.com.br;crismiura@pontue.com.br;jessicaangeli@pontue.com.br"
        subject = urllib.parse.quote("Atualização do ROI-ômetro Pontue")
        body    = urllib.parse.quote("\n".join(body_lines))
        outlook_url = f"https://outlook.cloud.microsoft/mail/deeplink/compose?to={emails}&subject={subject}&body={body}"

        st.markdown(f"""
        <div style="margin-top:1rem">
          <a href="{outlook_url}" target="_blank"
             style="display:inline-block;background:#38017b;color:white;padding:.7rem 1.4rem;
                    border-radius:10px;text-decoration:none;font-weight:600;font-size:.88rem;">
            ✉️ Compartilhar via Outlook
          </a>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT COLUMN ──────────────────────────────────────────────────────────────
with right_col:

    # ── Add / Edit button ──
    editing = st.session_state.editing
    if not editing:
        if st.button("➕ Registrar novo projeto", use_container_width=True):
            st.session_state.show_form = not st.session_state.show_form
            st.rerun()

    # ── Project form ──────────────────────────────────────────────────────────
    show_form = st.session_state.show_form or editing is not None

    if show_form:
        ed = editing  # may be None (new) or a project dict
        form_title = "✏️ Editar projeto" if ed else "🧮 Registrar novo projeto"

        with st.form("project_form", clear_on_submit=True):
            st.markdown(f"### {form_title}")

            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Nome do projeto", value=ed["name"] if ed else "", placeholder="Ex: Automação de Relatórios")
            with c2:
                area = st.selectbox("Área", AREAS, index=AREAS.index(ed["area"]) if ed else 0)

            summary = st.text_area("Resumo do projeto (máx. 130 palavras)",
                                   value=ed["summary"] if ed else "",
                                   placeholder="Descreva brevemente o projeto e seu impacto...",
                                   height=90)

            result_type = st.radio("Tipo de resultado",
                                   ["Economia (redução de custos)", "Lucro (geração de receita)"],
                                   index=0 if (not ed or ed["resultType"] == "Economia") else 1,
                                   horizontal=True)
            is_economia = result_type.startswith("Economia")

            st.markdown("---")
            if is_economia:
                st.markdown("**📊 Dados de economia**")
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.markdown("*Gasto mensal anterior*")
                    prev_h_val = ed["previousHours"] if ed else 0.0
                    prev_h = st.number_input("Horas mensais (anterior)", min_value=0.0, step=0.5, value=float(prev_h_val or 0))
                    prev_r_val = ed["previousHourlyRate"] if ed else 0.0
                    prev_r = st.number_input("Valor hora colaborador – anterior (R$)", min_value=0.0, step=0.01, value=float(prev_r_val or 0))
                with ec2:
                    st.markdown("*Gasto mensal atual*")
                    curr_h_val = ed["currentHours"] if ed else 0.0
                    curr_h = st.number_input("Horas mensais (atual)", min_value=0.0, step=0.5, value=float(curr_h_val or 0))
                    curr_r_val = ed["currentHourlyRate"] if ed else 0.0
                    curr_r = st.number_input("Valor hora colaborador – atual (R$)", min_value=0.0, step=0.01, value=float(curr_r_val or 0))
                st.caption("ℹ️ O cálculo adiciona 70% de encargos ao valor da hora.")
                profit = 0.0
            else:
                st.markdown("**💰 Dados de lucro**")
                profit_val = ed["profit"] if ed else 0.0
                profit = st.number_input("Lucro mensal obtido com a solução (R$)", min_value=0.0, step=0.01, value=float(profit_val or 0))
                prev_h = prev_r = curr_h = curr_r = 0.0

            st.markdown("---")
            st.markdown("**🔧 Custos de implementação**")
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                impl_h_val = ed["implementationHours"] if ed else 0.0
                impl_h = st.number_input("Horas gastas na implementação", min_value=0.0, step=0.5, value=float(impl_h_val or 0))
            with ic2:
                impl_r_val = ed["implementationHourlyRate"] if ed else 0.0
                impl_r = st.number_input("Valor hora responsável (R$)", min_value=0.0, step=0.01, value=float(impl_r_val or 0))
            with ic3:
                extra_val = ed["extraCosts"] if ed else 0.0
                extra = st.number_input("Custos mensais extras (R$)", min_value=0.0, step=0.01, value=float(extra_val or 0))
            st.caption("ℹ️ O cálculo adiciona 70% de encargos ao valor da hora do responsável.")

            fc1, fc2 = st.columns(2)
            with fc1:
                cancelled = st.form_submit_button("Cancelar", use_container_width=True)
            with fc2:
                submitted = st.form_submit_button(
                    "💾 Atualizar projeto" if ed else "💾 Salvar projeto e atualizar ROI",
                    use_container_width=True
                )

            if cancelled:
                st.session_state.editing = None
                st.session_state.show_form = False
                st.rerun()

            if submitted and name.strip():
                payload = calculate_roi({
                    "name": name.strip(),
                    "area": area,
                    "summary": summary.strip(),
                    "resultType": "Economia" if is_economia else "Lucro",
                    "previousHours": prev_h,
                    "previousHourlyRate": prev_r,
                    "currentHours": curr_h,
                    "currentHourlyRate": curr_r,
                    "profit": profit,
                    "implementationHours": impl_h,
                    "implementationHourlyRate": impl_r,
                    "extraCosts": extra,
                })
                save_project(payload, project_id=ed["id"] if ed else None)
                st.session_state.editing = None
                st.session_state.show_form = False
                st.rerun()

    # ── Project list ──────────────────────────────────────────────────────────
    if projects:
        st.markdown("### 📋 Histórico de Projetos")
        for p in projects:
            result_badge_cls = "proj-badge" if p["resultType"] == "Economia" else "proj-badge magenta"
            trend = "📈" if p["roi"] >= 0 else "📉"

            st.markdown(f"""
            <div class="proj-card">
              <span class="proj-badge">{p['area']}</span>
              <span class="{result_badge_cls}">{p['resultType']}</span>
              <div class="proj-name">{p['name']}</div>
              <div class="proj-summary">{p['summary']}</div>
              <div class="proj-stats">
                <div><div class="stat-label">Retorno (Anual)</div><div class="stat-value">{fmt_brl(p['returnAmount'])}</div></div>
                <div><div class="stat-label">Custo (Anual)</div><div class="stat-value">{fmt_brl(p['costAmount'])}</div></div>
                <div><div class="stat-label">ROI (Anual)</div><div class="stat-value">{trend} {fmt_pct(p['roi'])}</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2, _ = st.columns([1, 1, 5])
            with btn_col1:
                if st.button("✏️ Editar", key=f"edit_{p['id']}"):
                    st.session_state.editing = p
                    st.session_state.show_form = True
                    st.rerun()
            with btn_col2:
                if st.button("🗑️ Excluir", key=f"del_{p['id']}"):
                    delete_project(p["id"])
                    st.rerun()
    else:
        st.info("Nenhum projeto registrado ainda. Clique em **Registrar novo projeto** para começar!")
