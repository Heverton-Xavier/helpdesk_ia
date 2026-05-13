2. Ollama (para rodar as IAs localmente)

Baixe e instale: https://ollama.com/download/windows

Após instalar, o Ollama fica rodando em segundo plano automaticamente.

3. Modelos de IA (obrigatórios)

Abra o terminal e execute:
bash

# Modelo para gerar respostas de texto (2 GB)
ollama pull llama3.2

# Modelo para analisar imagens (4.5 GB)
ollama pull llava:7b

    💡 O download é feito uma única vez. Depois os modelos ficam salvos offline.

4. Dependências Python

No terminal, dentro da pasta do projeto:
bash

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar as bibliotecas
pip install -r requirements.txt

-------------------------------------------------------------------

▶️ Como Rodar o Projeto
bash

# Na pasta do projeto, com o venv ativado:
python -m api.app

A API estará disponível em: http://localhost:5000

--------------------------------------------------------------------

📡 Como Testar os Endpoints
Teste 1 — Classificar dúvida (Fase 1)

No PowerShell:
powershell

$body = '{"mensagem":"Paguei via Pix mas meu pedido continua aguardando"}'

Invoke-RestMethod -Uri http://localhost:5000/classificar -Method POST -ContentType "application/json" -Body $body

==============================================================

Linux/Mac (Terminal):
bash

curl -X POST http://localhost:5000/classificar \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"Paguei via Pix mas meu pedido continua aguardando"}'


--------------------------------------------------------------------

Teste 2 — Resposta com IA (Fase 2)
powershell

$body = '{"mensagem":"Meu cupom de desconto não funciona"}'

Invoke-RestMethod -Uri http://localhost:5000/atender -Method POST -ContentType "application/json" -Body $body

==============================================================

Linux/Mac (Terminal):
bash

curl -X POST http://localhost:5000/atender \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"Meu cupom de desconto não funciona"}'


--------------------------------------------------------------------

Teste 3 — Atendimento completo com pedido (Fase 3)
powershell

$body = '{"mensagem":"Comprovante de Pix em anexo","numero_pedido":"1006"}'

Invoke-RestMethod -Uri http://localhost:5000/atender-completo -Method POST -ContentType "application/json" -Body $body

==============================================================

Linux/Mac (Terminal):
bash

curl -X POST http://localhost:5000/atender-completo \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"Comprovante de Pix em anexo","numero_pedido":"1006"}'

--------------------------------------------------------------------

Teste 4 — Atendimento com imagem (Fase 3)
powershell

Passo 1: Criar imagem de teste (Windows)
powershell

Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(400, 200)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.Clear([System.Drawing.Color]::White)
$font = New-Object System.Drawing.Font("Arial", 24)
$g.DrawString("COMPROVANTE PIX", $font, [System.Drawing.Brushes]::Black, 50, 50)
$g.DrawString("Valor: R$ 349,90", $font, [System.Drawing.Brushes]::Black, 50, 100)
$g.DrawString("Pedido: #1006", $font, [System.Drawing.Brushes]::Black, 50, 150)
$bmp.Save("$PWD\data\imagens\comprovante_teste.png")
$g.Dispose()
$bmp.Dispose()
Write-Host "✅ Imagem criada!"

Passo 2: Converter para base64 e enviar (Windows)
powershell

$imgPath = "$PWD\data\imagens\comprovante_teste.png"
$imgBytes = [System.IO.File]::ReadAllBytes($imgPath)
$imgBase64 = [System.Convert]::ToBase64String($imgBytes)
$body = '{"mensagem":"Comprovante de Pix em anexo","numero_pedido":"1006","imagem_base64":"' + $imgBase64 + '"}'
Invoke-RestMethod -Uri http://localhost:5000/atender-completo -Method POST -ContentType "application/json" -Body $body

==============================================================

Linux/Mac:

Criar imagem: (use qualquer imagem PNG e salve em data/imagens/comprovante_teste.png)

Enviar:
bash

IMG_BASE64=$(base64 -w 0 data/imagens/comprovante_teste.png)
curl -X POST http://localhost:5000/atender-completo \
  -H "Content-Type: application/json" \
  -d "{\"mensagem\":\"Comprovante de Pix em anexo\",\"numero_pedido\":\"1006\",\"imagem_base64\":\"$IMG_BASE64\"}"