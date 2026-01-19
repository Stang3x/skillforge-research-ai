#!/bin/bash
# Research Assistant Entrypoint Script
#
# This script runs before the main application to:
# 1. Validate required environment variables
# 2. Set up data directories
# 3. Display startup information

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         RESEARCH ASSISTANT - Docker Container              ║${NC}"
echo -e "${CYAN}║                     Version 17.0                           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check required environment variables
echo -e "${YELLOW}Checking configuration...${NC}"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY is not set!${NC}"
    echo ""
    echo "Please set your Anthropic API key:"
    echo "  1. Create a .env file with: ANTHROPIC_API_KEY=your-key-here"
    echo "  2. Or pass it directly: docker run -e ANTHROPIC_API_KEY=your-key ..."
    echo ""
    exit 1
fi

echo -e "  ${GREEN}✓${NC} ANTHROPIC_API_KEY is set"

# Check optional Semantic Scholar API key
if [ -n "$SEMANTIC_SCHOLAR_API_KEY" ]; then
    echo -e "  ${GREEN}✓${NC} SEMANTIC_SCHOLAR_API_KEY is set (higher rate limits enabled)"
else
    echo -e "  ${YELLOW}○${NC} SEMANTIC_SCHOLAR_API_KEY not set (using default rate limits)"
    echo -e "    ${CYAN}Tip: Get a free key at https://www.semanticscholar.org/product/api${NC}"
fi

# Set up data directory
DATA_DIR="${RESEARCH_DATA_DIR:-/app/data}"
echo ""
echo -e "${YELLOW}Setting up data directories...${NC}"

mkdir -p "$DATA_DIR/pdfs" \
         "$DATA_DIR/diagrams" \
         "$DATA_DIR/exports" \
         "$DATA_DIR/obsidian_vault"

echo -e "  ${GREEN}✓${NC} Data directory: $DATA_DIR"

# Show disk space
DISK_USAGE=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)
echo -e "  ${GREEN}✓${NC} Current data size: ${DISK_USAGE:-0}"

# Count existing files
NOTE_COUNT=$(find "$DATA_DIR" -name "*.json" 2>/dev/null | wc -l)
EXPORT_COUNT=$(find "$DATA_DIR/exports" -name "*.md" -o -name "*.pdf" 2>/dev/null | wc -l)
echo -e "  ${GREEN}✓${NC} Existing notes: $NOTE_COUNT, exports: $EXPORT_COUNT"

echo ""
echo -e "${YELLOW}Available Knowledge Sources:${NC}"
echo -e "  ${GREEN}ARXIV${NC}     - Academic preprints"
echo -e "  ${GREEN}WIKI${NC}      - Wikipedia"
echo -e "  ${GREEN}GITHUB${NC}    - Repositories"
echo -e "  ${GREEN}HACKER${NC}    - HackerNews"
echo -e "  ${GREEN}STACK${NC}     - Stack Overflow"
echo -e "  ${CYAN}SCHOLAR${NC}   - Semantic Scholar (200M+ papers)"

echo ""
echo -e "${GREEN}Starting Research Assistant...${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"
echo ""

# Execute the main command
exec "$@"
