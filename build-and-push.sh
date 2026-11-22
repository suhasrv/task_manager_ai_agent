#!/bin/bash
# Bash script to build and push Docker images to Docker Hub
# Usage: ./build-and-push.sh v1.0.0

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <tag>"
    echo "Example: $0 v1.0.0"
    exit 1
fi

TAG=$1
DOCKER_USERNAME="suhasvr"
IMAGE_NAME="task_manager_agent"

echo "========================================="
echo "Building and Pushing Docker Images"
echo "Tag: $TAG"
echo "========================================="

# Build backend image
echo ""
echo "[1/4] Building backend image..."
docker build -f Dockerfile.backend -t "$DOCKER_USERNAME/${IMAGE_NAME}:backend-$TAG" .
docker build -f Dockerfile.backend -t "$DOCKER_USERNAME/${IMAGE_NAME}:backend-latest" .

# Build frontend image
echo ""
echo "[2/4] Building frontend image..."
docker build -f Dockerfile.frontend -t "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-$TAG" .
docker build -f Dockerfile.frontend -t "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest" .

# Login to Docker Hub (if not already logged in)
echo ""
echo "[3/4] Checking Docker Hub login..."
if ! docker info | grep -q "Username"; then
    echo "Please login to Docker Hub:"
    docker login
fi

# Push backend images
echo ""
echo "[4/4] Pushing backend images..."
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:backend-$TAG"
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:backend-latest"

# Push frontend images
echo "Pushing frontend images..."
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-$TAG"
docker push "$DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest"

echo ""
echo "========================================="
echo "Successfully pushed all images!"
echo "========================================="
echo "Backend: $DOCKER_USERNAME/${IMAGE_NAME}:backend-$TAG"
echo "Backend: $DOCKER_USERNAME/${IMAGE_NAME}:backend-latest"
echo "Frontend: $DOCKER_USERNAME/${IMAGE_NAME}:frontend-$TAG"
echo "Frontend: $DOCKER_USERNAME/${IMAGE_NAME}:frontend-latest"
echo ""
echo "To pull and run:"
echo "  docker pull $DOCKER_USERNAME/${IMAGE_NAME}:backend-$TAG"
echo "  docker pull $DOCKER_USERNAME/${IMAGE_NAME}:frontend-$TAG"

