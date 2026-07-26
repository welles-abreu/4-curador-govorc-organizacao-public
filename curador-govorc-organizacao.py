import os
import sys
import json
import requests
import smtplib
import urllib.parse
from email.message import EmailMessage
from datetime import datetime
from pydantic import BaseModel

# ==========================================
# IMPORTAÇÃO DO SDK DO GEMINI (COM TRATAMENTO DE ERRO)
# ==========================================
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai
        USE_NEW_SDK = False
    except ImportError:
        print("❌ ERRO: Nenhuma biblioteca do Gemini foi encontrada.")
        print("💡 Execute: pip install google-genai ou pip install google-generativeai")
        sys.exit(1)

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

# ⚠️ IMPORTANTE: Coloque aqui o link da sua imagem.
URL_IMAGEM_FIXA = "https://github.com/SEU_USUARIO/SEU_REPOSITORIO/blob/main/image_2ee60b.png"

# Trava de segurança: Corrige automaticamente a URL do GitHub para o formato "Raw" (direto),
# que é o único formato que a API do LinkedIn consegue ler para renderizar a imagem.
if "github.com" in URL_IMAGEM_FIXA and "/blob/" in URL_IMAGEM_FIXA:
    URL_IMAGEM_FIXA = URL_IMAGEM_FIXA.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

# Inicialização do Cliente Gemini
if not GEMINI_API_KEY:
    print("❌ ERRO: GEMINI_API_KEY não configurada nas variáveis de ambiente.")
    sys.exit(1)

if USE_NEW_SDK:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# SEMENTES TEMÁTICAS (LISTA EXPANDIDA PARA 45 DIAS)
# ==========================================
THEME_SEEDS = [
    {"tema": "Uso de IA para Modelos Preditivos de Arrecadação", "produto_nome": "Livro: Python para Análise de Dados"},
    {"tema": "Detecção de Anomalias e Fraudes em Licitações com Machine Learning", "produto_nome": "Monitor LG Ultrawide 29'' IPS"},
    {"tema": "Processamento de Linguagem Natural (NLP) analisando o PPA e LDO", "produto_nome": "Livro: Data Science para Negócios"},
    {"tema": "Automação de Pipelines de Dados (ETL) na Execução Financeira Pública", "produto_nome": "Teclado Ergonômico Logitech Wave Keys"},
    {"tema": "Otimização Algorítmica de Portfólio de Obras Públicas", "produto_nome": "Livro: Rápido e Devagar - Daniel Kahneman"},
    {"tema": "Categorização Automatizada de Despesas Públicas com IA", "produto_nome": "Fone de Ouvido Anker Soundcore Life Q30"},
    {"tema": "Visão Computacional e Drones na Medição de Contratos de Obras", "produto_nome": "Livro: Inteligência Artificial - Uma Abordagem Moderna"},
    {"tema": "Análise de Sentimentos em Consultas Públicas do Orçamento Participativo", "produto_nome": "Suporte Articulado de Mesa para Monitor"},
    {"tema": "Smart Contracts e Blockchain para Repasses Constitucionais", "produto_nome": "Livro: A Quarta Revolução Industrial"},
    {"tema": "Redes Neurais na Previsão de Fluxo de Caixa do Tesouro", "produto_nome": "SSD Kingston NV2 1TB NVMe M.2"},
    {"tema": "Bancos de Dados em Grafo (GraphDB) para Detectar Conluios", "produto_nome": "Livro: Engenharia de Confiabilidade do Google"},
    {"tema": "Gêmeos Digitais (Digital Twins) Simulando o Orçamento Público", "produto_nome": "Mouse Ergonômico Vertical Logitech MX"},
    {"tema": "Agentes LLM em Pré-Auditoria de Conformidade (Tribunais de Contas)", "produto_nome": "Livro: Clean Architecture"},
    {"tema": "Clustering de Demandas para Otimização de Compras Governamentais", "produto_nome": "Luminária de Mesa LED Baseus Screenbar"},
    {"tema": "Machine Learning para Previsão e Combate à Evasão Fiscal", "produto_nome": "Livro: Mãos à Obra: Aprendizado de Máquina"},
    {"tema": "Aprendizado Federado (Federated Learning) entre Entes Federativos", "produto_nome": "Apple iPad Air"},
    {"tema": "RPA (Robotic Process Automation) na Conciliação Bancária do SIAFI", "produto_nome": "Livro: Automatize Tarefas Maçantes com Python"},
    {"tema": "Transparência Algorítmica e Explainable AI (XAI) nos Gastos Públicos", "produto_nome": "Livro: Armas de Destruição Matemática"},
    {"tema": "Arquitetura Data Mesh: Descentralizando Dados no Governo", "produto_nome": "Livro: Data Mesh - Zhamak Dehghani"},
    {"tema": "Manutenção Preditiva de Ativos Públicos com IoT e IA", "produto_nome": "Monitor Dell 27'' 4K UHD"},
    {"tema": "Cibersegurança e Defesa Autônoma (IA) em Sistemas de Execução Orçamentária", "produto_nome": "Chave de Segurança Yubico YubiKey"},
    {"tema": "Data Storytelling na Prestação de Contas ao Cidadão", "produto_nome": "Livro: Storytelling com Dados"},
    {"tema": "Modelagem de Microdados para Otimização da Dívida Pública", "produto_nome": "Mesa com Regulagem de Altura Elétrica"},
    {"tema": "APIs e Arquitetura de Open Finance aplicadas à Arrecadação", "produto_nome": "Livro: A Era das Criptomoedas"},
    {"tema": "Survival Analysis (Análise de Sobrevivência) em Projetos Sociais", "produto_nome": "Mousepad Gamer Extra Grande Corsair"},
    {"tema": "Chatbots Jurídicos baseados em LLMs para Ordenadores de Despesa", "produto_nome": "Teclado Mecânico Keychron K2"},
    {"tema": "Inteligência Geoespacial (GeoAI) na Atualização do IPTU", "produto_nome": "Mouse Sem Fio Logitech MX Master 3S"},
    {"tema": "Práticas DevOps e CI/CD na Estabilidade do Portal da Transparência", "produto_nome": "Livro: Manual de DevOps"},
    {"tema": "Machine Learning para Alocação Otimizada de RH no Serviço Público", "produto_nome": "Carregador Sem Fio Anker"},
    {"tema": "Aprendizado por Reforço (Reinforcement Learning) no Timing de Licitações", "produto_nome": "Livro: Reinforcement Learning (Sutton)"},
    # --- Novos itens adicionados para completar ciclo de 45 dias sem repetição ---
    {"tema": "Modelos de Previsão de Gastos com Saúde Pública e IA", "produto_nome": "Livro: Deep Learning com Python"},
    {"tema": "Análise de Risco em Parcerias Público-Privadas usando Machine Learning", "produto_nome": "Monitor Curvo 34 Polegadas"},
    {"tema": "IA Generativa no Apoio à Redação de Editais de Licitação", "produto_nome": "Teclado Mecânico Keychron K8"},
    {"tema": "Otimização de Frotas Públicas e Logística com Algoritmos Avançados", "produto_nome": "Mouse sem fio Logitech Pebble"},
    {"tema": "O Potencial das Blockchains em Processos de Licitação Transparentes", "produto_nome": "Livro: Mastering Blockchain"},
    {"tema": "NLP para Classificação e Resumo de Jurisprudência no TCU", "produto_nome": "Kindle Paperwhite 16GB"},
    {"tema": "Identificação de Padrões de Corrupção Cruzando Dados com GraphDB", "produto_nome": "Livro: Graph Databases"},
    {"tema": "Automatização e Previsibilidade no Pagamento de Precatórios", "produto_nome": "Cadeira Ergonômica de Escritório"},
    {"tema": "Painéis de BI Dinâmicos para Monitoramento de Políticas Públicas", "produto_nome": "Elgato Stream Deck MK.2"},
    {"tema": "Análise de Impacto Regulatório com Simulações de Monte Carlo", "produto_nome": "Livro: Estatística Prática para Data Science"},
    {"tema": "Mineração de Processos (Process Mining) em Fluxos do SIAFI", "produto_nome": "Webcam Full HD 1080p"},
    {"tema": "Automação Inteligente de Triagem de Demandas na Ouvidoria", "produto_nome": "Fone Headset com Cancelamento de Ruído"},
    {"tema": "Auditoria Contínua em Folhas de Pagamento com Modelos de Classificação", "produto_nome": "SSD Externo Portátil 1TB"},
    {"tema": "Cidades Inteligentes e Alocação Estratégica de Orçamento para IoT", "produto_nome": "Roteador Mesh Wi-Fi 6"},
    {"tema": "People Analytics e Machine Learning no Serviço Público", "produto_nome": "Hub USB-C 7 em 1"}
]

# Schema estruturado para Pydantic
class AuditResult(BaseModel):
    aprovado: bool
    motivo: str

# ==========================================
# AGENTES DE IA (GEMINI)
# ==========================================

def get_daily_seed():
    """Seleciona o tema do dia baseado no dia do ano."""
    dia_do_ano = datetime.now().timetuple().tm_yday
    return THEME_SEEDS[dia_do_ano % len(THEME_SEEDS)]

def agente_gerador_texto(semente, url_pesquisa):
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
    6. No final, adicione o seguinte PS exato (incluindo o link de busca formatado):
    "PS: Para aprofundar ou melhorar seu setup de análise, recomendo: {semente['produto_nome']}. 🛒 Confira na Amazon: {url_pesquisa}"
    
    Gere apenas o texto do post, sem aspas, sem título, pronto para copiar e colar.
    """
    
    if USE_NEW_SDK:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    else:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()

def agente_auditor_antifake(texto_post):
    """Agente 2: Revisa o texto em busca de alucinações, mentiras ou viés político."""
    print("🕵️‍♂️ Agente Auditor: Checando alucinações e viés...")
    
    prompt = f"""
    Você é um Auditor Sênior de Conformidade e Fact-Checker do Governo.
    Sua missão é ler o texto abaixo, que será postado no LinkedIn, e avaliá-lo segundo 3 critérios:
    1. Viés Político: Há algum elogio ou crítica a políticos, governos específicos ou partidos? (Deve ser 100% neutro).
    2. Alucinação (Fake News): O texto cita leis que não existem, ou estatísticas inventadas exatas sem fonte? (Conceitos teóricos gerais de IA e governança são permitidos).
    3. Profissionalismo: A linguagem é técnica e adequada para o LinkedIn?
    
    Texto a ser analisado:
    '''
    {texto_post}
    '''
    
    Se o texto violar as regras, "aprovado" deve ser false e o "motivo" deve explicar a violação.
    """
    
    try:
        if USE_NEW_SDK:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AuditResult,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        else:
            model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
            
    except Exception as e:
        return {"aprovado": False, "motivo": f"Erro ao processar auditoria da IA: {str(e)}"}

# ==========================================
# INTEGRAÇÃO COM LINKEDIN E E-MAIL
# ==========================================

def create_linkedin_payload(texto_final, original_url, author_urn, thumbnail_url, product_name):
    """Monta o payload JSON para o LinkedIn injetando miniatura e título customizados."""
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
                        "originalUrl": original_url,
                        # Isso substitui o texto "Link da internet" pelo nome do produto
                        "title": {
                            "text": product_name
                        },
                        # Força a exibição da sua imagem customizada
                        "thumbnails": [
                            {
                                "url": thumbnail_url
                            }
                        ]
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
        print("⚠️ SENHA_APP_GMAIL não encontrada. O e-mail não será enviado.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"[{status}] Relatório LinkedIn - {AGENT_NAME}"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    corpo = f"Olá,\n\nAqui é o seu {AGENT_NAME}.\n\nStatus: {status}\nTema Semente: {assunto_tema}\n\n"
    if auditoria_detalhes:
        corpo += f"🔎 Detalhes da Auditoria:\n{auditoria_detalhes}\n\n"
    corpo += f"📝 Conteúdo:\n--------------------------------------------------\n{conteudo}\n--------------------------------------------------\n"
    if erro_msg:
        corpo += f"\n❌ Erro Técnico:\n{erro_msg}"
        
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
        sys.exit(1)
        
    # 1. Seleciona a semente e prepara as variáveis do dia
    semente = get_daily_seed()
    print(f"🎯 Tema Semente do Dia: {semente['tema']}")
    
    # Prepara o link de pesquisa da Amazon
    termo_busca = urllib.parse.quote_plus(semente['produto_nome'])
    url_pesquisa_amazon = f"https://www.amazon.com.br/s?k={termo_busca}&tag=SEU_LINK_AQUI"
    
    # 2. Agente 1: Gera o Texto
    texto_gerado = agente_gerador_texto(semente, url_pesquisa_amazon)
    
    # Insere o prefixo com a data de hoje
    data_hoje_formatada = datetime.now().strftime("%d/%m/%Y")
    texto_final_com_prefixo = f"Curadoria sobre Governança Orçamentária do dia ({data_hoje_formatada}):\n\n{texto_gerado}"
    
    # 3. Agente 2: Audita o Texto
    resultado_auditoria = agente_auditor_antifake(texto_final_com_prefixo)
    
    if not resultado_auditoria.get("aprovado", False):
        print(f"🛑 REPROVADO PELO AUDITOR: {resultado_auditoria.get('motivo')}")
        enviar_email_notificacao("BLOQUEADO PELA AUDITORIA", semente['tema'], texto_final_com_prefixo, auditoria_detalhes=resultado_auditoria.get('motivo'))
        sys.exit(1)
        
    print("✅ Aprovado pelo Auditor. Preparando envio ao LinkedIn...")
    
    # 4. Montagem e Envio ao LinkedIn (passando também o nome do produto para o título do card)
    payload = create_linkedin_payload(
        texto_final_com_prefixo, 
        url_pesquisa_amazon, 
        AUTHOR_URN, 
        URL_IMAGEM_FIXA, 
        semente['produto_nome']  # Isso vai substituir o "Link da internet"
    )
    
    post_id, erro_linkedin = post_to_linkedin(payload, ACCESS_TOKEN)
    
    # 5. Conclusão e Notificação
    if post_id:
        print(f"🚀 Post publicado com sucesso! ID: {post_id}")
        enviar_email_notificacao("SUCESSO", semente['tema'], texto_final_com_prefixo, auditoria_detalhes="Texto aprovado.")
    else:
        print(f"❌ Falha ao publicar: {erro_linkedin}")
        enviar_email_notificacao("ERRO NO LINKEDIN", semente['tema'], texto_final_com_prefixo, erro_msg=erro_linkedin)
        sys.exit(1)
