#!/usr/bin/env python3
"""
Full backend deployment for Mango Genome Database.
Uploads Python backend, sets up venv, modifies server.js to spawn uvicorn.
"""
import paramiko
import io
import os
import sys
import time
from pathlib import Path

HOST = '82.112.232.168'
PORT = 65002
USER = 'u666137017'
KEY_FILE = r'C:\Users\star\.ssh\mangodb_deploy'

LOCAL_BACKEND = Path(r'c:\Users\star\Desktop\rabia-faizan\mango-genome\backend')
SERVER_HOME = '/home/u666137017'
SERVER_DOMAIN = f'{SERVER_HOME}/domains/mangodb.cloud'
SERVER_BACKEND = f'{SERVER_DOMAIN}/backend'
SERVER_NODEJS = f'{SERVER_DOMAIN}/nodejs'

print('Connecting to server...')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_FILE, timeout=20)
sftp = ssh.open_sftp()
print('Connected!\n')

def run(cmd, timeout=30):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    result = o
    if e:
        result += '\nSTDERR: ' + e
    return result

def run_long(cmd, timeout=300, show=True):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    if show and o:
        print('  OUT:', o[:500])
    if show and e:
        print('  ERR:', e[:500])
    return o, e

def sftp_mkdir_p(path):
    """Create remote dir and parents"""
    parts = path.split('/')
    current = ''
    for p in parts:
        if not p:
            continue
        current = current + '/' + p
        try:
            sftp.mkdir(current)
        except:
            pass  # exists or no permission for parent

def upload_file_content(content, remote_path):
    """Upload string content as a file"""
    f = io.BytesIO(content.encode('utf-8'))
    sftp.putfo(f, remote_path)

# ============================================================
print('=' * 60)
print('STEP 1: Create backend directory structure')
print('=' * 60)

for d in [SERVER_BACKEND, f'{SERVER_BACKEND}/routers', f'{SERVER_BACKEND}/services',
          f'{SERVER_BACKEND}/schemas', f'{SERVER_BACKEND}/utils', f'{SERVER_BACKEND}/logs',
          f'{SERVER_BACKEND}/db', f'{SERVER_BACKEND}/data']:
    try:
        sftp.mkdir(d)
        print(f'  Created: {d}')
    except:
        print(f'  Exists:  {d}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 2: Upload backend Python files')
print('=' * 60)

files_to_upload = [
    (LOCAL_BACKEND / 'main.py', f'{SERVER_BACKEND}/main.py'),
    (LOCAL_BACKEND / 'requirements.txt', f'{SERVER_BACKEND}/requirements.txt'),
    (LOCAL_BACKEND / 'utils' / '__init__.py', f'{SERVER_BACKEND}/utils/__init__.py'),
    (LOCAL_BACKEND / 'utils' / 'fasta_utils.py', f'{SERVER_BACKEND}/utils/fasta_utils.py'),
    (LOCAL_BACKEND / 'utils' / 'plot_utils.py', f'{SERVER_BACKEND}/utils/plot_utils.py'),
    (LOCAL_BACKEND / 'schemas' / '__init__.py', f'{SERVER_BACKEND}/schemas/__init__.py'),
    (LOCAL_BACKEND / 'schemas' / 'blast.py', f'{SERVER_BACKEND}/schemas/blast.py'),
    (LOCAL_BACKEND / 'schemas' / 'msa.py', f'{SERVER_BACKEND}/schemas/msa.py'),
    (LOCAL_BACKEND / 'services' / '__init__.py', f'{SERVER_BACKEND}/services/__init__.py'),
    (LOCAL_BACKEND / 'services' / 'blast_service.py', f'{SERVER_BACKEND}/services/blast_service.py'),
    (LOCAL_BACKEND / 'services' / 'msa_service.py', f'{SERVER_BACKEND}/services/msa_service.py'),
    (LOCAL_BACKEND / 'routers' / '__init__.py', f'{SERVER_BACKEND}/routers/__init__.py'),
    (LOCAL_BACKEND / 'routers' / 'blast.py', f'{SERVER_BACKEND}/routers/blast.py'),
    (LOCAL_BACKEND / 'routers' / 'msa.py', f'{SERVER_BACKEND}/routers/msa.py'),
    (LOCAL_BACKEND / 'routers' / 'files.py', f'{SERVER_BACKEND}/routers/files.py'),
]

for local_path, remote_path in files_to_upload:
    if local_path.exists():
        try:
            sftp.put(str(local_path), remote_path)
            print(f'  Uploaded: {local_path.name} -> {remote_path}')
        except Exception as e:
            print(f'  FAILED: {local_path.name}: {e}')
    else:
        print(f'  MISSING locally: {local_path}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 3: Create backend .env')
print('=' * 60)

env_content = f"""DB_PATH={SERVER_BACKEND}/db
DATA_PATH={SERVER_BACKEND}/data
BLAST_BIN={SERVER_HOME}/tools/blast/bin
CLUSTALO_BIN={SERVER_HOME}/tools/clustalo
CORS_ORIGINS=["http://localhost:3000","https://mangodb.cloud","https://www.mangodb.cloud"]
LOG_DIR={SERVER_BACKEND}/logs
"""

upload_file_content(env_content, f'{SERVER_BACKEND}/.env')
print('  Created .env with server paths')
print(env_content)

# ============================================================
print('\n' + '=' * 60)
print('STEP 4: Create Python 3.11 virtual environment')
print('=' * 60)

print('  Running: python3.11 -m venv venv  (this may take 30s...)')
out, err = run_long(
    f'/opt/alt/python311/bin/python3.11 -m venv {SERVER_BACKEND}/venv',
    timeout=120, show=True
)
print(f'  Check venv: {run(f"ls {SERVER_BACKEND}/venv/bin/ | head -5")}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 5: Install Python requirements')
print('=' * 60)

pip = f'{SERVER_BACKEND}/venv/bin/pip'
print('  Upgrading pip...')
run_long(f'{pip} install --upgrade pip', timeout=60, show=False)

print('  Installing requirements (this takes 2-5 minutes)...')
requirements = (LOCAL_BACKEND / 'requirements.txt').read_text()
print(f'  Requirements:\n{requirements}')

out, err = run_long(
    f'cd {SERVER_BACKEND} && {pip} install -r requirements.txt 2>&1',
    timeout=600, show=True
)
print('  Done installing requirements')

# Verify key packages
print('\n  Verifying installs:')
for pkg in ['fastapi', 'uvicorn', 'biopython', 'matplotlib', 'pandas']:
    result = run(f'{SERVER_BACKEND}/venv/bin/python -c "import {pkg}; print({pkg}.__version__)" 2>&1')
    print(f'    {pkg}: {result}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 6: Create frontend .env.local (sets FASTAPI_URL for Next.js)')
print('=' * 60)

env_local_content = 'FASTAPI_URL=http://127.0.0.1:8000\n'
upload_file_content(env_local_content, f'{SERVER_NODEJS}/.env.local')
print(f'  Created {SERVER_NODEJS}/.env.local')
print(f'  Content: {env_local_content.strip()}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 7: Modify server.js to spawn Python backend')
print('=' * 60)

# Read current server.js
print('  Reading current server.js...')
current_serverjs = run(f'cat {SERVER_NODEJS}/server.js')

# Check if we already patched it
if 'MANGODB PYTHON BACKEND SPAWN' in current_serverjs:
    print('  server.js already patched, skipping')
else:
    spawn_prefix = r"""// === MANGODB PYTHON BACKEND SPAWN ===
process.env.FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';
(function spawnPythonBackend() {
  var sp = require('child_process').spawn;
  var fs = require('fs');
  var pt = require('path');
  var backendDir = pt.join(__dirname, '..', 'backend');
  var uvicorn = pt.join(backendDir, 'venv', 'bin', 'uvicorn');
  if (fs.existsSync(uvicorn)) {
    var bp = sp(uvicorn, ['main:app', '--host', '127.0.0.1', '--port', '8000', '--log-level', 'info'], {
      cwd: backendDir,
      detached: false,
      stdio: ['ignore', 'pipe', 'pipe'],
      env: Object.assign({}, process.env, {PYTHONUNBUFFERED: '1'})
    });
    bp.stdout.on('data', function(d) { process.stdout.write('[backend] ' + d); });
    bp.stderr.on('data', function(d) { process.stdout.write('[backend] ' + d); });
    bp.on('error', function(e) { console.error('[backend] spawn error:', e.message); });
    bp.on('exit', function(c, s) { console.log('[backend] exited code=' + c + ' signal=' + s); });
    process.on('exit', function() { try { bp.kill(); } catch(e) {} });
    process.on('SIGTERM', function() { try { bp.kill(); } catch(e) {} process.exit(0); });
    console.log('[server] Python backend spawned from ' + backendDir);
  } else {
    console.error('[server] WARNING: uvicorn not found at ' + uvicorn);
  }
})();
// === END MANGODB PYTHON BACKEND SPAWN ===

"""

    new_content = spawn_prefix + current_serverjs
    upload_file_content(new_content, f'{SERVER_NODEJS}/server.js')
    print('  server.js patched with Python backend spawn code')
    print(f'  New file size: {len(new_content)} bytes')

# ============================================================
print('\n' + '=' * 60)
print('STEP 8: Download BLAST+ and Clustal Omega on server')
print('=' * 60)

# Create tools directory
run(f'mkdir -p {SERVER_HOME}/tools')

# Download BLAST+
blast_url = 'https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.16.0/ncbi-blast-2.16.0+-x64-linux.tar.gz'
blast_tar = f'{SERVER_HOME}/tools/ncbi-blast-2.16.0+-x64-linux.tar.gz'

print('  Checking if BLAST+ already downloaded...')
blast_check = run(f'ls {SERVER_HOME}/tools/blast/bin/blastn 2>&1')
if 'blastn' in blast_check and 'No such' not in blast_check:
    print('  BLAST+ already installed at ~/tools/blast/')
else:
    print(f'  Downloading BLAST+ from NCBI (this may take 1-2 minutes)...')
    out, err = run_long(
        f'wget -q --show-progress -O {blast_tar} "{blast_url}" 2>&1 || '
        f'curl -L -o {blast_tar} "{blast_url}" 2>&1',
        timeout=300, show=True
    )
    print(f'  Download result (first 200): {(out+err)[:200]}')

    # Check if file downloaded
    size_check = run(f'ls -lh {blast_tar} 2>&1')
    print(f'  File: {size_check}')

    if 'No such file' not in size_check:
        print('  Extracting BLAST+...')
        out, err = run_long(
            f'cd {SERVER_HOME}/tools && tar -xzf {blast_tar} && '
            f'mv ncbi-blast-2.16.0+ blast && '
            f'echo "extracted" || echo "extract failed"',
            timeout=120, show=True
        )
        run(f'rm -f {blast_tar}')
        print(f'  BLAST+ binaries: {run(f"ls {SERVER_HOME}/tools/blast/bin/ | head -5")}')

# Download Clustal Omega
print('\n  Checking if Clustal Omega already downloaded...')
clustalo_check = run(f'ls {SERVER_HOME}/tools/clustalo 2>&1')
if 'clustalo' in clustalo_check and 'No such' not in clustalo_check:
    print('  Clustal Omega already installed')
else:
    clustalo_url = 'http://www.clustal.org/omega/clustal-omega-1.2.4-Ubuntu-x86_64'
    print(f'  Downloading Clustal Omega...')
    out, err = run_long(
        f'wget -q -O {SERVER_HOME}/tools/clustalo "{clustalo_url}" 2>&1 || '
        f'curl -L -o {SERVER_HOME}/tools/clustalo "{clustalo_url}" 2>&1',
        timeout=120, show=True
    )
    run(f'chmod +x {SERVER_HOME}/tools/clustalo')
    clustalo_ver = run(f'{SERVER_HOME}/tools/clustalo --version 2>&1')
    print(f'  Clustal Omega version: {clustalo_ver}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 9: Test uvicorn can start (quick test - 3 seconds)')
print('=' * 60)

test_result = run(
    f'cd {SERVER_BACKEND} && '
    f'timeout 3 {SERVER_BACKEND}/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --log-level info 2>&1 || true',
    timeout=10
)
print(f'  uvicorn test output (expect startup then timeout):\n  {test_result[:400]}')

# ============================================================
print('\n' + '=' * 60)
print('STEP 10: Restart the app (touch Passenger restart.txt)')
print('=' * 60)

run(f'touch {SERVER_NODEJS}/tmp/restart.txt')
print(f'  Touched {SERVER_NODEJS}/tmp/restart.txt')
print('  Waiting 3 seconds for Passenger to restart...')
time.sleep(3)

# Check new console.log
print(f'  console.log (first few lines after restart):')
new_log = run(f'cat {SERVER_NODEJS}/console.log 2>&1')
print('  ' + new_log[:600].replace('\n', '\n  '))

# ============================================================
print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)

print('\nBackend directory contents:')
print(run(f'ls -la {SERVER_BACKEND}/'))

print('\nTools directory:')
print(run(f'ls {SERVER_HOME}/tools/'))

print('\nNodeJS directory:')
print(run(f'ls {SERVER_NODEJS}/'))

print('\nvenv Python packages (key ones):')
print(run(f'{SERVER_BACKEND}/venv/bin/pip list 2>&1 | grep -E "fastapi|uvicorn|biopython|matplotlib|pandas"'))

print('\nDeploy COMPLETE!')
print('Next step: upload database files (db/ and data/) via deploy_db.py')
print('Then visit https://mangodb.cloud to verify the site')

sftp.close()
ssh.close()
