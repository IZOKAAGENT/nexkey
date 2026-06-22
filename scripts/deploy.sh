#!/bin/bash
# NEXKEY — Deployment Script
# Deploys agents to Vercel with health monitoring

set -e

echo "🔑 NEXKEY Deployment Script"
echo "=========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERCEL_ORG="izokaagent-3746s-projects"
VERCEL_PROJECT="nexkey"

# Check requirements
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}ERROR: Python 3 not found${NC}"
        exit 1
    fi
    
    # Check venv
    if [ ! -d "$PROJECT_DIR/.venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv "$PROJECT_DIR/.venv"
        source "$PROJECT_DIR/.venv/bin/activate"
        uv pip install pyyaml
    fi
    
    # Check Vercel CLI
    if ! command -v vercel &> /dev/null && ! command -v npx &> /dev/null; then
        echo -e "${RED}WARNING: Vercel CLI not found. Install with: npm i -g vercel${NC}"
    fi
    
    echo -e "${GREEN}✓ Requirements met${NC}"
}

# Run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    cd "$PROJECT_DIR"
    
    # Activate venv
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # Run test suite
    if [ -d "tests" ]; then
        python3 -m pytest tests/ -v --tb=short 2>/dev/null || {
            echo -e "${RED}Tests failed. Aborting deployment.${NC}"
            exit 1
        }
    fi
    
    echo -e "${GREEN}✓ Tests passed${NC}"
}

# Health check before deploy
pre_deploy_check() {
    echo -e "${YELLOW}Running pre-deploy health check...${NC}"
    
    cd "$PROJECT_DIR"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    # Run health check
    python3 scripts/health_check.py || {
        echo -e "${RED}Health check failed. Aborting deployment.${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✓ Health check passed${NC}"
}

# Deploy to Vercel
deploy() {
    echo -e "${YELLOW}Deploying to Vercel...${NC}"
    
    cd "$PROJECT_DIR"
    
    # Build and deploy
    if command -v vercel &> /dev/null; then
        vercel deploy --prod --confirm
    elif command -v npx &> /dev/null; then
        npx vercel deploy --prod --confirm
    else
        echo -e "${RED}ERROR: Cannot deploy. Install Vercel CLI.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Deployment complete${NC}"
}

# Post-deploy verification
post_deploy() {
    echo -e "${YELLOW}Running post-deploy verification...${NC}"
    
    # Wait a bit for deployment to propagate
    sleep 5
    
    # Run health check again
    cd "$PROJECT_DIR"
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    python3 scripts/health_check.py
    
    echo -e "${GREEN}✓ Post-deploy verification complete${NC}"
}

# Main execution
main() {
    echo ""
    check_requirements
    run_tests
    pre_deploy_check
    deploy
    post_deploy
    
    echo ""
    echo -e "${GREEN}🎉 NEXKEY deployment successful!${NC}"
    echo "=========================="
}

# Run main
main "$@"
