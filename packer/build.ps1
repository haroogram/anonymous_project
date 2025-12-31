# Packer AMI 빌드 스크립트 (Windows PowerShell)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Packer AMI 빌드 시작" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# 변수 파일 확인
if (-not (Test-Path "packer\variables.pkr.hcl")) {
    Write-Host "❌ variables.pkr.hcl 파일이 없습니다." -ForegroundColor Red
    Write-Host "packer\variables.pkr.hcl.example을 복사하여 설정하세요." -ForegroundColor Yellow
    exit 1
}

# Packer 설치 확인
$packerCmd = Get-Command packer -ErrorAction SilentlyContinue
if (-not $packerCmd) {
    Write-Host "❌ Packer가 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "https://www.packer.io/downloads 에서 설치하세요." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[1/3] Packer 설정 검증 중..." -ForegroundColor Yellow
packer validate -var-file=packer\variables.pkr.hcl packer.pkr.hcl

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Packer 설정 검증 실패" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/3] AMI 빌드 시작..." -ForegroundColor Yellow
Write-Host "이 작업은 10-15분 정도 소요될 수 있습니다." -ForegroundColor Cyan
Write-Host ""

packer build -var-file=packer\variables.pkr.hcl packer.pkr.hcl

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ AMI 빌드 완료!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Cyan
    Write-Host "1. AWS Console > EC2 > AMIs에서 생성된 AMI 확인" -ForegroundColor White
    Write-Host "2. 해당 AMI를 사용하여 EC2 인스턴스 생성" -ForegroundColor White
    Write-Host "3. Private Subnet에 배치" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ AMI 빌드 실패" -ForegroundColor Red
    exit 1
}

