import pandas as pd

df = pd.read_excel("Superstoredata.xls")  # Or Superstore.xlsx depending on your file

print("Preview of Data:")
print(df.head())

def get_schema(df):
    return "Table: sales(" + ", ".join([f"{col}" for col in df.columns]) + ")"

schema = get_schema(df)
print("\nInferred Schema:")
print(schema)

import gradio as gr
import pandas as pd
import duckdb
import requests

# Clean up the SQL from the model
def clean_sql_output(raw_sql):
    for junk in ["<s>", "</s>", "QUERY", "Query:", "query:"]:
        raw_sql = raw_sql.replace(junk, "")
    raw_sql = raw_sql.strip()

    if raw_sql.startswith("#") or raw_sql.startswith("--"):
        raw_sql = raw_sql.lstrip("#- ").strip()

    if raw_sql.lower().startswith("aggregate"):
        inside = raw_sql[9:].strip()
        if inside.endswith(")"):
            inside = inside[:-1]
        raw_sql = f"SELECT {inside}"

    if not raw_sql.lower().startswith("select"):
        raw_sql = "SELECT " + raw_sql

    return raw_sql.strip()


# Talk to Ollama + generate SQL
def ask_sql_ollama(question, schema):
    prompt = f"""
You are an expert SQL assistant.
You are querying a table named 'sales' with these columns:
{schema}

Translate the question into DuckDB-compatible SQL.
Do not explain. Only return the SQL.
Q: {question}
SQL:
"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "sqlcoder", "prompt": prompt, "stream": False}
    )
    return clean_sql_output(response.json().get("response", ""))


#  Main logic for UI
def query_sales(file, question):
    try:
        df = pd.read_excel(file.name)
        df.columns = df.columns.str.replace(" ", "_")
        schema = ", ".join(df.columns)

        sql = ask_sql_ollama(question, schema)

        if not sql or len(sql) < 10:
            return sql, "❌ Could not generate SQL query."

        con = duckdb.connect()
        con.register("sales", df)
        result = con.execute(sql).df()
        return sql, result

    except Exception as e:
        return "", f" Error: {e}"


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Offline English to SQL Assistant (Powered by Ollama + DuckDB)")
    gr.Markdown("Upload your Excel file, ask a question in English, get the SQL + result!")

    file_input = gr.File(label="📂 Upload Excel File (.xls or .xlsx)", file_types=[".xls", ".xlsx"])
    question_input = gr.Textbox(label="📝 Ask your question", placeholder="e.g. What are the top 5 states by sales?")
    run_btn = gr.Button("Run Query")

    sql_output = gr.Textbox(label="🧾 Generated SQL Query")
    result_output = gr.Dataframe(label=" Query Result")

    run_btn.click(query_sales, inputs=[file_input, question_input], outputs=[sql_output, result_output])

#Launch it!
demo.launch()


