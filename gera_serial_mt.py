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
TAMANHO_CHUNK = 2500000  # Tamanho do lote de linhas para cada worker

# ==========================================
# 1. FUNÇÕES DE CARREGAMENTO DOS METADADOS
# ==========================================
def carregar_filmes():
    """Carrega os metadados dos filmes usando leitura de linha por linha limpa."""
    arquivo_escolhido = METADADOS_UPDATED if os.path.exists(METADADOS_UPDATED) else METADADOS_PADRAO
    if os.path.exists(arquivo_escolhido):
        print(f"-> Usando metadados: {os.path.basename(arquivo_escolhido)}")
    else:
        print(f"Erro: Nenhum arquivo de metadados encontrado em: {PASTA_DATASET}")
        return {}

    filmes = {}
    with open(arquivo_escolhido, 'r', encoding='utf-8') as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa in ('[', ']'): 
                continue
            if linha_limpa.endswith(','): 
                linha_limpa = linha_limpa[:-1].strip()
            try:
                dados = json.loads(linha_limpa)
                # Mapeia usando o campo correto do seu arquivo: item_id
                id_raw = dados.get('item_id') or dados.get('movie_id') or dados.get('id')
                if id_raw is not None:
                    id_filme = int(id_raw)
                    filmes[id_filme] = dados.get('title', 'Sem Título')
            except Exception:
                continue
    return filmes

# ==========================================
# 2. WORKER PARALELO (MAP: PROCESSA CHUNKS)
# ==========================================
def processar_chunk_ratings(linhas_chunk):
    """
    Função executada pelos Workers em paralelo.
    Processa um lote de linhas do arquivo ratings de forma independente.
    """
    estatisticas_locais = defaultdict(lambda: {'soma': 0.0, 'contagem': 0})
    for linha in linhas_chunk:
        linha_limpa = linha.strip()
        if not linha_limpa or linha_limpa in ('[', ']'): 
            continue
        if linha_limpa.endswith(','): 
            linha_limpa = linha_limpa[:-1].strip()
            
        try:
            dados = json.loads(linha_limpa)
            id_raw = dados.get('item_id') or dados.get('movie_id') or dados.get('id') or dados.get('movieId')
            nota_raw = dados.get('rating') or dados.get('score')
            
            if id_raw is not None and nota_raw is not None:
                id_filme = int(id_raw)
                nota = float(nota_raw)
                estatisticas_locais[id_filme]['soma'] += nota
                estatisticas_locais[id_filme]['contagem'] += 1
        except Exception:
            continue
    
    return dict(estatisticas_locais)

# ==========================================
# 3. AGREGAÇÃO GLOBAL (REDUCE)
# ==========================================
def unificar_resultados(resultados_parciais):
    """Junta as contagens e somas calculadas por todos os workers."""
    estatisticas_globais = defaultdict(lambda: {'soma': 0.0, 'contagem': 0})
    for parcial in resultados_parciais:
        for id_filme, dados in parcial.items():
            estatisticas_globais[id_filme]['soma'] += dados['soma']
            estatisticas_globais[id_filme]['contagem'] += dados['contagem']
    return estatisticas_globais

# ==========================================
# HELPER: EXECUÇÃO PARALELA COM N WORKERS
# ==========================================
def executar_paralelo(todas_linhas, num_workers):
    """Executa o pipeline Map-Reduce com um número específico de workers."""
    total_linhas = len(todas_linhas)
    chunks = [todas_linhas[i:i + TAMANHO_CHUNK] for i in range(0, total_linhas, TAMANHO_CHUNK)]
    print(f"  Dividido em {len(chunks)} lotes para {num_workers} workers...")

    inicio = time.perf_counter()
    with mp.Pool(processes=num_workers) as pool:
        resultados_parciais = pool.map(processar_chunk_ratings, chunks)
    estatisticas = unificar_resultados(resultados_parciais)
    tempo = time.perf_counter() - inicio

    return estatisticas, tempo

# ==========================================
# 4. FLUXO DE EXECUÇÃO SEQUENCIAL E PARALELO
# ==========================================
if __name__ == '__main__':
    print("Carregando arquivo de metadados dos filmes...")
    filmes = carregar_filmes()
    print(f"Total de filmes catalogados: {len(filmes)}\n")
    
    if not filmes:
        print("Processamento interrompido: Mapeamento de filmes vazio.")
        exit()

    if not os.path.exists(ARQUIVO_RATINGS):
        print(f"Erro: Arquivo de avaliações não encontrado em: {ARQUIVO_RATINGS}")
        exit()

    print("Lendo arquivo ratings.json para a RAM (~1.4GB, aguarde)...")
    with open(ARQUIVO_RATINGS, 'r', encoding='utf-8') as f:
        todas_linhas = f.readlines()

    # Multiplica os dados para aumentar o volume de processamento e evidenciar o speedup
    FATOR_MULTIPLICACAO = 2  # Ajuste: 2x ~120s serial, 3x ~180s serial
    todas_linhas = todas_linhas * FATOR_MULTIPLICACAO
    print(f"[INFO] Dados multiplicados por {FATOR_MULTIPLICACAO}x para benchmark de carga.")

    total_linhas = len(todas_linhas)
    print(f"Total de linhas carregadas da base: {total_linhas}\n")

    # --- EXECUÇÃO SERIAL ---
    print("Iniciando processamento SERIAL...")
    inicio_s = time.perf_counter()
    estatisticas_serial = processar_chunk_ratings(todas_linhas)
    tempo_s = time.perf_counter() - inicio_s
    print(f"Tempo Serial Total: {tempo_s:.4f} segundos\n")
    print("-" * 50)

    # --- EXECUÇÃO PARALELA COM 2, 4, 8 E 12 THREADS ---
    resultados_por_workers = {}
    for num_workers in [2, 4, 8, 12]:
        print(f"\nIniciando processamento PARALELO com {num_workers} workers...")
        estatisticas, tempo = executar_paralelo(todas_linhas, num_workers)
        resultados_por_workers[num_workers] = {'estatisticas': estatisticas, 'tempo': tempo}
        speedup = tempo_s / tempo if tempo > 0 else 1
        print(f"  Tempo ({num_workers} workers): {tempo:.4f}s | Speedup: {speedup:.2f}x")

    print("\n" + "=" * 50)

    # --- ANÁLISE DE PERFORMANCE CONSOLIDADA ---
    print(f"\nANÁLISE DE DESEMPENHO CONSOLIDADA:")
    print(f"{'Modo':<20} {'Tempo (s)':<15} {'Speedup':<10}")
    print("-" * 45)
    print(f"{'Serial':<20} {tempo_s:<15.4f} {'1.00x':<10}")
    for num_workers, dados in resultados_por_workers.items():
        tempo_p = dados['tempo']
        speedup = tempo_s / tempo_p if tempo_p > 0 else 1
        print(f"{f'Paralelo ({num_workers} workers)':<20} {tempo_p:<15.4f} {f'{speedup:.2f}x':<10}")

    # Usa as estatísticas do último run (12 workers) para os rankings
    estatisticas_final = resultados_por_workers[12]['estatisticas']

    # --- IMPRESSÃO DOS RANKINGS GERAIS REALIZADOS ---
    # 1. Top 10 Filmes Mais Avaliados
    mais_avaliados = sorted(estatisticas_final.items(), key=lambda x: x[1]['contagem'], reverse=True)[:10]
    print("\n=========================================")
    print("   TOP 10 FILMES MAIS AVALIADOS (Geral)")
    print("=========================================")
    for i, (id_f, dados) in enumerate(mais_avaliados, 1):
        nome_filme = filmes.get(id_f, f"ID de Filme Desconhecido ({id_f})")
        print(f"{i}. {nome_filme} - {dados['contagem']} avaliações")

    # 2. Top 10 Filmes com Melhor Média Geral
    melhores_medias = []
    for id_f, dados in estatisticas_final.items():
        if dados['contagem'] >= MINIMO_AVALIACOES:
            media = dados['soma'] / dados['contagem']
            melhores_medias.append((id_f, media, dados['contagem']))
            
    melhores_medias = sorted(melhores_medias, key=lambda x: x[1], reverse=True)[:10]
    
    print("\n=========================================")
    print("   TOP 10 FILMES COM MELHOR MÉDIA (Geral)")
    print("=========================================")
    for i, (id_f, media, votos) in enumerate(melhores_medias, 1):
        nome_filme = filmes.get(id_f, f"ID de Filme Desconhecido ({id_f})")
        print(f"{i}. {nome_filme} - Nota Média: {media:.2f} ({votos} avaliações)")