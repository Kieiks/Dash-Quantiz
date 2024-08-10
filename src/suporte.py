import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
import plotly.graph_objects as go

# Install nltk resources if not already installed
nltk.download('stopwords')
def filtro_texto(df, coluna):
    
    portuguese_stop_words = set(stopwords.words('portuguese'))
    # Concatenate all titles into a single string, converting to lowercase
    all_titles = ' '.join(df[coluna]).lower()

    # Use regular expression to extract words, ignoring punctuation
    words = re.findall(r'\w+', all_titles)

    # Filter out stop words
    filtered_words = [word for word in words if word not in portuguese_stop_words]

    # Count occurrences of each word
    word_counts = Counter(filtered_words)

    # Convert to list of tuples and sort by frequency in descending order
    word_count_tuples = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    return word_count_tuples[:5]

def count_chart(df, col_chosen):
    df_chart = df[col_chosen].value_counts().nlargest(5).reset_index()
    df_chart.columns = [col_chosen, "count"]
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df_chart[col_chosen],
            x=df_chart["count"],
            orientation="h",
            marker_color="#041E41",
            text=df_chart["count"],
            textfont=dict(size=15),
        )
    )

    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=15))

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        bargap=0.3,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10, pad=15),
    )
    return fig


# Function to create a price chart


def price_chart(df, col_chosen):
    top_5 = df[col_chosen].value_counts().nlargest(5).index
    df_top_5 = df[df[col_chosen].isin(top_5)]
    fig = go.Figure()

    fig.add_trace(
        go.Box(
            x=df_top_5[col_chosen],
            y=df_top_5["Preco"],
            boxpoints="all",
            pointpos=0,
            jitter=0.5,
            whiskerwidth=0.2,
            marker_size=7,
            line_width=1,
            marker_color="#041E41",
            text=[i for i in df_top_5["Titulo"]],
            hovertemplate="<b>%{x}</b><br>%{text}<br><b>Preço</b>: %{y:.2f}<br>",
        )
    )

    for i in top_5:
        value = df_top_5[df_top_5[col_chosen] == i]["Preco"].median()

        fig.add_annotation(
            x=i,
            y=value,
            text=f"{value:.2f}",
            showarrow=False,
            bgcolor="white",
        )
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(tickfont=dict(size=15))

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig