# PowerShell script to build and push Docker images to Docker Hub
# Usage: .\build-and-push.ps1 -Tag "v1.0.0"

param(
    [Parameter(Mandatory=$true)]
    [string]$Tag
)

$DOCKER_USERNAME = "suhasvr"
$IMAGE_NAME = "task_manager_agent"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Building and Pushing Docker Images" -ForegroundColor Cyan
Write-Host "Tag: $Tag" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Build backend image
Write-Host "`n[1/4] Building backend image..." -ForegroundColor Yellow
docker build -f Dockerfile.backend -t "$DOCKER_USERNAME/${IMAGE_NAME}:backend-$Tag" .
docker build -f Dockerfile.backend -t "$DOCKER_USERNAME/${IMAGE_NAME}:backend-latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    exit 1
}

# Build frontend image
Write-Host "`n[2/4] Building frontend image..." -ForegroundColor Yellow
docker build -f Dockerfile.frontend -t "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-$Tag" .
docker build -f Dockerfile.frontend -t "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}

# Login to Docker Hub (if not already logged in)
Write-Host "`n[3/4] Checking Docker Hub login..." -ForegroundColor Yellow
docker info | Select-String -Pattern "Username" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Docker Hub:" -ForegroundColor Yellow
    docker login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker Hub login failed!" -ForegroundColor Red
        exit 1
    }
}

# Push backend images
Write-Host "`n[4/4] Pushing backend images..." -ForegroundColor Yellow
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:backend-$Tag"
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:backend-latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend push failed!" -ForegroundColor Red
    exit 1
}

# Push frontend images
Write-Host "Pushing frontend images..." -ForegroundColor Yellow
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-$Tag"
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "Successfully pushed all images!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Backend: $DOCKER_USERNAME/${IMAGE_NAME}:backend-$Tag" -ForegroundColor Cyan
Write-Host "Backend: $DOCKER_USERNAME/${IMAGE_NAME}:backend-latest" -ForegroundColor Cyan
Write-Host "Frontend: $DOCKER_USERNAME/${IMAGE_NAME}:frontend-$Tag" -ForegroundColor Cyan
Write-Host "Frontend: $DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest" -ForegroundColor Cyan
Write-Host "`nTo pull and run:" -ForegroundColor Yellow
Write-Host "  docker pull $DOCKER_USERNAME/${IMAGE_NAME}:backend-$Tag" -ForegroundColor White
Write-Host "  docker pull $DOCKER_USERNAME/${IMAGE_NAME}:frontend-$Tag" -ForegroundColor White

