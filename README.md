# Controle Financeiro Lima

Sistema local para controlar a hamburgueria e pizzaria.

## O que ele faz

- Importa Excel, CSV e PDF
- Classifica lançamentos por palavra-chave
- Mostra o que está estourando contra a meta
- Calcula lucro estimado
- Mostra quanto ainda pode gastar com mercadoria
- Exporta relatório em Excel
- Permite cadastrar regras novas

## Como rodar no computador

1. Abra o terminal dentro desta pasta.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Rode o sistema:

```bash
streamlit run app.py
```

4. O navegador abrirá automaticamente.

## Como usar

1. Coloque a meta do mês. Exemplo: R$55.000
2. Coloque os dias abertos. Exemplo: 26
3. Importe extrato, fatura ou planilha
4. Veja os alertas no Dashboard
5. Corrija os "Sem classificação"
6. Cadastre regras novas para o sistema aprender
7. Exporte o relatório final

## Metas usadas

- Mercadoria / insumos / embalagens: 35%
- Equipe / motoboy: 15%
- Fixos: 10%
- Taxas / sistemas / marketing: 5%
- Dívidas / impostos: 5%
- Pró-labore / retirada: 10%
- Investimento / manutenção: 5%
- Lucro desejado: 15%

## Observação importante

Não coloque senha de banco no sistema. O caminho seguro é baixar o extrato/fatura e importar o arquivo.