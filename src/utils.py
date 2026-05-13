from src.config import PRIORIDADE_MAP


def obter_prioridade(categoria):
    """Retorna a prioridade baseada na categoria."""
    return PRIORIDADE_MAP.get(categoria, "média")


def obter_resposta_base(categoria):
    """Retorna uma resposta base para a categoria (fallback caso LLM falhe)."""
    respostas = {
        "login": "Verifique se o email e senha estão corretos. Tente redefinir a senha se necessário.",
        "cadastro": "Confira se todos os campos obrigatórios foram preenchidos. Verifique se o email já não está cadastrado.",
        "produto": "Acesse a página do produto para ver descrição completa, fotos e avaliações de outros clientes.",
        "estoque": "O produto pode estar momentaneamente sem estoque. Clique em 'Avise-me' para ser notificado quando voltar.",
        "carrinho": "Limpe o cache do navegador e tente novamente. Verifique se o produto ainda está disponível.",
        "pagamento": "Verifique o status do pagamento no seu banco. O Pix pode levar alguns minutos para compensar. Se o problema persistir, entre em contato com o suporte financeiro.",
        "cupom": "Confira se o cupom foi digitado corretamente, se está dentro do prazo de validade e se o produto participa da promoção.",
        "pedido": "Acesse 'Meus Pedidos' no menu principal. Lá você encontra o status e detalhes de todas as suas compras.",
        "entrega": "Verifique o código de rastreio enviado por email. O prazo de entrega pode variar conforme a região. Acompanhe pelo site da transportadora.",
        "cancelamento": "Acesse 'Meus Pedidos' e selecione 'Cancelar'. Se o pedido já foi enviado, você precisará recusar a entrega ou devolver o produto."
    }
    return respostas.get(categoria, "Entre em contato com nosso suporte para mais informações.")