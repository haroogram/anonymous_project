$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "anonymous 프로젝트 환경 설정을 시작합니다" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# PowerShell 실행 정책 우회 (현재 프로세스만)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 1. Python 확인
Write-Host "[1/7] Python 버전 확인 중..." -ForegroundColor Yellow

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $response = Read-Host "winget으로 Python을 설치할까요? [y/N]"
        if ($response -match '^[yY]$') {
            winget install --id Python.Python.3.12 --exact --silent `
              --accept-package-agreements --accept-source-agreements
            Write-Host "⚠️  새 터미널에서 다시 실행하세요." -ForegroundColor Yellow
            exit 0
        }
    }
    exit 1
}

python --version

# 2. 가상환경
Write-Host "[2/7] 가상환경 생성 중..." -ForegroundColor Yellow
if (-not (Test-Path venv)) {
    python -m venv venv
}

# 3. 가상환경 활성화
Write-Host "[3/7] 가상환경 활성화 및 의존성 설치 중..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

if (Test-Path requirements.txt) {
    python -m pip install -r requirements.txt
} else {
    Write-Host "❌ requirements.txt 없음" -ForegroundColor Red
    exit 1
}

# 4. .env
Write-Host "[4/7] 환경 변수 설정 중..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
    } else {
@"
SECRET_KEY=django-insecure-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
"@ | Out-File -FilePath .env -Encoding UTF8

    }
}

# 5. migrate
Write-Host "[5/7] 데이터베이스 마이그레이션..." -ForegroundColor Yellow
python manage.py migrate --noinput

# 6. 초기 데이터
Write-Host "[6/7] 초기 데이터 로드..." -ForegroundColor Yellow
python manage.py load_initial_data
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ load_initial_data 없음 → 건너뜀" -ForegroundColor Yellow
}

# 7. collectstatic
Write-Host "[7/7] 정적 파일 수집..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ collectstatic 실패 (개발환경 OK)" -ForegroundColor Yellow
}

Write-Host "✅ 환경 설정 완료!" -ForegroundColor Green
Write-Host "python manage.py runserver"
