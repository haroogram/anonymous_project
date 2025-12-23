# anonymous 프로젝트 자동 환경 설정 스크립트 (Windows PowerShell)
# 사용법: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "anonymous 프로젝트 환경 설정을 시작합니다" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Python 버전 확인 및 설치
Write-Host ""
Write-Host "[1/7] Python 버전 확인 중..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion 확인됨" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "Python을 자동으로 설치하려고 시도합니다..." -ForegroundColor Yellow
    Write-Host ""
    
    # winget 사용 시도 (Windows 10/11)
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "winget을 사용하여 Python을 설치합니다..." -ForegroundColor Cyan
        $response = Read-Host "Python 설치를 진행하시겠습니까? (관리자 권한 필요) [y/N]"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
                Write-Host "✅ Python 설치 완료" -ForegroundColor Green
                Write-Host "⚠️  새 터미널을 열어서 스크립트를 다시 실행해주세요." -ForegroundColor Yellow
                exit 0
            } catch {
                Write-Host "❌ winget을 통한 Python 설치에 실패했습니다." -ForegroundColor Red
            }
        }
    }
    
    # Chocolatey 사용 시도
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "Chocolatey를 사용하여 Python을 설치합니다..." -ForegroundColor Cyan
        $response = Read-Host "Python 설치를 진행하시겠습니까? (관리자 권한 필요) [y/N]"
        if ($response -eq 'y' -or $response -eq 'Y') {
            try {
                choco install python3 -y
                Write-Host "✅ Python 설치 완료" -ForegroundColor Green
                Write-Host "⚠️  새 터미널을 열어서 스크립트를 다시 실행해주세요." -ForegroundColor Yellow
                exit 0
            } catch {
                Write-Host "❌ Chocolatey를 통한 Python 설치에 실패했습니다." -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
    Write-Host "❌ Python 자동 설치에 실패했습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "Python을 수동으로 설치하는 방법:" -ForegroundColor Cyan
    Write-Host "  1. Python 공식 사이트: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. winget 사용: winget install Python.Python.3.12" -ForegroundColor White
    Write-Host "  3. Chocolatey 사용: choco install python3" -ForegroundColor White
    Write-Host ""
    Write-Host "Python 설치 후 PATH에 등록되었는지 확인하고 스크립트를 다시 실행해주세요." -ForegroundColor Yellow
    exit 1
}

# 2. 가상환경 생성
Write-Host ""
Write-Host "[2/7] 가상환경 생성 중..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  venv 폴더가 이미 존재합니다. 기존 가상환경을 사용합니다." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ 가상환경 생성 완료" -ForegroundColor Green
}

# 3. 가상환경 활성화 및 의존성 설치
Write-Host ""
Write-Host "[3/7] 가상환경 활성화 및 의존성 설치 중..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# pip 업그레이드
python -m pip install --upgrade pip --quiet

# requirements.txt 설치
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "✅ 의존성 설치 완료" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt 파일을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# 4. .env 파일 생성
Write-Host ""
Write-Host "[4/7] 환경 변수 파일 설정 중..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env 파일이 이미 존재합니다. 기존 파일을 유지합니다." -ForegroundColor Yellow
} else {
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "✅ .env 파일 생성 완료 (.env.example을 복사했습니다)" -ForegroundColor Green
        Write-Host "   필요시 .env 파일을 수정하여 환경 변수를 설정하세요." -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  .env.example 파일이 없습니다. 기본 .env 파일을 생성합니다." -ForegroundColor Yellow
        @"
# Django Settings
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database 설정 (선택사항)
# MariaDB 사용 시 아래 주석을 해제하고 설정하세요
# DB_ENGINE=mysql
# DB_NAME=anonymous_db
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
"@ | Out-File -FilePath .env -Encoding UTF8
        Write-Host "✅ 기본 .env 파일 생성 완료" -ForegroundColor Green
    }
}

# 5. 데이터베이스 마이그레이션
Write-Host ""
Write-Host "[5/7] 데이터베이스 마이그레이션 실행 중..." -ForegroundColor Yellow
python manage.py migrate --noinput
Write-Host "✅ 데이터베이스 마이그레이션 완료" -ForegroundColor Green

# 6. 정적 파일 수집 (선택사항)
Write-Host ""
Write-Host "[6/7] 정적 파일 수집 중..." -ForegroundColor Yellow
try {
    python manage.py collectstatic --noinput --clear
    Write-Host "✅ 정적 파일 수집 완료" -ForegroundColor Green
} catch {
    Write-Host "⚠️  정적 파일 수집 중 오류 발생 (개발 환경에서는 무시 가능)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 환경 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 명령어로 개발 서버를 실행할 수 있습니다:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "또는 다음 명령어로 슈퍼유저를 생성할 수 있습니다:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  python manage.py createsuperuser" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

