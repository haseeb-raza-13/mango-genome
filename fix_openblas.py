#!/usr/bin/env python3
"""
Fix OpenBLAS thread limit and re-test backend.
The server limits pthread creation, causing numpy to hang during import.
Solution: set OPENBLAS_NUM_THREADS=1 in the uvicorn spawn environment.
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

BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'
VENV = f'{BACKEND}/venv'

# ============================================================
print('=== 1. Update server.js to add OPENBLAS_NUM_THREADS=1 ===')
current = run(f'cat {NODEJS}/server.js | head -40')
print('Current spawn env section:')
print(current[:500])

# Read full server.js
full_server = run(f'cat {NODEJS}/server.js', timeout=10)

# Update the spawn environment to add OPENBLAS_NUM_THREADS
old_env = "env: Object.assign({}, process.env, {PYTHONUNBUFFERED: '1'})"
new_env = ("env: Object.assign({}, process.env, {"
           "PYTHONUNBUFFERED: '1', "
           "OPENBLAS_NUM_THREADS: '1', "
           "OMP_NUM_THREADS: '1', "
           "MKL_NUM_THREADS: '1'"
           "})")

if old_env in full_server:
    updated = full_server.replace(old_env, new_env)
    sftp.putfo(io.BytesIO(updated.encode()), f'{NODEJS}/server.js')
    print(f'Updated server.js spawn env (added OPENBLAS/OMP/MKL thread limits)')
else:
    print(f'Pattern not found. Looking for env pattern...')
    # Show what's there
    env_lines = [l for l in full_server.split('\n') if 'env:' in l.lower() or 'PYTHONUNBUFFERED' in l]
    print('\n'.join(env_lines[:5]))

# ============================================================
print('\n=== 2. Update backend .env to add thread limits ===')
new_env_content = f"""DB_PATH={BACKEND}/db
DATA_PATH={BACKEND}/db
BLAST_BIN=/home/u666137017/tools/blast/bin
CLUSTALO_BIN=/home/u666137017/tools/clustalo
CORS_ORIGINS=["http://localhost:3000","https://mangodb.cloud","https://www.mangodb.cloud"]
LOG_DIR={BACKEND}/logs
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
"""
sftp.putfo(io.BytesIO(new_env_content.encode()), f'{BACKEND}/.env')
print('Updated backend .env (added thread limits, DATA_PATH points to db/)')
print(new_env_content)

# ============================================================
print('=== 3. Update main.py to set thread limits before imports ===')
main_py = run(f'head -5 {BACKEND}/main.py', timeout=10)
print(f'Current main.py header:\n{main_py}')

full_main = run(f'cat {BACKEND}/main.py', timeout=10)

# Prepend thread limit env vars before other imports
thread_fix = '''import os
# Limit OpenBLAS/NumPy threads to prevent CageFS thread exhaustion
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
'''

if 'OPENBLAS_NUM_THREADS' not in full_main:
    if full_main.startswith('"""'):
        # Has module docstring — insert after it
        end_of_docstring = full_main.index('"""', 3) + 3
        updated_main = full_main[:end_of_docstring] + '\n' + thread_fix + full_main[end_of_docstring:]
    else:
        updated_main = thread_fix + full_main
    sftp.putfo(io.BytesIO(updated_main.encode()), f'{BACKEND}/main.py')
    print('Prepended thread limit env vars to main.py')
else:
    print('Thread limits already in main.py')

# ============================================================
print('\n=== 4. Test health endpoint (60s timeout) ===')
test_script = f"""#!/bin/bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
cd {BACKEND}
{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8008 --log-level warning > /tmp/uv_test2.log 2>&1 &
UVPID=$!

for i in $(seq 1 40); do
  ss -tlnp 2>/dev/null | grep ':8008 ' >/dev/null 2>&1 && echo "Port 8008 open after ${{i}}s" && break
  sleep 1
done

echo '---HEALTH---'
curl -s --max-time 10 http://127.0.0.1:8008/health 2>&1
echo ''
echo '---DATABASES---'
curl -s --max-time 10 http://127.0.0.1:8008/blast/databases 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print('nucleotide dbs:', d.get('nucleotide',[])); print('protein dbs:', d.get('protein',[]))" 2>&1
echo ''
echo '---LOG (filtered)---'
grep -v 'matplotlib\\|CONFIGDIR\\|CACHEDIR\\|interactive\\|platform\\|OpenBLAS\\|pthread\\|ulimit\\|RLIMIT' /tmp/uv_test2.log | head -20
kill $UVPID 2>/dev/null
echo 'DONE'
"""
sftp.putfo(io.BytesIO(test_script.encode()), '/home/u666137017/test_backend2.sh')
run('chmod +x ~/test_backend2.sh')

print('Running test (50s timeout)...')
_, out, err = ssh.exec_command('bash ~/test_backend2.sh', timeout=60)
out.channel.recv_exit_status()
print(out.read().decode(errors='replace')[:1500])

# ============================================================
print('\n=== 5. Touch restart.txt ===')
run(f'touch {NODEJS}/tmp/restart.txt')
print('Touched restart.txt')

print('\n=== Done! ===')
print('Please visit https://mangodb.cloud in your browser to trigger the app restart.')
print('The Node.js server will spawn the Python backend automatically.')

sftp.close()
ssh.close()
