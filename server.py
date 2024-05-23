#!/usr/bin/env python3

# This script is a dashboard that shows some statistics about a book collection.
# The data is stored in a SQLite database and the dashboard is built using Plotly Dash.
# Requirements:
# - pandas, plotly, dash, dash-bootstrap-components, dash-draggable, dash-table, sqlite3
#
# Usage:
#   - Run the script and open a web browser at http://127.0.0.1:8050/

import sqlite3
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_draggable
import plotly.graph_objects as go

from dash import Dash, dcc, html, dash_table
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output

# Constants
DB_FOLDER = "sqlite_db"
DB_FILE = "livros.db"
DB_PATH = f"{DB_FOLDER}/{DB_FILE}"
TEMPLATE_COLOR = "plotly_white"


def perform_query(query) -> pd.DataFrame:
    """
    @brief:
        Perform a query on the SQLite database and return a DataFrame
    @param query:
        Query to be executed
    @return:
        Result of the query as a DataFrame
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_books_by_author_count():
    """
    @brief:
        Get the number of books by author
    @return:
        DataFrame with the number of books by author
    """
    query_books_by_author_count = """
        SELECT
            autor AS "Autor", count(*) AS "Count"
        FROM
            livros
        GROUP BY
            autor
        ORDER BY
            autor ASC
    """

    df_books_by_author_count = perform_query(query_books_by_author_count)

    fig_books_count_bar = px.bar(
        df_books_by_author_count,
        x="Autor",
        y="Count",
        title="Número de livros por autor",
        labels={"Autor": "Autor", "Count": "Quantidade de Livros"},
        template=TEMPLATE_COLOR,
    )

    # Ensure that the y-axis has integer ticks
    fig_books_count_bar.update_yaxes(dtick=1)
    fig_books_count_bar.update_layout(title_x=0.5)

    return fig_books_count_bar


def get_total_price_paid():
    """
    @brief:
        Get the total price paid for all books
    @return:
        Total price paid for all books
    """
    query_total_price_paid = """
        SELECT
            sum(preco_pago) AS "TotalPago"
        FROM
            livros
    """

    df_total_price_paid = perform_query(query_total_price_paid)
    total_price_paid = df_total_price_paid.iloc[0]["TotalPago"]

    return total_price_paid


def get_books_by_year():
    """
    @brief:
        Get the number of books read by year
    @return:
        DataFrame with the number of books read by year
    """
    query_books_by_year = """
        SELECT
            ano_primeira_leitura AS ano,
            COUNT(*) AS leituras
        FROM
            livros
        WHERE
            ano_primeira_leitura IS NOT NULL
        GROUP BY
            ano_primeira_leitura
        ORDER BY
            ano DESC;
    """

    df_books_by_year = perform_query(query_books_by_year)

    # Fill missing years with 0
    all_years = range(df_books_by_year["ano"].min(), df_books_by_year["ano"].max() + 1)
    df_complete = pd.DataFrame({"ano": all_years})
    df_books_by_year = df_complete.merge(df_books_by_year, on="ano", how="left").fillna(
        0
    )

    years = df_books_by_year["ano"].unique()

    # Agora, você pode criar o gráfico de barras
    fig_books_by_year = px.bar(
        df_books_by_year,
        x="ano",
        y="leituras",
        text="leituras",
        title="Quantidade de leituras por ano",
        labels={"ano": "Ano", "leituras": "Quantidade de Leituras"},
        template=TEMPLATE_COLOR,
    )

    fig_books_by_year.update_xaxes(tickvals=years)
    fig_books_by_year.update_layout(title_x=0.5)

    return fig_books_by_year


def get_expenditure_by_year():
    """
    @brief:
        Get the expenditure by year
    @return:
        DataFrame with the expenditure by year
    """

    query_expenditure_by_year = """
    SELECT
        ano_aquisicao AS "ano", sum(preco_pago) AS "valor gasto"
    FROM
        livros
    WHERE
        ano_aquisicao IS NOT NULL
    GROUP BY
        ano_aquisicao
    """

    df_expenditure_by_year = perform_query(query_expenditure_by_year)

    # Preencher os anos vazios com 0 no DataFrame df_expenditure_by_year
    all_years_expenditure = range(
        df_expenditure_by_year["ano"].min(), df_expenditure_by_year["ano"].max() + 1
    )
    df_complete_expenditure = pd.DataFrame({"ano": all_years_expenditure})
    df_expenditure_by_year = df_complete_expenditure.merge(
        df_expenditure_by_year, on="ano", how="left"
    ).fillna(0)

    years_expenditure = df_expenditure_by_year["ano"].unique()

    # Calcular o valor total acumulado ao longo dos anos
    df_expenditure_by_year["valor acumulado"] = df_expenditure_by_year[
        "valor gasto"
    ].cumsum()

    # Criar o gráfico de barras
    fig_expenditure_by_year = px.bar(
        df_expenditure_by_year,
        x="ano",
        y="valor gasto",
        text="valor gasto",
        title="Valor gasto",
        labels={"ano": "Ano", "valor gasto": "Valor gasto"},
        template=TEMPLATE_COLOR,
    )

    # Adicionar uma linha com o valor acumulado
    fig_expenditure_by_year.add_scatter(
        x=df_expenditure_by_year["ano"],
        y=df_expenditure_by_year["valor acumulado"],
        mode="lines",
        name="Valor acumulado",
    )

    # Definir os pontos de tick para o eixo x
    fig_expenditure_by_year.update_xaxes(tickvals=years_expenditure)

    total_price_paid = get_total_price_paid()

    # Adicione uma legenda mostrando o valor total gasto
    fig_expenditure_by_year.update_layout(
        title_x=0.5,
        annotations=[
            dict(
                x=0.5,
                y=1.1,
                xref="paper",
                yref="paper",
                text=f"Total gasto: R$ {total_price_paid:.2f}",
                showarrow=False,
                font=dict(size=12),
            )
        ],
    )

    return fig_expenditure_by_year


def get_count_books_by_types():
    """
    @brief:
        Get the number of books by type
    @return:
        DataFrame with the number of books by type
    """
    query_books_types = """
        SELECT
            tipo, count(tipo) AS quantidade
        FROM
            livros
        GROUP BY
            tipo
    """

    df_books_types = perform_query(query_books_types)

    fig_books_types_pie = px.pie(
        df_books_types,
        values="quantidade",
        names="tipo",
        title="Tipos de livros",
        template=TEMPLATE_COLOR,
    )

    fig_books_types_pie.update_layout(title_x=0.5)

    return fig_books_types_pie


def get_books_by_type():
    """
    @brief:
        Get the number of books by type
    @return:
        DataFrame with the number of books by type
    """
    query_books_by_type = """
        SELECT
            tipo AS Tipo, titulo AS Título, autor AS Autor
        FROM
            livros
    """

    df_books_by_type = perform_query(query_books_by_type)

    return df_books_by_type


def get_books_read_in_each_year():
    """
    @brief:
        Get the number of books read in each year
    @return:
        DataFrame with the number of books read in each year
    """
    query_books_read_in_each_year = """
        SELECT
            titulo AS "Título",
            ano_primeira_leitura AS "Ano da leitura"
        FROM
            livros
        WHERE
            ano_primeira_leitura IS NOT NULL
        ORDER BY
            ano_primeira_leitura DESC
    """

    df_books_read_in_each_year = perform_query(query_books_read_in_each_year)

    return df_books_read_in_each_year


def get_books_prices():
    """
    @brief:
        Get the prices of books
    @return:
        DataFrame with the prices of books
    """
    query_books_prices = """
        SELECT
            titulo AS "Título",
            preco_pago AS "Preço pago"
        FROM
            livros
        ORDER BY
            preco_pago DESC
    """

    df_books_prices = perform_query(query_books_prices)
    return df_books_prices


def get_avg_books_price():
    """
    @brief:
        Get the average price of books
    @return:
        Average price of books
    """
    query_avg_book_price = """
        SELECT
            avg(preco_pago) AS "Preço médio"
        FROM
            livros
        WHERE
            preco_pago > 0
    """

    df_avg_book_price = perform_query(query_avg_book_price)
    avg_book_price = df_avg_book_price.iloc[0]["Preço médio"]

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=avg_book_price,
            title={"text": "Preço médio dos livros", "font": {"size": 20}},
            number={"prefix": "R$", "font": {"size": 60}, "valueformat": ".2f"},
        )
    )

    fig.update_layout(
        template=None,
        height=200,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    )

    return fig


def get_avg_book_price_by_type(type):
    """
    @brief:
        Get the average price of books by type
    @return:
        Average price of books by type
    """
    query_avg_book_price_by_type = f"""
        SELECT
            avg(preco_pago) AS "Preço médio"
        FROM
            livros
        WHERE
            tipo = '{type}' AND preco_pago > 0
    """

    df_avg_book_price_by_type = perform_query(query_avg_book_price_by_type)
    avg_book_price_by_type = df_avg_book_price_by_type.iloc[0]["Preço médio"]

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=avg_book_price_by_type,
            title={
                "text": f"Preço médio dos livros do tipo {type}",
                "font": {"size": 20},
            },
            number={"prefix": "R$", "font": {"size": 60}, "valueformat": ".2f"},
        )
    )

    fig.update_layout(
        template=None,
        height=200,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
    )

    return fig


def get_books_not_available():
    """
    @brief:
        Get the books that are not available
    @return:
        DataFrame with the books that are not available
    """
    query_books_not_available = """
        SELECT
            titulo AS "Título", autor AS "Autor"
        FROM
            livros
        WHERE
            copia_no_acervo IS FALSE
    """

    df_books_not_available = perform_query(query_books_not_available)

    return df_books_not_available


def get_books_availability():
    """
    @brief:
        Get the availability of books
    @return:
        DataFrame with the availability of books
    """
    query_books_availability = """
        SELECT
            copia_no_acervo AS "Disponível", count(*) AS "Quantidade"
        FROM
            livros
        GROUP BY
            copia_no_acervo
    """

    df_books_availability = perform_query(query_books_availability)
    df_books_availability["Disponível"] = df_books_availability["Disponível"].map(
        {1: "Disponível", 0: "Não disponível"}
    )

    fig_books_availability = px.pie(
        df_books_availability,
        values="Quantidade",
        names="Disponível",
        title="Disponibilidade de livros no acervo",
        template=TEMPLATE_COLOR,
    )

    fig_books_availability.update_layout(title_x=0.5)

    return fig_books_availability


app = Dash(title="Acervo dashboard")

# Layout do aplicativo
app.layout = dbc.Container(
    [
        html.H1(
            "Acervo dashboard",
            style={
                "textAlign": "center",
                "margin": "center",
                "font-size": "40px",
                "font-family": "Arial",
                "font-weight": "bold",
            },
        ),
        dash_draggable.ResponsiveGridLayout(
            id="draggable",
            children=[
                html.Div(
                    id="draggable-books-count-bar",
                    children=[
                        dcc.Graph(
                            id="books-count-bar",
                            figure=get_books_by_author_count(),
                            responsive=True,
                            style={"min-height": "0", "flex-grow": "1"},
                        )
                    ],
                    style={
                        "height": "100%",
                        "width": "100%",
                        "display": "flex",
                        "flex-direction": "column",
                        "flex-grow": "0",
                    },
                ),
                dcc.Graph(
                    id="books-by-year-bar",
                    figure=get_books_by_year(),
                    responsive=True,
                    style={"min-height": "0", "flex-grow": "1"},
                ),
                dcc.Graph(
                    id="expenditure-by-year-bar",
                    figure=get_expenditure_by_year(),
                    responsive=True,
                    style={"min-height": "0", "flex-grow": "1"},
                ),
                dcc.Graph(
                    id="books-types-pie",
                    figure=get_count_books_by_types(),
                    responsive=True,
                    style={"min-height": "0", "flex-grow": "1"},
                ),
                dcc.Graph(
                    id="books-availability-pie",
                    figure=get_books_availability(),
                    responsive=True,
                    style={"min-height": "0", "flex-grow": "1"},
                ),
                html.Div(
                    id="draggable-dropdown-type-filter",
                    children=[
                        html.H2(
                            "Livros por tipo",
                            style={
                                "textAlign": "center",
                                "margin": "20px 20px 20px 50px",
                                "font-size": "17px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "color": "#566573",
                            },
                        ),
                        dcc.Dropdown(
                            id="dropdown-type-filter",
                            options=[
                                {"label": tipo, "value": tipo}
                                for tipo in get_books_by_type()["Tipo"].unique()
                            ],
                            multi=True,
                            placeholder="Selecione o(s) tipo(s) de livro(s) para filtrar",
                        ),
                        dash_table.DataTable(
                            id="table",
                            columns=[
                                {"name": i, "id": i}
                                for i in get_books_by_type().columns
                            ],
                            page_size=9,
                            sort_action="native",
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell={"textAlign": "center"},
                        ),
                    ],
                    style={"min-height": "0", "flex-grow": "1"},
                ),
                html.Div(
                    id="draggable-books-read-in-each-year",
                    children=[
                        html.H2(
                            "Livros lidos em cada ano",
                            style={
                                "textAlign": "center",
                                "margin": "20px 20px 20px 50px",
                                "font-size": "17px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "color": "#566573",
                            },
                        ),
                        dcc.Dropdown(
                            id="dropdown-year-filter",
                            options=[
                                {"label": str(ano), "value": ano}
                                for ano in get_books_read_in_each_year()[
                                    "Ano da leitura"
                                ].unique()
                            ],
                            placeholder="Selecione o ano para filtrar",
                        ),
                        dash_table.DataTable(
                            id="table-books-read-in-each-year",
                            columns=[
                                {"name": i, "id": i}
                                for i in get_books_read_in_each_year().columns
                            ],
                            page_size=9,
                            sort_action="native",
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell={"textAlign": "center"},
                        ),
                    ],
                ),
                html.Div(
                    id="draggable-books-prices",
                    children=[
                        html.H2(
                            "Preços dos livros",
                            style={
                                "textAlign": "center",
                                "margin": "20px 20px 20px 50px",
                                "font-size": "17px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "color": "#566573",
                            },
                        ),
                        dash_table.DataTable(
                            id="table-books-prices",
                            columns=[
                                {
                                    "name": i,
                                    "id": i,
                                    "type": "numeric",
                                    "format": Format(precision=2, scheme=Scheme.fixed),
                                }
                                for i in get_books_prices().columns
                            ],
                            data=get_books_prices().to_dict(orient="records"),
                            page_size=9,
                            sort_action="native",
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell={"textAlign": "center"},
                        ),
                    ],
                ),
                dcc.Graph(
                    id="avg-book-price",
                    figure=get_avg_books_price(),
                ),
                dcc.Graph(
                    id="avg-book-price-by-type-physical",
                    figure=get_avg_book_price_by_type("Físico"),
                ),
                dcc.Graph(
                    id="avg-book-price-by-type-digital",
                    figure=get_avg_book_price_by_type("Digital"),
                ),
                html.Div(
                    id="draggable-books-not-available",
                    children=[
                        html.H2(
                            "Livros não disponíveis",
                            style={
                                "textAlign": "center",
                                "margin": "20px 20px 20px 50px",
                                "font-size": "17px",
                                "font-family": "Arial",
                                "font-weight": "normal",
                                "color": "#566573",
                            },
                        ),
                        dash_table.DataTable(
                            id="table-books-not-available",
                            columns=[
                                {"name": i, "id": i}
                                for i in get_books_not_available().columns
                            ],
                            data=get_books_not_available().to_dict(orient="records"),
                            page_size=9,
                            sort_action="native",
                            style_header={
                                "backgroundColor": "rgb(230, 230, 230)",
                                "fontWeight": "bold",
                                "textAlign": "center",
                            },
                            style_cell={"textAlign": "center"},
                        ),
                    ],
                ),
            ],
        ),
    ]
)


@app.callback(Output("table", "data"), [Input("dropdown-type-filter", "value")])
def update_table(selected_types) -> list:
    df_books_by_type = get_books_by_type()
    filtered_data = (
        df_books_by_type
        if not selected_types
        else df_books_by_type[df_books_by_type["Tipo"].isin(selected_types)]
    )
    return filtered_data.to_dict(orient="records")


@app.callback(
    Output("table-books-read-in-each-year", "data"),
    [Input("dropdown-year-filter", "value")],
)
def update_table_books_read_in_each_year(selected_year) -> list:
    df_books_read_in_each_year = get_books_read_in_each_year()
    filtered_data = (
        df_books_read_in_each_year
        if not selected_year
        else df_books_read_in_each_year[
            df_books_read_in_each_year["Ano da leitura"] == selected_year
        ]
    )
    return filtered_data.to_dict(orient="records")


if __name__ == "__main__":
    app.run_server(debug=True)
