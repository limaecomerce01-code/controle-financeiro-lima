import streamlit as st
import pandas as pd
import re
import json
from pathlib import Path

st.set_page_config(page_title="Controle Financeiro", layout="wide")

RULES_PATH = Path("regras_classificacao.json")

GRUPOS_DISPONIVEIS = [
    "Entradas",
    "Mercadoria / insumos / embalagens",
    "Equipe / motoboy",
    "Fixos",
    "Taxas / sistemas / marketing",
    "Dívidas / impostos",
    "Pró-labore / retirada",
    "Investimento / manutenção",
    "Transferência interna",
    "Saldo",
    "Sem classificação",
]

DEFAULT_CATEGORY_GROUPS = {
    "Venda de produto": "Entradas",
    "Venda iFood": "Entradas",
    "Dinheiro": "Entradas",
    "Pix cliente": "Entradas",
    "Cartão": "Entradas",

    "Mercadoria": "Mercadoria / insumos / embalagens",
    "Carne": "Mercadoria / insumos / embalagens",
    "Bebidas": "Mercadoria / insumos / embalagens",
    "Embalagens": "Mercadoria / insumos / embalagens",
    "Gás": "Mercadoria / insumos / embalagens",
    "Frete e seguros sobre compras": "Mercadoria / insumos / embalagens",

    "Funcionário": "Equipe / motoboy",
    "Motoboy": "Equipe / motoboy",
    "Diarista": "Equipe / motoboy",

    "Aluguel": "Fixos",
    "Energia": "Fixos",
    "Internet": "Fixos",
    "Água": "Fixos",
    "Contabilidade": "Fixos",
    "Material de Expediente": "Fixos",
    "Serviços Assessorias/Consultorias": "Fixos",

    "Sistema / site": "Taxas / sistemas / marketing",
    "Marketing": "Taxas / sistemas / marketing",
    "Publicidade e Propaganda": "Taxas / sistemas / marketing",

    "Imposto": "Dívidas / impostos",
    "Cartão / dívida": "Dívidas / impostos",
    "Financiamento": "Dívidas / impostos",
    "Financiamento Moto": "Dívidas / impostos",
    "Empréstimo": "Dívidas / impostos",
    "Tarifas Bancárias": "Dívidas / impostos",
    "Juros Empréstimos": "Dívidas / impostos",

    "Pró-labore Renato": "Pró-labore / retirada",
    "Pró-labore Dayane": "Pró-labore / retirada",
    "Despesa pessoal": "Pró-labore / retirada",

    "Investimento / melhoria": "Investimento / manutenção",
    "Manutenção": "Investimento / manutenção",
    "Manutenção Veículos": "Investimento / manutenção",
    "Utensílios e Ferramentas": "Investimento / manutenção",
    "Manutenção Estrutura Física": "Investimento / manutenção",

    "Resgate caixinha PJ": "Transferência interna",
    "Aplicação caixinha PJ": "Transferência interna",
    "Transferência interna": "Transferência interna",

    "Saldo banco": "Saldo",
    "Saldo caixinha PJ": "Saldo",

    "Sem classificação": "Sem classificação",
}

DEFAULT_RULES = {
    "Venda iFood": ["ifood pago", "ifood"],
    "Venda de produto": ["pagseguro", "stone", "mercado pago", "pix recebido", "transferência recebida", "transferencia recebida"],
    "Mercadoria": ["atacadao", "atacadão", "assai", "assaí", "forte atacadista", "mercado", "supermercado", "comper", "servbem", "comprador"],
    "Carne": ["casa de carne", "açougue", "acougue", "guapore", "guaporé", "somente suinos", "somente suínos", "frigorifico", "frigorífico"],
    "Bebidas": ["bebida", "coca", "norsa", "ambev", "zero grau", "distribuidora"],
    "Embalagens": ["beira rio", "embalagem", "embalagens", "big embalagens", "m horizonte embalagens"],
    "Gás": ["valdeir", "gás", "gas", "botijao", "botijão"],
    "Motoboy": ["ygor", "motoboy", "entregador", "delivery"],
    "Funcionário": ["funcionario", "funcionário", "salario", "salário"],
    "Aluguel": ["aluguel", "up gestao", "up gestão"],
    "Energia": ["energisa"],
    "Internet": ["internet", "claro", "vivo", "tim", "cosmo telecom"],
    "Contabilidade": ["aline carvalho", "contabilidade", "contador"],
    "Sistema / site": ["cardapio web", "cardápio web", "sistema", "site", "creava", "canva"],
    "Marketing": ["facebook", "instagram", "meta ads", "tráfego", "trafego", "anuncio", "anúncio"],
    "Imposto": ["sefaz", "das", "imposto", "receita federal", "simples nacional"],
    "Cartão / dívida": ["dock", "andbank", "fatura", "votorantim", "cartao", "cartão"],
    "Financiamento Moto": ["yamaha"],
    "Empréstimo": ["empréstimo", "emprestimo", "resgate de empréstimo", "resgate de emprestimo"],
    "Investimento / melhoria": ["mercado livre", "mercadolivre", "casas bahia", "fritadeira", "celular", "obra", "gesso"],
    "Manutenção Veículos": ["helio", "hélio", "auto peças", "auto pecas", "mecanica", "mecânica"],
    "Utensílios e Ferramentas": ["parafusos", "ferramenta", "perfilados", "multiaco", "xomano"],
    "Despesa pessoal": ["disney", "netflix", "barbearia", "turismo", "viagem", "hotel", "restaurante", "wellhub"],
    "Pró-labore Renato": ["renato lucas", "renato"],
    "Pró-labore Dayane": ["dayane cristina", "dayane"],
    "Resgate caixinha PJ": ["resgate rdb", "resgate caixinha", "resgate da caixinha"],
    "Aplicação caixinha PJ": ["aplicação rdb", "aplicacao rdb", "aplicação caixinha", "aplicacao caixinha"],
}

LIMITS = {
    "Mercadoria / insumos / embalagens": 0.35,
    "Equipe / motoboy": 0.15,
    "Fixos": 0.10,
    "Taxas / sistemas / marketing": 0.05,
    "Dívidas / impostos": 0.05,
    "Pró-labore / retirada": 0.10,
    "Investimento / manutenção": 0.05,
}

INTERNAL_CATEGORIES = {
    "Resgate caixinha PJ",
    "Aplicação caixinha PJ",
    "Transferência interna",
    "Saldo banco",
    "Saldo caixinha PJ",
}

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]


def normalize_category(cat):
    c = str(cat).strip()
    mapa = {
        "Venda site": "Venda de produto",
        "Venda mesa": "Venda de produto",
        "Venda delivery": "Venda de produto",
        "Venda balcão": "Venda de produto",
        "Venda balcao": "Venda de produto",
        "Retirada Renato": "Pró-labore Renato",
        "Resgate RDB": "Resgate caixinha PJ",
        "Aplicação RDB": "Aplicação caixinha PJ",
        "Aplicacao RDB": "Aplicação caixinha PJ",
    }
    return mapa.get(c, c)


def init_state():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()

    if "rules" not in st.session_state:
        st.session_state.rules = load_rules()

    if "planos_contas" not in st.session_state:
        planos = []
        for plano, grupo in DEFAULT_CATEGORY_GROUPS.items():
            planos.append({
                "Plano de contas": plano,
                "Grupo interno": grupo,
                "Ativo": True,
            })
        st.session_state.planos_contas = pd.DataFrame(planos)

    if "bancos_config" not in st.session_state:
        st.session_state.bancos_config = [
            {"Banco": "Nubank PJ", "Tipo": "Conta corrente", "Saldo inicial": 0.0},
            {"Banco": "Caixinha PJ", "Tipo": "Caixinha PJ", "Saldo inicial": 0.0},
        ]


def load_rules():
    if RULES_PATH.exists():
        try:
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_RULES.copy()
    return DEFAULT_RULES.copy()


def save_rules(rules):
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)


def get_all_categories():
    if "planos_contas" not in st.session_state:
        return sorted(DEFAULT_CATEGORY_GROUPS.keys())

    planos = st.session_state.planos_contas.copy()

    if "Ativo" in planos.columns:
        planos = planos[planos["Ativo"] == True]

    cats = planos["Plano de contas"].dropna().astype(str).str.strip()
    cats = cats[cats != ""].unique().tolist()

    if "Sem classificação" not in cats:
        cats.append("Sem classificação")

    return sorted(cats)


def get_group(plano):
    plano = normalize_category(plano)

    if "planos_contas" in st.session_state:
        planos = st.session_state.planos_contas.copy()
        match = planos[planos["Plano de contas"].astype(str) == plano]
        if not match.empty:
            return str(match.iloc[0]["Grupo interno"])

    return DEFAULT_CATEGORY_GROUPS.get(plano, "Sem classificação")


def brl_to_float(text):
    if pd.isna(text):
        return 0.0
    if isinstance(text, (int, float)):
        return float(text)

    s = str(text).strip()
    if s == "":
        return 0.0

    negativo = "-" in s
    s = s.replace("R$", "").replace(" ", "")

    if "," in s:
        s = s.replace(".", "").replace(",", ".")

    s = re.sub(r"[^\d\.\-]", "", s)

    try:
        v = float(s)
        return -abs(v) if negativo else v
    except Exception:
        return 0.0


def money(v):
    try:
        v = float(v)
    except Exception:
        v = 0.0

    s = f"R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-{s}" if v < 0 else s


def normalize_text(s):
    return str(s).lower().strip()


def classify(desc, rules):
    d = normalize_text(desc)

    for category, keys in rules.items():
        for k in keys:
            if normalize_text(k) in d:
                return normalize_category(category)

    return "Sem classificação"


def parse_excel(file):
    df = pd.read_excel(file)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def parse_csv(file):
    try:
        df = pd.read_csv(file, sep=None, engine="python")
    except Exception:
        df = pd.read_csv(file, sep=";")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def parse_pdf(file):
    try:
        import pdfplumber
    except Exception:
        st.error("Para ler PDF, instale pdfplumber.")
        return pd.DataFrame()

    rows = []
    current_date = ""
    current_type = ""

    meses_num = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
        "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
        "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12",
    }

    def parse_date_token(day, mon, year="2026"):
        mon = mon.upper()
        return f"{day.zfill(2)}/{meses_num.get(mon, mon)}/{year}"

    skip_words = [
        "saldo do dia", "saldo final", "saldo inicial", "rendimento líquido",
        "rendimento liquido", "extrato gerado", "tem alguma dúvida",
        "caso a solução", "não nos responsabilizamos", "asseguramos",
        "nu financeira", "nu pagamentos", "cnpj", "agência", "agencia",
        "conta", "valores em r$", "movimentações", "movimentacoes",
        "total de depósitos", "total de depositos",
    ]

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            for raw_line in text.split("\n"):
                line = " ".join(raw_line.split()).strip()

                if not line:
                    continue

                low = line.lower()

                if any(w in low for w in skip_words):
                    continue

                m_header = re.match(
                    r"^(\d{2})\s+([A-ZÇ]{3})\s+(\d{4})\s+Total de (entradas|saídas|saidas)\s+([\+\-])\s*([\d\.]+,\d{2})$",
                    line,
                    re.I,
                )

                if m_header:
                    current_date = parse_date_token(
                        m_header.group(1),
                        m_header.group(2),
                        m_header.group(3),
                    )
                    current_type = "Entrada" if "entrada" in m_header.group(4).lower() else "Saída"
                    continue

                m_date_only = re.match(r"^(\d{2})\s+([A-ZÇ]{3})\s+(\d{4})", line, re.I)

                if m_date_only and "total de" not in low:
                    current_date = parse_date_token(
                        m_date_only.group(1),
                        m_date_only.group(2),
                        m_date_only.group(3),
                    )

                if "total de entradas" in low:
                    current_type = "Entrada"
                    continue

                if "total de saídas" in low or "total de saidas" in low:
                    current_type = "Saída"
                    continue

                m = re.search(r"(.+?)\s+(-?R?\$?\s*[\d\.]+,\d{2})$", line, re.I)

                if not m:
                    continue

                desc = m.group(1).strip()
                val = brl_to_float(m.group(2))

                if not desc or val == 0:
                    continue

                tipo = current_type

                if not tipo:
                    tipo = "Saída" if val < 0 else "Entrada"

                valor = abs(val) if tipo == "Entrada" else -abs(val)

                rows.append({
                    "Data": current_date,
                    "Descrição": desc,
                    "Valor": valor,
                    "Tipo": tipo,
                })

    return pd.DataFrame(rows)


def standardize_df(df, rules):
    data_col = None
    desc_col = None
    value_col = None
    plan_col = None

    for c in df.columns:
        lc = str(c).lower()

        if "data" in lc:
            data_col = c

        if (
            "descr" in lc or
            "lançamento" in lc or
            "lancamento" in lc or
            "histórico" in lc or
            "historico" in lc
        ):
            desc_col = c

        if "valor" in lc:
            value_col = c

        if "plano" in lc or "categoria" in lc:
            plan_col = c

    if desc_col is None:
        desc_col = df.columns[0]

    entrada_col = None
    saida_col = None

    for c in df.columns:
        lc = str(c).lower()
        if "entrada" in lc:
            entrada_col = c
        if "saída" in lc or "saida" in lc:
            saida_col = c

    if value_col is None and not (entrada_col or saida_col):
        for c in df.columns:
            vals = pd.to_numeric(df[c], errors="coerce")
            if vals.notna().sum() > 0:
                value_col = c
                break

    out = pd.DataFrame()
    out["Data"] = df[data_col] if data_col else ""
    out["Descrição"] = df[desc_col].astype(str)

    if entrada_col or saida_col:
        entradas_val = df[entrada_col].apply(brl_to_float) if entrada_col else 0
        saidas_val = df[saida_col].apply(brl_to_float) if saida_col else 0
        out["Valor"] = entradas_val - abs(saidas_val)
    else:
        out["Valor"] = df[value_col].apply(brl_to_float) if value_col else 0.0

    out["Tipo"] = out["Valor"].apply(lambda x: "Entrada" if x >= 0 else "Saída")
    out["Entrada"] = out["Valor"].apply(lambda x: x if x > 0 else 0.0)
    out["Saída"] = out["Valor"].apply(lambda x: abs(x) if x < 0 else 0.0)

    if plan_col:
        out["Plano de contas"] = df[plan_col].fillna("").astype(str)
        out["Plano de contas"] = out["Plano de contas"].replace("", "Sem classificação")
    else:
        out["Plano de contas"] = out["Descrição"].apply(lambda x: classify(x, rules))

    out["Plano de contas"] = out["Plano de contas"].apply(normalize_category)
    out["Grupo interno"] = out["Plano de contas"].apply(get_group)

    try:
        out["Data"] = pd.to_datetime(out["Data"], dayfirst=True, errors="coerce")
    except Exception:
        pass

    return out


def read_uploaded(file, rules):
    name = file.name.lower()

    if name.endswith(".xlsx") or name.endswith(".xls"):
        df = parse_excel(file)
    elif name.endswith(".csv"):
        df = parse_csv(file)
    elif name.endswith(".pdf"):
        df = parse_pdf(file)
    else:
        st.error("Formato não suportado. Use XLSX, XLS, CSV ou PDF.")
        return pd.DataFrame()

    if df.empty:
        return df

    return standardize_df(df, rules)


def calc_summary(df, meta, dias_abertos, lucro_pct):
    if df.empty:
        return {
            "entradas": 0.0,
            "saidas": 0.0,
            "lucro": 0.0,
            "meta_diaria": meta / max(dias_abertos, 1),
            "lucro_desejado": meta * lucro_pct / 100,
        }

    df_operacional = df[~df["Plano de contas"].isin(INTERNAL_CATEGORIES)].copy()

    entradas = float(df_operacional["Entrada"].sum())
    saidas = float(df_operacional["Saída"].sum())
    lucro = entradas - saidas

    return {
        "entradas": entradas,
        "saidas": saidas,
        "lucro": lucro,
        "meta_diaria": meta / max(dias_abertos, 1),
        "lucro_desejado": meta * lucro_pct / 100,
    }


def alert_table(df, meta):
    rows = []

    if df.empty:
        return pd.DataFrame()

    df_cost = df[
        (df["Tipo"] == "Saída") &
        (~df["Plano de contas"].isin(INTERNAL_CATEGORIES))
    ].copy()

    for group, pct in LIMITS.items():
        used = float(df_cost.loc[df_cost["Grupo interno"] == group, "Saída"].sum())
        limit = meta * pct
        diff = limit - used
        status = "OK" if diff >= 0 else "ESTOUROU"

        rows.append({
            "Grupo": group,
            "Limite ideal": limit,
            "Gasto atual": used,
            "Diferença": diff,
            "Status": status,
        })

    return pd.DataFrame(rows)


def get_month_name(dt):
    try:
        if pd.isna(dt):
            return "Sem data"
        return MESES[pd.to_datetime(dt).month - 1]
    except Exception:
        return "Sem data"


def calc_bancos(df, bancos_config, mes_saldos):
    rows = []
    saldo_inicial_total = 0.0
    saldo_final_total = 0.0

    if bancos_config is None:
        bancos_config = []

    for banco in bancos_config:
        nome = str(banco.get("Banco", "")).strip()
        tipo = str(banco.get("Tipo", "Conta corrente")).strip()

        try:
            saldo_inicial = float(banco.get("Saldo inicial", 0))
        except Exception:
            saldo_inicial = 0.0

        if not nome:
            continue

        entradas = 0.0
        saidas = 0.0

        if not df.empty:
            temp = df.copy()
            temp["Mês"] = temp["Data"].apply(get_month_name)
            temp = temp[temp["Mês"] == mes_saldos]

            if tipo == "Caixinha PJ":
                entradas += float(temp.loc[temp["Plano de contas"] == "Aplicação caixinha PJ", "Saída"].sum())
                saidas += float(temp.loc[temp["Plano de contas"] == "Resgate caixinha PJ", "Entrada"].sum())
                saidas += float(temp.loc[temp["Plano de contas"] == "Resgate caixinha PJ", "Saída"].sum())
            else:
                entradas += float(temp["Entrada"].sum())
                saidas += float(temp["Saída"].sum())

        saldo_final = saldo_inicial + entradas - saidas

        saldo_inicial_total += saldo_inicial
        saldo_final_total += saldo_final

        rows.append({
            "Mês": mes_saldos,
            "Banco": nome,
            "Tipo": tipo,
            "Saldo inicial": saldo_inicial,
            "Entradas": entradas,
            "Saídas": saidas,
            "Saldo final calculado": saldo_final,
        })

    saldos = pd.DataFrame(rows)

    resumo = pd.DataFrame([{
        "Mês": mes_saldos,
        "Saldo inicial total": saldo_inicial_total,
        "Saldo final total": saldo_final_total,
        "Resultado de caixa": saldo_final_total - saldo_inicial_total,
    }])

    return saldos, resumo


def build_dre(df, saldos_df=None):
    linhas = [
        "SALDO INICIAL BANCOS",
        "RECEITA BRUTA",
        "(+) Venda de produto",
        "(+) Venda iFood",
        "CUSTOS VARIÁVEIS",
        "Mercadoria / insumos / embalagens",
        "Equipe / motoboy",
        "MARGEM CONTRIBUIÇÃO",
        "% MARGEM CONTRIBUIÇÃO",
        "DESPESAS FIXAS",
        "Fixos",
        "Taxas / sistemas / marketing",
        "Dívidas / impostos",
        "Pró-labore / retirada",
        "Investimento / manutenção",
        "Sem classificação",
        "RESULTADO OPERACIONAL",
        "MOVIMENTAÇÃO CAIXINHA PJ",
        "Aplicação caixinha PJ",
        "Resgate caixinha PJ",
        "SALDO FINAL BANCOS",
        "RESULTADO DE CAIXA",
    ]

    dre = pd.DataFrame({"Plano de contas": linhas})

    for mes in MESES:
        dre[mes] = 0.0

    if not df.empty:
        temp = df.copy()
        temp["Mês"] = temp["Data"].apply(get_month_name)

        for mes in MESES:
            dmes = temp[temp["Mês"] == mes].copy()

            if dmes.empty:
                continue

            dmes_oper = dmes[~dmes["Plano de contas"].isin(INTERNAL_CATEGORIES)]

            venda_produto = float(dmes_oper.loc[dmes_oper["Plano de contas"] == "Venda de produto", "Entrada"].sum())
            venda_ifood = float(dmes_oper.loc[dmes_oper["Plano de contas"] == "Venda iFood", "Entrada"].sum())

            outras_entradas = float(
                dmes_oper.loc[
                    (dmes_oper["Tipo"] == "Entrada") &
                    (~dmes_oper["Plano de contas"].isin(["Venda de produto", "Venda iFood"])),
                    "Entrada"
                ].sum()
            )

            receita = venda_produto + venda_ifood + outras_entradas

            mercadoria = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Mercadoria / insumos / embalagens", "Saída"].sum())
            equipe = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Equipe / motoboy", "Saída"].sum())

            custos_var = mercadoria + equipe
            margem = receita - custos_var
            margem_pct = (margem / receita * 100) if receita else 0.0

            fixos = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Fixos", "Saída"].sum())
            taxas = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Taxas / sistemas / marketing", "Saída"].sum())
            dividas = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Dívidas / impostos", "Saída"].sum())
            prolabore = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Pró-labore / retirada", "Saída"].sum())
            investimento = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Investimento / manutenção", "Saída"].sum())
            sem_class = float(dmes_oper.loc[dmes_oper["Grupo interno"] == "Sem classificação", "Saída"].sum())

            despesas = fixos + taxas + dividas + prolabore + investimento + sem_class
            resultado = receita - custos_var - despesas

            aplicacao = float(dmes.loc[dmes["Plano de contas"] == "Aplicação caixinha PJ", "Saída"].sum())
            resgate = float(dmes.loc[dmes["Plano de contas"] == "Resgate caixinha PJ", "Entrada"].sum())
            resgate_saida = float(dmes.loc[dmes["Plano de contas"] == "Resgate caixinha PJ", "Saída"].sum())

            if resgate == 0 and resgate_saida > 0:
                resgate = resgate_saida

            valores = {
                "RECEITA BRUTA": receita,
                "(+) Venda de produto": venda_produto + outras_entradas,
                "(+) Venda iFood": venda_ifood,
                "CUSTOS VARIÁVEIS": custos_var,
                "Mercadoria / insumos / embalagens": mercadoria,
                "Equipe / motoboy": equipe,
                "MARGEM CONTRIBUIÇÃO": margem,
                "% MARGEM CONTRIBUIÇÃO": margem_pct,
                "DESPESAS FIXAS": despesas,
                "Fixos": fixos,
                "Taxas / sistemas / marketing": taxas,
                "Dívidas / impostos": dividas,
                "Pró-labore / retirada": prolabore,
                "Investimento / manutenção": investimento,
                "Sem classificação": sem_class,
                "RESULTADO OPERACIONAL": resultado,
                "MOVIMENTAÇÃO CAIXINHA PJ": resgate - aplicacao,
                "Aplicação caixinha PJ": aplicacao,
                "Resgate caixinha PJ": resgate,
            }

            for linha, valor in valores.items():
                dre.loc[dre["Plano de contas"] == linha, mes] = valor

    if saldos_df is not None and not saldos_df.empty:
        for _, row in saldos_df.iterrows():
            mes = row.get("Mês", "")

            if mes in MESES:
                saldo_inicial = float(row.get("Saldo inicial total", 0))
                saldo_final = float(row.get("Saldo final total", 0))

                dre.loc[dre["Plano de contas"] == "SALDO INICIAL BANCOS", mes] = saldo_inicial
                dre.loc[dre["Plano de contas"] == "SALDO FINAL BANCOS", mes] = saldo_final
                dre.loc[dre["Plano de contas"] == "RESULTADO DE CAIXA", mes] = saldo_final - saldo_inicial

    return dre


def style_money_df(df, pct_rows=None):
    if df.empty:
        return df

    formatted = df.copy()
    pct_rows = pct_rows or []

    for c in formatted.columns:
        if c == "Plano de contas":
            continue

        new_values = []

        for i, v in formatted[c].items():
            row_label = formatted.loc[i, "Plano de contas"] if "Plano de contas" in formatted.columns else None

            try:
                val = float(v)
            except Exception:
                new_values.append(v)
                continue

            if row_label in pct_rows:
                new_values.append(f"{val:.2f}%".replace(".", ","))
            else:
                new_values.append(money(val))

        formatted[c] = new_values

    return formatted


def make_excel_download(df):
    import io

    buffer = io.BytesIO()
    export_df = df.copy()

    if "Grupo interno" in export_df.columns:
        export_df = export_df.drop(columns=["Grupo interno"])

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df.to_excel(writer, index=False, sheet_name="Lancamentos")

    buffer.seek(0)

    return buffer


init_state()

st.title("🍔 Controle Financeiro Lima")
st.caption("Sistema para controlar restaurante, classificar extrato, acompanhar caixa e mirar lucro.")

with st.sidebar:
    st.header("Metas do mês")

    meta = st.number_input("Meta de faturamento do mês", min_value=0.0, value=55000.0, step=500.0)
    dias_abertos = st.number_input("Dias abertos no mês", min_value=1, value=26, step=1)
    lucro_pct = st.number_input("Lucro desejado (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)

    st.divider()

    st.header("Importar")
    uploaded = st.file_uploader("Importe extrato, fatura ou planilha", type=["pdf", "xlsx", "xls", "csv"])

    if uploaded:
        if st.button("Importar e classificar"):
            df_new = read_uploaded(uploaded, st.session_state.rules)

            if not df_new.empty:
                st.session_state.df = df_new
                st.success(f"Arquivo importado com {len(df_new)} lançamentos.")
            else:
                st.warning("Não encontrei lançamentos no arquivo.")

    st.divider()
    st.caption("Não suba extratos no GitHub. Use o GitHub só para o código.")

tabs = st.tabs([
    "Dashboard",
    "DRE Mensal",
    "Lançamentos",
    "Sem classificação",
    "Regras / Planos de contas",
    "Bancos / Saldos",
    "Exportar",
])

df = st.session_state.df.copy()

with tabs[0]:
    st.subheader("Dashboard")

    summary = calc_summary(df, meta, dias_abertos, lucro_pct)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas identificadas", money(summary["entradas"]))
    c2.metric("Saídas identificadas", money(summary["saidas"]))
    c3.metric("Resultado estimado", money(summary["lucro"]))
    c4.metric("Meta diária", money(summary["meta_diaria"]))

    st.divider()

    st.subheader("Alertas por categoria")

    alerts = alert_table(df, meta)

    if alerts.empty:
        st.info("Importe um arquivo para ver os alertas.")
    else:
        show_alerts = alerts.copy()

        for c in ["Limite ideal", "Gasto atual", "Diferença"]:
            show_alerts[c] = show_alerts[c].apply(money)

        st.dataframe(show_alerts, use_container_width=True, hide_index=True)

    st.divider()

    if not df.empty:
        st.subheader("Resumo por plano de contas")

        resumo = (
            df[~df["Plano de contas"].isin(INTERNAL_CATEGORIES)]
            .groupby("Plano de contas", as_index=False)
            .agg(Entradas=("Entrada", "sum"), Saídas=("Saída", "sum"))
        )

        resumo["Resultado"] = resumo["Entradas"] - resumo["Saídas"]

        show = resumo.copy()

        for c in ["Entradas", "Saídas", "Resultado"]:
            show[c] = show[c].apply(money)

        st.dataframe(show, use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("DRE Mensal")

    mes_dre = st.selectbox("Mês usado para saldos bancários", MESES, index=5)

    saldos_calc, saldos_resumo = calc_bancos(df, st.session_state.bancos_config, mes_dre)
    dre = build_dre(df, saldos_resumo)

    st.dataframe(
        style_money_df(dre, pct_rows=["% MARGEM CONTRIBUIÇÃO"]),
        use_container_width=True,
        hide_index=True,
    )

    st.caption("Resultado operacional mostra a operação. Resultado de caixa mostra se o dinheiro total dos bancos/caixinhas aumentou ou diminuiu.")

with tabs[2]:
    st.subheader("Lançamentos")

    if df.empty:
        st.info("Importe um arquivo para editar os lançamentos.")
    else:
        edit_df = df[["Data", "Descrição", "Tipo", "Entrada", "Saída", "Plano de contas"]].copy()

        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=False,
            column_config={
                "Plano de contas": st.column_config.SelectboxColumn(
                    "Plano de contas",
                    options=get_all_categories(),
                    required=True,
                ),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo",
                    options=["Entrada", "Saída"],
                    required=True,
                ),
                "Entrada": st.column_config.NumberColumn("Entrada", format="R$ %.2f"),
                "Saída": st.column_config.NumberColumn("Saída", format="R$ %.2f"),
            },
            disabled=["Data", "Descrição", "Entrada", "Saída"],
            key="editor_lancamentos",
        )

        if st.button("Salvar alterações dos lançamentos"):
            new_df = st.session_state.df.copy()

            for idx, row in edited.iterrows():
                cat = normalize_category(row["Plano de contas"])
                new_df.loc[idx, "Plano de contas"] = cat
                new_df.loc[idx, "Grupo interno"] = get_group(cat)

            st.session_state.df = new_df
            st.success("Alterações salvas.")

with tabs[3]:
    st.subheader("Sem classificação")

    if df.empty:
        st.info("Importe um arquivo primeiro.")
    else:
        mask = df["Plano de contas"].fillna("").eq("Sem classificação")
        sem = df[mask].copy()

        if sem.empty:
            st.success("Não há lançamentos sem classificação.")
        else:
            st.write(f"{len(sem)} lançamentos sem classificação.")

            sem_edit = sem[["Data", "Descrição", "Tipo", "Entrada", "Saída", "Plano de contas"]].copy()

            edited_sem = st.data_editor(
                sem_edit,
                use_container_width=True,
                hide_index=False,
                column_config={
                    "Plano de contas": st.column_config.SelectboxColumn(
                        "Plano de contas",
                        options=get_all_categories(),
                        required=True,
                    ),
                    "Entrada": st.column_config.NumberColumn("Entrada", format="R$ %.2f"),
                    "Saída": st.column_config.NumberColumn("Saída", format="R$ %.2f"),
                },
                disabled=["Data", "Descrição", "Tipo", "Entrada", "Saída"],
                key="editor_sem_classificacao",
            )

            if st.button("Salvar classificações"):
                new_df = st.session_state.df.copy()

                for idx, row in edited_sem.iterrows():
                    cat = normalize_category(row["Plano de contas"])
                    new_df.loc[idx, "Plano de contas"] = cat
                    new_df.loc[idx, "Grupo interno"] = get_group(cat)

                st.session_state.df = new_df
                st.success("Classificações salvas. Os itens classificados sairão dessa aba.")

with tabs[4]:
    st.subheader("Planos de contas")

    st.write("Aqui você pode adicionar, editar ou desativar os nomes que aparecem na classificação.")

    planos_editados = st.data_editor(
        st.session_state.planos_contas,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Plano de contas": st.column_config.TextColumn(
                "Plano de contas",
                required=True,
            ),
            "Grupo interno": st.column_config.SelectboxColumn(
                "Grupo interno",
                options=GRUPOS_DISPONIVEIS,
                required=True,
            ),
            "Ativo": st.column_config.CheckboxColumn(
                "Ativo",
                default=True,
            ),
        },
        key="editor_planos_contas",
    )

    if st.button("Salvar planos de contas"):
        planos_editados["Plano de contas"] = planos_editados["Plano de contas"].astype(str).str.strip()
        planos_editados = planos_editados[planos_editados["Plano de contas"] != ""]
        st.session_state.planos_contas = planos_editados
        st.success("Planos de contas salvos.")

    st.divider()

    st.subheader("Cadastro rápido de palavras-chave")

    st.write("Escolha um plano de contas e cole várias palavras-chave separadas por vírgula.")

    col1, col2 = st.columns([1, 2])

    with col1:
        plano_rapido = st.selectbox(
            "Escolha o plano de contas",
            options=get_all_categories(),
            key="plano_rapido_regras",
        )

    with col2:
        palavras_rapidas = st.text_area(
            "Palavras-chave",
            placeholder="Exemplo: açaí, atacadão, forte atacadista, supermercado, mercado",
            key="palavras_rapidas_regras",
        )

    if st.button("Adicionar palavras ao plano de contas"):
        if not palavras_rapidas.strip():
            st.warning("Digite pelo menos uma palavra-chave.")
        else:
            plano_rapido = normalize_category(plano_rapido)

            novas_palavras = [
                palavra.strip()
                for palavra in palavras_rapidas.split(",")
                if palavra.strip()
            ]

            if plano_rapido not in st.session_state.rules:
                st.session_state.rules[plano_rapido] = []

            adicionadas = 0
            repetidas = 0

            for palavra in novas_palavras:
                if palavra not in st.session_state.rules[plano_rapido]:
                    st.session_state.rules[plano_rapido].append(palavra)
                    adicionadas += 1
                else:
                    repetidas += 1

            save_rules(st.session_state.rules)

            st.success(
                f"{adicionadas} palavra(s) adicionada(s) em: {plano_rapido}. "
                f"{repetidas} já existiam."
            )

    st.divider()

    st.subheader("Regras cadastradas")

    st.write("Aqui você pode editar ou excluir palavras-chave manualmente.")

    rules_df_rows = []

    for cat, keys in st.session_state.rules.items():
        for key in keys:
            rules_df_rows.append(
                {
                    "Plano de contas": normalize_category(cat),
                    "Palavra-chave": key,
                }
            )

    rules_df = pd.DataFrame(rules_df_rows)

    edited_rules = st.data_editor(
        rules_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Plano de contas": st.column_config.SelectboxColumn(
                "Plano de contas",
                options=get_all_categories(),
                required=True,
            ),
            "Palavra-chave": st.column_config.TextColumn(
                "Palavra-chave",
                required=True,
            ),
        },
        key="rules_editor",
    )

    if st.button("Salvar regras editadas"):
        new_rules = {}

        for _, row in edited_rules.dropna().iterrows():
            cat = normalize_category(row["Plano de contas"])
            key = str(row["Palavra-chave"]).strip()

            if not key:
                continue

            new_rules.setdefault(cat, [])

            if key not in new_rules[cat]:
                new_rules[cat].append(key)

        st.session_state.rules = new_rules
        save_rules(new_rules)
        st.success("Regras salvas.")
with tabs[5]:
    st.subheader("Bancos / Saldos")

    st.write("Cadastre as contas que você quer acompanhar. Exemplo: Nubank PJ, Caixinha PJ, Caixa, Mercado Pago, Dinheiro em caixa.")

    bancos_df = pd.DataFrame(st.session_state.bancos_config)

    edited_bancos = st.data_editor(
        bancos_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Banco": st.column_config.TextColumn("Banco"),
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo",
                options=["Conta corrente", "Caixinha PJ", "Dinheiro", "Cartão", "Outro"],
                required=True,
            ),
            "Saldo inicial": st.column_config.NumberColumn("Saldo inicial", format="R$ %.2f"),
        },
        key="bancos_editor",
    )

    if st.button("Salvar bancos"):
        st.session_state.bancos_config = edited_bancos.fillna("").to_dict("records")
        st.success("Bancos salvos.")

    st.divider()

    mes_saldos = st.selectbox("Mês para calcular saldos", MESES, index=5, key="mes_saldos")

    saldos_calc, saldos_resumo = calc_bancos(df, st.session_state.bancos_config, mes_saldos)

    if not saldos_calc.empty:
        show_saldos = saldos_calc.copy()

        for c in ["Saldo inicial", "Entradas", "Saídas", "Saldo final calculado"]:
            show_saldos[c] = show_saldos[c].apply(money)

        st.dataframe(show_saldos, use_container_width=True, hide_index=True)

        st.subheader("Resumo geral dos bancos")

        show_resumo = saldos_resumo.copy()

        for c in ["Saldo inicial total", "Saldo final total", "Resultado de caixa"]:
            show_resumo[c] = show_resumo[c].apply(money)

        st.dataframe(show_resumo, use_container_width=True, hide_index=True)

        resultado = float(saldos_resumo["Resultado de caixa"].iloc[0])

        if resultado > 0:
            st.success(f"Sobrou dinheiro no caixa no mês: {money(resultado)}")
        elif resultado < 0:
            st.error(f"Faltou dinheiro no caixa no mês: {money(resultado)}")
        else:
            st.info("O caixa terminou igual ao início do mês.")
    else:
        st.info("Cadastre pelo menos um banco/conta.")

    st.caption("Para a Caixinha PJ: Aplicação caixinha PJ aumenta a caixinha. Resgate caixinha PJ diminui a caixinha.")

with tabs[6]:
    st.subheader("Exportar")

    if df.empty:
        st.info("Importe um arquivo primeiro.")
    else:
        buffer = make_excel_download(df)

        st.download_button(
            label="Baixar Excel organizado",
            data=buffer,
            file_name="controle_financeiro_lima.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.write("Prévia do arquivo exportado:")

        export_preview = df.copy()

        if "Grupo interno" in export_preview.columns:
            export_preview = export_preview.drop(columns=["Grupo interno"])

        st.dataframe(export_preview, use_container_width=True, hide_index=True)
