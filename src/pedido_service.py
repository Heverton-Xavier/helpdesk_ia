import json
from src.config import PEDIDOS_JSON


def carregar_pedidos():
    """Carrega a base de pedidos do JSON."""
    try:
        with open(PEDIDOS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {PEDIDOS_JSON}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON: {PEDIDOS_JSON}")
        return {}


def consultar_pedido(numero_pedido):
    """
    Consulta um pedido pelo número.
    Retorna dicionário com dados do pedido ou None se não encontrado.
    """
    pedidos = carregar_pedidos()
    pedido = pedidos.get(str(numero_pedido))
    
    if pedido:
        return {
            "encontrado": True,
            "numero_pedido": str(numero_pedido),
            "dados": pedido
        }
    else:
        return {
            "encontrado": False,
            "numero_pedido": str(numero_pedido),
            "dados": None
        }


def decidir_abrir_chamado(categoria, prioridade, dados_pedido, analise_imagem=""):
    """
    Decide automaticamente se deve abrir um chamado.
    
    Critérios:
    - Prioridade crítica → abre chamado
    - Prioridade alta + pedido com problema → abre chamado
    - Pagamento pendente + comprovante enviado → abre chamado
    - Entrega com problema → abre chamado
    - Outros casos → não abre
    """
    motivos = []
    abrir = False
    
    # Regra 1: Prioridade crítica sempre abre chamado
    if prioridade == "crítica":
        abrir = True
        motivos.append("Prioridade crítica detectada")
    
    # Regra 2: Pedido não encontrado
    if not dados_pedido.get("encontrado", False):
        abrir = True
        motivos.append("Pedido não encontrado na base")
    
    # Regra 3: Pagamento pendente
    if dados_pedido.get("encontrado"):
        pedido = dados_pedido.get("dados", {})
        if pedido.get("status_pagamento") == "pendente":
            abrir = True
            motivos.append("Pagamento pendente")
        
        # Regra 4: Entrega com problema
        if pedido.get("status_entrega") in ["atrasado", "extraviado", "não enviado"]:
            if categoria in ["entrega", "pedido"]:
                abrir = True
                motivos.append("Problema na entrega")
        
        # Regra 5: Cancelamento solicitado
        if categoria == "cancelamento":
            abrir = True
            motivos.append("Solicitação de cancelamento")
    
    # Regra 6: Imagem enviada sugere problema
    if analise_imagem and "erro" in analise_imagem.lower():
        abrir = True
        motivos.append("Evidência de erro na imagem")
    
    return {
        "abrir_chamado": abrir,
        "motivos": motivos if motivos else ["Não foram identificados critérios para abertura de chamado"],
        "prioridade_chamado": prioridade
    }