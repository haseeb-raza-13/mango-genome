#!/usr/bin/env python3
"""
Upload BLAST databases (db/) and data files (data/) to server,
then run health endpoint test and give final status.
"""
import paramiko, io, os, time
from pathlib import Path

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

LOCAL_DB = Path(r'c:\Users\star\Desktop\rabia-faizan\MangoDB\db')
LOCAL_DATA = Path(r'c:\Users\star\Desktop\rabia-faizan\MangoDB\data')

# ============================================================
print('=== 1. Upload BLAST database files (db/) ===')
db_files = list(LOCAL_DB.iterdir())
total_size = sum(f.stat().st_size for f in db_files if f.is_file())
print(f'  {len(db_files)} files, {total_size / 1024 / 1024:.1f} MB total')

uploaded = 0
failed = 0
for i, f in enumerate(sorted(db_files, key=lambda x: x.stat().st_size, reverse=True)):
    if not f.is_file():
        continue
    remote = f'{BACKEND}/db/{f.name}'
    size_mb = f.stat().st_size / 1024 / 1024
    try:
        sftp.put(str(f), remote)
        uploaded += 1
        print(f'  [{i+1}/{len(db_files)}] {f.name} ({size_mb:.1f}MB) OK')
    except Exception as e:
        failed += 1
        print(f'  [{i+1}/{len(db_files)}] {f.name} FAILED: {e}')

print(f'\n  db/ upload done: {uploaded} OK, {failed} failed')

# ============================================================
print('\n=== 2. Upload data/ files ===')
data_files = list(LOCAL_DATA.iterdir())
for f in sorted(data_files):
    if not f.is_file():
        continue
    remote = f'{BACKEND}/data/{f.name}'
    try:
        sftp.put(str(f), remote)
        print(f'  {f.name} OK')
    except Exception as e:
        print(f'  {f.name} FAILED: {e}')

# ============================================================
print('\n=== 3. Verify db/ on server ===')
db_count = run(f'ls {BACKEND}/db/ | wc -l')
db_size = run(f'du -sh {BACKEND}/db/ 2>&1')
print(f'  Files in db/: {db_count}')
print(f'  db/ total size: {db_size}')

# ============================================================
print('\n=== 4. Test backend health (write shell script to home dir) ===')
test_script = f"""#!/bin/bash
cd {BACKEND}
{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8007 --log-level warning > /tmp/uv_test.log 2>&1 &
UVPID=$!

for i in $(seq 1 25); do
  ss -tlnp 2>/dev/null | grep ':8007 ' >/dev/null 2>&1 && break
  sleep 1
done

echo '=HEALTH='
curl -s http://127.0.0.1:8007/health 2>&1
echo ''
echo '=DATABASES='
curl -s http://127.0.0.1:8007/blast/databases 2>&1 | head -c 300
echo ''
echo '=LOG='
grep -v 'matplotlib\\|CONFIGDIR\\|CACHEDIR\\|interactive\\|platform' /tmp/uv_test.log | head -15
kill $UVPID 2>/dev/null
echo 'TEST_DONE'
"""
script_buf = io.BytesIO(test_script.encode())
sftp.putfo(script_buf, '/home/u666137017/test_backend.sh')
run('chmod +x ~/test_backend.sh')

print('  Running backend test (45s timeout)...')
_, out, err = ssh.exec_command('bash ~/test_backend.sh', timeout=55)
out.channel.recv_exit_status()
result = out.read().decode(errors='replace')
print(result[:1200])

# ============================================================
print('\n=== 5. Trigger Passenger restart ===')
run(f'touch {NODEJS}/tmp/restart.txt')
print('  Touched restart.txt')
curl_from_server = run(
    'curl -sk --max-time 20 -o /dev/null -w "%{http_code}" https://mangodb.cloud/ 2>&1',
    timeout=30
)
print(f'  curl from server: {curl_from_server}')

# ============================================================
print('\n=== 6. Final summary ===')
print('Tools:')
print(f'  blastn: {run("/home/u666137017/tools/blast/bin/blastn -version 2>&1 | head -1")}')
print(f'  clustalo: {run("/home/u666137017/tools/clustalo --version 2>&1")}')
print('\nBackend:')
print(f'  Files: {run(f"ls {BACKEND}/")}')
print(f'  db/: {run(f"ls {BACKEND}/db/ | head -5")} ...')
print(f'  data/: {run(f"ls {BACKEND}/data/")}')
print('\nFrontend:')
print(f'  server.js patched: {run(f"grep -c MANGODB {NODEJS}/server.js")} occurrences')
print(f'  .env.local: {run(f"cat {NODEJS}/.env.local")}')

print('\n' + '='*60)
print('DEPLOYMENT COMPLETE!')
print('='*60)
print('''
NEXT STEPS FOR USER:
1. Visit https://mangodb.cloud in your browser
   - This triggers Passenger to restart Node.js with our patched server.js
   - Node.js will automatically spawn the Python backend on port 8000

2. Wait ~15 seconds after first visit for the backend to initialize

3. Try BLAST: go to /blast, paste a sequence, click Search

4. Try MSA: go to /msa, upload FASTA files, click Align

5. Check logs if anything fails:
   ssh -p 65002 u666137017@82.112.232.168 -i C:\\Users\\star\\.ssh\\mangodb_deploy
   cat ~/domains/mangodb.cloud/nodejs/console.log
   cat ~/domains/mangodb.cloud/backend/logs/backend.log
''')

sftp.close()
ssh.close()
