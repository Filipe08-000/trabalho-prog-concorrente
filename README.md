# trabalho-prog-concorrente
Trabalho de duplas para a matéria de programação concorrente distribuída.  

# Sistema Paralelo de Processamento de Avaliações de Filmes com MovieLens 10M

## Disciplina

Programação Concorrente e Distribuída

## Professor

Rafael Marconi

## Integrantes

- Filipe Ferreira
- Max Muller

---

# Descrição

Este projeto utiliza o dataset MovieLens 10M para processar milhões de avaliações de filmes em paralelo, gerando rankings automáticos por categoria.

O foco principal do sistema é demonstrar conceitos de:

- concorrência
- paralelismo
- processamento distribuído
- análise de desempenho
- escalabilidade
- processamento de grandes volumes de dados

O sistema processa mais de 10 milhões de avaliações utilizando múltiplos workers, reduzindo significativamente o tempo de execução em comparação com o processamento serial.

---

# Objetivos

- Processar mais de 10 milhões de avaliações de filmes
- Gerar Top 10 filmes por categoria
- Calcular médias de avaliações
- Identificar filmes mais populares
- Executar processamento paralelo utilizando múltiplos workers
- Comparar execução serial vs paralela
- Medir ganho de performance e escalabilidade

---

# Dataset

Foi utilizado o dataset MovieLens 10M, disponibilizado pelo GroupLens Research.

O dataset contém:

- 10 milhões de avaliações
- aproximadamente 10 mil filmes
- milhares de usuários
- informações de gêneros e timestamps

Fonte oficial:

https://www.kaggle.com/datasets/amirmotefaker/movielens-10m-dataset-latest-version
https://grouplens.org/datasets/movielens/10m/

---

# Funcionalidades

## Rankings

- Top 10 filmes por gênero
- Top 10 filmes globais
- Filmes mais avaliados
- Filmes com melhor média
- Usuários mais ativos

## Processamento Paralelo

O sistema divide o processamento em múltiplos workers para acelerar os cálculos.

Exemplo:

- Worker 1 → Ação
- Worker 2 → Comédia
- Worker 3 → Drama
- Worker 4 → Ficção Científica

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
- Pandas
- PostgreSQL
- FastAPI
- multiprocessing
- concurrent.futures
- Docker
- Docker Compose

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

Para cada categoria de filme:

1. Coletar filmes do gênero
2. Agrupar avaliações
3. Calcular média das notas
4. Ordenar filmes por score
5. Retornar Top 10

---

# Processamento Paralelo

O sistema utiliza múltiplos processos para distribuir a carga de trabalho.

Estratégia utilizada:

- divisão por gênero
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

## Top 10 Ficção Científica

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

# Considerações Finais

O projeto demonstra na prática a utilização de técnicas de programação concorrente e distribuída aplicadas ao processamento de grandes volumes de dados.

A utilização de múltiplos workers permitiu reduzir significativamente o tempo de execução, evidenciando os benefícios do paralelismo em aplicações de análise de dados em larga escala.
