#!/usr/bin/env python3
"""
Upload fixed msa_service.py, create clustalo wrapper, trigger restart, test backend.
"""
import paramiko, io, time

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

def run_long(cmd, timeout=60):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return (o + '\n' + e).strip()

TOOLS = '/home/u666137017/tools'
BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'
VENV = f'{BACKEND}/venv'

# ============================================================
print('=== 1. Upload fixed msa_service.py ===')
sftp.put(
    r'c:\Users\star\Desktop\rabia-faizan\mango-genome\backend\services\msa_service.py',
    f'{BACKEND}/services/msa_service.py'
)
print('Uploaded msa_service.py')

# Verify the fix
check = run(f'{VENV}/bin/python -c "from services.msa_service import run_msa; print(\'import OK\')" 2>&1',
            timeout=15)
# Need to run from backend dir
check2 = run(f'cd {BACKEND} && {VENV}/bin/python -c "from services.msa_service import run_msa; print(\'import OK\')" 2>&1',
             timeout=15)
print(f'Import check: {check2}')

# ============================================================
print('\n=== 2. Create clustalo wrapper script (LD_LIBRARY_PATH) ===')
wrapper = f"""#!/bin/bash
export LD_LIBRARY_PATH={TOOLS}/clustalo_env/lib:$LD_LIBRARY_PATH
exec {TOOLS}/clustalo_env/bin/clustalo "$@"
"""
f = io.BytesIO(wrapper.encode())
sftp.putfo(f, f'{TOOLS}/clustalo')
run(f'chmod +x {TOOLS}/clustalo')
print(f'Created wrapper at {TOOLS}/clustalo')

# Test it
clustalo_ver = run(f'{TOOLS}/clustalo --version 2>&1')
print(f'clustalo --version: {clustalo_ver}')

# ============================================================
print('\n=== 3. Verify backend imports work end-to-end ===')
py_code = (
    'import sys; sys.path.insert(0, ".")\n'
    'from services.blast_service import get_available_databases\n'
    'from services.msa_service import run_msa\n'
    'import main\n'
    'print("ALL IMPORTS OK")\n'
)
import_cmd = f"cd {BACKEND} && {VENV}/bin/python -c '{py_code}' 2>&1"
import_test = run(import_cmd, timeout=20)
print(import_test[:400])

# ============================================================
print('\n=== 4. Test health endpoint (uvicorn on port 8004) ===')
health_test = run_long(
    f'cd {BACKEND} && '
    f'{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8004 --log-level warning &'
    f' UVPID=$! && sleep 4 && '
    f'curl -s http://127.0.0.1:8004/health 2>&1 && '
    f'echo "" && '
    f'curl -s http://127.0.0.1:8004/blast/databases 2>&1 && '
    f'echo "" && '
    f'kill $UVPID 2>/dev/null && echo "TEST_DONE"',
    timeout=30
)
print('Health + databases test:')
print(health_test[:600])

# ============================================================
print('\n=== 5. Trigger app restart ===')
# Touch restart.txt
run(f'touch {NODEJS}/tmp/restart.txt')
print('Touched restart.txt')

# Try curl from server to trigger restart
print('Making HTTP request from server to mangodb.cloud...')
curl_result = run_long(
    'curl -s --max-time 20 -o /dev/null -w "%{http_code} %{time_total}s" '
    'https://mangodb.cloud/ 2>&1 || '
    'curl -s --max-time 20 -o /dev/null -w "%{http_code} %{time_total}s" '
    '--resolve "mangodb.cloud:443:82.112.232.168" https://mangodb.cloud/ 2>&1',
    timeout=30
)
print(f'curl result: {curl_result}')

time.sleep(5)

# ============================================================
print('\n=== 6. Check if backend started ===')
port_check = run('ss -tlnp 2>/dev/null | grep 8000 || echo "Port 8000 not listening"')
print(f'Port 8000: {port_check}')

print('\nConsole log (after restart):')
print(run(f'strings {NODEJS}/console.log | tail -20'))

# ============================================================
print('\n=== 7. Quick MSA test ===')
msa_test = run_long(
    f'cd {BACKEND} && '
    f'{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8005 --log-level warning &'
    f' UVPID=$! && sleep 4 && '
    f"curl -s -X POST http://127.0.0.1:8005/msa/align "
    f'-F "sequence_text=>seq1\\nACGTACGTACGT\\n>seq2\\nACGTACGGACGT" 2>&1 | head -c 200 && '
    f'kill $UVPID 2>/dev/null && echo "MSA_TEST_DONE"',
    timeout=30
)
print('MSA test:')
print(msa_test[:400])

sftp.close()
ssh.close()
print('\nDone!')
