import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from src.classificador import carregar_modelo, prever
from src.utils import obter_prioridade, obter_resposta_base
from src.llm_service import gerar_resposta_llm, analisar_imagem, gerar_resposta_final
from src.pedido_service import consultar_pedido, decidir_abrir_chamado
import base64
import os

app = Flask(__name__)

# Carregar modelo
print("=" * 50)
print("🛒 HelpDesk IA - Iniciando...")
print("=" * 50)
print("Carregando modelo de classificação...")
modelo = carregar_modelo()
print("✅ Modelo carregado e pronto!\n")


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "projeto": "HelpDesk Inteligente",
        "fase": "3 - Atendimento Multimodal",
        "endpoints": {
            "/classificar": "POST - Fase 1: classifica a dúvida",
            "/atender": "POST - Fase 2: classifica + gera resposta IA",
            "/atender-completo": "POST - Fase 3: texto + pedido + imagem + decisão"
        }
    })


@app.route("/classificar", methods=["POST"])
def classificar():
    dados = request.get_json()
    if not dados or "mensagem" not in dados:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

    mensagem = dados["mensagem"].strip()
    if len(mensagem) < 5:
        return jsonify({"erro": "Mensagem muito curta"}), 400

    try:
        resultado = prever(mensagem, modelo)
        categoria = resultado[0]["categoria"]
        confianca = resultado[0]["confianca"]
        prioridade = obter_prioridade(categoria)
        resposta_base = obter_resposta_base(categoria)

        return jsonify({
            "categoria": categoria,
            "prioridade": prioridade,
            "confianca": confianca,
            "resposta_base": resposta_base
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/atender", methods=["POST"])
def atender():
    dados = request.get_json()
    if not dados or "mensagem" not in dados:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

    mensagem = dados["mensagem"].strip()
    if len(mensagem) < 5:
        return jsonify({"erro": "Mensagem muito curta"}), 400

    try:
        resultado = prever(mensagem, modelo)
        categoria = resultado[0]["categoria"]
        confianca = resultado[0]["confianca"]
        prioridade = obter_prioridade(categoria)

        print(f"\n📩 Mensagem: {mensagem}")
        print(f"🏷️ Categoria: {categoria} | ⚡ Prioridade: {prioridade}")
        print("🤖 Gerando resposta com IA...")

        resposta_llm = gerar_resposta_llm(mensagem, categoria, prioridade)

        if resposta_llm is None:
            print("⚠️ LLM falhou, usando resposta base.")
            resposta_llm = obter_resposta_base(categoria)
        else:
            print("✅ Resposta gerada com sucesso!")

        return jsonify({
            "categoria": categoria,
            "prioridade": prioridade,
            "confianca": confianca,
            "resposta": resposta_llm
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/atender-completo", methods=["POST"])
def atender_completo():
    """
    FASE 3: Atendimento completo com texto, pedido e imagem.
    Entrada: { "mensagem": "...", "numero_pedido": "...", "imagem_base64": "..." (opcional) }
    """
    dados = request.get_json()

    if not dados or "mensagem" not in dados:
        return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

    mensagem = dados["mensagem"].strip()
    numero_pedido = dados.get("numero_pedido", "").strip()
    imagem_base64_str = dados.get("imagem_base64", "")

    if len(mensagem) < 5:
        return jsonify({"erro": "Mensagem muito curta"}), 400

    try:
        # 1. Classificar a mensagem
        resultado = prever(mensagem, modelo)
        categoria = resultado[0]["categoria"]
        confianca = resultado[0]["confianca"]
        prioridade = obter_prioridade(categoria)

        print(f"\n📩 Mensagem: {mensagem}")
        print(f"🏷️ Categoria: {categoria} | ⚡ Prioridade: {prioridade}")

        # 2. Consultar pedido (se informado)
        dados_pedido = None
        if numero_pedido:
            print(f"🔍 Consultando pedido: {numero_pedido}")
            dados_pedido = consultar_pedido(numero_pedido)
        else:
            dados_pedido = {"encontrado": False, "numero_pedido": None, "dados": None}

        # 3. Analisar imagem (se enviada)
        analise_img = ""
        if imagem_base64_str:
            print("🖼️ Analisando imagem...")
            # Salvar imagem temporária
            img_path = "temp_imagem.png"
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(imagem_base64_str))
            
            analise_img = analisar_imagem(img_path)
            print(f"📊 Análise: {analise_img[:100]}...")
            
            # Limpar arquivo temporário
            if os.path.exists(img_path):
                os.remove(img_path)
        else:
            analise_img = "Nenhuma imagem enviada"

        # 4. Decidir se abre chamado
        decisao = decidir_abrir_chamado(categoria, prioridade, dados_pedido, analise_img)
        print(f"🎯 Decisão: {'Abrir chamado' if decisao['abrir_chamado'] else 'Não abrir'} - {', '.join(decisao['motivos'])}")

        # 5. Gerar resposta final
        print("🤖 Gerando resposta final...")
        resposta_final = gerar_resposta_final(
            mensagem, categoria, prioridade, dados_pedido, analise_img, decisao
        )

        if resposta_final is None:
            resposta_final = obter_resposta_base(categoria)
            print("⚠️ LLM falhou, usando resposta base.")
        else:
            print("✅ Resposta final gerada!")

        return jsonify({
            "categoria": categoria,
            "prioridade": prioridade,
            "confianca": confianca,
            "dados_pedido": dados_pedido,
            "analise_imagem": analise_img,
            "decisao_chamado": decisao,
            "resposta": resposta_final
        })

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar: {str(e)}"}), 500


if __name__ == "__main__":
    print("\n🚀 API rodando em http://localhost:5000")
    print("Endpoints disponíveis:")
    print("  POST /classificar      - Fase 1")
    print("  POST /atender          - Fase 2")
    print("  POST /atender-completo - Fase 3")
    print("  GET  /                - Status\n")
    app.run(debug=True, host="0.0.0.0", port=5000)