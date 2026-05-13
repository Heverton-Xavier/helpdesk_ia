import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

CHAMADOS_CSV = os.path.join(DATA_DIR, "chamados.csv")
PEDIDOS_JSON = os.path.join(DATA_DIR, "pedidos.json")
IMAGENS_DIR = os.path.join(DATA_DIR, "imagens")

CLASSIFICADOR_PKL = os.path.join(MODELS_DIR, "classificador.pkl")
VECTORIZER_PKL = os.path.join(MODELS_DIR, "vectorizer.pkl")

# Categorias
CATEGORIAS = [
    "login", "cadastro", "produto", "estoque", "carrinho",
    "pagamento", "cupom", "pedido", "entrega", "cancelamento"
]

# Mapeamento categoria → prioridade
PRIORIDADE_MAP = {
    "login": "baixa",
    "cadastro": "baixa",
    "produto": "baixa",
    "estoque": "média",
    "carrinho": "média",
    "cupom": "média",
    "pedido": "alta",
    "entrega": "alta",
    "pagamento": "crítica",
    "cancelamento": "crítica"
}

# Configuração DeepSeek
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"