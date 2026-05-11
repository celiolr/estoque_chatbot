Write-Host "Criando o ambiente virtual Python..." -ForegroundColor DarkGreen
py -3.12 -m venv venv

Write-Host "Ativando o ambiente virtual..." -ForegroundColor DarkGreen
.\venv\Scripts\activate

Write-Host "Atualizando o pip..." -ForegroundColor DarkGreen
python -m pip install --upgrade pip

Write-Host "Instalando dependencias do projeto (requirements.txt)..." -ForegroundColor DarkGreen
pip install -r requirements.txt

Write-Host "Verificando se o arquivo .env existe..." -ForegroundColor DarkGreen
if (-not (Test-Path ".env")) {
    Set-Content -Path ".env" -Value "OPENAI_API_KEY='sk-SuaChaveDaOpenAiAqui...'"
    Set-Content -Path ".env" -Value "GROQ_API_KEY='gsk_SuaChaveDoGroqAqui...'"
    Write-Host "Arquivo .env criado com sucesso. Por favor, adicione suas chaves de APIs." -ForegroundColor Yellow
} else {
    Write-Host "Arquivo .env ja existe." -ForegroundColor Cyan
}

Write-Host "Atualizacao concluida!" -ForegroundColor DarkGreen