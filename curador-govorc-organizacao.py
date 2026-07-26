import os
import sys
import json
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime
import google.generativeai as genai
import typing_extensions as typing

# ==========================================
# CONFIGURAÇÕES DE AMBIENTE E APIs
# ==========================================
LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
AUTHOR_URN = os.environ.get('LINKEDIN_URN_ID')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

SENHA_APP_GMAIL = os.environ.get('SENHA_APP_GMAIL')
EMAIL_REMETENTE = "wellesmatias@gmail.com"
EMAIL_DESTINO = "wellesmatias@gmail.com"
AGENT_NAME = "Agente Orçamentário Multi-IA"

# Configuração do Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ ERRO: GEMINI_API_KEY não configurada.")
    sys.exit(1)

# ==========================================
# SEMENTES TEMÁTICAS (30 DIAS)
# ==========================================
# O bot usa isso apenas como "inspiração" diária. O texto será inédito.
THEME_SEEDS = [
    {"tema": "Uso de IA para Modelos Preditivos de Arrecadação", "produto_nome": "Livro: Python para Análise de Dados", "produto_url": "https://www.amazon.com.br/dp/B07P882X4G?tag=SEU_LINK_AQUI"},
    {"tema": "Detecção de Anomalias e Fraudes em Licitações com Machine Learning", "produto_nome": "Monitor LG Ultrawide 29'' IPS", "produto_url": "https://www.amazon.com.br/dp/B095198J2Y?tag=SEU_LINK_AQUI"},
    {"tema": "Processamento de Linguagem Natural (NLP) analisando o PPA e LDO", "produto_nome": "Livro: Data Science para Negócios", "produto_url": "https://www.amazon.com.br/dp/8576089726?tag=SEU_LINK_AQUI"},
    {"tema": "Automação de Pipelines de Dados (ETL) na Execução Financeira Pública", "produto_nome": "Teclado Ergonômico Logitech Wave Keys", "produto_url": "https://www.amazon.com.br/dp/B0CKD47X8Y?tag=SEU_LINK_AQUI"},
    {"tema": "Otimização Algorítmica de Portfólio de Obras Públicas", "produto_nome": "Livro: Rápido e Devagar - Daniel Kahneman", "produto_url": "https://www.amazon.com.br/dp/853900383X?tag=SEU_LINK_AQUI"},
    {"tema": "Categorização Automatizada de Despesas Públicas com IA", "produto_nome": "Fone de Ouvido Anker Soundcore Life Q30", "produto_url": "https://www.amazon.com.br/dp/B08HMWZBXC?tag=SEU_LINK_AQUI"},
    {"tema": "Visão Computacional e Drones na Medição de Contratos de Obras", "produto_nome": "Livro: Inteligência Artificial - Uma Abordagem Moderna", "produto_url": "https://www.amazon.com.br/dp/8535237013?tag=SEU_LINK_AQUI"},
    {"tema": "Análise de Sentimentos em Consultas Públicas do Orçamento Participativo", "produto_nome": "Suporte Articulado de Mesa para Monitor", "produto_url": "https://www.amazon.com.br/dp/B0765RFSZ7?tag=SEU_LINK_AQUI"},
    {"tema": "Smart Contracts e Blockchain para Repasses Constitucionais", "produto_nome": "Livro: A Quarta Revolução Industrial", "produto_url": "https://www.amazon.com.br/dp/8539007428?tag=SEU_LINK_AQUI"},
    {"tema": "Redes Neurais na Previsão de Fluxo de Caixa do Tesouro", "produto_nome": "SSD Kingston NV2 1TB NVMe M.2", "produto_url": "https://www.amazon.com.br/dp/B0BBWH1R8H?tag=SEU_LINK_AQUI"},
    {"tema": "Bancos de Dados em Grafo (GraphDB) para Detectar Conluios", "produto_nome": "Livro: Engenharia de Confiabilidade do Google", "produto_url": "https://www.amazon.com.br/dp/857522543X?tag=SEU_LINK_AQUI"},
    {"tema": "Gêmeos Digitais (Digital Twins) Simulando o Orçamento Público", "produto_nome": "Mouse Ergonômico Vertical Logitech MX", "produto_url": "https://www.amazon.com.br/dp/B07DKL44ZZ?tag=SEU_LINK_AQUI"},
    {"tema": "Agentes LLM em Pré-Auditoria de Conformidade (Tribunais de Contas)", "produto_nome": "Livro: Clean Architecture", "produto_url": "https://www.amazon.com.br/dp/8550804606?tag=SEU_LINK_AQUI"},
    {"tema": "Clustering de Demandas para Otimização de Compras Governamentais", "produto_nome": "Luminária de Mesa LED Baseus Screenbar", "produto_url": "https://www.amazon.com.br/dp/B08XBM7J3V?tag=SEU_LINK_AQUI"},
    {"tema": "Machine Learning para Previsão e Combate à Evasão Fiscal", "produto_nome": "Livro: Mãos à Obra: Aprendizado de Máquina", "produto_url": "https://www.amazon.com.br/dp/8550811777?tag=SEU_LINK_AQUI"},
    {"tema": "Aprendizado Federado (Federated Learning) entre Entes Federativos", "produto_nome": "Apple iPad Air", "produto_url": "https://www.amazon.com.br/dp/B09V3JG7B9?tag=SEU_LINK_AQUI"},
    {"tema": "RPA (Robotic Process Automation) na Conciliação Bancária do SIAFI", "produto_nome": "Livro: Automatize Tarefas Maçantes com Python", "produto_url": "https://www.amazon.com.br/dp/8575228129?tag=SEU_LINK_AQUI"},
    {"tema": "Transparência Algorítmica e Explainable AI (XAI) nos Gastos Públicos", "produto_nome": "Livro: Armas de Destruição Matemática", "produto_url": "https://www.amazon.com.br/dp/8532532456?tag=SEU_LINK_AQUI"},
    {"tema": "Arquitetura Data Mesh: Descentralizando Dados no Governo", "produto_nome": "Livro: Data Mesh - Zhamak Dehghani", "produto_url": "https://www.amazon.com.br/dp/1492092398?tag=SEU_LINK_AQUI"},
    {"tema": "Manutenção Preditiva de Ativos Públicos com IoT e IA", "produto_nome": "Monitor Dell 27'' 4K UHD", "produto_url": "https://www.amazon.com.br/dp/B09D8Q1K96?tag=SEU_LINK_AQUI"},
    {"tema": "Cibersegurança e Defesa Autônoma (IA) em Sistemas de Execução Orçamentária", "produto_nome": "Chave de Segurança Yubico YubiKey", "produto_url": "https://www.amazon.com.br/dp/B07HBD71HL?tag=SEU_LINK_AQUI"},
    {"tema": "Data Storytelling na Prestação de Contas ao Cidadão", "produto_nome": "Livro: Storytelling com Dados", "produto_url": "https://www.amazon.com.br/dp/8550804681?tag=SEU_LINK_AQUI"},
    {"tema": "Modelagem de Microdados para Otimização da Dívida Pública", "produto_nome": "Mesa com Regulagem de Altura Elétrica", "produto_url": "https://www.amazon.com.br/dp/B09JGG2BQR?tag=SEU_LINK_AQUI"},
    {"tema": "APIs e Arquitetura de Open Finance aplicadas à Arrecadação", "produto_nome": "Livro: A Era das Criptomoedas", "produto_url": "https://www.amazon.com.br/dp/8537816825?tag=SEU_LINK_AQUI"},
    {"tema": "Survival Analysis (Análise de Sobrevivência) em Projetos Sociais", "produto_nome": "Mousepad Gamer Extra Grande Corsair", "produto_url": "https://www.amazon.com.br/dp/B01798VS4C?tag=SEU_LINK_AQUI"},
    {"tema": "Chatbots Jurídicos baseados em LLMs para Ordenadores de Despesa", "produto_nome": "Teclado Mecânico Keychron K2", "produto_url": "https://www.amazon.com.br/dp/B07Y9Y69N7?tag=SEU_LINK_AQUI"},
    {"tema": "Inteligência Geoespacial (GeoAI) na Atualização do IPTU", "produto_nome": "Mouse Sem Fio Logitech MX Master 3S", "produto_url": "https://www.amazon.com.br/dp/B0B11QNDBD?tag=SEU_LINK_AQUI"},
    {"tema": "Práticas DevOps e CI/CD na Estabilidade do Portal da Transparência", "produto_nome": "Livro: Manual de DevOps", "produto_url": "https://www.amazon.com.br/dp/8550802492?tag=SEU_LINK_AQUI"},
    {"tema": "Machine Learning para Alocação Otimizada de RH no Serviço Público", "produto_nome": "Carregador Sem Fio Anker", "produto_url": "https://www.amazon.com.br/dp/B07THHQMHM?tag=SEU_LINK_AQUI"},
    {"tema": "Aprendizado por Reforço (Reinforcement Learning) no Timing de Licitações", "produto_nome": "Livro: Reinforcement Learning (Sutton)", "produto_url": "https://www.amazon.com.br/dp/0262039249?tag=SEU_LINK_AQUI"}
]

# ==========================================
# AGENTES DE IA (GEMINI)
# ==========================================

def get_daily_seed():
    """Seleciona o tema do dia baseado no dia do ano (Evita repetição em 30 dias)."""
    dia_do_ano = datetime.now().timetuple().tm_yday
    return THEME_SEEDS[dia_do_ano % len(THEME_SEEDS)]

def agente_gerador_texto(semente):
    """Agente 1: Cria o texto do post do zero baseado na semente."""
    print("✍️ Agente Gerador: Escrevendo rascunho inédito...")
    
    prompt = f"""
    Você é um Desenvolvedor Python Sênior e Especialista em Conteúdo Técnico.
    Escreva um post para o LinkedIn sobre o tema: "{semente['tema']}".
    
    Regras estritas:
    1. Hook (gancho) irresistível nas 3 primeiras linhas (máximo 210 caracteres) antes de pular linha.
    2. Parágrafos curtos (máximo 3 linhas para escaneabilidade).
    3. Foco estritamente técnico, científico, focando na máquina pública, alocação de recursos e eficiência.
    4. ZERO viés político partidário ou juízo de valor sobre governos. Totalmente neutro.
    5. Uso moderado e elegante de emojis.
    6. No final, adicione o seguinte PS exato (incluindo o link):
    "PS: Para aprofundar ou melhorar seu setup de análise, recomendo: {semente['produto_nome']}. 🛒 Confira: {semente['produto_url']}"
    
    Gere apenas o texto do post, sem aspas, sem título, pronto para copiar e colar.
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

# Estrutura JSON esperada da auditoria
class AuditResult(typing.TypedDict):
    aprovado: bool
    motivo: str

def agente_auditor_antifake(texto_post):
    """Agente 2: Revisa o texto em busca de alucinações, mentiras ou viés político."""
    print("🕵️‍♂️ Agente Auditor: Checando alucinações e viés...")
    
    prompt = f"""
    Você é um Auditor Sênior de Conformidade e Fact-Checker do Governo.
    Sua missão é ler o texto abaixo, que será postado no LinkedIn, e avaliá-lo segundo 3 critérios:
    1. Viés Político: Há algum elogio ou crítica a políticos, governos específicos ou partidos? (Deve ser 100% neutro).
    2. Alucinação (Fake News): O texto cita leis que não existem, ou estatísticas inventadas exatas (ex: "a IA economizou 34.5% no orçamento") sem fonte? (Conceitos teóricos gerais de IA e governança são permitidos).
    3. Profissionalismo: A linguagem é técnica e adequada para o LinkedIn?
    
    Texto a ser analisado:
    '''
    {texto_post}
    '''
    
    Responda EXCLUSIVAMENTE em formato JSON. Se o texto violar as regras, "aprovado" deve ser false e o "motivo" deve explicar a violação.
    """
    
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=AuditResult,
            temperature=0.1 # Temperatura baixa para garantir rigor na auditoria
        )
    )
    
    try:
        resultado = json.loads(response.text)
        return resultado
    except Exception as e:
        return {"aprovado": False, "motivo": f"Erro ao processar auditoria da IA: {str(e)}"}

# ==========================================
# INTEGRAÇÃO COM LINKEDIN E E-MAIL
# ==========================================

def create_linkedin_payload(texto_final, original_url, author_urn):
    """Monta o payload JSON para o LinkedIn no formato Article (Gera o Card da Amazon)."""
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": texto_final
                },
                "shareMediaCategory": "ARTICLE", 
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": original_url
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    return payload

def post_to_linkedin(payload, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    try:
        response = requests.post(LINKEDIN_API_URL, headers=headers, json=payload)
        response.raise_for_status() 
        return response.json().get('id'), None
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return None, str(e)

def enviar_email_notificacao(status, assunto_tema, conteudo, auditoria_detalhes="", erro_msg=""):
    """Envia um e-mail com o status da execução."""
    if not SENHA_APP_GMAIL:
        print("⚠️ SENHA_APP_GMAIL não encontrada. O e-mail de relatório não será enviado.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"[{status}] Relatório de Atividade LinkedIn - {AGENT_NAME}"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    corpo = f"Olá,\n\nAqui é o seu {AGENT_NAME}.\n\nStatus da Execução: {status}\nTema Semente: {assunto_tema}\n\n"
    
    if auditoria_detalhes:
        corpo += f"🔎 Detalhes da Auditoria:\n{auditoria_detalhes}\n\n"
        
    corpo += f"📝 Conteúdo:\n--------------------------------------------------\n{conteudo}\n--------------------------------------------------\n"
    
    if erro_msg:
        corpo += f"\n❌ Detalhes do Erro Técnico:\n{erro_msg}"
        
    msg.set_content(corpo)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

# ==========================================
# FLUXO PRINCIPAL (MAIN)
# ==========================================
if __name__ == "__main__":
    print(f"🤖 Iniciando {AGENT_NAME}...")
    
    if not ACCESS_TOKEN or not AUTHOR_URN:
        erro_msg = "Credenciais do LinkedIn não configuradas."
        print(f"❌ ERRO: {erro_msg}")
        enviar_email_notificacao("FALHA CRÍTICA", "Erro de Inicialização", "Abortado.", erro_msg=erro_msg)
        sys.exit(1)
        
    # 1. Seleciona a semente (garante não repetição em 30 dias)
    semente = get_daily_seed()
    print(f"🎯 Tema Semente do Dia: {semente['tema']}")
    
    # 2. Agente 1: Gera o Texto
    texto_gerado = agente_gerador_texto(semente)
    
    # 3. Agente 2: Audita o Texto (Anti-alucinação)
    resultado_auditoria = agente_auditor_antifake(texto_gerado)
    
    if not resultado_auditoria.get("aprovado", False):
        print(f"🛑 REPROVADO PELO AUDITOR: {resultado_auditoria.get('motivo')}")
        enviar_email_notificacao(
            "BLOQUEADO PELA AUDITORIA", 
            semente['tema'], 
            texto_gerado, 
            auditoria_detalhes=resultado_auditoria.get('motivo')
        )
        sys.exit(1) # Aborta a execução para não postar
        
    print("✅ Aprovado pelo Auditor. Preparando envio ao LinkedIn...")
    
    # 4. Montagem e Envio ao LinkedIn
    payload = create_linkedin_payload(texto_gerado, semente['produto_url'], AUTHOR_URN)
    post_id, erro_linkedin = post_to_linkedin(payload, ACCESS_TOKEN)
    
    # 5. Conclusão e Notificação
    if post_id:
        print(f"🚀 Post publicado com sucesso! ID: {post_id}")
        enviar_email_notificacao("SUCESSO", semente['tema'], texto_gerado, auditoria_detalhes="O texto passou no crivo técnico de alucinação e viés.")
    else:
        print(f"❌ Falha ao publicar na API do LinkedIn: {erro_linkedin}")
        enviar_email_notificacao("ERRO NO LINKEDIN", semente['tema'], texto_gerado, erro_msg=erro_linkedin)
        sys.exit(1)
