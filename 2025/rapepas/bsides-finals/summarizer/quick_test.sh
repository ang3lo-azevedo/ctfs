#!/bin/bash
echo "[*] Quick test of CVE-2021-22204 exploit"
echo "[*] This tests if the exploit works, bypassing the LLM"
echo ""

# Check if docker is running
if ! docker ps &> /dev/null; then
    echo "[!] Docker not running or no permission"
    echo "[!] Try: sudo systemctl start docker"
    exit 1
fi

# Check if vuln container exists
if ! docker ps -a | grep -q "summarizer.*vuln"; then
    echo "[*] Starting vuln container..."
    cd dist
    docker-compose up -d vuln
    cd ..
    sleep 3
fi

echo "[*] Testing exploit..."
python3 test_direct.py

echo ""
echo "[*] If you see flag output above, the exploit WORKS"
echo "[*] If not, check:"
echo "    1. Container is running: docker ps"
echo "    2. ExifTool version in container"
echo "    3. DjVu file structure"
