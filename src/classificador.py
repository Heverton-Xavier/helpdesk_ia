import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from src.config import CHAMADOS_CSV, CLASSIFICADOR_PKL, VECTORIZER_PKL, CATEGORIAS

def carregar_dados():
    """Carrega a base de chamados do CSV."""
    df = pd.read_csv(CHAMADOS_CSV)
    return df["mensagem"], df["categoria"]


def criar_pipeline():
    """Cria o pipeline: TF-IDF + Naive Bayes com parâmetros ajustados."""
    pipeline = Pipeline([
        ("vectorizer", TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 3),
            max_features=8000,
            min_df=1,
            max_df=0.9,
            sublinear_tf=True
        )),
        ("classifier", MultinomialNB(alpha=0.01))
    ])
    return pipeline


def treinar_modelo(salvar=True):
    """Treina o pipeline e salva o modelo se solicitado."""
    print("=" * 60)
    print("TREINANDO MODELO DE CLASSIFICAÇÃO")
    print("=" * 60)

    print("\nCarregando dados...")
    X, y = carregar_dados()

    print(f"Base carregada: {len(X)} registros")
    print(f"Distribuição:\n{y.value_counts()}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Treino: {len(X_train)} | Teste: {len(X_test)}")
    print("\nTreinando pipeline...")
    pipeline = criar_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acuracia = accuracy_score(y_test, y_pred)

    print(f"\nAcurácia: {acuracia:.2%}")
    print("\nRelatório de classificação:")
    print(classification_report(y_test, y_pred, zero_division=0))

    if salvar:
        joblib.dump(pipeline, CLASSIFICADOR_PKL)
        print(f"\nModelo salvo em: {CLASSIFICADOR_PKL}")

    return pipeline


def carregar_modelo():
    """Carrega o modelo treinado do disco."""
    try:
        pipeline = joblib.load(CLASSIFICADOR_PKL)
        print(f"Modelo carregado de: {CLASSIFICADOR_PKL}")
        return pipeline
    except FileNotFoundError:
        print("Modelo não encontrado. Execute treinar_modelo() primeiro.")
        return None


def prever(mensagem, pipeline=None):
    """
    Classifica uma ou mais mensagens.
    Retorna lista de dicionários com categoria e confiança.
    """
    if pipeline is None:
        pipeline = carregar_modelo()

    if pipeline is None:
        return None

    if isinstance(mensagem, str):
        mensagem = [mensagem]

    categorias = pipeline.predict(mensagem)
    probabilidades = pipeline.predict_proba(mensagem)

    resultados = []
    for i, cat in enumerate(categorias):
        confianca = max(probabilidades[i])
        resultados.append({
            "categoria": cat,
            "confianca": round(confianca * 100, 2)
        })

    return resultados


if __name__ == "__main__":
    pipeline = treinar_modelo(salvar=True)

    print("\n" + "=" * 60)
    print("TESTES RÁPIDOS")
    print("=" * 60)

    testes = [
        "Paguei com Pix e não confirmou",
        "Meu código de rastreio não funciona",
        "Cupom de desconto expirou",
        "Quero cancelar meu pedido",
        "Não consigo fazer login",
        "Carrinho travou na finalização",
        "Boleto não compensou ainda",
        "Onde encontro a ficha técnica do produto?",
        "Entrega atrasada faz 10 dias",
        "Quero me cadastrar mas CPF não aceito",
    ]

    for frase in testes:
        resultado = prever(frase, pipeline)
        print(f"\nFrase: {frase}")
        print(f"Categoria: {resultado[0]['categoria']} (confiança: {resultado[0]['confianca']}%)")