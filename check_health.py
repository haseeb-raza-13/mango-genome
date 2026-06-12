#!/usr/bin/env python3
"""Check health endpoint result safely (ASCII-only output)"""
import paramiko, io, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('82.112.232.168', port=65002, username='u666137017',
            key_filename=r'C:\Users\star\.ssh\mangodb_deploy', timeout=20)
sftp = ssh.open_sftp()

def run(cmd, timeout=30):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode('ascii', errors='replace').strip()
    e = err.read().decode('ascii', errors='replace').strip()
    return o + ('\nSTDERR: ' + e if e else '')

BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'
VENV = f'{BACKEND}/venv'

# ============================================================
print('=== Test health with OPENBLAS fix (60s timeout) ===')
test_script = f"""#!/bin/bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd {BACKEND}
{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8009 --log-level warning > /tmp/uv3.log 2>&1 &
UVPID=$!

for i in $(seq 1 40); do
  ss -tlnp 2>/dev/null | grep ':8009 ' >/dev/null 2>&1 && echo "Port open after ${{i}}s" && break
  sleep 1
done

echo '---HEALTH---'
curl -s --max-time 10 http://127.0.0.1:8009/health 2>&1
echo ''
echo '---DATABASES---'
curl -s --max-time 10 http://127.0.0.1:8009/blast/databases 2>&1 | head -c 500
echo ''
echo '---LOG---'
cat /tmp/uv3.log | strings | grep -v -E 'matplotlib|CONFIGDIR|CACHEDIR|interactive|platform|OpenBLAS|pthread|ulimit|RLIMIT|blas_thread' | head -15
kill $UVPID 2>/dev/null
echo 'END'
"""
sftp.putfo(io.BytesIO(test_script.encode()), '/home/u666137017/test3.sh')
run('chmod +x ~/test3.sh')

print('Running...')
_, out, err = ssh.exec_command('bash ~/test3.sh', timeout=65)
out.channel.recv_exit_status()
result = out.read().decode('ascii', errors='replace')
print(result[:2000])

# ============================================================
print('\n=== Verify main.py has OPENBLAS fix ===')
print(run(f'head -10 {BACKEND}/main.py'))

print('\n=== Verify server.js has thread limits ===')
print(run(f'grep -A2 "OPENBLAS" {NODEJS}/server.js | head -10'))

print('\n=== Check DATA_PATH in .env ===')
print(run(f'grep -E "DATA_PATH|DB_PATH|OPENBLAS" {BACKEND}/.env'))

print('\n=== db/ file count ===')
print(run(f'ls {BACKEND}/db/*.fasta 2>&1 | wc -l'))
print(run(f'ls -lh {BACKEND}/db/ISRAELKEITTPROTEIN.fasta 2>&1'))

sftp.close()
ssh.close()
