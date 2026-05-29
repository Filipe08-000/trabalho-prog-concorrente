import multiprocessing as mp
import time
import json
import os
from collections import defaultdict

# ==========================================
# CONFIGURAÇÃO DE CAMINHOS ABSOLUTOS
# ==========================================
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_DATASET = os.path.join(DIRETORIO_ATUAL, 'movie_dataset_public_final', 'raw')

ARQUIVO_RATINGS = os.path.join(PASTA_DATASET, 'ratings.json')
METADADOS_UPDATED = os.path.join(PASTA_DATASET, 'metadata_updated.json')
METADADOS_PADRAO = os.path.join(PASTA_DATASET, 'metadata.json')

MINIMO_AVALIACOES = 50
TAMANHO_CHUNK = 100000  # Quantidade de linhas por worker

# ==========================================
# FUNÇÃO AUXILIAR DE EXTRAÇÃO DE DADOS
# ==========================================
def extrair_dados_filme(dados, dicionario_filmes):
    """Extrai e padroniza as informações de um dicionário de filme."""
    id_raw = dados.get('movie_id') or dados.get('id') or dados.get('movieId') or dados.get('item_id')
    if id_raw is None:
        return
    
    id_filme = int(id_raw)
    titulo = dados.get('title') or dados.get('original_title') or "Sem Título"
    
    generos_raw = dados.get('genres') or dados.get('genre') or []
    if isinstance(generos_raw, str):
        generos = [g.strip() for g in generos_raw.split('|')]
    elif isinstance(generos_raw, list):
        generos = [g if isinstance(g, str) else g.get('name', '') for g in generos_raw]
    else:
        generos = []

    dicionario_filmes[id_filme] = {'titulo': titulo, 'generos': generos}

# ==========================================
# 1. FUNÇÕES PRINCIPAIS E MAP-REDUCE
# ==========================================
def carregar_filmes():
    """Carrega o catálogo de filmes tratando formatos de Array JSON e vírgulas residuais."""
    if os.path.exists(METADADOS_UPDATED):
        arquivo_escolhido = METADADOS_UPDATED
        print("-> Usando metadados atualizados (metadata_updated.json)")
    elif os.path.exists(METADADOS_PADRAO):
        arquivo_escolhido = METADADOS_PADRAO
        print("-> Usando metadados padrão (metadata.json)")
    else:
        print(f"Erro: Nenhum arquivo de metadados encontrado na pasta: {PASTA_DATASET}")
        return {}

    filmes = {}
    
    # Estratégia 1: Tenta carregar o arquivo completo como Array JSON válido
    try:
        with open(arquivo_escolhido, 'r', encoding='utf-8') as f:
            dados_completos = json.load(f)
            if isinstance(dados_completos, list):
                for item in dados_completos:
                    extrair_dados_filme(item, filmes)
                if filmes:
                    return filmes
    except Exception:
        pass  # Se falhar (por formatação ou tamanho), vai para a estratégia alternativa por linha

    # Estratégia 2: Leitura linha por linha limpando pontuações de array ([, ], e ,)
    filmes = {}
    with open(arquivo_escolhido, 'r', encoding='utf-8') as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa in ('[', ']'):
                continue
            if linha_limpa.endswith(','):
                linha_limpa = linha_limpa[:-1].strip()
            if linha_limpa.endswith(']'):
                linha_limpa = linha_limpa[:-1].strip()
            
            try:
                dados = json.loads(linha_limpa)
                extrair_dados_filme(dados, filmes)
            except Exception:
                continue
    return filmes

def processar_chunk_ratings(linhas_chunk):
    """
    Função MAP: Processa um bloco de avaliações limpando a formatação de arrays JSON.
    """
    estatisticas_locais = defaultdict(lambda: {'soma': 0.0, 'contagem': 0})
    for linha in linhas_chunk:
        linha_limpa = linha.strip()
        # Ignora delimitadores de array JSON
        if not linha_limpa or linha_limpa in ('[', ']'):
            continue
        # Remove vírgulas residuais no fim da linha
        if linha_limpa.endswith(','):
            linha_limpa = linha_limpa[:-1].strip()
        if linha_limpa.endswith(']'):
            linha_limpa = linha_limpa[:-1].strip()
            
        try:
            dados = json.loads(linha_limpa)
            id_raw = dados.get('movie_id') or dados.get('id') or dados.get('movieId') or dados.get('item_id')
            nota_raw = dados.get('rating') or dados.get('score')
            
            if id_raw is not None and nota_raw is not None:
                id_filme = int(id_raw)
                nota = float(nota_raw)
                estatisticas_locais[id_filme]['soma'] += nota
                estatisticas_locais[id_filme]['contagem'] += 1
        except Exception:
            continue
    
    return dict(estatisticas_locais)

def unificar_resultados(resultados_parciais):
    """Função REDUCE: Junta os dicionários criados pelos workers."""
    estatisticas_globais = defaultdict(lambda: {'soma': 0.0, 'contagem': 0})
    for parcial in resultados_parciais:
        for id_filme, dados in parcial.items():
            estatisticas_globais[id_filme]['soma'] += dados['soma']
            estatisticas_globais[id_filme]['contagem'] += dados['contagem']
    return estatisticas_globais

# ==========================================
# 2. EXECUÇÃO SERIAL VS PARALELA
# ==========================================
def processamento_serial(linhas_totais):
    print("Iniciando processamento SERIAL...")
    inicio = time.perf_counter()
    resultado = processar_chunk_ratings(linhas_totais)
    fim = time.perf_counter()
    tempo = fim - inicio
    print(f"Tempo Serial: {tempo:.4f} segundos")
    return resultado, tempo

def processamento_paralelo(linhas_totais):
    cpus = mp.cpu_count()
    print(f"Iniciando processamento PARALELO com {cpus} workers...")
    inicio = time.perf_counter()
    
    chunks = [linhas_totais[i:i + TAMANHO_CHUNK] for i in range(0, len(linhas_totais), TAMANHO_CHUNK)]
    
    with mp.Pool(processes=cpus) as pool:
        resultados_parciais = pool.map(processar_chunk_ratings, chunks)
        
    resultado = unificar_resultados(resultados_parciais)
    fim = time.perf_counter()
    tempo = fim - inicio
    print(f"Tempo Paralelo: {tempo:.4f} segundos")
    return resultado, tempo

# ==========================================
# 3. GERAÇÃO DOS RANKINGS
# ==========================================
def gerar_rankings(estatisticas, filmes):
    print("\nCalculando médias e gerando rankings...")
    medias_filmes = {}
    
    for id_filme, dados in estatisticas.items():
        if dados['contagem'] >= MINIMO_AVALIACOES and id_filme in filmes:
            media = dados['soma'] / dados['contagem']
            medias_filmes[id_filme] = {
                'titulo': filmes[id_filme]['titulo'],
                'generos': filmes[id_filme]['generos'],
                'media': media,
                'total_avaliacoes': dados['contagem']
            }

    if not medias_filmes:
        print("Aviso: Nenhum filme cruzou os critérios mínimos ou os IDs de avaliações não batem com os metadados.")
        return

    # Top Populares
    populares = sorted(medias_filmes.values(), key=lambda x: x['total_avaliacoes'], reverse=True)[:5]
    print("\n--- TOP 5 FILMES MAIS POPULARES ---")
    for f in populares:
        print(f"{f['titulo']} - Avaliações: {f['total_avaliacoes']}")

    # Top Categorias
    categorias_alvo = ['Action', 'Comedy', 'Sci-Fi', 'Romance', 'Drama']
    for categoria in categorias_alvo:
        filmes_categoria = [f for f in medias_filmes.values() if any(categoria.lower() in g.lower() for g in f['generos'])]
        if not filmes_categoria:
            continue
        top10 = sorted(filmes_categoria, key=lambda x: x['media'], reverse=True)[:10]
        
        print(f"\n--- TOP 10 MELHORES FILMES: {categoria.upper()} ---")
        for i, f in enumerate(top10, 1):
            print(f"{i}. {f['titulo']} - Nota Média: {f['media']:.2f} ({f['total_avaliacoes']} avaliações)")

# ==========================================
# 4. BLOCO PRINCIPAL
# ==========================================
if __name__ == '__main__':
    print("Carregando arquivo de metadados dos filmes...")
    filmes = carregar_filmes()
    print(f"Total de filmes catalogados: {len(filmes)}")
    
    if not filmes:
        print("Processamento interrompido: Não foi possível mapear os filmes.")
        exit()

    if not os.path.exists(ARQUIVO_RATINGS):
        print(f"Erro: Arquivo de avaliações não encontrado em: {ARQUIVO_RATINGS}")
        exit()

    print("Lendo arquivo ratings.json para a RAM (Aguarde, arquivo de ~1.4GB)...")
    with open(ARQUIVO_RATINGS, 'r', encoding='utf-8') as f:
        todas_linhas = f.readlines()
        
    print(f"Total de linhas carregadas da base de dados: {len(todas_linhas)}\n")

    # Execução e medição dos tempos
    estatisticas_serial, tempo_s = processamento_serial(todas_linhas)
    print("-" * 40)
    estatisticas_paralelo, tempo_p = processamento_paralelo(todas_linhas)
    print("-" * 40)
    
    # Exibição do Speedup
    speedup = tempo_s / tempo_p
    print(f"\nANÁLISE DE DESEMPENHO:")
    print(f"Tempo Serial: {tempo_s:.2f}s")
    print(f"Tempo Paralelo: {tempo_p:.2f}s")
    print(f"Speedup: {speedup:.2f}x mais rápido em modo paralelo.")
    
    gerar_rankings(estatisticas_paralelo, filmes)