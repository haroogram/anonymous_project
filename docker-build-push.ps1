param(
    [Parameter(Mandatory=$true)]
    [string]$DockerHubUsername,
    
    [string]$ImageName = "anonymous-project",
    
    [string]$Tag = "latest"
)

$ErrorActionPreference = "Stop"

$FullImageName = "${DockerHubUsername}/${ImageName}:${Tag}"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker 이미지 빌드 및 푸시" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "이미지: $FullImageName" -ForegroundColor Yellow

# 1. Docker 로그인 확인
Write-Host "`n[1/3] Docker Hub 로그인 상태 확인..." -ForegroundColor Yellow
$loginStatus = docker info 2>&1 | Select-String "Username"
if (-not $loginStatus) {
    Write-Host "Docker Hub에 로그인이 필요합니다." -ForegroundColor Yellow
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker 로그인 실패" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Docker Hub 로그인 확인" -ForegroundColor Green

# 2. 이미지 빌드
Write-Host "`n[2/3] Docker 이미지 빌드 중..." -ForegroundColor Yellow
docker build -t $FullImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 이미지 빌드 실패" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 이미지 빌드 완료" -ForegroundColor Green

# 3. Docker Hub에 푸시
Write-Host "`n[3/3] Docker Hub에 푸시 중..." -ForegroundColor Yellow
docker push $FullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 이미지 푸시 실패" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 이미지 푸시 완료" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "완료! 이미지: $FullImageName" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "`n사용 방법:"
Write-Host "docker pull $FullImageName"
Write-Host "docker run -d -p 8000:8000 --env-file .env $FullImageName"
