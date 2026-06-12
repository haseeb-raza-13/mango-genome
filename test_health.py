#!/usr/bin/env python3
"""
Test the FastAPI backend health endpoint and trigger app restart.
Writes a shell script to server to avoid paramiko timeout issues.
"""
import paramiko, time, io

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('82.112.232.168', port=65002, username='u666137017',
            key_filename=r'C:\Users\star\.ssh\mangodb_deploy', timeout=20)
sftp = ssh.open_sftp()

def run(cmd, timeout=30):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return o + ('\nSTDERR: ' + e if e else '')

BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'
VENV = f'{BACKEND}/venv'

# ============================================================
print('=== 1. Write test script to server ===')
test_script = f"""#!/bin/bash
set -e
BACKEND={BACKEND}
VENV={VENV}
PORT=8006

echo "Starting uvicorn on port $PORT..."
cd $BACKEND
$VENV/bin/uvicorn main:app --host 127.0.0.1 --port $PORT --log-level warning > /tmp/uvicorn_test.log 2>&1 &
UVPID=$!
echo "PID: $UVPID"

# Wait for port to open (up to 30 seconds)
for i in $(seq 1 30); do
  if ss -tlnp 2>/dev/null | grep ":$PORT " >/dev/null 2>&1; then
    echo "Port open after ${{i}}s"
    break
  fi
  sleep 1
done

echo ""
echo "=== HEALTH ENDPOINT ==="
curl -s http://127.0.0.1:$PORT/health 2>&1
echo ""

echo "=== BLAST DATABASES ==="
curl -s http://127.0.0.1:$PORT/blast/databases 2>&1
echo ""

echo "=== UVICORN LOG ==="
cat /tmp/uvicorn_test.log | grep -v "matplotlib\|CONFIGDIR\|CACHEDIR\|interactive\|platform" | head -20

kill $UVPID 2>/dev/null
echo "TEST_COMPLETE"
"""

f = io.BytesIO(test_script.encode())
sftp.putfo(f, '/tmp/test_backend.sh')
run('chmod +x /tmp/test_backend.sh')
print('Test script written')

# ============================================================
print('\n=== 2. Run backend test (60s timeout) ===')
_, out, err = ssh.exec_command('/tmp/test_backend.sh', timeout=70)
out.channel.recv_exit_status()
result = out.read().decode(errors='replace')
err_out = err.read().decode(errors='replace')
print(result[:1500])
if err_out:
    print('STDERR:', err_out[:200])

# ============================================================
print('\n=== 3. Check BLAST+ binaries and databases ===')
print(run(f'/home/u666137017/tools/blast/bin/blastn -version 2>&1'))
print(run(f'ls {BACKEND}/db/ 2>&1'))
print(run(f'ls {BACKEND}/data/ 2>&1'))

# ============================================================
print('\n=== 4. Trigger Passenger restart from server ===')
run(f'touch {NODEJS}/tmp/restart.txt')

# Try hitting the site from the server itself
curl_result = run(
    'curl -s --max-time 25 -o /dev/null -w "HTTP %{http_code} in %{time_total}s" '
    'https://mangodb.cloud/ 2>&1',
    timeout=35
)
print(f'curl to mangodb.cloud: {curl_result}')

time.sleep(3)

print('\nConsole log (recent):')
print(run(f'strings {NODEJS}/console.log | grep -v "^$" | tail -15'))

# ============================================================
print('\n=== 5. Check if server.js was patched correctly ===')
patch_check = run(f'grep -c "MANGODB PYTHON BACKEND SPAWN" {NODEJS}/server.js')
print(f'Spawn patch in server.js: {patch_check} occurrences')

fastapi_url_check = run(f'grep "FASTAPI_URL" {NODEJS}/server.js | head -2')
print(f'FASTAPI_URL in server.js: {fastapi_url_check}')

env_local_check = run(f'cat {NODEJS}/.env.local')
print(f'.env.local: {env_local_check}')

# ============================================================
print('\n=== Summary ===')
print(f'clustalo: {run("/home/u666137017/tools/clustalo --version 2>&1")}')
print(f'blastn: {run("/home/u666137017/tools/blast/bin/blastn -version 2>&1 | head -1")}')
print(f'Backend .env: {run(f"cat {BACKEND}/.env")}')
print(f'\nAll backend files:')
print(run(f'ls -la {BACKEND}/'))

sftp.close()
ssh.close()
