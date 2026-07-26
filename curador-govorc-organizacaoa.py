import os
import sys
import json
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Configurações da API do LinkedIn (Community Management API - App ID: 260411821)
LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
AUTHOR_URN = os.environ.get('LINKEDIN_URN_ID')  # Ajustado conforme solicitado

# Configurações de E-mail
SENHA_APP_GMAIL = os.environ.get('SENHA_APP_GMAIL')
EMAIL_REMETENTE = "wellesmatias@gmail.com"
EMAIL_DESTINO = "wellesmatias@gmail.com"
AGENT_NAME = "Curador Orçamentário"

# Repositório de Conteúdos (30 temas - garante que não se repitam em menos de 30 dias).
# Regras aplicadas: Hook curto, foco na máquina pública, isenção e recomendação suave.
CONTENT_DATABASE = [
    {
        "tema": "Modelos Preditivos de Arrecadação",
        "hook": "A previsão de receitas sempre foi o calcanhar de Aquiles do planejamento fiscal. Hoje, modelos preditivos de IA mudam o jogo. 📊\n\nMas como a máquina pública absorve isso? 👇",
        "body": "A governança orçamentária moderna exige mais do que projeções lineares. Algoritmos de Machine Learning conseguem cruzar variáveis macroeconômicas em tempo real.\n\nIsso permite antecipar flutuações de arrecadação tributária com precisão cirúrgica, evitando contingenciamentos abruptos que paralisam serviços essenciais.\n\nA transição da intuição para a ciência de dados não é uma opção, é um imperativo de responsabilidade fiscal.",
        "pitch_amazon": "Liderar essa transição exige domínio técnico. 'Python para Análise de Dados' é o guia definitivo para extrair inteligência de bases complexas. Uma leitura essencial para gestores modernos.",
        "produto_nome": "Livro: Python para Análise de Dados",
        "produto_url": "https://www.amazon.com.br/dp/B07P882X4G?tag=SEU_LINK_AQUI",
        "ai_prompt": "A sleek, modern abstract 3D composition showing interconnected glowing nodes and bar charts over a dark blue background, corporate tech aesthetic, 8k resolution --ar 16:9"
    },
    {
        "tema": "Detecção de Anomalias em Licitações",
        "hook": "O combate ao desperdício no orçamento público ganhou um aliado implacável: algoritmos de detecção de anomalias. ⚙️\n\nDescubra como blindar o ciclo orçamentário. 👇",
        "body": "Auditar notas de empenho manualmente é um processo custoso. A Inteligência Artificial permite a varredura integral de 100% das contratações públicas.\n\nTreinando redes neurais com o histórico de compras, padrões de sobrepreço são sinalizados automaticamente antes da liquidação do pagamento.\n\nA governança atua na prevenção. A tecnologia garante que cada centavo chegue ao destino planejado com rastreabilidade.",
        "pitch_amazon": "Analisar painéis de conformidade demanda muito espaço de tela. Um monitor ultrawide transforma a produtividade de quem lida com grandes volumes de dados diariamente.",
        "produto_nome": "Monitor LG Ultrawide 29'' IPS",
        "produto_url": "https://www.amazon.com.br/dp/B095198J2Y?tag=SEU_LINK_AQUI",
        "ai_prompt": "Abstract digital eye made of glowing code and financial graphs, scanning through blocks of data, dark background with gold accents --ar 16:9"
    },
    {
        "tema": "Processamento de Linguagem Natural (NLP) no PPA",
        "hook": "PPA e LDO analisados em segundos. O Processamento de Linguagem Natural (NLP) acelera a consistência jurídica do orçamento. 🏛️\n\nComo a IA lê leis orçamentárias? 👇",
        "body": "A redação de diretrizes orçamentárias envolve milhares de páginas. O NLP consegue extrair entidades, metas e restrições diretamente dos textos legais.\n\nAutomatizar a leitura de emendas parlamentares com IA assegura que não haja choque de normativas, verificando a aderência constitucional.\n\nO resultado é um processo legislativo mais ágil, técnico e blindado contra inseguranças jurídicas.",
        "pitch_amazon": "Entender o impacto dos dados nas organizações é vital. 'Data Science para Negócios' traduz conceitos complexos em estratégias aplicáveis. Leitura obrigatória para inovadores no setor público.",
        "produto_nome": "Livro: Data Science para Negócios",
        "produto_url": "https://www.amazon.com.br/dp/8576089726?tag=SEU_LINK_AQUI",
        "ai_prompt": "Glowing holographic books and legal documents floating inside a minimalist server room, neural network lines connecting texts --ar 16:9"
    },
    {
        "tema": "Automação de ETL na Execução Financeira",
        "hook": "Pipelines de dados (ETL) são o coração da transparência ativa na execução orçamentária. 📉\n\nSair da extração manual é o primeiro passo da governança. 👇",
        "body": "Sistemas estruturantes geram terabytes de informações diárias. Sem rotinas automatizadas, esses dados permanecem ociosos em silos governamentais.\n\nCom automação em nuvem, orquestramos a ingestão de dados para Data Lakes, permitindo análises em tempo real por órgãos de controle.\n\nA governança de dados transforma números brutos em evidências prontas para a tomada de decisão.",
        "pitch_amazon": "Escrever rotinas de ETL diariamente cobra um preço físico. Um teclado ergonômico mecânico é um investimento na sua saúde e velocidade de digitação. Transformador.",
        "produto_nome": "Teclado Ergonômico Logitech Wave Keys",
        "produto_url": "https://www.amazon.com.br/dp/B0CKD47X8Y?tag=SEU_LINK_AQUI",
        "ai_prompt": "Data flowing like liquid gold through transparent tubes forming an organizational chart, representing ETL processes --ar 16:9"
    },
    {
        "tema": "Otimização de Portfólio de Obras Públicas",
        "hook": "Como priorizar obras públicas com recursos escassos? A IA aplica algoritmos de otimização no orçamento de investimentos. 🏗️\n\nA matemática da alocação eficiente. 👇",
        "body": "Decisões de infraestrutura muitas vezes carecem de modelagem técnica. Algoritmos simulam milhões de cenários de alocação de capital.\n\nConsiderando impacto socioeconômico e manutenção, a IA indica a cesta de projetos que maximiza o Retorno Social do Investimento (SROI).\n\nA matemática fornece a base técnica necessária para um planejamento estatal rigoroso.",
        "pitch_amazon": "A tomada de decisão sob pressão exige clareza mental. 'Rápido e Devagar', de Daniel Kahneman, é a maior obra já escrita sobre como nossas mentes fazem escolhas complexas.",
        "produto_nome": "Livro: Rápido e Devagar - Daniel Kahneman",
        "produto_url": "https://www.amazon.com.br/dp/853900383X?tag=SEU_LINK_AQUI",
        "ai_prompt": "Golden architectural blueprint morphing into glowing binary code and graphs, representing public works optimization --ar 16:9"
    },
    {
        "tema": "Categorização Automatizada de Despesas",
        "hook": "A imprecisão ao classificar despesas distorce o balanço do setor público. O uso de IA organiza as bases orçamentárias. 🗂️\n\nAdeus à classificação manual. 👇",
        "body": "O erro humano na inserção da Natureza de Despesa gera relatórios inconsistentes, prejudicando a prestação de contas aos tribunais.\n\nModelos baseados em IA leem o objeto da licitação e a nota fiscal para classificar a despesa com precisão superior a 98%.\n\nUma taxonomia financeira automatizada é a espinha dorsal de uma matriz de custos real do Estado.",
        "pitch_amazon": "Ambientes de trabalho agitados prejudicam o foco em análises delicadas. Um fone com cancelamento de ruído ativo permite imersão total no planejamento estratégico.",
        "produto_nome": "Fone de Ouvido Anker Soundcore Life Q30",
        "produto_url": "https://www.amazon.com.br/dp/B08HMWZBXC?tag=SEU_LINK_AQUI",
        "ai_prompt": "Neat folders of data glowing and organizing themselves automatically in a vast digital archive, blue and gold light trails --ar 16:9"
    },
    {
        "tema": "Visão Computacional na Medição de Contratos",
        "hook": "Medições de obras públicas baseadas em drones e Visão Computacional. Orçamento governado por evidências visuais matemáticas. 📸\n\nComo a IA fiscaliza no campo? 👇",
        "body": "O pagamento de construtoras depende de medição física, frequentemente sujeita a assimetrias de informação no canteiro de obras.\n\nModelos de Visão Computacional analisando imagens de drones calculam volumes de terraplanagem e avanço físico em tempo real.\n\nO desembolso passa a ser vinculado estritamente à execução, erradicando ineficiências nos contratos.",
        "pitch_amazon": "Para compreender a fundo os modelos que analisam imagens, a literatura seminal é chave. 'Inteligência Artificial: Uma Abordagem Moderna' é o alicerce global da área.",
        "produto_nome": "Livro: Inteligência Artificial - Uma Abordagem Moderna",
        "produto_url": "https://www.amazon.com.br/dp/8535237013?tag=SEU_LINK_AQUI",
        "ai_prompt": "Digital eye lens focusing on a bridge construction wireframe, scanning laser converting reality into data metrics --ar 16:9"
    },
    {
        "tema": "Análise de Sentimentos em Consultas Públicas",
        "hook": "Como incluir a voz da sociedade no Orçamento Participativo em larga escala? A IA processa milhares de sugestões cidadãs. 👥\n\nPlanejamento estratégico plural. 👇",
        "body": "A formulação da LOA deve refletir demandas sociais. No entanto, compilar milhares de formulários textuais é inviável sem tecnologia.\n\nAlgoritmos de NLP mapeiam tópicos emergentes e mensuram a urgência do sentimento cidadão a partir de opiniões não estruturadas.\n\nA governança utiliza dados para traduzir o anseio da população diretamente em rubricas orçamentárias.",
        "pitch_amazon": "A saúde cervical de quem analisa dados o dia inteiro não tem preço. Um suporte ergonômico articulado alinha seu monitor à altura dos olhos, prevenindo lesões.",
        "produto_nome": "Suporte Articulado de Mesa para Monitor ELG",
        "produto_url": "https://www.amazon.com.br/dp/B0765RFSZ7?tag=SEU_LINK_AQUI",
        "ai_prompt": "Glowing speech bubbles transforming into structured bar charts, representing citizen feedback becoming data --ar 16:9"
    },
    {
        "tema": "Smart Contracts para Vinculações Constitucionais",
        "hook": "A rigidez orçamentária é alta. E se usássemos Smart Contracts para automatizar repasses obrigatórios? 🔗\n\nBlockchain e IA no tesouro público. 👇",
        "body": "Percentuais mínimos para Saúde e Educação exigem cálculos contínuos sobre a Receita Corrente Líquida. Erros geram rejeição de contas.\n\nIntegrar IA para auditar parâmetros e Smart Contracts para executar a transferência automatiza a conformidade legal.\n\nReduz-se a burocracia, garantindo que o dinheiro chegue à ponta com governança irretocável.",
        "pitch_amazon": "A interseção entre macroeconomia e disrupção digital é fascinante. O clássico 'A Quarta Revolução Industrial' mapeia exatamente essas transformações nos Estados.",
        "produto_nome": "Livro: A Quarta Revolução Industrial",
        "produto_url": "https://www.amazon.com.br/dp/8539007428?tag=SEU_LINK_AQUI",
        "ai_prompt": "Blockchain glowing nodes intertwining with a glowing budget ledger book, transparent digital architecture --ar 16:9"
    },
    {
        "tema": "Previsão de Fluxo de Caixa do Tesouro",
        "hook": "O descasamento entre arrecadação e despesa pressiona a Dívida. Redes Neurais projetam o fluxo de caixa diário do Estado. 📉\n\nIA na Gestão de Tesouraria. 👇",
        "body": "Administrar o caixa único exige manter liquidez sem incorrer em custos de oportunidade desnecessários emitindo títulos a mercado.\n\nModelos temporais identificam sazonalidades complexas nos pagamentos e entrada de impostos, otimizando o saldo diário.\n\nUma tesouraria baseada em IA minimiza a necessidade de antecipação de receita, economizando juros ao pagador de impostos.",
        "pitch_amazon": "Profissionais de dados precisam de velocidade de leitura e gravação. Atualizar sua máquina com um SSD NVMe de última geração é o upgrade mais perceptível no processamento local.",
        "produto_nome": "SSD Kingston NV2 1TB NVMe M.2",
        "produto_url": "https://www.amazon.com.br/dp/B0BBWH1R8H?tag=SEU_LINK_AQUI",
        "ai_prompt": "A river of glowing digital numbers flowing smoothly like a liquid into a glowing financial reservoir --ar 16:9"
    },
    {
        "tema": "Grafos na Detecção de Conluios em Licitações",
        "hook": "A governança atinge o ápice quando a fraude é cortada pela raiz. Bancos de Dados em Grafo expõem cartéis invisíveis. 🕸️\n\nA rede secreta revelada. 👇",
        "body": "Empresas que combinam preços compartilham sócios ocultos ou endereços IP, passando despercebidas em análises tabulares simples.\n\nA IA conecta as relações societárias, cruzando dados abertos para identificar agrupamentos suspeitos em frações de segundo.\n\nO processo licitatório ganha uma barreira intransponível de inteligência, protegendo a integridade do certame.",
        "pitch_amazon": "Construir sistemas tão resilientes exige referências robustas. 'Engenharia de Confiabilidade do Google (SRE)' ensina os princípios de arquitetura das gigantes de tecnologia.",
        "produto_nome": "Livro: Engenharia de Confiabilidade do Google",
        "produto_url": "https://www.amazon.com.br/dp/857522543X?tag=SEU_LINK_AQUI",
        "ai_prompt": "Complex glowing network graph showing nodes and connections overlaid on a stylized courthouse --ar 16:9"
    },
    {
        "tema": "Gêmeos Digitais (Digital Twins) no Orçamento",
        "hook": "E se a taxa de juros subisse hoje? Com Gêmeos Digitais da economia, simulamos impactos orçamentários antes que ocorram. 🌐\n\nO simulador de voo do Estado. 👇",
        "body": "A técnica de Digital Twins cria uma réplica virtual de toda a engrenagem fiscal, da folha de pagamento ao serviço da dívida.\n\nA IA roda testes de estresse em tempo real, avaliando o impacto de crises globais no orçamento anual com antecedência.\n\nA governança deixa de ser reativa e passa a ser profilática, protegendo os serviços essenciais.",
        "pitch_amazon": "Horas simulando cenários exigem ergonomia de excelência. Um mouse vertical reposiciona seu pulso de forma natural, evitando dores crônicas (LER/DORT).",
        "produto_nome": "Mouse Ergonômico Vertical Logitech MX",
        "produto_url": "https://www.amazon.com.br/dp/B07DKL44ZZ?tag=SEU_LINK_AQUI",
        "ai_prompt": "Holographic glowing digital twin of a stylized city and financial ledger, high end corporate tech --ar 16:9"
    },
    {
        "tema": "Agentes LLM em Auditoria de Conformidade",
        "hook": "Tribunais de Contas podem usar Modelos de Linguagem (LLMs) para pré-auditar balanços públicos em minutos. 🤖\n\nA IA acelerando o controle externo. 👇",
        "body": "Julgar contas públicas exige recursos massivos. Agentes baseados em IA generativa podem ser treinados na jurisprudência das Cortes.\n\nEles escaneiam notas explicativas e demonstrativos, apontando inconsistências normativas para o auditor humano focar no mérito.\n\nO controle torna-se tempestivo, atuando na correção enquanto a execução acontece.",
        "pitch_amazon": "Criar códigos que integram IAs complexas exige organização. 'Clean Architecture' é o manual definitivo para projetar softwares robustos, modulares e de fácil manutenção.",
        "produto_nome": "Livro: Clean Architecture - Robert C. Martin",
        "produto_url": "https://www.amazon.com.br/dp/8550804606?tag=SEU_LINK_AQUI",
        "ai_prompt": "Artificial intelligence brain composed of glowing legal scripts and financial charts, inspecting a glowing document --ar 16:9"
    },
    {
        "tema": "Otimização de Compras Governamentais via Clustering",
        "hook": "Por que cada órgão compra insumos separadamente? Algoritmos de clustering agrupam demandas para gerar compras em escala. 📦\n\nEficiência guiada por IA. 👇",
        "body": "A fragmentação das compras públicas pulveriza o poder de barganha. Sistemas de IA podem agrupar o Plano de Contratações (PCA) do Estado.\n\nAo identificar similaridades através de clustering, o governo lança editais unificados, derrubando o custo unitário.\n\nA governança sobre as aquisições reverte grandes volumes de economia direta para novos investimentos.",
        "pitch_amazon": "O estudo noturno exige um ambiente com iluminação adequada. Uma luminária Screenbar reduz o brilho na tela e diminui drasticamente a fadiga visual do gestor.",
        "produto_nome": "Luminária de Mesa LED Baseus Screenbar",
        "produto_url": "https://www.amazon.com.br/dp/B08XBM7J3V?tag=SEU_LINK_AQUI",
        "ai_prompt": "Multiple small boxes combining into a massive glowing golden cube on a futuristic conveyor belt --ar 16:9"
    },
    {
        "tema": "Previsão de Evasão Fiscal com Machine Learning",
        "hook": "Garantir a receita é tão vital quanto alocar bem a despesa. O Machine Learning identifica padrões sutis de evasão fiscal. 🔎\n\nInteligência Tributária avançada. 👇",
        "body": "A base da governança orçamentária é a capacidade de arrecadar sem distorções. A sonegação esvazia as políticas de Estado.\n\nAlgoritmos treinam em milhões de notas, identificando redes fantasmas, operações simuladas e fraudes cruzadas de forma autônoma.\n\nAumentar a receita combatendo a evasão (sem criar novos impostos) é o ápice da governança digital.",
        "pitch_amazon": "Quer construir seus próprios modelos preditivos? 'Mãos à Obra: Aprendizado de Máquina com Scikit-Learn' é a ponte perfeita entre a teoria da IA e o código funcional em Python.",
        "produto_nome": "Livro: Mãos à Obra: Aprendizado de Máquina",
        "produto_url": "https://www.amazon.com.br/dp/8550811777?tag=SEU_LINK_AQUI",
        "ai_prompt": "Magnifying glass hovering over complex tax documents revealing hidden red warning nodes --ar 16:9"
    },
    {
        "tema": "Aprendizado Federado (Federated Learning) entre Entes",
        "hook": "Como compartilhar IA entre União, Estados e Municípios sem ferir a LGPD? A resposta está no Aprendizado Federado. 🇧🇷\n\nA governança descentralizada. 👇",
        "body": "Bases de dados de saúde e assistência social exigem sigilo estrito, o que dificulta cruzamentos orçamentários entre as esferas de poder.\n\nO Federated Learning treina a IA localmente. Os dados não saem do município, mas o algoritmo viaja pela rede aprendendo padrões globais de eficiência.\n\nA tecnologia preserva o sigilo do cidadão enquanto fornece aos gestores métricas nacionais valiosas.",
        "pitch_amazon": "Para profissionais que precisam esquematizar redes complexas e fazer anotações rápidas em reuniões, o iPad Air com Apple Pencil substitui perfeitamente cadernos, organizando ideias digitais.",
        "produto_nome": "Apple iPad Air (5ª Geração)",
        "produto_url": "https://www.amazon.com.br/dp/B09V3JG7B9?tag=SEU_LINK_AQUI",
        "ai_prompt": "Glowing map of Brazil composed of digital nodes, interconnected by bright light beams, representing decentralized data --ar 16:9"
    },
    {
        "tema": "RPA (Robotic Process Automation) na Conciliação Bancária",
        "hook": "A conciliação bancária do Estado ainda toma milhares de horas humanas. Robôs de software (RPA) liquidam essa fatura. 🤖\n\nProdutividade na contabilidade pública. 👇",
        "body": "Cruzar milhares de extratos bancários com os registros contábeis do SIAFI é uma tarefa mecânica, demorada e suscetível a erros de digitação.\n\nCom RPA, scripts automatizados acessam portais bancários, baixam arquivos OFX e realizam a conciliação linha por linha durante a madrugada.\n\nO servidor público deixa de ser um digitador de dados para atuar como um auditor analítico e estratégico.",
        "pitch_amazon": "Para quem deseja dar os primeiros passos na criação desses robôs, recomendo fortemente o livro 'Automatize tarefas maçantes com Python'. É o guia mais prático do mercado para não-programadores.",
        "produto_nome": "Livro: Automatize Tarefas Maçantes com Python",
        "produto_url": "https://www.amazon.com.br/dp/8575228129?tag=SEU_LINK_AQUI",
        "ai_prompt": "A digital glowing robot hand moving blocks of financial data into perfectly aligned slots on a transparent screen --ar 16:9"
    },
    {
        "tema": "Transparência Algorítmica nos Gastos Públicos",
        "hook": "Se a IA decide onde alocar recursos, como garantir que ela não tem vieses? A governança moderna exige Transparência Algorítmica. ⚖️\n\nAudiência pública para códigos. 👇",
        "body": "Quando modelos de Machine Learning otimizam a distribuição de merenda escolar ou medicamentos, o critério não pode ser uma 'caixa preta'.\n\nO código-fonte de algoritmos de impacto social precisa de auditoria (Explainable AI - XAI) para garantir que variáveis discriminatórias não estejam influenciando os gastos.\n\nA responsabilidade fiscal passa não só pelos números, mas pela equidade matemática dos algoritmos.",
        "pitch_amazon": "Compreender o lado obscuro do uso desenfreado de dados é vital para gestores éticos. O aclamado 'Armas de Destruição Matemática' expõe como algoritmos podem aumentar a desigualdade se mal governados.",
        "produto_nome": "Livro: Armas de Destruição Matemática",
        "produto_url": "https://www.amazon.com.br/dp/8532532456?tag=SEU_LINK_AQUI",
        "ai_prompt": "A glowing clear glass box revealing complex algorithms inside, representing transparency and ethical AI in governance --ar 16:9"
    },
    {
        "tema": "Data Mesh: Descentralizando Dados no Governo",
        "hook": "Centralizar todos os dados do governo em um único setor cria gargalos. A arquitetura 'Data Mesh' distribui a inteligência. 🕸️\n\nA democracia da análise de dados. 👇",
        "body": "Os Data Lakes centralizados muitas vezes falham na administração pública devido à lentidão nas respostas aos órgãos solicitantes.\n\nO Data Mesh trata os dados como 'produtos' gerenciados pelos próprios domínios (Saúde, Educação, Segurança), governados por padrões centrais de interoperabilidade.\n\nO orçamento ganha agilidade quando cada secretaria orçamentária é autônoma, mas conectada a uma matriz única de verdade.",
        "pitch_amazon": "Implementar conceitos de malha de dados exige uma mudança de paradigma. O livro de Zhamak Dehghani sobre Data Mesh é a fonte primária e definitiva sobre o tema para arquitetos de software e gestores.",
        "produto_nome": "Livro: Data Mesh - Zhamak Dehghani",
        "produto_url": "https://www.amazon.com.br/dp/1492092398?tag=SEU_LINK_AQUI",
        "ai_prompt": "Multiple distinct glowing data spheres orbiting a central transparent pillar, representing data mesh architecture --ar 16:9"
    },
    {
        "tema": "Manutenção Preditiva de Ativos Públicos com IoT",
        "hook": "A substituição de frota pública e equipamentos hospitalares pesa no orçamento. Sensores IoT e IA preveem falhas antes da quebra. 🚑\n\nA engenharia da economia fiscal. 👇",
        "body": "Gastos emergenciais com maquinário quebrado custam muito mais do que manutenções programadas. Contudo, prever quando uma máquina falhará era impossível.\n\nSensores IoT capturam temperatura e vibração, alimentando modelos de IA que alertam a equipe sobre a fadiga iminente de peças críticas em hospitais e frotas.\n\nA despesa de capital (CAPEX) é otimizada estendendo o ciclo de vida útil do patrimônio público de forma cirúrgica.",
        "pitch_amazon": "Equipar espaços de monitoramento IoT requer telas amplas e nítidas. O Monitor Dell de 27 polegadas 4K oferece a resolução ideal para analistas de dashboards complexos.",
        "produto_nome": "Monitor Dell 27'' 4K UHD",
        "produto_url": "https://www.amazon.com.br/dp/B09D8Q1K96?tag=SEU_LINK_AQUI",
        "ai_prompt": "A high-tech digital schematic of a government ambulance with glowing nodes indicating sensor health checks, dark aesthetic --ar 16:9"
    },
    {
        "tema": "Cibersegurança nos Sistemas de Execução Orçamentária",
        "hook": "A modernização fiscal atrai ataques cibernéticos. Proteger o SIAFI e os cofres públicos exige IA de defesa autônoma. 🛡️\n\nA muralha invisível do Tesouro. 👇",
        "body": "Os sistemas de pagamento do Estado lidam com bilhões de reais diariamente. Ransomwares e invasões representam risco de paralisação sistêmica.\n\nFerramentas de defesa orientadas a IA mapeiam a rede interna do governo para identificar movimentações laterais e bloqueiam tráfego malicioso instantaneamente.\n\nA governança de TI e o orçamento andam de mãos dadas; proteger os dados é proteger o erário e a continuidade dos serviços.",
        "pitch_amazon": "Proteger senhas de acesso aos sistemas de dados governamentais é não-negociável. As chaves físicas de segurança YubiKey adicionam uma camada de criptografia de hardware impenetrável ao seu fluxo de trabalho.",
        "produto_nome": "Chave de Segurança Yubico YubiKey 5 NFC",
        "produto_url": "https://www.amazon.com.br/dp/B07HBD71HL?tag=SEU_LINK_AQUI",
        "ai_prompt": "A glowing neon shield protecting a giant digital safe filled with binary code, representing cybersecurity in public finance --ar 16:9"
    },
    {
        "tema": "Storytelling com Dados na Prestação de Contas",
        "hook": "Planilhas densas não geram engajamento social. O 'Data Storytelling' transforma os demonstrativos fiscais em narrativas compreensíveis. 📈\n\nTransparência que o cidadão entende. 👇",
        "body": "Publicar arquivos CSV no portal da transparência cumpre a lei, mas não necessariamente informa a sociedade ou os parlamentares leigos.\n\nTécnicas de visualização de dados convertem a Lei de Diretrizes Orçamentárias em painéis dinâmicos e fluxos lógicos de receita-despesa.\n\nQuando o gestor consegue comunicar visualmente os impactos das restrições fiscais, aprovar reformas essenciais torna-se um debate técnico, não ideológico.",
        "pitch_amazon": "Quer aprender a comunicar os números com clareza irrefutável? 'Storytelling com Dados' de Cole Nussbaumer é a bíblia da visualização da informação. Um livro que muda carreiras.",
        "produto_nome": "Livro: Storytelling com Dados",
        "produto_url": "https://www.amazon.com.br/dp/8550804681?tag=SEU_LINK_AQUI",
        "ai_prompt": "Elegant, minimalist bar and line charts coming to life and unfolding like a beautiful glowing book, dark sophisticated background --ar 16:9"
    },
    {
        "tema": "Modelagem de Microdados da Dívida Pública",
        "hook": "A gestão da dívida pública exige precisão atômica. Modelagem em nível de microdados refina o custo de captação do Estado. 💵\n\nIA na rolagem da dívida. 👇",
        "body": "Agregações macroeconômicas escondem assimetrias nos prazos e indexadores dos títulos públicos estaduais e federais.\n\nAplicar algoritmos de otimização em cada contrato individual permite renegociações cirúrgicas e emissões ajustadas ao apetite do mercado secundário em tempo real.\n\nEssa governança em microescala pode poupar milhões em juros ao ano, abrindo margem orçamentária para a política pública real.",
        "pitch_amazon": "Estudos detalhados exigem uma postura impecável para não prejudicar a saúde. Trabalhar em pé algumas horas do dia com uma Standing Desk elétrica melhora o foco e a circulação sanguínea.",
        "produto_nome": "Mesa com Regulagem de Altura Elétrica GenioDesk",
        "produto_url": "https://www.amazon.com.br/dp/B09JGG2BQR?tag=SEU_LINK_AQUI",
        "ai_prompt": "Microscopic view of golden digital threads intertwining to form a massive glowing coin, symbolizing microdata in macroeconomics --ar 16:9"
    },
    {
        "tema": "Open Finance aplicado ao Setor Público",
        "hook": "E se o cidadão pudesse unificar o pagamento de todos os tributos através da arquitetura de Open Finance? 💳\n\nO Tesouro Aberto e a inovação financeira. 👇",
        "body": "A fragmentação das guias de arrecadação (IPTU, IPVA, taxas) gera altos níveis de inadimplência por puro atrito no pagamento.\n\nA utilização de APIs no padrão Open Banking permite que o Estado se integre diretamente aos aplicativos bancários dos contribuintes com alertas unificados.\n\nSimplificar a experiência do cidadão é a estratégia mais inteligente de governança para elevar a arrecadação de forma voluntária e pacífica.",
        "pitch_amazon": "Entender o futuro do dinheiro e dos pagamentos digitais é crucial. O livro 'A Era das Criptomoedas e do Blockchain' oferece o panorama institucional que todo gestor público precisa dominar.",
        "produto_nome": "Livro: A Era das Criptomoedas",
        "produto_url": "https://www.amazon.com.br/dp/8537816825?tag=SEU_LINK_AQUI",
        "ai_prompt": "A glowing digital bridge connecting a modern bank vault to a classic government courthouse, blue and cyan cyber colors --ar 16:9"
    },
    {
        "tema": "Análise de Sobrevivência (Survival Analysis) em Projetos Públicos",
        "hook": "Quantos meses um projeto social sobrevive após perder o financiamento original? Modelos estatísticos preveem a perenidade da política pública. ⏳\n\nO fim das 'obras inacabadas'. 👇",
        "body": "Obras e projetos frequentemente morrem nas transições de mandato ou quando o orçamento federal inicial cessa.\n\nUtilizando 'Survival Analysis' (técnica da biologia aplicada à economia), podemos calcular matematicamente a probabilidade de continuidade de um projeto com base na sua matriz de financiamento.\n\nIsso permite que o Estado invista o recurso restrito nos projetos com maior probabilidade estatística de gerar impacto no longo prazo.",
        "pitch_amazon": "A imersão em estatística avançada fica melhor com periféricos adequados. Um mousepad gigante e de alta qualidade acomoda o setup perfeitamente, proporcionando fluidez para quem programa.",
        "produto_nome": "Mousepad Gamer Extra Grande Corsair",
        "produto_url": "https://www.amazon.com.br/dp/B01798VS4C?tag=SEU_LINK_AQUI",
        "ai_prompt": "A digital glowing hourglass where the falling sand turns into upward-trending bar charts, deep metallic background --ar 16:9"
    },
    {
        "tema": "Chatbots e LLMs no Suporte aos Ordenadores de Despesa",
        "hook": "Tirar dúvidas sobre a Lei 14.133 (Licitações) é demorado. Agentes conversacionais (LLMs) guiam o servidor na execução da despesa. 💬\n\nDireito Financeiro como Serviço (LaaS). 👇",
        "body": "Ordenadores de despesa, por precaução jurídica, frequentemente travam processos orçamentários por dúvidas na interpretação da lei de compras.\n\nChatbots corporativos treinados com a base de dados dos acórdãos do TCU e pareceres da AGU fornecem respostas embasadas em segundos.\n\nA IA reduz a burocracia do medo, conferindo segurança jurídica e celeridade à aplicação do recurso público no que importa.",
        "pitch_amazon": "Produtividade ao digitar comandos e interagir com IAs passa por um bom teclado. O Teclado Mecânico Keychron K2 é uma lenda entre desenvolvedores pela sua construção impecável e resposta tátil.",
        "produto_nome": "Teclado Mecânico Keychron K2",
        "produto_url": "https://www.amazon.com.br/dp/B07Y9Y69N7?tag=SEU_LINK_AQUI",
        "ai_prompt": "A friendly glowing AI core projecting a hologram of an organized legal document to a stylized user interface --ar 16:9"
    },
    {
        "tema": "Inteligência Geoespacial (GeoAI) na Tributação",
        "hook": "Atualizar a planta genérica de valores do IPTU custa milhões. A Inteligência Geoespacial cruza imagens de satélite e automatiza a avaliação. 🗺️\n\nA justiça fiscal vista do espaço. 👇",
        "body": "O cadastro imobiliário desatualizado corrói a arrecadação própria dos municípios e gera severas injustiças tributárias.\n\nAlgoritmos de GeoAI detectam novas áreas construídas, ampliações ou piscinas comparando anos fiscais por satélite com extrema precisão.\n\nA cobrança justa sobre o patrimônio consolida a governança orçamentária local, garantindo sustentabilidade aos cofres municipais sem depender de repasses federais.",
        "pitch_amazon": "O uso de Sistemas de Informação Geográfica (QGIS, ArcGIS) exige precisão absurda do cursor. O mouse Logitech MX Master 3S é o padrão ouro para trabalho especializado e navegação em mapas complexos.",
        "produto_nome": "Mouse Sem Fio Logitech MX Master 3S",
        "produto_url": "https://www.amazon.com.br/dp/B0B11QNDBD?tag=SEU_LINK_AQUI",
        "ai_prompt": "A glowing holographic satellite map hovering over a physical city budget report, scanning laser identifying newly constructed structures --ar 16:9"
    },
    {
        "tema": "Integração Contínua (CI/CD) no Portal da Transparência",
        "hook": "Atualizar portais de transparência não deve gerar indisponibilidade. O uso de práticas DevOps no setor público garante estabilidade. 🔄\n\nSoftware governamental com nível de Big Tech. 👇",
        "body": "A transparência orçamentária perde eficácia quando os servidores governamentais entram em manutenção ou caem em dias de pico de acessos.\n\nA adoção de pipelines de CI/CD (Integração e Entrega Contínuas) permite atualizações de bases de dados diárias sem interrupção do serviço ao cidadão.\n\nA governança se moderniza quando a infraestrutura técnica suporta o escrutínio público com velocidade e estabilidade ininterruptas.",
        "pitch_amazon": "A transição para a cultura ágil no setor público requer líderes preparados. O 'Manual de DevOps' é o guia essencial para transformar a TI governamental de um centro de custos para um motor de eficiência.",
        "produto_nome": "Livro: Manual de DevOps",
        "produto_url": "https://www.amazon.com.br/dp/8550802492?tag=SEU_LINK_AQUI",
        "ai_prompt": "An infinity loop symbol glowing with code streams representing CI/CD DevOps over a transparent government building --ar 16:9"
    },
    {
        "tema": "Alocação Otimizada de RH com Machine Learning",
        "hook": "A folha de pagamento é a maior rubrica do orçamento. Como a IA pode alocar médicos e policiais onde eles são mais necessários? 👥\n\nA inteligência por trás das escalas. 👇",
        "body": "O repasse orçamentário para pagamento de pessoal é rígido, mas a eficiência da alocação desses profissionais é flexível e frequentemente mal gerida.\n\nModelos de Machine Learning predizem picos de demanda hospitalar ou criminalidade por geolocalização e dia da semana, distribuindo plantonistas de forma matemática.\n\nMaximizar a produção do serviço público sem aumentar a folha de pagamento é a definição suprema de responsabilidade orçamentária.",
        "pitch_amazon": "Manter os dispositivos corporativos organizados em cima da mesa ajuda na clareza mental. Um hub de carregamento sem fio e organizador de cabos da Anker transforma uma mesa caótica em um ambiente zen.",
        "produto_nome": "Carregador Sem Fio Anker PowerWave",
        "produto_url": "https://www.amazon.com.br/dp/B07THHQMHM?tag=SEU_LINK_AQUI",
        "ai_prompt": "Glowing human silhouettes moving smoothly into strategic geometric slots on a glowing city map, precision resource allocation --ar 16:9"
    },
    {
        "tema": "Aprendizado por Reforço (Reinforcement Learning) em Licitações",
        "hook": "E se algoritmos aprendessem sozinhos qual o melhor momento de lançar um edital para conseguir os menores preços? 🏆\n\nA IA jogando a favor dos cofres públicos. 👇",
        "body": "Mercados de insumos hospitalares e asfalto flutuam sazonalmente. Lançar licitações na época errada gera contratos superfaturados pela escassez momentânea.\n\nAgentes de Aprendizado por Reforço podem ser treinados nas séries temporais de inflação setorial para sugerir o timing exato da compra.\n\nA economia de escala aliada ao domínio temporal do mercado protege ferozmente a capacidade de investimento do Estado.",
        "pitch_amazon": "Entender o Aprendizado por Reforço é tocar no estado da arte da IA. O livro 'Reinforcement Learning: An Introduction' de Sutton e Barto é o manual acadêmico definitivo para os verdadeiramente curiosos.",
        "produto_nome": "Livro: Reinforcement Learning (Sutton & Barto)",
        "produto_url": "https://www.amazon.com.br/dp/0262039249?tag=SEU_LINK_AQUI",
        "ai_prompt": "A glowing chessboard where a robotic hand moves a budget coin piece to checkmate, representing strategic timing and reinforcement learning --ar 16:9"
    }
]

def enviar_email_notificacao(status, assunto_tema, conteudo, erro_msg=""):
    """
    Envia um e-mail com o status da publicação diária.
    """
    if not SENHA_APP_GMAIL:
        print("⚠️ SENHA_APP_GMAIL não encontrada. O e-mail de relatório não será enviado.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"[{status}] Relatório de Atividade LinkedIn - {AGENT_NAME}"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    corpo = f"""Olá,

Aqui é o seu agente {AGENT_NAME}.

Status da Execução: {status}
Tema do Dia: {assunto_tema}

📝 Conteúdo Publicado / Tentado:
--------------------------------------------------
{conteudo}
--------------------------------------------------
"""
    if erro_msg:
        corpo += f"\n❌ Detalhes do Erro:\n{erro_msg}"
        
    msg.set_content(corpo)

    try:
        print("📧 Conectando ao servidor SMTP do Gmail...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail de notificação enviado com sucesso para:", EMAIL_DESTINO)
    except Exception as e:
        print(f"❌ Erro ao enviar o e-mail: {e}")

def get_daily_content():
    """
    Seleciona o tema do dia baseado no dia do ano.
    Como temos 16 itens, um mesmo tema só se repetirá a cada 16 dias.
    """
    dia_do_ano = datetime.now().timetuple().tm_yday
    indice_hoje = dia_do_ano % len(CONTENT_DATABASE)
    return CONTENT_DATABASE[indice_hoje]

def create_linkedin_payload(content, author_urn):
    """
    Monta o payload JSON e a formatação final do texto visando monetização gentil.
    """
    # Construção do texto: Hook + Body + PS Suave + Link
    texto_final = f"{content['hook']}\n\n{content['body']}\n\nPS: {content['pitch_amazon']}\n\n🛒 Confira a recomendação aqui: {content['produto_url']}"
    
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": texto_final
                },
                # 'ARTICLE' gera nativamente um "Card" no LinkedIn usando a imagem da URL da Amazon
                "shareMediaCategory": "ARTICLE", 
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Ferramentas e literaturas para aperfeiçoar a Governança."
                        },
                        "originalUrl": content['produto_url'],
                        "title": {
                            "text": content['produto_nome']
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    return payload, texto_final

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
        erro_detalhado = f"HTTP {e.response.status_code}: {e.response.text}"
        return None, erro_detalhado
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    print(f"🤖 Iniciando {AGENT_NAME}: Orçamento, IA & Monetização...")
    
    # 1. Validação de Credenciais Básicas
    if not ACCESS_TOKEN or not AUTHOR_URN:
        erro_msg = "Variáveis LINKEDIN_ACCESS_TOKEN e LINKEDIN_URN_ID não configuradas no ambiente."
        print(f"❌ ERRO: {erro_msg}")
        enviar_email_notificacao("FALHA", "Erro de Configuração", "Execução abortada por falta de credenciais do LinkedIn.", erro_msg)
        sys.exit(1)
        
    # 2. Seleção do Conteúdo Rotativo
    daily_content = get_daily_content()
    print(f"🎯 Tema selecionado: {daily_content['tema']}")
    
    print(f"🎨 Dica de Prompt de Imagem (Midjourney/DALL-E):\n{daily_content['ai_prompt']}\n")
    
    # 3. Montagem do Payload
    print("🛠️ Montando o Payload do LinkedIn...")
    payload, texto_postagem = create_linkedin_payload(daily_content, AUTHOR_URN)
    
    # 4. Disparo
    print("🚀 Disparando postagem para a rede...")
    post_id, erro = post_to_linkedin(payload, ACCESS_TOKEN)
    
    # 5. Avaliação de Resultados e Envio de E-mail
    if post_id:
        print(f"✅ Post publicado com sucesso! ID: {post_id}")
        enviar_email_notificacao("SUCESSO", daily_content['tema'], texto_postagem)
    else:
        print(f"❌ Falha ao publicar. Detalhes: {erro}")
        enviar_email_notificacao("ERRO", daily_content['tema'], texto_postagem, erro)
        sys.exit(1)
