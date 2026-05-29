# trabalho-prog-concorrente
Trabalho de duplas para a matéria de programação concorrente distribuída.  
 
# Sistema Paralelo de Processamento de Avaliações de Filmes com MovieLens 10.5 M
 
## Disciplina
 
Programação Concorrente e Distribuída
 
## Professor
 
Rafael Marconi
 
## Integrantes
 
- Filipe Ferreira
- Max Muller
---
 
# Descrição
 
Este projeto utiliza o dataset MovieLens 10.5 M para processar milhões de avaliações de filmes em paralelo, gerando rankings automáticos por categoria.
 
O foco principal do sistema é demonstrar conceitos de:
 
- concorrência
- paralelismo
- processamento distribuído
- análise de desempenho
- escalabilidade
- processamento de grandes volumes de dados
O sistema processa mais de 10.5 milhões de avaliações utilizando múltiplos workers, reduzindo significativamente o tempo de execução em comparação com o processamento serial.
 
---
 
# Objetivos
 
- Processar mais de 10.5 milhões de avaliações de filmes
- Calcular médias de avaliações
- Identificar filmes mais populares
- Executar processamento paralelo utilizando múltiplos workers
- Comparar execução serial vs paralela
- Medir ganho de performance e escalabilidade
---
 
# Dataset
 
Foi utilizado o dataset MovieLens 10.5 M, disponibilizado pelo GroupLens Research.
 
O dataset contém:
 
- 10.5 milhões de avaliações
- aproximadamente 10 mil filmes
- milhares de usuários
- informações de gêneros e timestamps
Fonte oficial:
 
https://grouplens.org/datasets/movielens/tag-genome-2021/
 
---
 
# Funcionalidades
 
## Rankings
 
- Top 10 filmes de todos listados
- Filmes mais avaliados
- Filmes com melhor média
## Processamento Paralelo
 
O sistema divide o processamento em múltiplos workers para acelerar os cálculos.
 
Cada worker processa:
 
- agrupamento de avaliações
- cálculo de médias
- ordenação
- geração de rankings
---
 
# Arquitetura
 
```txt
Cliente/API
     ↓
Banco de Dados
     ↓
Fila de Processamento
     ↓
+-----------+-----------+
| Worker 1  | Worker 2  |
| Worker 3  | Worker 4  |
+-----------+-----------+
```
 
---
 
# Tecnologias Utilizadas
 
- Python
- FastAPI
- multiprocessing
- concurrent.futures
  
---
 
# Estrutura do Projeto
 
```txt
project/
│
├── api/
├── workers/
├── database/
├── datasets/
├── processing/
├── benchmarks/
├── docker-compose.yml
└── README.md
```
 
---
 
# Algoritmo Utilizado
 
---
 
# Processamento Paralelo
 
O sistema utiliza múltiplos processos para distribuir a carga de trabalho.
 
Estratégia utilizada:
 
- processamento em paralelo
- agregação final dos resultados
Tecnologias utilizadas:
 
```python
multiprocessing
ProcessPoolExecutor
```
 
---
 
# Benchmark
 
Exemplo de comparação entre execução serial e paralela:
 
| Workers | Tempo |
|---|---|
| 1 | 120s |
| 2 | 70s |
| 4 | 38s |
| 8 | 22s |
 
O processamento paralelo reduz significativamente o tempo total de execução.
 
---
 
# Escalabilidade
 
O sistema foi projetado para suportar grandes volumes de dados através de:
 
- processamento paralelo
- divisão de tarefas
- múltiplos workers
- execução distribuída
- otimização de consultas
---
 
# Exemplo de Resultado
 
| Ranking | Filme | Nota Média |
|---|---|---|
| 1 | Interstellar | 4.8 |
| 2 | Blade Runner | 4.7 |
| 3 | Matrix | 4.7 |
| 4 | Alien | 4.6 |
| 5 | Star Wars | 4.6 |
 
---
 
# Como Executar
 
## Clonar o projeto
 
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```
 
---
 
## Instalar dependências
 
```bash
pip install -r requirements.txt
```
 
---
 
## Executar o sistema
 
```bash
python main.py
```
 
---
 
# Conceitos Aplicados
 
## Concorrência
 
- múltiplos processos
- sincronização
- divisão de tarefas
## Processamento Distribuído
 
- workers independentes
- paralelização de cálculos
- distribuição de carga
## Banco de Dados
 
- consultas SQL
- agregações
- armazenamento de grandes volumes
## Performance
 
- benchmark
- throughput
- speedup
- escalabilidade
---
 
# Resultados Obtidos
 
## Dados Processados
 
| Métrica | Valor |
|---|---|
| Total de filmes catalogados | 84.661 |
| Total de linhas carregadas da base | 28.490.116 |
| Workers utilizados | 12 |
| Lotes de processamento | 12 |
 
## Análise de Desempenho
 
| Modo | Tempo |
|---|---|
| Serial | 70.35s |
| Paralelo (12 workers) | 25.94s |
| **Speedup** | **2.71x mais rápido** |
 
O processamento paralelo com 12 workers reduziu o tempo de execução de **70.35 segundos** para **25.94 segundos**, atingindo um speedup de **2.71x** em relação ao modo serial.
 
---
 
## TOP 10 Filmes Mais Avaliados (Geral)
 
| Ranking | Filme | Avaliações |
|---|---|---|
| 1 | Shawshank Redemption, The (1994) | 98.967 |
| 2 | Forrest Gump (1994) | 97.772 |
| 3 | Pulp Fiction (1994) | 93.156 |
| 4 | Silence of the Lambs, The (1991) | 88.573 |
| 5 | Matrix, The (1999) | 85.431 |
| 6 | Star Wars: Episode IV - A New Hope (1977) | 82.450 |
| 7 | Jurassic Park (1993) | 76.792 |
| 8 | Schindler's List (1993) | 72.143 |
| 9 | Braveheart (1995) | 69.190 |
| 10 | Toy Story (1995) | 68.884 |
 
---
 
## TOP 10 Filmes com Melhor Média (Geral)
 
| Ranking | Filme | Nota Média | Avaliações |
|---|---|---|---|
| 1 | Planet Earth II (2016) | 4.48 | 1.104 |
| 2 | Planet Earth (2006) | 4.46 | 1.681 |
| 3 | Shawshank Redemption, The (1994) | 4.42 | 98.967 |
| 4 | Band of Brothers (2001) | 4.39 | 1.317 |
| 5 | Cosmos | 4.39 | 263 |
| 6 | ID de Filme Desconhecido (66616) | 4.37 | 51 |
| 7 | ID de Filme Desconhecido (172591) | 4.37 | 606 |
| 8 | Cosmos: A Spacetime Odissey | 4.36 | 180 |
| 9 | Twin Peaks (1989) | 4.35 | 303 |
| 10 | ID de Filme Desconhecido (174053) | 4.35 | 1.378 |
 
---
 
# Considerações Finais
 
O projeto demonstra na prática a utilização de técnicas de programação concorrente e distribuída aplicadas ao processamento de grandes volumes de dados.
 
A utilização de múltiplos workers permitiu reduzir significativamente o tempo de execução, evidenciando os benefícios do paralelismo em aplicações de análise de dados em larga escala.
