# Stock Data Ingest

Sistema automatizado de ingestão e análise de dados financeiros do mercado brasileiro de ações e FIIs, com processamento inteligente via LLMs (OpenAI GPT / Anthropic Claude).

## Visão Geral

Pipeline completo de ETL (Extract, Transform, Load) para dados financeiros de múltiplas fontes, com análise automatizada por IA:

- **Extração**: Web scraping automatizado via Selenium
- **Transformação**: Processamento com GPT-4o ou Claude Sonnet 4
- **Carga**: Estruturação em CSV e Markdown

### Fontes de Dados

| Fonte | Dados Extraídos | Formato Output |
|-------|----------------|----------------|
| **Suno Research** | Relatórios de análise | Markdown (resumos) |
| **Suno Research** | Carteiras recomendadas | CSV estruturado |
| **Meus Dividendos** | Carteira pessoal | CSV estruturado |

## Arquitetura
```
stock-data-ingest/
├── automation/
│   ├── analysis/                    # Módulo de processamento com IA
│   │   ├── claude_client.py        # Cliente Anthropic Claude
│   │   ├── openai_client.py        # Cliente OpenAI GPT
│   │   └── processors.py           # Processadores de dados
│   │
│   ├── suno/                        # Módulo Suno Research
│   │   ├── auth.py                 # Autenticação
│   │   ├── reports.py              # Scraper de relatórios
│   │   └── wallets.py              # Scraper de carteiras
│   │
│   ├── meus_dividendos/            # Módulo Meus Dividendos
│   │   └── scraper.py              # Scraper de carteira pessoal
│   │
│   ├── config.py                    # Configurações e variáveis de ambiente
│   ├── driver.py                    # Gerenciador Selenium WebDriver
│   └── utils.py                     # Utilitários (parsing, limpeza HTML)
│
├── downloads-publico/               # Dados públicos (gitignored)
│   ├── html-relatorios/
│   ├── resumos-relatorios/
│   ├── html-carteiras/
│   ├── html-carteiras-csv/
│   └── carteiras-csv/
│
├── downloads-privado/               # Dados privados (gitignored)
│   ├── meus-dividendos/
│   └── meus-dividendos-csv/
│
├── file-stock-extractor.ipynb       # Notebook principal de execução
├── .env                             # Credenciais (não versionado)
└── requirements.txt
```

## Funcionalidades Detalhadas

### 1. Relatórios Suno Research

**Extração:**
- Acessa portal Suno Research
- Detecta relatórios não lidos (via opacity CSS)
- Salva HTML completo de cada relatório

**Processamento com IA:**
- Identifica recomendações de COMPRA/VENDA/AJUSTE
- Extrai: ticker, preço-teto, alocação, dividend yield
- Gera resumo estruturado em Markdown
- Classifica arquivos: `com-recomendacao-` ou `sem-recomendacao-`

### 2. Carteiras Suno Research

**Pipeline de 3 etapas:**
```
HTML → Markdown (IA extrai tabelas) → CSV normalizado (IA padroniza colunas)
```

**Carteiras suportadas:**
- Carteiras nacionais (ações e FIIs)
- Carteira internacional (5 variações)
- Fundos imobiliários (múltiplas carteiras)

**Normalização CSV:**
- Colunas padronizadas: Posição, Ticker, Empresa, Setor, Preço de Entrada, Preço Atual, Preço Teto, Peso na Carteira, Rentabilidade, Dividend Yield, Recomendação
- Adiciona coluna "Tipo Carteira" automaticamente

### 3. Meus Dividendos

**Extração:**
- Login automatizado
- Navega até SmartFolio > Carteira > Todos
- Extrai tabela HTML da carteira completa
- Remove atributos CSS desnecessários

**Processamento:**
- Conversão direta HTML → CSV via IA
- Mantém estrutura e títulos originais

## Instalação

### 1. Pré-requisitos
```bash
# Python 3.8+
# Chrome/Chromium instalado no sistema
```

### 2. Dependências
```bash
pip install webdriver-manager selenium openai python-dotenv beautifulsoup4 yfinance anthropic
```

**Pacotes principais:**
- `selenium` - Automação de navegador
- `webdriver-manager` - Gerenciamento automático do ChromeDriver
- `openai` - API OpenAI GPT
- `anthropic` - API Anthropic Claude
- `beautifulsoup4` - Parsing e limpeza de HTML
- `yfinance` - Dados financeiros complementares

### 3. Configuração de Credenciais

Crie `.env` na raiz do projeto:
```env
# Suno Research
SUNO_EMAIL=seu_email@example.com
SUNO_PASSWORD=sua_senha_segura

# Meus Dividendos
MEUS_DIVIDENDOS_EMAIL=seu_email@example.com
MEUS_DIVIDENDOS_PASSWORD=sua_senha_segura

# LLM APIs
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 💻 Uso

### Jupyter Notebook

Execute `file-stock-extractor.ipynb` célula por célula:

#### 1. Configuração Inicial
```python
# Escolha o provider de IA
PROVIDER = "claude"  # ou "openai"

# Inicializa WebDriver (manter aberto durante toda sessão)
driver = get_or_create_driver(driver)
```

#### 2. Pipeline Suno - Relatórios
```python
# Extração
login_suno(driver)
download_suno_reports(driver, os.path.join(DOWNLOADS_PUBLIC, "html-relatorios"))

# Processamento com IA
process_reports(
    html_folder=os.path.join(DOWNLOADS_PUBLIC, "html-relatorios"),
    output_folder=os.path.join(DOWNLOADS_PUBLIC, "resumos-relatorios"),
    provider=PROVIDER
)
```

**Output:** Arquivos `.md` com resumos classificados

#### 3. Pipeline Suno - Carteiras
```python
# Extração
login_suno(driver)
download_suno_wallets(driver, os.path.join(DOWNLOADS_PUBLIC, "html-carteiras"))

# Processamento (2 etapas)
process_suno_wallets_step1_html_to_md(html_folder, md_folder)
process_suno_wallets_step2_md_to_csv(md_folder, csv_folder)
```

**Output:** Arquivos `.csv` com carteiras normalizadas

#### 4. Pipeline Meus Dividendos
```python
# Extração
download_meus_dividendos_wallet(driver, os.path.join(DOWNLOADS_PRIVATE, "meus-dividendos"))

# Processamento
process_meus_dividendos_to_csv(html_file, csv_folder)
```

**Output:** `carteira-meus-dividendos-YYYY-MM-DD.csv`

## 🧠 Detalhes Técnicos

### LLM Clients

**OpenAI Client:**
- Modelo padrão: `gpt-4o`
- Temperature: 0.7 (análise) / 0 (conversão)
- Max tokens: 4096-16384 (adaptativo)
- Response format: JSON para relatórios

**Claude Client:**
- Modelo padrão: `claude-sonnet-4-20250514`
- Temperature: 0.7 (análise) / 0 (conversão)
- Max tokens: 8192
- System prompt otimizado para análise financeira

### Web Scraping

**Estratégias de Web Scraping:**
- Scroll infinito com detecção de novos elementos
- Detecção de relatórios lidos (opacity CSS)
- Retry logic para elementos stale
- Alternância de janelas para múltiplas páginas
- Preferência por xpath em vez de css
- Wait dinâmico com WebDriverWait

**Estratégias de seletores:**
- **Preferência por CSS Selectors** para elementos com classes/IDs estáveis
- **XPath seletivo** apenas para buscas por texto interno (ex: botões sem IDs)
- **Prioridade**: ID > CSS Class > XPath

**Limpeza de HTML:**
- Remove: scripts, styles, SVG, nav, forms
- Remove atributos: style, data-*, onclick, class, id, etc
- Mantém estrutura semântica para processamento LLM

### Processamento de Dados

**Prompts especializados:**
- **Relatórios**: Identificação de recomendações + resumo executivo
- **Carteiras**: Extração tabular com padronização de colunas
- **Meus Dividendos**: Conversão direta mantendo estrutura

**Filtros inteligentes:**
- Processa apenas arquivos criados no dia atual
- Skip de arquivos já processados (checksum por nome)
- Classificação automática por prefixo

## 🔄 Fluxo de Dados

```
┌─────────────────┐
│  Suno Research  │
│   (Web Login)   │
└────────┬────────┘
         │
         ├──> Relatórios HTML
         │         │
         │         └──> [GPT/Claude] ──> Markdown (resumos)
         │
         └──> Carteiras HTML
                   │
                   └──> [GPT/Claude] ──> MD ──> [GPT/Claude] ──> CSV

┌─────────────────┐
│Meus Dividendos  │
│   (Web Login)   │
└────────┬────────┘
         │
         └──> Carteira HTML ──> [GPT/Claude] ──> CSV
```

## Estrutura de Outputs

### Resumos de Relatórios (Markdown)
```markdown
# Análise PETR4 - Compra Recomendada

**Ticker**: PETR4  
**Recomendação**: COMPRA  
**Preço-teto**: R$ 42,50  
**Alocação sugerida**: 5%  

**Justificativa**:
Empresa apresenta fundamentos sólidos com P/L de 3.2x...
```

### Carteiras (CSV)
```csv
Posição,Ticker,Empresa,Setor,Preço de Entrada (R$),Preço Atual (R$),Preço Teto (R$),Peso na Carteira (%),Rentabilidade (%),Dividend Yield (%),Recomendação,Tipo Carteira
1,PETR4,Petrobras,Petróleo,32.50,38.20,42.50,8.5,17.54,12.3,MANTER,Dividendos
```

## Boas Práticas

### Segurança
- ✅ Credenciais via `.env` (nunca hardcoded)
- ✅ `.gitignore` para pastas de downloads
- ✅ Separação dados públicos/privados

### Performance
- ✅ Reutilização do WebDriver entre execuções
- ✅ Processamento batch com filtro de data
- ✅ Skip de arquivos já processados

### Manutenibilidade
- ✅ Modularização por fonte de dados
- ✅ Clientes LLM intercambiáveis (OpenAI/Claude)
- ✅ Logging descritivo em cada etapa

## ⚠️ Limitações e Avisos

### Confidencialidade
- **Aviso:** Este projeto foi criado para fins educacionais e de uso pessoal. Nenhum dado sensível ou proprietário é distribuído junto ao código. Execute apenas em fontes que você tem autorização para acessar.

---

## 🔧 Melhorias Futuras

#### 1. Sistema de Logging Estruturado
**Objetivo**: Rastreabilidade completa de execuções e debugging eficiente

**Requisitos:**
- Log rotativo diário em `logs/scraper_YYYYMMDD.log`
- Níveis apropriados: INFO (operações), WARNING (skips), ERROR (falhas)
- Formato: timestamp, módulo, nível, mensagem
- Console output simultâneo para execução interativa
- Stack traces completos em erros

**Benefícios:**
- Auditoria de execuções passadas
- Identificação rápida de padrões de falha
- Debugging sem precisar reproduzir erros

---

#### 2. Screenshots Automáticos em Falhas
**Objetivo**: Captura visual do estado do navegador quando algo falha

**Requisitos:**
- Salvamento automático em `logs/screenshots/error_NOME_TIMESTAMP.png`
- Captura ao detectar: TimeoutException, ElementNotFound, StaleElement
- Incluir URL atual e timestamp no log
- Limpeza automática de screenshots > 30 dias

**Benefícios:**
- Debugging visual de seletores quebrados
- Identificação de mudanças no layout dos sites
- Reduz tempo de troubleshooting

---

#### 3. Retry Logic com Backoff Exponencial (conecta com a última melhoria)
**Objetivo**: Resiliência a falhas temporárias de rede/elementos

**Requisitos:**
- Decorator `@retry_on_exception` configurável
- 3 tentativas padrão com delays: 2s, 4s, 8s (backoff exponencial)
- Aplicar em: clicks, buscas de elementos, fetch de páginas
- Log de cada tentativa falha
- Exceções específicas para retry: StaleElement, Timeout, WebDriverException

**Benefícios:**
- Reduz falhas por timing issues
- Lida com instabilidades momentâneas dos sites
- Melhora taxa de sucesso geral

---

#### 4. Validação de Integridade de Dados
**Objetivo**: Garantir qualidade dos dados extraídos antes de salvar

**Requisitos:**
- Schemas de validação para: Carteiras (tickers, percentuais), Relatórios (estrutura JSON)
- Verificações: tickers válidos (4-6 chars), percentuais (0-100%), preços (> 0)
- Quarentena de dados inválidos em `logs/invalid_data/`
- Alertas quando > 20% dos dados falham validação
- Relatório de qualidade de dados por execução

**Benefícios:**
- Detecta mudanças estruturais nos sites fonte
- Previne propagação de dados corrompidos
- Alerta precoce de problemas

---

#### 5. Page Object Pattern (POP)
**Objetivo**: Manutenibilidade e isolamento de seletores

**Requisitos:**
- Classes por página: `SunoLoginPage`, `SunoReportsPage`, `SunoWalletsPage`, `MeusDividendosPage`
- Encapsular: locators, ações (login, click, scroll), validações
- Seletores centralizados (fácil atualização quando sites mudam)
- Métodos fluent: `page.login().navigate_to_reports()`

**Benefícios:**
- Seletores quebrados? Atualiza em 1 lugar só
- Código mais legível e testável
- Reutilização de lógica comum

---

#### 6. Context Manager para Gerenciamento de Janelas
**Objetivo**: Simplificar navegação entre múltiplas abas/janelas

**Requisitos:**
- Context manager `with switch_to_new_window(driver):` 
- Automação de: detecção de nova janela, switch, close, retorno
- Timeout configurável para janela aparecer
- Tratamento de erro: fecha janela e retorna mesmo em exceção

**Benefícios:**
- Elimina código boilerplate repetitivo
- Garante sempre retorno à janela original
- Reduz bugs de janelas órfãs

---

#### 7. Healthcheck e Auto-Recovery do Driver
**Objetivo**: Detectar e recuperar de crashes do WebDriver

**Requisitos:**
- Função `is_driver_alive()` antes de operações críticas
- Auto-reinicialização em caso de crash
- Preservação do estado: cookies, sessão (se possível)
- Limite de tentativas de recovery (3x) antes de falha total

**Benefícios:**
- Execuções longas mais estáveis
- Reduz necessidade de intervenção manual
- Continua de onde parou em caso de crash

---

#### 8. Métricas e Monitoramento
**Objetivo**: Visibilidade de performance e saúde do pipeline

**Requisitos:**
- Métricas por execução: duração total, itens processados, taxa de sucesso, erros
- Salvamento em `logs/metrics_YYYYMMDD.json`
- Dashboard opcional (Streamlit) com histórico
- Alertas quando: taxa de erro > 10%, duração > 2x média, 0 itens extraídos

**Benefícios:**
- Identificação de degradação de performance
- Planejamento de otimizações baseado em dados
- Detecção proativa de problemas

---

#### 9. Modo Headless Configurável
**Objetivo**: Execução em servidores sem GUI

**Requisitos:**
- Flag `HEADLESS=true` no `.env`
- Opções adicionais: `--disable-gpu`, `--no-sandbox` (para Docker)
- Window size configurável para screenshots consistentes
- User-agent realista para evitar detecção

**Uso:**
- Execução em servidores Linux
- CI/CD pipelines
- Scheduled tasks (cron)

---

#### 10. Containerização com Docker
**Objetivo**: Ambiente reproduzível e deploy simplificado

**Requisitos:**
- `Dockerfile` com Python 3.8+, Chrome, ChromeDriver
- Volume mounts para: `.env`, `downloads-*`, `logs/`
- Docker Compose para orquestração
- Imagem otimizada (< 500MB se possível)

**Benefícios:**
- "Funciona na minha máquina" resolvido
- Deploy em cloud (AWS ECS, GCP Cloud Run)
- Isolamento de dependências

---

#### 11. Scheduler Integrado
**Objetivo**: Execução automática diária sem cron manual

**Requisitos:**
- Biblioteca `schedule` ou `APScheduler`
- Configuração: horário de execução, dias da semana
- Execução em background como daemon
- Logs de cada execução agendada

**Configuração exemplo:**
```env
SCHEDULE_ENABLED=true
SCHEDULE_TIME=08:00
SCHEDULE_DAYS=MON,TUE,WED,THU,FRI
```

---

#### 12. Testes Automatizados
**Objetivo**: Garantir funcionamento após mudanças

**Requisitos:**
- **Unit tests**: Funções de parsing, limpeza HTML, validações
- **Integration tests**: Login, navegação básica (com mock/recording)
- **Smoke tests**: Verifica se sites ainda acessíveis
- Framework: `pytest` com fixtures para driver
- CI/CD: rodar testes em cada PR

**Benefícios:**
- Confiança para refatorar
- Detecta breaking changes nos sites
- Documentação viva do comportamento esperado

---

#### 13. Notificações de Execução
**Objetivo**: Alertas sobre conclusão e problemas

**Requisitos:**
- Canais: Email, Telegram, Slack (configurável)
- Notificar quando: execução completa, erros críticos, dados inválidos
- Resumo: itens processados, tempo total, taxa de sucesso
- Throttling: não spammar (máx 1 notificação/hora)

**Configuração exemplo:**
```env
NOTIFY_EMAIL=seu@email.com
NOTIFY_TELEGRAM_TOKEN=...
NOTIFY_ON=completion,errors
```

---

#### 14. Auto-Repair de Seletores com LLM
**Objetivo**: Recuperação automática quando seletores CSS/XPath quebram

**Problema:**
Sites frequentemente mudam estrutura HTML, quebrando seletores. Atualmente requer:
- Inspeção manual do HTML
- Identificação do novo seletor
- Atualização do código
- Redeploy

**Solução Proposta:**
Sistema inteligente que usa LLM para descobrir novos seletores automaticamente.

**Requisitos Funcionais:**

1. **Detecção de Seletor Quebrado**
   - Captura `NoSuchElementException` ou `TimeoutException`
   - Identifica qual seletor falhou e seu contexto (ex: "botão login", "tabela carteira")
   - Salva screenshot + HTML da página atual

2. **Análise com LLM**
   - Extrai HTML relevante (body ou section específica)
   - Envia para GPT-4o/Claude com prompt especializado
   - Context: descrição semântica do elemento ("botão com texto 'Login'", "tabela com colunas ticker/preço")
   - LLM retorna: novos seletores candidatos (CSS + XPath alternativo)

3. **Validação de Seletores Sugeridos**
   - Testa cada seletor candidato na página atual
   - Valida: elemento encontrado, visível, clicável (se botão)
   - Verifica se múltiplos elementos (ambiguidade)
   - Ranking por confiabilidade

4. **Aplicação e Logging**
   - Usa seletor validado temporariamente para continuar execução
   - Salva mapeamento em `logs/selector_repairs.json`:
```json
     {
       "timestamp": "2026-01-06T10:30:00",
       "page": "SunoLoginPage",
       "element": "LOGIN_BUTTON",
       "old_selector": {"type": "ID", "value": "login_button"},
       "new_selector": {"type": "CSS", "value": "button[type='submit'].login-btn"},
       "confidence": 0.95,
       "status": "temporary"
     }
```
   - Gera alerta para revisão manual
   - Cria PR automático (opcional) com sugestão de fix

5. **Fallback Strategy**
   - Tentativa 1: Seletor original
   - Tentativa 2: Seletores históricos (de `selector_repairs.json`)
   - Tentativa 3: LLM auto-repair
   - Tentativa 4: Notifica falha crítica e pausa execução

**Prompt LLM Especializado:**
```
Você é um especialista em web scraping e seletores CSS/XPath.

CONTEXTO:
- Página: {page_name}
- Elemento buscado: {element_description}
- Seletor antigo (quebrado): {old_selector}

TAREFA:
Analise o HTML abaixo e sugira 3 seletores alternativos (ordem de preferência):
1. CSS Selector (preferencial)
2. XPath com texto
3. XPath estrutural

CRITÉRIOS:
- Seletor deve ser específico (evitar ambiguidade)
- Priorizar IDs/classes estáveis
- Evitar índices numéricos ([1], [2])
- Considerar acessibilidade (aria-labels, data-testid)

HTML:
{html_snippet}

RESPOSTA (JSON):
{
  "selectors": [
    {"type": "CSS", "value": "...", "confidence": 0.9, "reasoning": "..."},
    {"type": "XPATH", "value": "...", "confidence": 0.7, "reasoning": "..."}
  ],
  "changes_detected": "Descrição do que mudou no HTML"
}
```

**Requisitos Técnicos:**

- **Parsing inteligente de HTML**:
  - Extrair apenas seção relevante (não enviar HTML completo)
  - Limite: 4000 tokens para LLM
  - Priorizar: ancestors do elemento antigo, siblings, elementos com texto similar

- **Cache de seletores**:
  - SQLite ou JSON com histórico de mudanças
  - TTL: considerar seletor "estável" após 30 dias sem falha
  - Versionamento: rastrear quando cada seletor funcionou

- **Rate limiting LLM**:
  - Máx 10 tentativas/dia (custo)
  - Não tentar auto-repair em loop infinito
  - Backoff: 1h entre tentativas para mesmo seletor

- **Segurança**:
  - Nunca executar JavaScript sugerido pelo LLM
  - Validar seletores em sandbox primeiro
  - Whitelist de atributos permitidos

**Configuração (.env):**
```env
AUTO_REPAIR_ENABLED=true
AUTO_REPAIR_MAX_ATTEMPTS=3
AUTO_REPAIR_CONFIDENCE_THRESHOLD=0.8
AUTO_REPAIR_NOTIFY_EMAIL=dev@example.com
```

**Fluxo de Execução:**
```
Seletor falha
    ↓
Screenshot + HTML
    ↓
LLM analisa → Sugere novos seletores
    ↓
Valida cada sugestão
    ↓
Seletor válido encontrado?
    ├─ SIM → Usa temporariamente + Log + Alerta
    └─ NÃO → Fallback manual + Pausa execução
```

**Benefícios:**
- **Reduz downtime**: De horas/dias para minutos
- **Reduz custos**: Menos manutenção manual
- **Dados históricos**: Aprende padrões de mudança dos sites
- **Semi-automação**: Sugestões precisam aprovação humana

**Riscos e Mitigações:**

| Risco | Mitigação |
|-------|-----------|
| LLM sugere seletor errado | Validação obrigatória antes de usar |
| Custos de API elevados | Rate limiting + cache agressivo |
| Loop infinito de tentativas | Máximo 3 tentativas/seletor/dia |
| Falso positivo (elemento errado) | Validação semântica (texto esperado) |
| HTML gigante > limite tokens | Extração inteligente só de seção relevante |

---

**Desenvolvido com ☕**
