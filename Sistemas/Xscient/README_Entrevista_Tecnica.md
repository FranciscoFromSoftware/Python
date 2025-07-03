# Sistema de Gravação e Transcrição de Entrevistas Técnicas

## 📋 Visão Geral

Este sistema permite gravar áudio, capturar screenshots da tela e transcrever automaticamente o áudio para texto, sendo ideal para:

- **Entrevistas técnicas** (presenciais ou remotas)
- **Reuniões importantes** que precisam de documentação
- **Aulas e apresentações** que requerem registro audiovisual
- **Sessões de brainstorming** que precisam ser documentadas
- **Qualquer situação** que necessite de captura simultânea de áudio e tela

## 🚀 Funcionalidades

### ✅ Gravação de Áudio
- Gravação em tempo real do microfone
- Qualidade de áudio otimizada para reconhecimento de voz
- Formato WAV compatível com sistemas de transcrição
- Controle manual de início/fim (Ctrl+C)

### ✅ Captura de Tela
- Screenshots automáticos em intervalos configuráveis
- Numeração sequencial com timestamp
- Formato PNG para boa qualidade
- Thread separada para não interferir na gravação

### ✅ Transcrição Automática
- Conversão de áudio para texto usando Google Speech Recognition
- Configurado para português brasileiro
- Processamento automático após gravação
- Salvamento em arquivo de texto formatado

## 📦 Instalação

### 1. Pré-requisitos
- Python 3.7 ou superior
- Microfone funcionando
- Conexão com internet (para transcrição)
- Permissões de acesso ao microfone e tela

### 2. Instalar Dependências
```bash
pip install -r requirements_entrevista.txt
```

### 3. Dependências Instaladas
- `pyaudio>=0.2.11` - Gravação de áudio
- `pyautogui>=0.9.54` - Captura de tela
- `Pillow>=9.0.0` - Processamento de imagens
- `SpeechRecognition>=3.8.1` - Transcrição de áudio

## 🎯 Como Usar

### Execução Básica
```bash
python Entrevista_Tecnica_Transcrita.py
```

### Fluxo de Execução
1. **Inicialização**: Sistema configura áudio e cria pastas necessárias
2. **Gravação**: Inicia captura de áudio e screenshots simultaneamente
3. **Interrupção**: Pressione `Ctrl+C` para parar a gravação
4. **Transcrição**: Sistema pergunta se deseja transcrever o áudio
5. **Finalização**: Arquivos são organizados e salvos

### Exemplo de Uso
```bash
$ python Entrevista_Tecnica_Transcrita.py

Sistema de Gravação de Áudio e Captura de Tela
==================================================
Este sistema irá:
1. Gravar áudio do seu microfone
2. Capturar screenshots da tela
3. Oferecer transcrição do áudio (opcional)
==================================================
Pasta 'screenshots' criada automaticamente.
Iniciando captura de tela a cada 2 segundos...
Iniciando gravação de áudio e captura de tela...
Pressione Ctrl+C para parar a gravação.
--------------------------------------------------
Dicas para melhor qualidade:
- Fale claramente e em volume adequado
- Evite ruídos de fundo
- Mantenha distância consistente do microfone
--------------------------------------------------
Screenshot salvo: screenshots/screenshot_20250628_143015_0001.png
Screenshot salvo: screenshots/screenshot_20250628_143017_0002.png
...

^C
Interrompendo gravação...

Gravação finalizada!
Arquivos salvos:
- Áudio: audio.wav
- Screenshots: pasta 'screenshots'
- Tamanho do arquivo de áudio: 2.45 MB

Deseja transcrever o áudio? (s/n): s

Iniciando transcrição do áudio...
Carregando arquivo de áudio...
Processando transcrição (pode demorar alguns minutos)...
Transcrição concluída com sucesso!
Transcrição salva em: transcricao.txt

Transcrição concluída e salva!
Arquivo: transcricao.txt
```

## 📁 Arquivos Gerados

### Estrutura de Arquivos
```
projeto/
├── Entrevista_Tecnica_Transcrita.py    # Script principal
├── requirements_entrevista.txt         # Dependências
├── audio.wav                           # Arquivo de áudio gravado
├── transcricao.txt                     # Transcrição do áudio
└── screenshots/                        # Pasta com capturas de tela
    ├── screenshot_20250628_143015_0001.png
    ├── screenshot_20250628_143017_0002.png
    └── ...
```

### Descrição dos Arquivos
- **`audio.wav`**: Arquivo de áudio em formato WAV (qualidade CD)
- **`transcricao.txt`**: Texto transcrito com formatação organizada
- **`screenshots/`**: Pasta com todas as capturas de tela em PNG

## ⚙️ Configurações

### Variáveis Configuráveis
```python
# Intervalo entre capturas de tela (em segundos)
DURACAO_CAPTURA_TELA = 2

# Nome da pasta onde os screenshots serão salvos
PASTA_SCREENSHOTS = "screenshots"
```

### Configurações de Áudio
- **Formato**: 16-bit PCM (paInt16)
- **Canais**: 1 (mono)
- **Taxa de amostragem**: 44100 Hz (qualidade CD)
- **Buffer**: 1024 frames

### Configurações de Transcrição
- **Serviço**: Google Speech Recognition
- **Idioma**: Português brasileiro (pt-BR)
- **Limite**: 10MB por arquivo
- **Formato**: WAV obrigatório

## 🔧 Personalização

### Alterar Intervalo de Captura
```python
# Para capturar a cada 5 segundos
DURACAO_CAPTURA_TELA = 5

# Para capturar a cada 1 segundo (mais screenshots)
DURACAO_CAPTURA_TELA = 1
```

### Alterar Pasta de Screenshots
```python
# Para salvar em pasta personalizada
PASTA_SCREENSHOTS = "minhas_capturas"
```

### Transcrição Manual
```python
# Para transcrever arquivo específico
texto = transcrever_audio("meu_audio.wav")
if not texto.startswith("Erro"):
    salvar_transcricao(texto, "minha_transcricao.txt")
```

## ⚠️ Limitações e Observações

### Limitações Técnicas
- **Múltiplos monitores**: Captura apenas a tela principal
- **Qualidade de áudio**: Afeta diretamente a precisão da transcrição
- **Tamanho de arquivo**: Máximo 10MB para transcrição
- **Conexão internet**: Necessária para transcrição

### Dicas para Melhor Qualidade
1. **Áudio**:
   - Use microfone de boa qualidade
   - Evite ruídos de fundo
   - Fale claramente e em volume adequado
   - Mantenha distância consistente do microfone

2. **Transcrição**:
   - Áudio claro melhora a precisão
   - Evite falas muito rápidas
   - Pausas ajudam no reconhecimento
   - Verifique a conexão com internet

3. **Screenshots**:
   - Intervalos menores = mais arquivos
   - Considere o espaço em disco
   - PNG mantém boa qualidade

## 🐛 Solução de Problemas

### Erro: "No module named 'pyaudio'"
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux/Mac
sudo apt-get install python3-pyaudio  # Ubuntu/Debian
brew install portaudio                # Mac
```

### Erro: "Microfone não encontrado"
- Verifique se o microfone está conectado
- Confirme permissões de acesso ao microfone
- Teste o microfone em outras aplicações

### Erro: "Sem conexão com internet"
- Verifique sua conexão
- A transcrição requer internet
- Tente novamente mais tarde

### Erro: "Áudio não reconhecido"
- Verifique a qualidade do áudio
- Tente falar mais claramente
- Evite ruídos de fundo
- Verifique se o arquivo não está corrompido

### Screenshots não salvando
- Verifique permissões de escrita
- Confirme se há espaço em disco
- Verifique se a pasta foi criada

## 📊 Exemplo de Saída

### Arquivo de Transcrição (`transcricao.txt`)
```
TRANSCRIÇÃO DA ENTREVISTA TÉCNICA
==================================================
Data/Hora: 2025-06-28 14:30:15
==================================================

Olá, bem-vindo à entrevista técnica. Vamos começar 
falando sobre suas experiências anteriores com Python 
e desenvolvimento web. Pode me contar um pouco sobre 
os projetos que você desenvolveu?

Sim, claro! Trabalhei principalmente com Django e Flask 
para desenvolvimento web. Um dos projetos mais 
interessantes foi um sistema de e-commerce que 
desenvolvi usando Django REST Framework...

Muito interessante! E como você lidou com questões de 
performance nesse projeto?
```

### Log de Execução
```
Screenshot salvo: screenshots/screenshot_20250628_143015_0001.png
Screenshot salvo: screenshots/screenshot_20250628_143017_0002.png
Screenshot salvo: screenshots/screenshot_20250628_143019_0003.png
...
Áudio salvo: audio.wav
Total de screenshots capturados: 45
Duração aproximada da gravação: 90.2 segundos
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

**Nota**: Este sistema é ideal para uso pessoal e profissional, oferecendo uma solução completa para documentação de entrevistas e reuniões técnicas. 