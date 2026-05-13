import ollama
import base64
import os
import json


def corrigir_texto(texto):
    """Corrige erros comuns do Llama 3.2 em português."""
    correcoes = {
        "Quero": "Quero",
        "meninas": "minúsculas",
        "maisculas": "maiúsculas",
        "  ": " ",
    }
    
    for errado, certo in correcoes.items():
        texto = texto.replace(errado, certo)
    
    return texto


def gerar_resposta_llm(mensagem, categoria, prioridade):
    """
    Gera uma resposta humanizada usando Ollama (Llama 3.2 local).
    Usado na Fase 2 — endpoint /atender.
    """
    prompt = f"""
Você é um assistente de helpdesk de uma loja online brasileira chamada TechStore.
Responda SEMPRE em português do Brasil, de forma amigável, profissional e objetiva.

CONTEXTO DA DÚVIDA:
- Categoria identificada: {categoria}
- Prioridade: {prioridade}
- Mensagem do cliente: "{mensagem}"

INSTRUÇÕES:
1. Cumprimente o cliente com "Olá!"
2. Mostre que entendeu o problema
3. Forneça um passo a passo numerado para resolver
4. Se for prioridade crítica, demonstre urgência e atenção redobrada
5. Se for prioridade baixa, seja leve e tranquilo
6. Ofereça ajuda adicional ao final
7. NÃO prometa prazos exatos nem valores
8. NÃO invente funcionalidades que não existem
9. Mantenha resposta entre 5 e 15 linhas
10. Use tom empático mas profissional
11. REVISE a gramática: use acentos corretos, evite erros de digitação

Responda apenas a mensagem final para o cliente, sem metadados.
"""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "Você é um atendente de helpdesk brasileiro, prestativo, empático e eficiente. Você fala português do Brasil fluentemente e sem erros gramaticais."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.5,
                "num_predict": 500
            }
        )
        resposta = response["message"]["content"].strip()
        resposta = corrigir_texto(resposta)
        return resposta
    except Exception as e:
        print(f"❌ Erro Ollama (gerar_resposta_llm): {e}")
        return None


def simular_analise_imagem(caminho_imagem, tamanho_kb):
    """
    Simula uma análise de imagem baseada no nome do arquivo e tamanho.
    Usado como fallback quando o modelo de visão não está disponível.
    """
    nome_arquivo = os.path.basename(caminho_imagem).lower()
    
    if "comprovante" in nome_arquivo or "pix" in nome_arquivo:
        return "Imagem analisada (simulação): Comprovante de pagamento Pix detectado. O documento contém dados de transação bancária e parece ser legítimo."
    elif "erro" in nome_arquivo or "print" in nome_arquivo:
        return "Imagem analisada (simulação): Print de tela com mensagem de erro do sistema detectado. O erro aparece durante o uso do site."
    elif "produto" in nome_arquivo or "danificado" in nome_arquivo:
        return "Imagem analisada (simulação): Foto de produto com possível avaria na embalagem. Recomenda-se avaliação da equipe de qualidade."
    elif "cupom" in nome_arquivo:
        return "Imagem analisada (simulação): Print de cupom de desconto que apresenta erro ao ser aplicado no carrinho de compras."
    elif "login" in nome_arquivo:
        return "Imagem analisada (simulação): Tela de login com mensagem de erro. Possível problema de credenciais ou conta bloqueada."
    elif "entrega" in nome_arquivo or "rastreio" in nome_arquivo:
        return "Imagem analisada (simulação): Informações de rastreamento de entrega. O status mostra divergência na data prevista."
    elif tamanho_kb < 1:
        return "Imagem analisada (simulação): Imagem muito pequena para análise detalhada. Possivelmente um ícone ou placeholder de teste."
    elif tamanho_kb < 10:
        return f"Imagem analisada (simulação): Arquivo compacto de {tamanho_kb:.1f} KB. A qualidade pode estar reduzida, mas o conteúdo parece relevante."
    else:
        return f"Imagem analisada (simulação): Arquivo de {tamanho_kb:.1f} KB recebido com sucesso. O conteúdo parece estar relacionado à dúvida relatada pelo cliente."


def analisar_imagem(caminho_imagem):
    """
    Analisa uma imagem usando LLaVA 7B (modelo multimodal leve).
    
    Fluxo:
    1. Tenta LLaVA 7B (~8 GB RAM)
    2. Se falhar, tenta Moondream (~4 GB RAM)  
    3. Se ambos falharem, usa simulação baseada no arquivo
    """
    if not os.path.exists(caminho_imagem):
        return "Imagem não encontrada no sistema."

    try:
        tamanho_kb = os.path.getsize(caminho_imagem) / 1024
        
        with open(caminho_imagem, "rb") as f:
            imagem_bytes = f.read()
        
        imagem_base64 = base64.b64encode(imagem_bytes).decode("utf-8")
        
        # Prompt neutro para evitar bloqueios de segurança
        prompt = """
Descreva esta imagem de forma técnica e objetiva em português do Brasil:
1. Qual o tipo de conteúdo visual mostrado (documento, tela de sistema, produto, etc.)?
2. Quais elementos visuais estão presentes (cores, textos, números, logotipos)?
3. A imagem parece mostrar algum erro, confirmação ou problema?

Apenas descreva o que vê. Não interprete dados pessoais. Máximo 4 linhas.
"""
        
        # Tentativa 1: LLaVA 7B
        try:
            print("🖼️ Tentando análise com LLaVA 7B...")
            response = ollama.chat(
                model="llava:7b",
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [imagem_base64]
                }],
                options={"num_predict": 120}
            )
            resultado = response["message"]["content"].strip()
            
            # Verificar se a resposta é um bloqueio
            if "não posso ajudar" in resultado.lower() or "desculpe" in resultado.lower():
                print("⚠️ LLaVA bloqueou a análise. Tentando Moondream...")
                raise Exception("Resposta bloqueada pelo modelo")
            
            print("✅ Imagem analisada com LLaVA 7B")
            return resultado
            
        except Exception as erro_llava:
            print(f"   LLaVA falhou: {str(erro_llava)[:60]}...")
            
            # Tentativa 2: Moondream
            try:
                print("🖼️ Tentando análise com Moondream...")
                response = ollama.chat(
                    model="moondream",
                    messages=[{
                        "role": "user",
                        "content": prompt,
                        "images": [imagem_base64]
                    }],
                    options={"num_predict": 120}
                )
                resultado = response["message"]["content"].strip()
                print("✅ Imagem analisada com Moondream")
                return resultado
                
            except Exception as erro_moondream:
                print(f"   Moondream falhou: {str(erro_moondream)[:60]}...")
                print("⚠️ Nenhum modelo de visão disponível. Usando simulação.")
                return simular_analise_imagem(caminho_imagem, tamanho_kb)
            
    except Exception as e:
        return f"Erro ao processar imagem: {str(e)}"


def gerar_resposta_final(mensagem, categoria, prioridade, dados_pedido, analise_imagem, decisao):
    """
    Gera a resposta final completa para o cliente (Fase 3).
    Inclui contexto do pedido, análise da imagem e decisão sobre chamado.
    """
    # Formatar dados do pedido para o prompt
    if dados_pedido and dados_pedido.get("encontrado"):
        cliente = dados_pedido.get("dados", {}).get("cliente", "Cliente")
        produto = dados_pedido.get("dados", {}).get("produto", "produto")
        status = dados_pedido.get("dados", {}).get("status_pedido", "não informado")
        pagamento = dados_pedido.get("dados", {}).get("status_pagamento", "não informado")
        entrega = dados_pedido.get("dados", {}).get("status_entrega", "não informado")
        metodo = dados_pedido.get("dados", {}).get("metodo_pagamento", "não informado")
        
        info_pedido = f"""
Pedido #{dados_pedido.get('numero_pedido')}:
- Cliente: {cliente}
- Produto: {produto}
- Status do pedido: {status}
- Status do pagamento: {pagamento}
- Método de pagamento: {metodo}
- Status da entrega: {entrega}
"""
    else:
        info_pedido = "Nenhum pedido encontrado com esse número."
        cliente = "Cliente"

    prompt = f"""
Você é um assistente de helpdesk de uma loja online brasileira chamada TechStore.
Responda SEMPRE em português do Brasil, de forma completa, profissional e empática.

CONTEXTO COMPLETO DO ATENDIMENTO:

📩 Mensagem do cliente: "{mensagem}"
🏷️ Categoria identificada: {categoria}
⚡ Prioridade: {prioridade}

📦 DADOS DO PEDIDO:
{info_pedido}

🖼️ ANÁLISE DA IMAGEM ENVIADA:
{analise_imagem if analise_imagem else "Nenhuma imagem foi enviada pelo cliente."}

🎯 DECISÃO AUTOMÁTICA DO SISTEMA:
- Chamado aberto: {"SIM" if decisao.get("abrir_chamado") else "NÃO"}
- Motivo: {", ".join(decisao.get("motivos", ["Não especificado"]))}
- Prioridade do chamado: {decisao.get("prioridade_chamado", "não definida")}

INSTRUÇÕES PARA SUA RESPOSTA:
1. Cumprimente o cliente pelo nome: {cliente}
2. Mencione o número do pedido
3. Explique o que você viu na imagem enviada (se houver análise)
4. Informe que um chamado foi aberto (se for o caso) e explique por quê
5. Forneça orientações numeradas e claras para os próximos passos
6. Se for prioridade crítica, demonstre urgência e atenção
7. Mantenha tom profissional mas acolhedor
8. NÃO invente dados que não estão no contexto
9. NÃO prometa prazos exatos nem valores
10. Use no máximo 15 linhas
11. REVISE a gramática do português (acentos, crase, concordância)

Responda apenas a mensagem final para o cliente, sem metadados.
"""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "Você é um atendente de helpdesk brasileiro completo, profissional e eficiente. Você sempre responde em português correto e bem escrito."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.5,
                "num_predict": 600
            }
        )
        resposta = response["message"]["content"].strip()
        resposta = corrigir_texto(resposta)
        return resposta
    except Exception as e:
        print(f"❌ Erro Ollama (gerar_resposta_final): {e}")
        return None