#!/bin/bash
#
# Build script for Bioclin MCP Server Docker image
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="bioclin-mcp"
IMAGE_TAG="latest"
BUILD_ARGS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tag)
      IMAGE_TAG="$2"
      shift 2
      ;;
    --no-cache)
      BUILD_ARGS="--no-cache"
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --tag TAG        Set image tag (default: latest)"
      echo "  --no-cache       Build without using cache"
      echo "  --help           Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${GREEN}Building Bioclin MCP Server Docker Image${NC}"
echo "=========================================="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}Error: Dockerfile not found${NC}"
    exit 1
fi

# Check if required files exist
echo -e "${YELLOW}Checking required files...${NC}"
REQUIRED_FILES=("bioclin_mcp_server.py" "bioclin_schemas.py" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: Required file '$file' not found${NC}"
        exit 1
    fi
    echo "  ✓ $file"
done
echo ""

# Build the image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build $BUILD_ARGS -t "${IMAGE_NAME}:${IMAGE_TAG}" . || {
    echo -e "${RED}Build failed!${NC}"
    exit 1
}

echo ""
echo -e "${GREEN}Build completed successfully!${NC}"
echo ""

# Show image info
echo -e "${YELLOW}Image information:${NC}"
docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Test the image:"
echo "     docker run -it --rm ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "  2. Run with custom API URL:"
echo "     docker run -it --rm -e BIOCLIN_API_URL=\"https://your-api.com\" ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "  3. Use with docker-compose:"
echo "     docker-compose up -d"
echo ""
