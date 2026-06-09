
import streamlit as st
import pandas as pd
import re
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Controle Financeiro Lima", layout="wide")

RULES_PATH = Path("regras_classificacao.json")

DEFAULT_RULES = {
    "Mercadoria": ["atacadao", "atacadão", "mercado", "supermercado", "comper", "fort atacadista", "assai", "assaí"],
    "Carne": ["acougue", "açougue", "carne", "frigorifico", "frigorífico"],
    "Bebidas": ["bebida", "coca", "ambev", "distribuidora"],
    "Embalagens": ["embalagem", "beira rio", "embaagens", "big embalagens", "m horizonte embalagens"],
    "Gás": ["valdeir", "gas", "gás", "botijao", "botijão"],
    "Funcionário": ["funcionario", "funcionário", "salario", "salário", "dayane", "aline funcionario"],
    "Motoboy": ["motoboy", "entregador", "ygor", "delivery"],
    "Aluguel": ["aluguel", "up gestao", "up gestão"],
    "Energia": ["energisa", "energia"],
    "Internet": ["internet", "vivo", "claro", "tim", "oi"],
    "Sistema / site": ["sistema", "site", "jg automacao", "automacao", "canva"],
    "Contabilidade": ["contabilidade", "contador", "aline carvalho"],
    "Imposto": ["das", "imposto", "receita federal", "simples nacional"],
    "Marketing": ["meta ads", "facebook", "instagram", "anuncio", "anúncio", "trafego", "tráfego"],
    "Cartão / dívida": ["dock", "andbank", "fatura", "banco votorantim", "cartao", "cartão"],
    "Financiamento": ["yamaha", "financiamento"],
    "Investimento / melhoria": ["ferramenta", "mercado livre", "mercadolivre", "casas bahia", "fritadeira", "celular", "obra", "gesso"],
    "Manutenção": ["manutencao", "manutenção", "helio", "hélio", "mecanica", "mecânica"],
    "Retirada Renato": ["renato lucas", "renato"],
    "Despesa pessoal": ["turismo", "viagem", "disney", "restaurante", "passeio", "hotel", "resort", "picanha", "quiosque"],
    "Movimentação caixinha PJ": ["resgate rdb", "aplicação rdb", "aplicacao rdb", "rdb"],
    "Pró-labore Renato": ["renato lucas", "renato"],
    "Pró-labore Dayane": ["dayane cristina", "wellhub dayane"],
}

LIMITS = {
    "Mercadoria / insumos / embalagens": 0.35,
    "Equipe / motoboy": 0.15,
    "Fixos": 0.10,
    "Taxas / sistemas / marketing": 0.05,
    "Dívidas / impostos": 0.05,
    "Pró-labore / retirada": 0.10,
    "Investimento / manutenção": 0.05,
    "Lucro desejado": 0.15,
}

CATEGORY_GROUPS = {
    "Mercadoria": "Mercadoria / insumos / embalagens",
    "Carne": "Mercadoria / insumos / embalagens",
    "Bebidas": "Mercadoria / insumos / embalagens",
    "Embalagens": "Mercadoria / insumos / embalagens",
    "Gás": "Mercadoria / insumos / embalagens",
    "Funcionário": "Equipe / motoboy",
    "Motoboy": "Equipe / motoboy",
    "Aluguel": "Fixos",
    "Energia": "Fixos",
    "Internet": "Fixos",
    "Contabilidade": "Fixos",
    "Sistema / site": "Taxas / sistemas / marketing",
    "Marketing": "Taxas / sistemas / marketing",
    "Imposto": "Dívidas / impostos",
    "Cartão / dívida": "Dívidas / impostos",
    "Financiamento": "Dívidas / impostos",
    "Retirada Renato": "Pró-labore / retirada",
    "Despesa pessoal": "Pró-labore / retirada",
    "Investimento / melhoria": "Investimento / manutenção",
    "Manutenção": "Investimento / manutenção",
    "Sem classificação": "Sem classificação",
    "Venda de produto": "Entradas",
    "Venda iFood": "Entradas",
    "Dinheiro": "Entradas",
    "Pix cliente": "Entradas",
    "Cartão": "Entradas",
    "Movimentação caixinha PJ": "Transferência interna",
    "Transferência interna": "Transferência interna",
    "Saldo banco": "Saldo",
    "Saldo caixinha PJ": "Saldo",
    "Pró-labore Renato": "Pró-labore / retirada",
    "Pró-labore Dayane": "Pró-labore / retirada",
    "Diarista": "Equipe / motoboy",
    "Frete e seguros sobre compras": "Mercadoria / insumos / embalagens",
    "Material de Expediente": "Fixos",
    "Serviços Assessorias/Consultorias": "Fixos",
    "Publicidade e Propaganda": "Taxas / sistemas / marketing",
    "Tarifas Bancárias": "Dívidas / impostos",
    "Juros Empréstimos": "Dívidas / impostos",
}

# Categorias escondidas em relatórios de operação porque são movimento de caixa, não venda nem despesa.
INTERNAL_CATEGORIES = {"Movimentação caixinha PJ", "Transferência interna", "Saldo banco", "Saldo caixinha PJ"}

ALL_CATEGORIES = sorted(set(CATEGORY_GROUPS.keys()))

def normalize_category(cat):
    """Unifica nomes antigos de vendas para simplificar o Plano de Contas."""
    c = str(cat).strip()
    mapa = {
        "Venda site": "Venda de produto",
        "Venda mesa": "Venda de produto",
        "Venda delivery": "Venda de produto",
        "Venda balcão": "Venda de produto",
        "Venda balcao": "Venda de produto",
        "Retirada Renato": "Pró-labore Renato",
    }
    return mapa.get(c, c)


def load_rules():
    if RULES_PATH.exists():
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_RULES.copy()

def save_rules(rules):
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

def brl_to_float(text):
    """Converte valores brasileiros para float, aceitando R$ 1.234,56, -R$ 14,00 e números já prontos."""
    if pd.isna(text):
        return 0.0
    if isinstance(text, (int, float)):
        return float(text)
    s = str(text).strip()
    if s == "":
        return 0.0
    negativo = "-" in s
    s = s.replace("R$", "").replace(" ", "")
    # Formato brasileiro: 1.234,56
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    s = re.sub(r"[^\d\.\-]", "", s)
    try:
        v = float(s)
        return -abs(v) if negativo else v
    except Exception:
        return 0.0

def normalize_text(s):
    return str(s).lower().strip()

def classify(desc, rules):
    d = normalize_text(desc)
    for category, keys in rules.items():
        for k in keys:
            if normalize_text(k) in d:
                return category
    return "Sem classificação"

def parse_excel(file):
    df = pd.read_excel(file)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def parse_csv(file):
    try:
        df = pd.read_csv(file, sep=None, engine="python")
    except:
        df = pd.read_csv(file, sep=";")
    df.columns = [str(c).strip() for c in df.columns]
    return df

def parse_pdf(file):
    try:
        import pdfplumber
    except Exception:
        st.error("Para ler PDF, instale pdfplumber: pip install pdfplumber")
        return pd.DataFrame()

    rows = []
    current_date = ""
    current_type = ""
    meses = {"JAN":"01", "FEV":"02", "MAR":"03", "ABR":"04", "MAI":"05", "JUN":"06", "JUL":"07", "AGO":"08", "SET":"09", "OUT":"10", "NOV":"11", "DEZ":"12"}

    def parse_date_token(day, mon, year="2026"):
        mon = mon.upper()
        return f"{day.zfill(2)}/{meses.get(mon, mon)}/{year}"

    skip_words = [
        "saldo do dia", "saldo final", "saldo inicial", "rendimento líquido", "rendimento liquido",
        "extrato gerado", "tem alguma dúvida", "caso a solução", "não nos responsabilizamos",
        "asseguramos", "nu financeira", "nu pagamentos", "cnpj", "agência", "agencia", "conta",
        "valores em r$", "movimentações", "movimentacoes", "total de depósitos", "total de depositos",
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

                # Ex: 09 MAI 2026 Total de entradas + 956,13
                m_header = re.match(r"^(\d{2})\s+([A-ZÇ]{3})\s+(\d{4})\s+Total de (entradas|saídas|saidas)\s+([\+\-])\s*([\d\.]+,\d{2})$", line, re.I)
                if m_header:
                    current_date = parse_date_token(m_header.group(1), m_header.group(2), m_header.group(3))
                    current_type = "Entrada" if "entrada" in m_header.group(4).lower() else "Saída"
                    continue

                # Ex: 10 MAI 2026 Total de entradas + 1.555,30 sem lançar o total como movimentação
                m_date_only = re.match(r"^(\d{2})\s+([A-ZÇ]{3})\s+(\d{4})", line, re.I)
                if m_date_only and "total de" not in low:
                    current_date = parse_date_token(m_date_only.group(1), m_date_only.group(2), m_date_only.group(3))

                if "total de entradas" in low:
                    current_type = "Entrada"
                    continue
                if "total de saídas" in low or "total de saidas" in low:
                    current_type = "Saída"
                    continue

                # Pega valor no fim da linha: 564,56 ou -R$ 564,56
                m = re.search(r"(.+?)\s+(-?R?\$?\s*[\d\.]+,\d{2})$", line, re.I)
                if not m:
                    continue
                desc = m.group(1).strip()
                val = brl_to_float(m.group(2))
                if not desc or val == 0:
                    continue
                if desc.lower().startswith(("total de entradas", "total de saídas", "total de saidas", "saldo")):
                    continue

                tipo = current_type
                if not tipo:
                    tipo = "Saída" if val < 0 else "Entrada"
                valor = abs(val) if tipo == "Entrada" else -abs(val)
                rows.append({"Data": current_date, "Descrição": desc, "Valor": valor, "Tipo": tipo})

    return pd.DataFrame(rows)

def standardize_df(df, rules):
    cols = {c.lower(): c for c in df.columns}
    data_col = None
    desc_col = None
    value_col = None
    type_col = None
    plan_col = None

    for c in df.columns:
        lc = c.lower()
        if "data" in lc:
            data_col = c
        if "descr" in lc or "lançamento" in lc or "lancamento" in lc or "histórico" in lc or "historico" in lc:
            desc_col = c
        if "valor" in lc:
            value_col = c
        if "entrada" in lc or "tipo" in lc:
            type_col = c
        if "plano" in lc or "categoria" in lc:
            plan_col = c

    if desc_col is None:
        desc_col = df.columns[0]
    if value_col is None:
        # tenta achar coluna numérica
        for c in df.columns:
            vals = pd.to_numeric(df[c], errors="coerce")
            if vals.notna().sum() > 0:
                value_col = c
                break

    out = pd.DataFrame()
    out["Data"] = df[data_col] if data_col else ""
    out["Descrição"] = df[desc_col].astype(str)

    # Se a planilha já tiver colunas separadas Entrada e Saída, usa as duas.
    entrada_col = None
    saida_col = None
    for c in df.columns:
        lc = str(c).lower()
        if "entrada" in lc:
            entrada_col = c
        if "saída" in lc or "saida" in lc:
            saida_col = c

    if entrada_col or saida_col:
        entradas_val = df[entrada_col].apply(brl_to_float) if entrada_col else 0
        saidas_val = df[saida_col].apply(brl_to_float) if saida_col else 0
        out["Valor"] = entradas_val - saidas_val.abs()
    else:
        out["Valor"] = df[value_col].apply(brl_to_float) if value_col else 0.0

    out["Valor"] = pd.to_numeric(out["Valor"], errors="coerce").fillna(0.0)

    if type_col:
        out["Tipo"] = df[type_col].astype(str)
        out.loc[out["Tipo"].str.lower().str.contains("saída|saida", na=False), "Valor"] = -out["Valor"].abs()
        out.loc[out["Tipo"].str.lower().str.contains("entrada", na=False), "Valor"] = out["Valor"].abs()
    else:
        out["Tipo"] = out["Valor"].apply(lambda x: "Entrada" if x > 0 else "Saída")

    if plan_col and plan_col != desc_col:
        out["Categoria"] = df[plan_col].fillna("").astype(str)
        out["Categoria"] = out.apply(lambda r: classify(r["Descrição"], rules) if r["Categoria"].strip() in ["", "nan", "Sem classificação"] else r["Categoria"], axis=1)
    else:
        out["Categoria"] = out["Descrição"].apply(lambda x: classify(x, rules))

    out["Categoria"] = out["Categoria"].apply(normalize_category)
    out["Grupo"] = out["Categoria"].map(CATEGORY_GROUPS).fillna("Sem classificação")
    out["Entrada"] = out["Valor"].apply(lambda x: x if x > 0 else 0.0)
    out["Saída"] = out["Valor"].apply(lambda x: abs(x) if x < 0 else 0.0)
    out["Observação"] = ""
    return out

def prepare_summary(df, meta_faturamento):
    df2 = df.copy()
    if df2.empty:
        return 0.0, 0.0, 0.0, pd.DataFrame(columns=["Grupo", "Valor_abs", "Limite ideal", "Diferença", "Status"])

    df2["Valor"] = pd.to_numeric(df2["Valor"], errors="coerce").fillna(0.0)
    df2["Grupo"] = df2["Grupo"].fillna("Sem classificação").astype(str)
    df2["Categoria"] = df2.get("Categoria", "Sem classificação").fillna("Sem classificação").astype(str)
    df2["Valor_abs"] = df2["Valor"].abs()
    df_operacao = df2[~df2["Categoria"].isin(INTERNAL_CATEGORIES)].copy()

    entradas = df_operacao[df_operacao["Valor"] > 0]["Valor"].sum()
    saidas = df_operacao[df_operacao["Valor"] < 0]["Valor_abs"].sum()
    lucro_estimado = entradas - saidas

    summary = df_operacao[df_operacao["Valor"] < 0].groupby("Grupo", as_index=False)["Valor_abs"].sum()
    summary["Limite ideal"] = summary["Grupo"].map(lambda g: float(LIMITS.get(g, 0)) * float(meta_faturamento)).astype(float)
    summary["Valor_abs"] = pd.to_numeric(summary["Valor_abs"], errors="coerce").fillna(0.0).astype(float)
    summary["Diferença"] = summary["Limite ideal"] - summary["Valor_abs"]
    summary["Status"] = summary.apply(lambda r: "OK" if r["Valor_abs"] <= r["Limite ideal"] or r["Limite ideal"] == 0 else "ESTOUROU", axis=1)
    return entradas, saidas, lucro_estimado, summary


def fmt_brl(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def mes_pt_from_date(x):
    if pd.isna(x) or str(x).strip() == "":
        return "Sem data"
    dt = pd.to_datetime(x, dayfirst=True, errors="coerce")
    if pd.isna(dt):
        return "Sem data"
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    return meses[dt.month-1]

def soma_categoria_mes(dfm, categoria):
    if dfm.empty:
        return 0.0
    return float(dfm.loc[dfm["Categoria"].eq(categoria), "Valor"].abs().sum())

def soma_categorias_mes(dfm, categorias):
    if dfm.empty:
        return 0.0
    return float(dfm.loc[dfm["Categoria"].isin(categorias), "Valor"].abs().sum())

def prepare_dre_mensal(df, saldos_bancos=None, mes_saldo="Junho"):
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    saldos_bancos = saldos_bancos or {}
    dfx = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
    if dfx.empty:
        dfx = pd.DataFrame(columns=["Data", "Categoria", "Valor"])
    if "Categoria" not in dfx.columns:
        dfx["Categoria"] = "Sem classificação"
    if "Valor" not in dfx.columns:
        dfx["Valor"] = 0.0
    dfx["Categoria"] = dfx["Categoria"].fillna("Sem classificação").astype(str).apply(normalize_category)
    dfx["Valor"] = pd.to_numeric(dfx["Valor"], errors="coerce").fillna(0.0)
    dfx["Mês"] = dfx.get("Data", "").apply(mes_pt_from_date) if "Data" in dfx.columns else "Sem data"

    rows = []
    def add_row(nome, valores=None):
        row = {"Plano de Contas": nome}
        valores = valores or {}
        for m in meses:
            row[m] = float(valores.get(m, 0.0))
        rows.append(row)

    # Saldos dos bancos cadastrados, flexível para qualquer empresa/usuário.
    bancos_df = saldos_bancos.get("bancos_df", pd.DataFrame()) if isinstance(saldos_bancos, dict) else pd.DataFrame()
    add_row("SALDO INICIAL", {mes_saldo: saldos_bancos.get("saldo_inicial_total", 0.0) if isinstance(saldos_bancos, dict) else 0.0})
    if isinstance(bancos_df, pd.DataFrame) and not bancos_df.empty:
        for _, b in bancos_df.iterrows():
            nome_banco = str(b.get("Banco", "Banco")).strip() or "Banco"
            add_row(nome_banco, {mes_saldo: float(b.get("Saldo inicial", 0.0) or 0.0)})

    # receitas e despesas por mês
    receita_prod = {}
    receita_ifood = {}
    custos = {}
    equipe = {}
    fixos = {}
    sistemas_marketing = {}
    dividas = {}
    prolabore = {}
    investimento = {}
    sem_class = {}
    caixinha_mov = {}
    margem = {}
    margem_pct = {}
    desp_fixas_total = {}

    for m in meses:
        dfm = dfx[dfx["Mês"].eq(m)].copy()
        # ignora movimento interno da caixinha na operação
        dfm_op = dfm[~dfm["Categoria"].isin(INTERNAL_CATEGORIES)].copy()
        receita_prod[m] = soma_categoria_mes(dfm_op[dfm_op["Valor"] > 0], "Venda de produto") + soma_categoria_mes(dfm_op[dfm_op["Valor"] > 0], "Pix cliente") + soma_categoria_mes(dfm_op[dfm_op["Valor"] > 0], "Dinheiro") + soma_categoria_mes(dfm_op[dfm_op["Valor"] > 0], "Cartão")
        receita_ifood[m] = soma_categoria_mes(dfm_op[dfm_op["Valor"] > 0], "Venda iFood")
        custos[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Mercadoria", "Carne", "Bebidas", "Embalagens", "Gás", "Frete e seguros sobre compras"])
        equipe[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Funcionário", "Motoboy", "Diarista"])
        fixos[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Aluguel", "Energia", "Internet", "Contabilidade", "Material de Expediente", "Serviços Assessorias/Consultorias"])
        sistemas_marketing[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Sistema / site", "Marketing", "Publicidade e Propaganda"])
        dividas[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Imposto", "Cartão / dívida", "Financiamento", "Tarifas Bancárias", "Juros Empréstimos"])
        prolabore[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Pró-labore Renato", "Pró-labore Dayane", "Despesa pessoal"])
        investimento[m] = soma_categorias_mes(dfm_op[dfm_op["Valor"] < 0], ["Investimento / melhoria", "Manutenção"])
        sem_class[m] = soma_categoria_mes(dfm_op[dfm_op["Valor"] < 0], "Sem classificação")
        caixinha_mov[m] = float(dfm.loc[dfm["Categoria"].eq("Movimentação caixinha PJ"), "Valor"].sum())
        receita = receita_prod[m] + receita_ifood[m]
        margem[m] = receita - custos[m]
        margem_pct[m] = (margem[m] / receita) if receita else 0.0
        desp_fixas_total[m] = equipe[m] + fixos[m] + sistemas_marketing[m] + dividas[m] + prolabore[m] + investimento[m] + sem_class[m]

    receita_total = {m: receita_prod[m] + receita_ifood[m] for m in meses}
    add_row("RECEITAS BRUTA", receita_total)
    add_row("(+) Venda Produtos", receita_prod)
    add_row("(+) Venda Produtos iFood", receita_ifood)
    add_row("CUSTOS VARIÁVEIS:", custos)
    add_row("Compras de mercadorias", custos)
    add_row("Frete e Seguros sobre compras", {})
    add_row("Diarista", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Diarista") for m in meses})
    add_row("MARGEM CONTRIBUIÇÃO", margem)
    add_row("% MARGEM CONTRIBUIÇÃO", {m: margem_pct[m] for m in meses})
    add_row("DESPESAS FIXAS:", desp_fixas_total)
    add_row("Salário/Folha de pagamento", {m: soma_categorias_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], ["Funcionário", "Motoboy"]) for m in meses})
    add_row("Pró-labore Renato", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Pró-labore Renato") for m in meses})
    add_row("Pró-labore Dayane", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Pró-labore Dayane") for m in meses})
    add_row("Aluguel", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Aluguel") for m in meses})
    add_row("Energia Elétrica", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Energia") for m in meses})
    add_row("Internet", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Internet") for m in meses})
    add_row("Sistemas de Gestão", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Sistema / site") for m in meses})
    add_row("Marketing Digital", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Marketing") for m in meses})
    add_row("Utensílios e Ferramentas", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Investimento / melhoria") for m in meses})
    add_row("Manutenção Veículos", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Manutenção") for m in meses})
    add_row("Gás", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Gás") for m in meses})
    add_row("Serviços Contabilidade", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Contabilidade") for m in meses})
    add_row("Emprestimo", {m: soma_categorias_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], ["Cartão / dívida", "Juros Empréstimos"]) for m in meses})
    add_row("Publicidade e Propaganda", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Publicidade e Propaganda") for m in meses})
    add_row("Tarifas Bancárias", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Tarifas Bancárias") for m in meses})
    add_row("Financiamento Moto", {m: soma_categoria_mes(dfx[(dfx["Mês"].eq(m)) & (dfx["Valor"] < 0)], "Financiamento") for m in meses})
    add_row("Sem classificação", sem_class)
    add_row("MOVIMENTO CAIXINHA PJ", caixinha_mov)
    add_row("SALDO FINAL", {mes_saldo: saldos_bancos.get("saldo_final_total", 0.0) if isinstance(saldos_bancos, dict) else 0.0})
    if isinstance(bancos_df, pd.DataFrame) and not bancos_df.empty:
        for _, b in bancos_df.iterrows():
            nome_banco = str(b.get("Banco", "Banco")).strip() or "Banco"
            add_row(f"{nome_banco} - saldo final", {mes_saldo: float(b.get("Saldo final automático", 0.0) or 0.0)})

    dre = pd.DataFrame(rows)
    return dre

def style_dre(row):
    nome = str(row.get("Plano de Contas", ""))
    styles = []
    for col in row.index:
        if col == "Plano de Contas":
            if nome.isupper() or nome in ["SALDO INICIAL", "SALDO FINAL", "RECEITAS BRUTA", "CUSTOS VARIÁVEIS:", "MARGEM CONTRIBUIÇÃO", "% MARGEM CONTRIBUIÇÃO", "DESPESAS FIXAS:", "MOVIMENTO CAIXINHA PJ"]:
                styles.append("font-weight: bold; background-color: #dbeafe;")
            else:
                styles.append("")
        else:
            if nome in ["CUSTOS VARIÁVEIS:", "DESPESAS FIXAS:"]:
                styles.append("background-color: #fde2d5; font-weight: bold;")
            elif nome in ["RECEITAS BRUTA"]:
                styles.append("background-color: #dff3e6; font-weight: bold;")
            elif nome in ["MARGEM CONTRIBUIÇÃO", "% MARGEM CONTRIBUIÇÃO"]:
                styles.append("background-color: #e8f0fe; font-weight: bold;")
            elif nome in ["SALDO INICIAL", "SALDO FINAL", "MOVIMENTO CAIXINHA PJ"]:
                styles.append("background-color: #dbeafe; font-weight: bold;")
            else:
                styles.append("")
    return styles

def format_dre_value(v, row_name):
    if row_name == "% MARGEM CONTRIBUIÇÃO":
        return f"{float(v)*100:.2f}%".replace(".", ",")
    return fmt_brl(v)



BANK_SOURCE_OPTIONS = ["Extrato importado", "Caixinha PJ (RDB)", "Manual"]

MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

def default_bancos_df():
    return pd.DataFrame([
        {"Banco": "Nubank PJ", "Tipo": "Extrato importado", "Saldo inicial": 0.0, "Entradas manuais": 0.0, "Saídas manuais": 0.0},
        {"Banco": "Caixinha PJ", "Tipo": "Caixinha PJ (RDB)", "Saldo inicial": 0.0, "Entradas manuais": 0.0, "Saídas manuais": 0.0},
    ])

def banco_movimentos(df, mes, tipo):
    """Calcula entradas e saídas de bancos de forma automática quando possível."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return 0.0, 0.0
    dfx = df.copy()
    if "Valor" not in dfx.columns:
        return 0.0, 0.0
    dfx["Valor"] = pd.to_numeric(dfx["Valor"], errors="coerce").fillna(0.0)
    dfx["Mês"] = dfx.get("Data", "").apply(mes_pt_from_date) if "Data" in dfx.columns else "Sem data"
    dfm = dfx[dfx["Mês"].eq(mes)].copy()
    if dfm.empty:
        return 0.0, 0.0
    tipo = str(tipo)
    if tipo == "Extrato importado":
        # Movimento real da conta importada: tudo que entrou e tudo que saiu.
        entradas = float(dfm.loc[dfm["Valor"] > 0, "Valor"].sum())
        saidas = float(dfm.loc[dfm["Valor"] < 0, "Valor"].abs().sum())
        return entradas, saidas
    if tipo == "Caixinha PJ (RDB)":
        desc = dfm.get("Descrição", pd.Series([""] * len(dfm))).astype(str).str.lower()
        aplicacao = dfm[desc.str.contains("aplica", na=False) & desc.str.contains("rdb", na=False)]
        resgate = dfm[desc.str.contains("resgate", na=False) & desc.str.contains("rdb", na=False)]
        # Para a caixinha: aplicação aumenta saldo; resgate diminui saldo.
        entradas = float(aplicacao["Valor"].abs().sum())
        saidas = float(resgate["Valor"].abs().sum())
        return entradas, saidas
    return 0.0, 0.0

def preparar_bancos(df, bancos_base, mes):
    if not isinstance(bancos_base, pd.DataFrame) or bancos_base.empty:
        bancos_base = default_bancos_df()
    bancos = bancos_base.copy()
    for col in ["Banco", "Tipo"]:
        if col not in bancos.columns:
            bancos[col] = ""
    for col in ["Saldo inicial", "Entradas manuais", "Saídas manuais"]:
        if col not in bancos.columns:
            bancos[col] = 0.0
        bancos[col] = pd.to_numeric(bancos[col], errors="coerce").fillna(0.0)
    bancos["Tipo"] = bancos["Tipo"].replace("", "Manual")

    entradas_calc = []
    saidas_calc = []
    saldo_final = []
    for _, r in bancos.iterrows():
        ent_auto, sai_auto = banco_movimentos(df, mes, r.get("Tipo", "Manual"))
        if r.get("Tipo", "Manual") == "Manual":
            ent = float(r.get("Entradas manuais", 0.0))
            sai = float(r.get("Saídas manuais", 0.0))
        else:
            ent = ent_auto + float(r.get("Entradas manuais", 0.0))
            sai = sai_auto + float(r.get("Saídas manuais", 0.0))
        ini = float(r.get("Saldo inicial", 0.0))
        entradas_calc.append(ent)
        saidas_calc.append(sai)
        saldo_final.append(ini + ent - sai)
    bancos["Entradas automáticas"] = entradas_calc
    bancos["Saídas automáticas"] = saidas_calc
    bancos["Saldo final automático"] = saldo_final
    return bancos

def saldos_from_bancos(bancos_calc):
    if not isinstance(bancos_calc, pd.DataFrame) or bancos_calc.empty:
        bancos_calc = default_bancos_df()
        bancos_calc["Entradas automáticas"] = 0.0
        bancos_calc["Saídas automáticas"] = 0.0
        bancos_calc["Saldo final automático"] = bancos_calc["Saldo inicial"]
    return {
        "bancos_df": bancos_calc.copy(),
        "saldo_inicial_total": float(pd.to_numeric(bancos_calc.get("Saldo inicial", 0), errors="coerce").fillna(0).sum()),
        "saldo_final_total": float(pd.to_numeric(bancos_calc.get("Saldo final automático", 0), errors="coerce").fillna(0).sum()),
    }

st.title("🍔 Controle Financeiro Lima")
st.caption("Sistema simples para controlar a hamburgueria, alertar estouros e mirar 15% de lucro.")

with st.sidebar:
    st.header("Metas do mês")
    meta_faturamento = st.number_input("Meta de faturamento do mês", value=55000.0, step=1000.0)
    dias_abertos = st.number_input("Dias abertos no mês", value=26, step=1)
    lucro_desejado = st.number_input("Lucro desejado (%)", value=15.0, step=1.0) / 100

    st.divider()
    st.header("Regras")
    rules = load_rules()
    if st.button("Salvar regras atuais"):
        save_rules(rules)
        st.success("Regras salvas.")

uploaded = st.file_uploader(
    "Importe extrato, fatura ou planilha",
    type=["xlsx", "xls", "csv", "pdf"],
    accept_multiple_files=True
)

if "dados" not in st.session_state:
    st.session_state["dados"] = pd.DataFrame(columns=["Data", "Descrição", "Valor", "Tipo", "Categoria", "Grupo", "Entrada", "Saída", "Observação"])

if uploaded:
    all_dfs = []
    for file in uploaded:
        name = file.name.lower()
        if name.endswith((".xlsx", ".xls")):
            raw = parse_excel(file)
        elif name.endswith(".csv"):
            raw = parse_csv(file)
        elif name.endswith(".pdf"):
            raw = parse_pdf(file)
        else:
            raw = pd.DataFrame()
        if not raw.empty:
            all_dfs.append(standardize_df(raw, rules))

    if all_dfs:
        st.session_state["dados"] = pd.concat(all_dfs, ignore_index=True)

df = st.session_state["dados"]

with st.sidebar:
    st.divider()
    st.header("Bancos e saldos")
    mes_saldo = st.selectbox("Mês dos saldos", MESES_PT, index=5)
    st.caption("Cadastre quantos bancos quiser. O saldo final é automático: saldo inicial + entradas - saídas. Se sair mais do que entrou, fica negativo.")

    if "bancos_base" not in st.session_state:
        st.session_state["bancos_base"] = default_bancos_df()

    bancos_editados = st.data_editor(
        st.session_state["bancos_base"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_bancos",
        column_config={
            "Banco": st.column_config.TextColumn("Banco / Conta"),
            "Tipo": st.column_config.SelectboxColumn("Tipo", options=BANK_SOURCE_OPTIONS),
            "Saldo inicial": st.column_config.NumberColumn("Saldo inicial", format="R$ %.2f"),
            "Entradas manuais": st.column_config.NumberColumn("Entradas manuais", format="R$ %.2f"),
            "Saídas manuais": st.column_config.NumberColumn("Saídas manuais", format="R$ %.2f"),
        }
    )
    st.session_state["bancos_base"] = bancos_editados
    bancos_calc = preparar_bancos(df, bancos_editados, mes_saldo)
    saldos_bancos = saldos_from_bancos(bancos_calc)

    st.markdown("**Saldos calculados**")
    bancos_view = bancos_calc[["Banco", "Saldo inicial", "Entradas automáticas", "Saídas automáticas", "Saldo final automático"]].copy()
    st.dataframe(
        bancos_view.style.format({
            "Saldo inicial": "R$ {:,.2f}",
            "Entradas automáticas": "R$ {:,.2f}",
            "Saídas automáticas": "R$ {:,.2f}",
            "Saldo final automático": "R$ {:,.2f}",
        }),
        use_container_width=True,
        height=220
    )

tab1, tab_dre, tab2, tab3, tab4, tab_bancos = st.tabs(["Dashboard", "DRE Mensal", "Lançamentos", "Sem classificação", "Regras", "Bancos / Saldos"])

with tab1:
    entradas, saidas, lucro_estimado, summary = prepare_summary(df, meta_faturamento)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas identificadas", f"R$ {entradas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("Saídas identificadas", f"R$ {saidas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("Lucro estimado", f"R$ {lucro_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c4.metric("Meta diária", f"R$ {meta_faturamento/dias_abertos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.subheader("Alertas por categoria")
    if summary.empty:
        st.info("Importe um arquivo para ver os alertas.")
    else:
        def color_status(val):
            if val == "ESTOUROU":
                return "background-color: #ffcccc; color: #8a0000; font-weight: bold;"
            if val == "OK":
                return "background-color: #d8f5d0; color: #145214; font-weight: bold;"
            return ""

        summary_view = summary.rename(columns={"Grupo": "Categoria geral"})
        st.dataframe(
            summary_view.style.map(color_status, subset=["Status"]).format({
                "Valor_abs": "R$ {:,.2f}",
                "Limite ideal": "R$ {:,.2f}",
                "Diferença": "R$ {:,.2f}",
            }),
            use_container_width=True
        )

    limite_mercadoria = meta_faturamento * 0.35
    gasto_mercadoria = summary.loc[summary["Grupo"] == "Mercadoria / insumos / embalagens", "Valor_abs"].sum() if not summary.empty else 0
    restante_mercadoria = limite_mercadoria - gasto_mercadoria

    st.subheader("Compra da semana")
    meta_dia = meta_faturamento / dias_abertos
    teto_6_dias = meta_dia * 6 * 0.35
    st.write(f"Para uma compra de quarta até segunda, o teto saudável é aproximadamente **R$ {teto_6_dias:,.2f}**.".replace(",", "X").replace(".", ",").replace("X", "."))
    st.write(f"No mês, ainda pode gastar com mercadoria: **R$ {restante_mercadoria:,.2f}**.".replace(",", "X").replace(".", ",").replace("X", "."))

with tab_dre:
    st.subheader("DRE mensal / Plano de contas")
    st.caption("Visão no modelo da sua planilha: meses nas colunas, plano de contas nas linhas, saldos dos bancos e caixinha PJ monitorados no topo e no final.")
    dre = prepare_dre_mensal(df, saldos_bancos=saldos_bancos, mes_saldo=mes_saldo)

    dre_format = dre.copy()
    for col in dre_format.columns:
        if col != "Plano de Contas":
            dre_format[col] = [format_dre_value(v, row_name) for v, row_name in zip(dre_format[col], dre_format["Plano de Contas"])]

    st.dataframe(
        dre_format.style.apply(style_dre, axis=1),
        use_container_width=True,
        height=720
    )

    import io
    buffer_dre = io.BytesIO()
    with pd.ExcelWriter(buffer_dre, engine="openpyxl") as writer:
        dre.to_excel(writer, index=False, sheet_name="DRE_Mensal")
    st.download_button(
        "Baixar DRE mensal em Excel",
        data=buffer_dre.getvalue(),
        file_name="dre_mensal_lima.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab2:
    st.subheader("Lançamentos importados")

    # A coluna Grupo é usada só por dentro para gerar os alertas.
    # Ela não aparece mais para não atrapalhar o preenchimento do Plano de Contas.
    df_editor = df.drop(columns=["Grupo"], errors="ignore")

    edited = st.data_editor(
        df_editor,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Categoria": st.column_config.SelectboxColumn("Plano de contas", options=ALL_CATEGORIES),
        }
    )
    edited["Valor"] = pd.to_numeric(edited["Valor"], errors="coerce").fillna(0.0)
    edited["Categoria"] = edited["Categoria"].apply(normalize_category)
    edited["Grupo"] = edited["Categoria"].map(CATEGORY_GROUPS).fillna("Sem classificação")
    edited["Entrada"] = edited["Valor"].apply(lambda x: x if x > 0 else 0.0)
    edited["Saída"] = edited["Valor"].apply(lambda x: abs(x) if x < 0 else 0.0)
    st.session_state["dados"] = edited

    if not edited.empty:
        output = edited.drop(columns=["Grupo"], errors="ignore").copy()
        resumo_export = prepare_summary(edited, meta_faturamento)[3].rename(columns={"Grupo": "Categoria geral"})
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            output.to_excel(writer, index=False, sheet_name="Lancamentos")
            resumo_export.to_excel(writer, index=False, sheet_name="Resumo")
            prepare_dre_mensal(edited, saldos_bancos=saldos_bancos, mes_saldo=mes_saldo).to_excel(writer, index=False, sheet_name="DRE_Mensal")
        st.download_button(
            "Baixar relatório em Excel",
            data=buffer.getvalue(),
            file_name="relatorio_controle_financeiro_lima.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with tab3:
    st.subheader("Lançamentos sem classificação")
    st.caption("Agora você pode classificar direto por aqui. Escolha o Plano de contas na tabela e clique em Salvar classificações.")

    pend = df[df["Categoria"] == "Sem classificação"].copy()
    if pend.empty:
        st.success("Nenhum lançamento sem classificação.")
    else:
        # Mostra só o que precisa para classificar rápido, mantendo o índice original escondido
        pend_editor = pend.drop(columns=["Grupo"], errors="ignore").copy()

        # Colunas que normalmente não precisam ser editadas nesta aba
        disabled_cols = [c for c in pend_editor.columns if c != "Categoria"]

        edited_pend = st.data_editor(
            pend_editor,
            use_container_width=True,
            num_rows="fixed",
            hide_index=True,
            column_config={
                "Categoria": st.column_config.SelectboxColumn(
                    "Plano de contas",
                    options=ALL_CATEGORIES,
                    required=True
                ),
            },
            disabled=disabled_cols,
            key="editor_sem_classificacao"
        )

        col_a, col_b = st.columns([1, 2])
        with col_a:
            salvar_pendentes = st.button("Salvar classificações", type="primary")
        with col_b:
            st.info("Depois de salvar, os itens classificados saem desta aba automaticamente.")

        if salvar_pendentes:
            dados_atualizados = st.session_state["dados"].copy()
            alterados = 0

            # Como o índice original foi preservado no pend_editor, usamos ele para atualizar a base principal
            for idx, row in edited_pend.iterrows():
                nova_categoria = normalize_category(row.get("Categoria", "Sem classificação"))
                if nova_categoria != "Sem classificação" and idx in dados_atualizados.index:
                    dados_atualizados.at[idx, "Categoria"] = nova_categoria
                    alterados += 1

            dados_atualizados["Grupo"] = dados_atualizados["Categoria"].map(CATEGORY_GROUPS).fillna("Sem classificação")
            dados_atualizados["Valor"] = pd.to_numeric(dados_atualizados["Valor"], errors="coerce").fillna(0.0)
            dados_atualizados["Entrada"] = dados_atualizados["Valor"].apply(lambda x: x if x > 0 else 0.0)
            dados_atualizados["Saída"] = dados_atualizados["Valor"].apply(lambda x: abs(x) if x < 0 else 0.0)
            st.session_state["dados"] = dados_atualizados

            if alterados > 0:
                st.success(f"{alterados} lançamento(s) classificado(s) com sucesso.")
                st.rerun()
            else:
                st.warning("Nenhum item foi alterado. Escolha um Plano de contas diferente de Sem classificação.")

with tab4:
    st.subheader("Cadastrar nova regra")
    col1, col2 = st.columns(2)
    with col1:
        palavra = st.text_input("Palavra-chave. Ex: Beira Rio")
    with col2:
        categoria = st.selectbox("Categoria", ALL_CATEGORIES)

    if st.button("Adicionar regra"):
        if palavra.strip():
            rules.setdefault(categoria, [])
            rules[categoria].append(palavra.strip())
            save_rules(rules)
            st.success(f"Regra adicionada: {palavra} → {categoria}")
        else:
            st.error("Digite uma palavra-chave.")

    st.subheader("Regras atuais")
    rules_df = pd.DataFrame([{"Categoria": k, "Palavras-chave": ", ".join(v)} for k, v in rules.items()])
    st.dataframe(rules_df, use_container_width=True)


with tab_bancos:
    st.subheader("Bancos / Saldos cadastrados")
    st.caption("Aqui você confere o saldo inicial, entradas, saídas e saldo final automático de cada banco. Serve para Nubank PJ, Caixinha PJ, Caixa, Sicredi, dinheiro em caixa ou qualquer outra conta.")
    st.dataframe(
        bancos_calc.style.format({
            "Saldo inicial": "R$ {:,.2f}",
            "Entradas manuais": "R$ {:,.2f}",
            "Saídas manuais": "R$ {:,.2f}",
            "Entradas automáticas": "R$ {:,.2f}",
            "Saídas automáticas": "R$ {:,.2f}",
            "Saldo final automático": "R$ {:,.2f}",
        }),
        use_container_width=True
    )
    st.info("Para a Caixinha PJ, o sistema entende Aplicação RDB como entrada na caixinha e Resgate RDB como saída da caixinha.")
