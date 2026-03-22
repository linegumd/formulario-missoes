import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Oferta de Dons e Serviços – IP Redenção",
    page_icon="✝️",
    layout="centered",
)

# ── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 760px; }
    h1 { font-size: 1.6rem !important; }
    h3 { color: #0F6E56; font-size: 1rem !important; border-bottom: 2px solid #E1F5EE; padding-bottom: 4px; }
    .stCheckbox label { font-size: 0.9rem; }
    .tag-presencial  { background:#E1F5EE; color:#0F6E56; padding:1px 7px; border-radius:10px; font-size:0.7rem; margin-left:4px; }
    .tag-distancia   { background:#FEF3C7; color:#92400E; padding:1px 7px; border-radius:10px; font-size:0.7rem; margin-left:4px; }
    .tag-ambos       { background:#EDE9FE; color:#5B21B6; padding:1px 7px; border-radius:10px; font-size:0.7rem; margin-left:4px; }
    .info-box { background:#E1F5EE; border-radius:8px; padding:10px 14px; font-size:0.82rem; color:#085041; margin-bottom:1rem; }
    footer { display:none; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.image("logoIPR.png", width=400)
st.title("Oferta de Dons e Serviços aos Missionários")
st.markdown(
    "Registre os dons e serviços que você pode oferecer aos missionários e suas "
    "famílias quando estiverem em Brasília ou à distância. "
    "Sua participação é uma expressão preciosa da vida em comunidade."
)
st.divider()

# ── Funções auxiliares ───────────────────────────────────────────────────────
def checkboxes(items: list[tuple[str, str]], prefix: str) -> list[str]:
    """Renderiza checkboxes e retorna lista dos marcados."""
    cols = st.columns(2)
    selecionados = []
    for i, (label, tag) in enumerate(items):
        with cols[i % 2]:
            tag_html = f'<span class="tag-{tag}">{tag}</span>' if tag else ""
            checked = st.checkbox(label, key=f"{prefix}_{i}")
            if checked:
                selecionados.append(label)
    return selecionados

def salvar_no_sheets(dados: dict) -> bool:
    """Salva os dados no Google Sheets via Service Account."""
    try:
        # Carrega credenciais do st.secrets (configurado no Streamlit Cloud)
        creds_dict = st.secrets["gcp_service_account"]
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)

        # Abre a planilha pelo nome (deve estar compartilhada com o e-mail da service account)
        sheet = client.open(st.secrets["sheets"]["nome_planilha"]).sheet1

        # Cabeçalhos (cria se a planilha estiver vazia)
        if sheet.row_count == 0 or sheet.cell(1, 1).value is None:
            sheet.append_row(list(dados.keys()))

        sheet.append_row(list(dados.values()))
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# ────────────────────────────────────────────────────────────────────────────
# FORMULÁRIO
# ────────────────────────────────────────────────────────────────────────────
with st.form("form_missionarios", clear_on_submit=True):

    # ── 1. Dados pessoais ────────────────────────────────────────────────────
    st.markdown("### 👤 Seus dados")
    c1, c2 = st.columns(2)
    nome      = c1.text_input("Nome completo *")
    whatsapp  = c2.text_input("Telefone / WhatsApp *")
    c3, c4 = st.columns(2)
    email     = c3.text_input("E-mail")
    celula    = c4.text_input("Igreja")

    # ── 2. Saúde e bem-estar ─────────────────────────────────────────────────
    st.markdown("### 🏥 Saúde e bem-estar")
    saude_itens = [
        ("Consulta odontológica",              "presencial"),
        ("Tratamento odontológico",            "presencial"),
        ("Consulta médica",                    "presencial"),
        ("Consulta por telemedicina",          "distância"),
        ("Psicologia / aconselhamento",        "ambos"),
        ("Fisioterapia",                       "presencial"),
        ("Nutrição / orientação alimentar",    "ambos"),
        ("Enfermagem / cuidados básicos",      "presencial"),
        ("Farmacêutico / orientação de medicamentos", "ambos"),
        ("Outro serviço de saúde",             ""),
    ]
    saude_cols = st.columns(2)
    saude_sel = []
    for i, (label, tag) in enumerate(saude_itens):
        with saude_cols[i % 2]:
            if st.checkbox(label, key=f"saude_{i}"):
                saude_sel.append(label)
    saude_obs = st.text_input("Especialidade ou observação (saúde)", placeholder="Ex: ortopedia, pediatria...")

    # ── 3. Educação e idiomas ────────────────────────────────────────────────
    st.markdown("### 📚 Educação e idiomas")
    educ_itens = [
        ("Reforço escolar – educação infantil",  "ambos"),
        ("Reforço escolar – ensino fundamental", "ambos"),
        ("Reforço escolar – ensino médio",       "ambos"),
        ("Aulas de inglês",                      "ambos"),
        ("Aulas de espanhol",                    "ambos"),
        ("Português para estrangeiros",          "ambos"),
        ("Aulas de outro idioma",                "ambos"),
        ("Apoio em redação / escrita",           "ambos"),
        ("Apoio pedagógico / homeschooling",     "ambos"),
        ("Cursos ou capacitação profissional",   "ambos"),
    ]
    educ_cols = st.columns(2)
    educ_sel = []
    for i, (label, tag) in enumerate(educ_itens):
        with educ_cols[i % 2]:
            if st.checkbox(label, key=f"educ_{i}"):
                educ_sel.append(label)
    educ_obs = st.text_input("Idioma(s) ou matérias que domina", placeholder="Ex: matemática, francês, física...")

    # ── 4. Hospedagem e acolhimento ──────────────────────────────────────────
    st.markdown("### 🏠 Hospedagem e acolhimento")
    hosp_itens = [
        ("Quarto em minha casa",               "presencial"),
        ("Casa disponível para estadia",       "presencial"),
        ("Sítio / chácara para descanso",      "presencial"),
        ("Apartamento / imóvel por temporada", "presencial"),
        ("Refeições / alimentação",            "presencial"),
        ("Transporte / carona em Brasília",    "presencial"),
        ("Cuidado de crianças (childcare)",    "presencial"),
        ("Companhia / apoio emocional",        "ambos"),
    ]
    hosp_cols = st.columns(2)
    hosp_sel = []
    for i, (label, tag) in enumerate(hosp_itens):
        with hosp_cols[i % 2]:
            if st.checkbox(label, key=f"hosp_{i}"):
                hosp_sel.append(label)
    hosp_obs = st.text_input("Capacidade (nº de pessoas) e período disponível", placeholder="Ex: 4 pessoas, disponível jan–fev")

    # ── 5. Serviços domésticos e práticos ────────────────────────────────────
    st.markdown("### 🍽️ Serviços domésticos e práticos")
    dom_itens = [
        ("Preparar refeições / marmitas",        "presencial"),
        ("Fazer bolo / doces / salgados",        "presencial"),
        ("Costura / arremendo de roupas",        "presencial"),
        ("Cabeleireiro / barbearia",             "presencial"),
        ("Reparos domésticos / elétrica",        "presencial"),
        ("Manutenção de computadores / celular", "ambos"),
        ("Compras e delivery",                   "presencial"),
        ("Orientação burocrática / documentos",  "ambos"),
    ]
    dom_cols = st.columns(2)
    dom_sel = []
    for i, (label, tag) in enumerate(dom_itens):
        with dom_cols[i % 2]:
            if st.checkbox(label, key=f"dom_{i}"):
                dom_sel.append(label)

    # ── 6. Assessoria jurídica, financeira e administrativa ─────────────────
    st.markdown("### ⚖️ Assessoria jurídica, financeira e administrativa")
    jur_itens = [
        ("Advocacia / orientação jurídica",          "ambos"),
        ("Direito de família / documentação",        "ambos"),
        ("Direito trabalhista / previdenciário",     "ambos"),
        ("Contabilidade / declaração de IR",         "ambos"),
        ("Planejamento financeiro pessoal",          "ambos"),
        ("Abertura / gestão de MEI ou empresa",      "ambos"),
        ("Assessoria em investimentos",              "ambos"),
        ("Auxílio com visto / imigração",            "ambos"),
        ("Tradução juramentada de documentos",       "ambos"),
        ("Gestão de bens / imóveis à distância",     "distância"),
        ("Seguros (saúde, vida, residencial)",       "ambos"),
        ("Orientação em compras / importação",       "ambos"),
    ]
    jur_cols = st.columns(2)
    jur_sel = []
    for i, (label, tag) in enumerate(jur_itens):
        with jur_cols[i % 2]:
            if st.checkbox(label, key=f"jur_{i}"):
                jur_sel.append(label)
    jur_obs = st.text_input("Especialidade ou área de atuação (jurídica/financeira)", placeholder="Ex: direito tributário, planejamento de aposentadoria...")

    # ── 7. Apoio espiritual e pastoral ──────────────────────────────────────
    st.markdown("### 🙏 Apoio espiritual e pastoral")
    esp_itens = [
        ("Intercessão regular pelo missionário",    "distância"),
        ("Cartas / mensagens de encorajamento",     "distância"),
        ("Discipulado / mentoria",                  "ambos"),
        ("Apoio aos filhos em grupo de jovens",     "presencial"),
        ("Visita pastoral em campo (se viável)",    "presencial"),
        ("Grupos de oração online",                 "distância"),
    ]
    esp_cols = st.columns(2)
    esp_sel = []
    for i, (label, tag) in enumerate(esp_itens):
        with esp_cols[i % 2]:
            if st.checkbox(label, key=f"esp_{i}"):
                esp_sel.append(label)

    # ── 8. Disponibilidade ───────────────────────────────────────────────────
    st.markdown("### 📅 Disponibilidade")
    periodos_opcoes = [
        "Qualquer época do ano",
        "Férias (janeiro/fevereiro)",
        "Férias de julho",
        "Finais de semana",
        "Dias úteis",
        "Horário noturno",
        "Sob agendamento prévio",
    ]
    periodos = st.multiselect("Quando você pode oferecer esses serviços?", periodos_opcoes)
    modalidade = st.selectbox(
        "Modalidade preferida",
        ["", "Somente presencial (em Brasília)", "Somente à distância (online)", "Ambas as modalidades"],
    )

    # ── 9. Observações finais ─────────────────────────────────────────────────
    st.markdown("### 💬 Observações")
    obs_gerais = st.text_area(
        "Outros dons, serviços ou informações que deseja compartilhar",
        placeholder="Descreva livremente outros dons ou qualquer detalhe que julgue importante...",
        height=100,
    )

    # ── Consentimento ─────────────────────────────────────────────────────────
    st.markdown("")
    consentimento = st.checkbox(
        "Autorizo que a equipe de missões entre em contato comigo pelo WhatsApp/e-mail informados "
        "para coordenar os serviços. Meus dados serão usados exclusivamente pelo Serviço de Missões "
        "e Evangelismo da IP Redenção, conforme a LGPD."
    )

    st.markdown(
        '<div class="info-box">🔒 Seus dados serão usados exclusivamente pelo Serviço de Missões '
        "e Evangelismo da IP Redenção para coordenar o apoio aos missionários e suas famílias.</div>",
        unsafe_allow_html=True,
    )

    enviado = st.form_submit_button("✉️ Enviar minha oferta de serviços", use_container_width=True)

# ── Processamento após envio ──────────────────────────────────────────────────
if enviado:
    if not nome or not whatsapp:
        st.error("Por favor, preencha nome e WhatsApp — são campos obrigatórios.")
    elif not consentimento:
        st.warning("É necessário autorizar o contato para enviar o formulário.")
    else:
        todos_servicos = (
            saude_sel + educ_sel + hosp_sel + dom_sel + jur_sel + esp_sel
        )

        dados = {
            "Data/Hora":                datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Nome":                     nome,
            "WhatsApp":                 whatsapp,
            "E-mail":                   email,
            "Igreja":                       celula,
            "Saúde":                    "; ".join(saude_sel),
            "Saúde – obs":              saude_obs,
            "Educação/Idiomas":         "; ".join(educ_sel),
            "Educação – obs":           educ_obs,
            "Hospedagem":               "; ".join(hosp_sel),
            "Hospedagem – obs":         hosp_obs,
            "Serviços domésticos":      "; ".join(dom_sel),
            "Jurídico/Financeiro":      "; ".join(jur_sel),
            "Jurídico/Financeiro – obs": jur_obs,
            "Apoio espiritual":         "; ".join(esp_sel),
            "Disponibilidade":          "; ".join(periodos),
            "Modalidade":               modalidade,
            "Observações gerais":       obs_gerais,
            "Total de serviços":        len(todos_servicos),
        }

        ok = salvar_no_sheets(dados)

        if ok:
            st.balloons()
            st.success(
                "✅ **Obrigado pela sua oferta!** Que Deus abençoe imensamente o seu coração generoso. "
                "A equipe de missões entrará em contato em breve."
            )
            with st.expander("Ver resumo do que você ofereceu"):
                for categoria, servicos in [
                    ("Saúde", saude_sel), ("Educação/Idiomas", educ_sel),
                    ("Hospedagem", hosp_sel), ("Domésticos", dom_sel),
                    ("Jurídico/Financeiro", jur_sel), ("Espiritual", esp_sel),
                ]:
                    if servicos:
                        st.markdown(f"**{categoria}:** {', '.join(servicos)}")
