import os
import glob
from datetime import datetime, date
from automation.analysis.openai_client import AnalysisClient
from automation.analysis.claude_client import ClaudeClient

def get_client(provider="openai"):
    if provider == "claude":
        return ClaudeClient()
    else:
        return AnalysisClient()

def process_reports(html_folder, output_folder, provider="openai"):
    """
    Processes HTML reports into Markdown summaries using OpenAI or Claude.
    """
    client = get_client(provider)
    os.makedirs(output_folder, exist_ok=True)
    today = date.today()
    
    # List HTML files created today
    html_files = [
        os.path.join(html_folder, f) 
        for f in os.listdir(html_folder)
        if f.endswith(".html") and datetime.fromtimestamp(os.path.getctime(os.path.join(html_folder, f))).date() == today
    ]
    
    print(f"Encontrados {len(html_files)} relatórios de hoje para processar.")
    
    for file_path in html_files:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # Check if already processed
        # Simplified check: looking for any file starting with prefix-filename
        existing = glob.glob(os.path.join(output_folder, f"*-{file_name}.md"))
        if existing:
            print(f"Pulando {file_name} (já processado).")
            continue
            
        print(f"Processando: {file_name}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
                
            prompt = f"""
                Você é um especialista em investimentos de longo prazo. Receberá a seguir um relatório em HTML.
    
                **TAREFA**:
                1. Apenas se o relaótio não for o "radar-fii" (que tem uma extensa lista de FIIs e seus índices), verificar se o relatório contém recomendação de COMPRA, VENDA ou AJUSTE DE CARTEIRA de algum ativo.
                2. Caso contenha, listar (em Markdown):
                - Nome do ativo
                - Se é compra, venda ou ajuste
                - Preço-teto (se houver)
                - Percentual de alocação (se houver)
                - Curta justificativa
                3. Se não houver nenhuma recomendação (ou for o "radar-fii"), apresente apenas um resumo sucinto do conteúdo (em Markdown), enfatizando o que for relevante para investimentos de longo prazo.
                4. Evite adjetivos em excesso.
                5. Retorne JSON com keys: "fileNamePrefix" ("com-recomendacao" ou "sem-recomendacao") e "result" (markdown).
    
                **RELATÓRIO (HTML)**:
                {html_content}
            """
            
            # Select model based on provider logic or defaults
            model = "gpt-4o" if provider == "openai" else "claude-sonnet-4-20250514"
            response = client.analyze_report(prompt, model=model)
            
            if isinstance(response, dict):
                prefix = response.get("fileNamePrefix", "nd")
                result = response.get("result", "")
                
                output_file = os.path.join(output_folder, f"{prefix}-{file_name}.md")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"Salvo: {output_file}")
            else:
                print(f"Erro: Resposta inesperada para {file_name}: {response}")
                
        except Exception as e:
            print(f"Erro ao processar {file_name}: {e}")

def process_suno_wallets_step1_html_to_md(html_folder, output_md_folder, provider="openai"):
    """Step 1: Convert Suno HTML wallets to MD (containing CSV data)"""
    client = get_client(provider)
    os.makedirs(output_md_folder, exist_ok=True)
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    html_files = [
        os.path.join(html_folder, f) 
        for f in os.listdir(html_folder)
        if f.endswith(".html") and datetime.fromtimestamp(os.path.getctime(os.path.join(html_folder, f))).date() == today
    ]
    
    print(f"Encontrados {len(html_files)} carteiras HTML de hoje para processar.")

    for file_path in html_files:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_md_folder, f"{file_name}-{today_str}.md")
        
        if os.path.exists(output_file):
            print(f"Pulando {file_name} (já convertido para MD).")
            continue
            
        print(f"Processando carteira: {file_name}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                 html_content = f.read()
    
            prompt = f"""
            - Você é um especialista em planilhas extremamente meticuloso. Receberá a seguir um relatório em HTML que contém dados tabulares.
            - Analise o conteúdo e organize as informações relevantes em um ou mais blocos CSV.
            - Retorne SOMENTE o texto em formato Markdown (.md), contendo as tabelas CSV.
            - Se precisar de mais de um CSV, separe-os com um título.
            - Ignore colunas sem dados.
            - Ignore a coluna "Ativo".
            
            Relatório (HTML):
            {html_content}
            """
            
            model = "gpt-4o" if provider == "openai" else "claude-sonnet-4-20250514"
            # Increase token limit for large spreadsheets
            result_md = client.convert_spreadsheet(prompt, model=model, max_tokens=8192 if provider=="claude" else 16384)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result_md)
            print(f"Salvo MD: {output_file}")
            
        except Exception as e:
            print(f"Erro ao processar carteira {file_name}: {e}")

def process_suno_wallets_step2_md_to_csv(md_folder, output_csv_folder, provider="openai"):
    """Step 2: Extract CSV from MD files and normalize columns"""
    client = get_client(provider)
    os.makedirs(output_csv_folder, exist_ok=True)
    today_str = date.today().strftime("%Y-%m-%d")
    
    # Filter for relevant files (simplified logic from original)
    md_files = glob.glob(os.path.join(md_folder, f"*-{today_str}.md"))
    
    print(f"Encontrados {len(md_files)} arquivos MD para converter em CSV.")
    
    for file_path in md_files:
        file_name_base = os.path.basename(file_path).replace(".md", ".csv")
        output_file = os.path.join(output_csv_folder, file_name_base)
        
        print(f"Convertendo para CSV: {os.path.basename(file_path)}...")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            prompt = f"""
            Você receberá um arquivo `.md` contendo tabelas em formato CSV.
            Nome do arquivo: {os.path.basename(file_path)}
            Sua tarefa é **extrair exclusivamente a tabela principal da carteira de ativos** e **padronizar os nomes das colunas**.
            
            1. Identifique a tabela correta.
            2. Padronize colunas para: Posição, Ticker, Empresa, Setor, Preço de Entrada (R$), Preço Atual (R$), Preço Teto (R$), Peso na Carteira (%), Rentabilidade (%), Dividend Yield (%), Recomendação.
            3. Mantenha formatação CSV (separado por , ou ; conforme padrão).
            4. Retorne APENAS a tabela CSV.
            5. Insira coluna 'Tipo Carteira'.
            
            Conteúdo:
            {content}
            """
            
            model = "gpt-4o" if provider == "openai" else "claude-sonnet-4-20250514"
            result_csv = client.convert_spreadsheet(prompt, model=model, max_tokens=8192 if provider=="claude" else 16384)
            
            # Clean markdown code blocks if any
            if result_csv.startswith("```csv"):
                result_csv = result_csv[6:]
            if result_csv.endswith("```"):
                result_csv = result_csv[:-3]
            result_csv = result_csv.strip()
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result_csv)
            print(f"Salvo CSV: {output_file}")
            
        except Exception as e:
            print(f"Erro ao converter {os.path.basename(file_path)}: {e}")

def process_meus_dividendos_to_csv(html_file, output_csv_folder, provider="openai"):
    """
    Converts Meus Dividendos HTML to CSV.
    """
    client = get_client(provider)
    os.makedirs(output_csv_folder, exist_ok=True)
    
    if not os.path.exists(html_file):
        print(f"File not found: {html_file}")
        return

    print(f"Processando Meus Dividendos: {os.path.basename(html_file)}...")

    try:
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        prompt = f"""
        - Você é um especialista em planilhas extremamente meticuloso. Receberá a seguir uma planilha em HTML.
        - Converta para CSV separado por ponto e vírgula (;).
        - Mantenha títulos.
        - Retorne APENAS o CSV.
        
        Planilha (HTML):
        {html_content}
        """
        
        model = "gpt-4o" if provider == "openai" else "claude-sonnet-4-20250514"
        csv_output = client.convert_spreadsheet(prompt, model=model, max_tokens=8192 if provider=="claude" else 16384)
        
        # Save
        today_str = date.today().strftime("%Y-%m-%d")
        filename = os.path.join(output_csv_folder, f"carteira-meus-dividendos-{today_str}.csv")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(csv_output)
        print(f"Salvo Meus Dividendos CSV: {filename}")
        
    except Exception as e:
        print(f"Erro ao processar Meus Dividendos: {e}")
