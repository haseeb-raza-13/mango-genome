#!/usr/bin/env python3
"""Fix clustalo download and verify all packages"""
import paramiko, time, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('82.112.232.168', port=65002, username='u666137017',
            key_filename=r'C:\Users\star\.ssh\mangodb_deploy', timeout=20)

def run(cmd, timeout=30):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return o + ('\nSTDERR: ' + e if e else '')

def run_long(cmd, timeout=300):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return (o + '\n' + e).strip()

VENV = '/home/u666137017/domains/mangodb.cloud/backend/venv'
BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
TOOLS = '/home/u666137017/tools'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'

print('=== Verify all Python packages ===')
verify = run(f'''{VENV}/bin/python -c "
import fastapi; print('fastapi:', fastapi.__version__)
import uvicorn; print('uvicorn:', uvicorn.__version__)
from Bio import SeqIO; print('biopython: OK')
import matplotlib; print('matplotlib:', matplotlib.__version__)
import pandas; print('pandas:', pandas.__version__)
import numpy; print('numpy:', numpy.__version__)
import seaborn; print('seaborn:', seaborn.__version__)
import dotenv; print('python-dotenv: OK')
import multipart; print('python-multipart: OK')
print('ALL OK')
" 2>&1''')
print(verify)

print('\n=== Fix clustalo ===')
# Remove the bad HTML file
run(f'rm -f {TOOLS}/clustalo')

# Try clustalo from multiple sources
print('\nTrying clustalo download from clustal.org (https)...')
result = run_long(
    f'wget -q --no-check-certificate -O {TOOLS}/clustalo '
    f'"https://www.clustal.org/omega/clustal-omega-1.2.4-Ubuntu-x86_64" 2>&1 && '
    f'head -c 4 {TOOLS}/clustalo | xxd | head -1',
    timeout=60
)
print('Result:', result[:200])

# Check if it's a valid ELF binary (starts with 7f 45 4c 46)
is_elf = run(f'file {TOOLS}/clustalo 2>&1')
print(f'File type: {is_elf}')

if 'ELF' not in is_elf:
    print('Not an ELF binary, trying alternative sources...')
    run(f'rm -f {TOOLS}/clustalo')

    # Try bioconda conda-forge static binary via github release
    print('Trying GitHub release...')
    github_url = 'https://github.com/GSLBiotech/clustal-omega/releases/download/1.2.4/clustal-omega-1.2.4-Ubuntu-x86_64'
    result2 = run_long(
        f'wget -q --no-check-certificate -O {TOOLS}/clustalo "{github_url}" 2>&1 || '
        f'curl -L -k -o {TOOLS}/clustalo "{github_url}" 2>&1',
        timeout=60
    )
    print('Result:', result2[:200])
    is_elf2 = run(f'file {TOOLS}/clustalo 2>&1')
    print(f'File type: {is_elf2}')

    if 'ELF' not in is_elf2:
        print('GitHub also failed. Trying Debian package extraction method...')
        run(f'rm -f {TOOLS}/clustalo')

        # Install via Debian package extraction
        deb_url = 'http://ftp.debian.org/debian/pool/main/c/clustal-omega/clustalo_1.2.4-6_amd64.deb'
        extract_cmds = f'''
cd /tmp && \
wget -q -O clustalo.deb "{deb_url}" 2>&1 && \
ar x clustalo.deb data.tar.xz 2>/dev/null && \
tar -xJf data.tar.xz ./usr/bin/clustalo 2>/dev/null && \
cp usr/bin/clustalo {TOOLS}/clustalo && \
rm -f clustalo.deb data.tar.xz && \
rm -rf usr && \
echo "debian extract ok"
'''
        result3 = run_long(extract_cmds.strip(), timeout=120)
        print('Debian result:', result3[:300])
        is_elf3 = run(f'file {TOOLS}/clustalo 2>&1')
        print(f'File type: {is_elf3}')

# Set executable and test
run(f'chmod +x {TOOLS}/clustalo')
clustalo_test = run(f'{TOOLS}/clustalo --version 2>&1')
print(f'\nClustal Omega version: {clustalo_test}')

print('\n=== Check uvicorn can start backend ===')
# Start uvicorn on a test port and check health
test_run = run(
    f'cd {BACKEND} && timeout 5 {VENV}/bin/uvicorn main:app '
    f'--host 127.0.0.1 --port 8002 --log-level warning 2>&1 || true',
    timeout=10
)
print('uvicorn test:', test_run[:300])

print('\n=== Check current console.log (ASCII-safe) ===')
print(run(f'strings {NODEJS}/console.log | head -20'))

print('\n=== Check tools directory ===')
print(run(f'ls -lh {TOOLS}/'))

print('\n=== Check BLAST+ is functional ===')
print(run(f'{TOOLS}/blast/bin/blastn -version 2>&1'))

print('\n=== Port check ===')
print(run('ss -tlnp 2>/dev/null | grep -E "8000|3000" || echo "No processes on 8000/3000"'))

ssh.close()
