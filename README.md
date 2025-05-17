# egnlishtosql-ollama
# English to SQL Assistant (Offline, with Ollama)

This is a lightweight, offline AI assistant that lets you upload Excel files and ask natural language questions. It generates SQL using a local LLM (`sqlcoder` via Ollama) and runs it on your data with DuckDB.

## Features
- Upload `.xls` or `.xlsx`
- Ask in plain English
- See generated SQL
- View results in a table
- 100% offline (no OpenAI API)

## How to Run

1. Install [Ollama](https://ollama.com/download) and run:

   ```bash
   ollama run sqlcoder
