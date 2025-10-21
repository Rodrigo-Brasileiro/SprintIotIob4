# 🧠 Face Recognition Microservice – FastAPI + OpenCV + MediaPipe

## 📋 Descrição

Este projeto é um **microserviço de reconhecimento facial** desenvolvido com **FastAPI**, **OpenCV** e **MediaPipe**, projetado para **autenticação biométrica leve e local**.  
Ele permite o **cadastro facial** e a **verificação em tempo real via webcam**, podendo ser integrado a aplicações **web**, **mobile** ou **IoT (Arduino, Raspberry Pi)**.  

---

## 🧩 Arquitetura da Solução

- **FastAPI** → Framework backend rápido e moderno para APIs assíncronas.  
- **OpenCV** → Captura e processamento de imagens em tempo real.  
- **MediaPipe FaceMesh** → Detecção e rastreamento de pontos faciais (468 landmarks).  
- **NumPy** → Manipulação de arrays e cálculos vetoriais para comparação facial.  
- **SQLite** → Armazenamento local de logs e registros de uso.  
- **Docker** → Containerização para garantir portabilidade e compatibilidade.  

---

## ⚙️ Pré-requisitos

Certifique-se de ter os seguintes componentes instalados:

| Tecnologia | Versão recomendada |
|-------------|-------------------|
| 🐍 Python | 3.10 – 3.11 |
| 🐋 Docker Desktop | 25.0+ |
| 🧱 Docker Compose | 2.20+ |
| 💻 Navegador compatível | Chrome / Edge |

> ⚠️ O `MediaPipe` **não é compatível com Python 3.12+**.  
> Se for rodar **localmente (sem Docker)**, use preferencialmente **Python 3.10 ou 3.11**.

---

## 🚀 Como executar o projeto

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/seuusuario/face-microservice.git
cd face-microservice
```

### 2️⃣ Subir o container com Docker
```bash
docker compose up -d --build
```

### 3️⃣ Acessar a aplicação

- **API Swagger** → [http://localhost:8000/docs](http://localhost:8000/docs)  
- **Demo Web (Webcam)** → [http://localhost:8000/demo](http://localhost:8000/demo)

---

## 🧠 Como funciona

### 📸 `/enroll` – Cadastro facial

1. O usuário informa um nome.  
2. A webcam é acionada e captura **3 imagens** do rosto:  
   - **Frontal**  
   - **Virando à direita**  
   - **Virando à esquerda**  
3. O sistema gera um **vetor de características (embedding facial)** para cada ângulo.  
4. As informações são salvas em `data/encodings/encodings.npz`.

---

### 🔍 `/verify` – Verificação facial

1. O usuário é filmado pela webcam.  
2. O vetor atual é comparado com os embeddings salvos.  
3. O sistema calcula a **precisão da similaridade facial** (em %) e retorna o resultado:

```json
{
  "matched": true,
  "user": "Rodrigo",
  "precision": 92.4
}
```

---

## 📂 Estrutura do projeto

```
face-microservice/
│
├── app/
│   ├── main.py              # API FastAPI principal
│   ├── camera.py            # Captura e leitura da webcam
│   ├── face_recognition.py  # Lógica de detecção e comparação facial
│   ├── models.py            # Estruturas de dados (Pydantic)
│   └── utils.py             # Funções auxiliares
│
├── data/
│   └── encodings/           # Embeddings salvos (.npz)
│
├── templates/
│   └── index.html           # Interface web simples para captura via webcam
│
├── Dockerfile               # Configuração do container
├── docker-compose.yml       # Orquestração Docker
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação
```

---

## 🧰 Principais dependências

```txt
fastapi==0.111.0
uvicorn==0.30.0
opencv-python==4.10.0
mediapipe==0.10.9
numpy==1.26.4
jinja2==3.1.4
```

---

## 🔧 Executar sem Docker (modo local)

Se desejar rodar localmente (com Python 3.10 ou 3.11):

```bash
python -m venv venv
venv\Scripts\activate      # (Windows)
# source venv/bin/activate  (Linux/Mac)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Depois, acesse:  
👉 [http://127.0.0.1:8000/demo](http://127.0.0.1:8000/demo)

---

## 🧭 Fluxo de uso

1. **Acesse o endpoint `/demo`** no navegador.  
2. **Permita o acesso à câmera.**  
3. Clique em **“Cadastrar rosto”**, insira seu nome e siga as instruções de posição.  
4. Após o cadastro, use **“Verificar rosto”** para testar o reconhecimento.  
5. O sistema exibirá se o rosto foi reconhecido e a **precisão percentual da correspondência**.

---

## 🚧 Possíveis problemas

| Problema | Solução |
|----------|----------|
| ❌ Webcam não abre no localhost | Verifique se o navegador permitiu o acesso à câmera. |
| ❌ MediaPipe não instala | Confirme se está usando Python ≤ 3.11 ou utilize Docker. |
| ❌ Erro de porta ocupada | Execute `docker compose down` e suba novamente. |

---

## 💡 Futuras melhorias

- 🔒 Integração com autenticação JWT.  
- ☁️ Salvamento dos embeddings no **AWS S3** ou **Firebase**.  
- 🤖 Treinamento incremental para múltiplos usuários.  
- 📱 Interface mobile (React Native ou Flutter).  
- 🧬 Substituir o MediaPipe por **FaceNet** ou **InsightFace** para maior precisão.  
- 🧑‍💻 Dashboard administrativo com histórico de verificações.

---

## 🧑‍💻 Autor

**Rodrigo Brasileiro**  
💼 Engenharia de Software – FIAP  
🌍 Projeto voltado à **Global Solution 2025 – Resiliência e Monitoramento Inteligente**
