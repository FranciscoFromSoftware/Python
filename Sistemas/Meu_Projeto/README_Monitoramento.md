# Sistema de Monitoramento de Atividade do Computador

## 📋 Visão Geral

Este sistema monitora continuamente as atividades do usuário no computador, rastreando qual aplicativo ou janela está ativa e por quanto tempo. Os dados são coletados em tempo real, salvos em arquivo JSON como backup e posteriormente inseridos em um banco de dados MySQL para análise e geração de relatórios.

### Casos de Uso Ideais:
- **Análise de produtividade** pessoal ou corporativa
- **Auditoria de uso** de aplicativos
- **Relatórios de tempo** gasto em diferentes atividades
- **Otimização de fluxo de trabalho**
- **Controle de tempo** em projetos específicos

## 🚀 Funcionalidades

### ✅ Monitoramento em Tempo Real
- Captura automática de janelas ativas
- Detecção de mudanças de aplicativo
- Registro preciso de tempo de uso
- Intervalo configurável de verificação

### ✅ Armazenamento Seguro
- Backup automático em arquivo JSON
- Inserção em banco de dados MySQL
- Configuração via variáveis de ambiente
- Tratamento robusto de erros

### ✅ Análise de Dados
- Estrutura de dados organizada
- Compatível com pandas para análise
- Timestamps precisos em formato ISO
- Duração calculada automaticamente

## 📦 Instalação

### 1. Pré-requisitos
- Python 3.7 ou superior
- MySQL Server rodando (local ou remoto)
- Permissões de acesso às janelas do sistema
- Arquivo `.env` configurado

### 2. Instalar Dependências
```bash
pip install -r requirements_monitoramento.txt
```

### 3. Dependências Instaladas
- `psutil>=5.9.0` - Informações do sistema
- `pygetwindow>=0.0.9` - Captura de janelas ativas
- `pandas>=1.5.0` - Manipulação de dados
- `sqlalchemy>=1.4.0` - ORM para banco de dados
- `pymysql>=1.0.0` - Driver MySQL
- `python-dotenv>=0.19.0` - Variáveis de ambiente

### 4. Configurar Banco de Dados
```sql
-- Criar banco de dados
CREATE DATABASE meus_dados;

-- Usar o banco
USE meus_dados;

-- Criar tabela para os dados
CREATE TABLE uso_aplicativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_end DATETIME,
    application_or_url VARCHAR(500),
    duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5. Configurar Arquivo .env
Crie um arquivo `.env` no mesmo diretório do script:
```env
LOGIN=seu_usuario_mysql
PASSWORD=sua_senha_mysql
```

## 🎯 Como Usar

### Execução Básica
```bash
python Meu_Dia.py
```

### Fluxo de Execução
1. **Inicialização**: Sistema carrega configurações e conecta ao banco
2. **Monitoramento**: Loop contínuo verificando janelas ativas
3. **Detecção**: Identifica mudanças de aplicativo
4. **Registro**: Salva dados em JSON e MySQL
5. **Finalização**: Resumo completo ao pressionar Ctrl+C

### Exemplo de Uso
```bash
$ python Meu_Dia.py

Sistema de Monitoramento de Atividade do Computador
============================================================
Este sistema irá monitorar:
1. Qual aplicativo/janela está ativo
2. Por quanto tempo cada atividade durou
3. Salvar dados em JSON e MySQL
============================================================
Intervalo de verificação: 5 segundos
Arquivo de backup: activity_log.json
Banco de dados: meus_dados.uso_aplicativos
============================================================
Iniciando rastreamento de atividade. Pressione Ctrl+C para parar.
------------------------------------------------------------
Ativo agora: Documento - Microsoft Word em 2025-06-28T14:30:15.123456
Log: Documento - Microsoft Word por 45.67 segundos
Ativo agora: https://www.google.com - Google Chrome em 2025-06-28T14:31:00.789012
Log: https://www.google.com - Google Chrome por 120.45 segundos
Ativo agora: Visual Studio Code em 2025-06-28T14:33:01.234567
...

^C
------------------------------------------------------------
Interrupção detectada. Finalizando monitoramento...
Log da sessão final: Visual Studio Code por 180.23 segundos
Log salvo temporariamente em activity_log.json
Rastreamento de atividade parado.

Inserindo dados no banco de dados...

--- DataFrame Gerado ---
Total de registros: 15
Colunas: ['timestamp_end', 'application_or_url', 'duration_seconds']

Primeiros registros:
                    timestamp_end    application_or_url  duration_seconds
0  2025-06-28T14:30:15.123456  Documento - Microsoft Word            45.67
1  2025-06-28T14:31:00.789012  https://www.google.com - Google Chrome           120.45
2  2025-06-28T14:33:01.234567  Visual Studio Code           180.23

Dados inseridos com sucesso na tabela 'uso_aplicativos' do MySQL.
Total de registros inseridos: 15

============================================================
MONITORAMENTO FINALIZADO
============================================================
Total de atividades registradas: 15
Arquivo de backup: activity_log.json
Dados inseridos em: meus_dados.uso_aplicativos
============================================================
```

## 📁 Arquivos Gerados

### Estrutura de Arquivos
```
projeto/
├── Meu_Dia.py                    # Script principal
├── requirements_monitoramento.txt # Dependências
├── .env                          # Credenciais (não versionado)
├── activity_log.json             # Backup dos dados
└── README_Monitoramento.md       # Esta documentação
```

### Descrição dos Arquivos
- **`Meu_Dia.py`**: Script principal de monitoramento
- **`activity_log.json`**: Backup dos dados em formato JSON
- **`.env`**: Arquivo com credenciais do banco (não versionado)
- **`requirements_monitoramento.txt`**: Lista de dependências

## ⚙️ Configurações

### Variáveis Configuráveis
```python
# Intervalo entre verificações (em segundos)
RECORD_INTERVAL_SECONDS = 5

# Arquivo de backup JSON
OUTPUT_FILE = "activity_log.json"

# Configurações do banco de dados
DATABASE_HOST = "localhost"
DATABASE_NAME = "meus_dados"
TABLE_NAME = "uso_aplicativos"
```

### Configurações de Monitoramento
- **Intervalo de verificação**: 5 segundos (configurável)
- **Detecção**: Mudanças de janela ativa
- **Precisão**: Até 0.01 segundos
- **Compatibilidade**: Windows, Linux, macOS

### Configurações de Banco de Dados
- **Tipo**: MySQL
- **Conexão**: Local ou remota
- **Tabela**: `uso_aplicativos`
- **Modo**: Append (adiciona sem apagar)

## 🔧 Personalização

### Alterar Intervalo de Verificação
```python
# Para verificação mais frequente (mais preciso)
RECORD_INTERVAL_SECONDS = 1

# Para verificação menos frequente (menos uso de CPU)
RECORD_INTERVAL_SECONDS = 10
```

### Alterar Configurações do Banco
```python
# Para banco remoto
DATABASE_HOST = "192.168.1.100"

# Para tabela personalizada
TABLE_NAME = "minhas_atividades"
```

### Personalizar Estrutura de Dados
```python
# Adicionar campos personalizados
activity_log.append({
    "timestamp_end": timestamp_now.isoformat(),
    "application_or_url": current_active_window,
    "duration_seconds": round(duration_seconds, 2),
    "usuario": "francisco",  # Campo adicional
    "categoria": "trabalho"  # Campo adicional
})
```

## 📊 Estrutura de Dados

### Tabela MySQL
```sql
CREATE TABLE uso_aplicativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_end DATETIME,
    application_or_url VARCHAR(500),
    duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Arquivo JSON
```json
[
    {
        "timestamp_end": "2025-06-28T14:30:15.123456",
        "application_or_url": "Documento - Microsoft Word",
        "duration_seconds": 45.67
    },
    {
        "timestamp_end": "2025-06-28T14:31:00.789012",
        "application_or_url": "https://www.google.com - Google Chrome",
        "duration_seconds": 120.45
    }
]
```

## 📈 Análise de Dados

### Consultas SQL Úteis
```sql
-- Tempo total por aplicativo
SELECT 
    application_or_url,
    SUM(duration_seconds) as tempo_total_segundos,
    SUM(duration_seconds)/3600 as tempo_total_horas
FROM uso_aplicativos 
GROUP BY application_or_url 
ORDER BY tempo_total_segundos DESC;

-- Atividades por dia
SELECT 
    DATE(timestamp_end) as data,
    COUNT(*) as total_atividades,
    SUM(duration_seconds)/3600 as tempo_total_horas
FROM uso_aplicativos 
GROUP BY DATE(timestamp_end)
ORDER BY data DESC;

-- Aplicativos mais usados hoje
SELECT 
    application_or_url,
    SUM(duration_seconds)/3600 as horas_hoje
FROM uso_aplicativos 
WHERE DATE(timestamp_end) = CURDATE()
GROUP BY application_or_url 
ORDER BY horas_hoje DESC;
```

### Análise com Pandas
```python
import pandas as pd
from sqlalchemy import create_engine

# Conectar ao banco
engine = create_engine('mysql+pymysql://usuario:senha@localhost/meus_dados')

# Carregar dados
df = pd.read_sql('SELECT * FROM uso_aplicativos', engine)

# Análise por aplicativo
analise = df.groupby('application_or_url')['duration_seconds'].agg([
    'count', 'sum', 'mean'
]).sort_values('sum', ascending=False)

print(analise)
```

## ⚠️ Limitações e Observações

### Limitações Técnicas
- **Janelas minimizadas**: Não são detectadas
- **Aplicativos em tela cheia**: Podem não ser detectados
- **Múltiplos monitores**: Funciona apenas com monitor principal
- **Permissões**: Requer acesso às janelas do sistema

### Considerações de Privacidade
- **Dados sensíveis**: O sistema captura títulos de janelas
- **URLs**: Navegadores podem expor URLs nos títulos
- **Armazenamento**: Dados ficam em arquivo local e banco
- **Uso**: Apenas para análise pessoal/profissional

### Dicas para Melhor Funcionamento
1. **Permissões**: Garanta acesso às janelas do sistema
2. **Intervalo**: Ajuste conforme necessidade (1-10 segundos)
3. **Backup**: Verifique regularmente o arquivo JSON
4. **Banco**: Mantenha MySQL rodando durante o monitoramento

## 🐛 Solução de Problemas

### Erro: "No module named 'pymysql'"
```bash
pip install pymysql
```

### Erro: "Access denied for user"
- Verifique credenciais no arquivo `.env`
- Confirme se o usuário tem acesso ao banco
- Teste conexão manual com MySQL

### Erro: "Table doesn't exist"
```sql
CREATE TABLE uso_aplicativos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp_end DATETIME,
    application_or_url VARCHAR(500),
    duration_seconds DECIMAL(10,2)
);
```

### Erro: "Cannot connect to MySQL"
- Verifique se MySQL está rodando
- Confirme host e porta corretos
- Teste conexão: `mysql -u usuario -p`

### Erro: "Permission denied"
- Execute como administrador (Windows)
- Verifique permissões de escrita no diretório
- Confirme acesso às janelas do sistema

### Dados não sendo salvos
- Verifique se o arquivo `.env` existe
- Confirme se as variáveis estão corretas
- Teste conexão com banco manualmente

## 🔒 Segurança

### Boas Práticas
- **Arquivo .env**: Nunca versionar no Git
- **Credenciais**: Use senhas fortes
- **Acesso**: Restrinja acesso ao banco
- **Backup**: Mantenha cópias dos dados

### Exemplo de .gitignore
```
.env
*.json
__pycache__/
*.pyc
```

## 📊 Exemplo de Relatório

### Relatório Diário
```
RELATÓRIO DE ATIVIDADE - 2025-06-28
====================================
Total de atividades: 45
Tempo total monitorado: 8.5 horas

TOP 5 APLICATIVOS:
1. Visual Studio Code: 3.2 horas (37.6%)
2. Google Chrome: 2.1 horas (24.7%)
3. Microsoft Word: 1.8 horas (21.2%)
4. Excel: 0.9 horas (10.6%)
5. Outlook: 0.5 horas (5.9%)

ATIVIDADES POR HORA:
09:00-10:00: 12 atividades
10:00-11:00: 8 atividades
11:00-12:00: 15 atividades
...
```

## 🤝 Contribuições

Para contribuir com melhorias:
1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Implemente as melhorias
4. Teste adequadamente
5. Envie um pull request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

**Francisco H. Lomas**
- Criado em: 28/06/2025
- Versão: 1.0

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção de solução de problemas
2. Consulte a documentação do código
3. Abra uma issue no repositório

---

**Nota**: Este sistema é ideal para análise de produtividade pessoal e corporativa, oferecendo insights valiosos sobre o uso do tempo no computador. 