#!/usr/bin/env python3
"""
Fix Clustal Omega installation and verify backend works.
Tries: clustal.org direct → Debian .deb extraction → miniconda fallback
"""
import paramiko, time, io, urllib.request, ssl

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

def run_long(cmd, timeout=600):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return (o + '\n' + e).strip()

TOOLS = '/home/u666137017/tools'
BACKEND = '/home/u666137017/domains/mangodb.cloud/backend'
NODEJS = '/home/u666137017/domains/mangodb.cloud/nodejs'
VENV = f'{BACKEND}/venv'
sftp = ssh.open_sftp()

# ============================================================
print('=== Check ClustalOmegaCommandline availability in biopython ===')
biopython_check = run(f'''{VENV}/bin/python -c "
from Bio.Align.Applications import ClustalOmegaCommandline
print('ClustalOmegaCommandline: AVAILABLE')
cline = ClustalOmegaCommandline(cmd='clustalo', infile='test.fa', outfile='out.fa')
print('cline object:', str(cline)[:80])
" 2>&1''')
print(biopython_check)

# ============================================================
print('\n=== Attempt 1: clustal.org page scrape for real URL ===')
page_check = run(
    'curl -s "http://www.clustal.org/omega/" 2>&1 | grep -o '
    '"[^ \"]*clustal[^ \"]*" | head -20'
)
print('clustal.org links:', page_check[:400])

# ============================================================
print('\n=== Attempt 2: Direct download with curl -L (follow redirects) ===')
direct = run_long(
    f'curl -L --max-time 60 '
    f'-o {TOOLS}/clustalo_test '
    f'"http://www.clustal.org/omega/clustal-omega-1.2.4-Ubuntu-x86_64" 2>&1; '
    f'file {TOOLS}/clustalo_test',
    timeout=90
)
print(direct[:400])
is_elf_1 = 'ELF' in direct
print(f'Is ELF binary: {is_elf_1}')
run(f'rm -f {TOOLS}/clustalo_test')

# ============================================================
print('\n=== Attempt 3: Debian .deb package extraction ===')
deb_result = run_long('''
mkdir -p /tmp/cw && cd /tmp/cw && rm -rf * &&
wget -q "http://ftp.debian.org/debian/pool/main/c/clustal-omega/clustalo_1.2.4-6_amd64.deb" -O clustalo.deb 2>&1 &&
echo "DEB_SIZE=$(ls -la clustalo.deb | awk '{print $5}')" &&
ar xv clustalo.deb 2>&1 &&
echo "AR_FILES=$(ls)" &&
for f in data.tar.*; do
  echo "Trying to extract from $f ($(file $f))";
  tar -xf "$f" --wildcards "*/clustalo" 2>&1 && echo "extracted OK" && break;
done &&
FOUND=$(find . -name clustalo -type f 2>/dev/null | head -1) &&
echo "Found binary: $FOUND" &&
if [ -n "$FOUND" ]; then
  cp "$FOUND" /home/u666137017/tools/clustalo &&
  chmod +x /home/u666137017/tools/clustalo &&
  echo "INSTALL_OK"
fi
''', timeout=120)
print(deb_result[:600])

# Check result
clustalo_check = run(f'file {TOOLS}/clustalo 2>&1')
print(f'\nFile check: {clustalo_check}')
is_elf_3 = 'ELF' in clustalo_check

# ============================================================
if not is_elf_3:
    print('\n=== Attempt 4: micromamba (fastest conda alternative) ===')
    micro_result = run_long('''
mkdir -p /home/u666137017/tools &&
cd /home/u666137017/tools &&
echo "Downloading micromamba..." &&
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba 2>&1 | head -5 &&
ls -la bin/micromamba &&
echo "micromamba ready" &&
./bin/micromamba create -p /home/u666137017/tools/clustalo_env -c bioconda -c conda-forge clustalo=1.2.4 -y 2>&1 | tail -20
''', timeout=600)
    print(micro_result[:800])

    clustalo_env_check = run(f'{TOOLS}/clustalo_env/bin/clustalo --version 2>&1')
    print(f'clustalo from micromamba: {clustalo_env_check}')

    if 'Clustal Omega' in clustalo_env_check or '1.2.4' in clustalo_env_check:
        # Link to tools
        run(f'cp {TOOLS}/clustalo_env/bin/clustalo {TOOLS}/clustalo && chmod +x {TOOLS}/clustalo')
        print('Linked clustalo to ~/tools/clustalo')

# Final check
print('\n=== Final clustalo check ===')
clustalo_final = run(f'{TOOLS}/clustalo --version 2>&1')
print(f'clustalo --version: {clustalo_final}')

if 'Clustal Omega' in clustalo_final or '1.2.4' in clustalo_final:
    print('SUCCESS: Clustal Omega is installed!')
else:
    print('WARN: clustalo not yet working - MSA feature will be unavailable for now')
    print('Consider re-running this script or manually installing clustalo')

# ============================================================
print('\n=== Trigger Passenger restart and test backend ===')
run(f'touch {NODEJS}/tmp/restart.txt')
print('Touched restart.txt')

# Make HTTP request to trigger app startup
print('\nMaking HTTP request to trigger app start...')
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request('https://mangodb.cloud/', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        status = r.status
        content_length = len(r.read())
        print(f'  HTTP response: {status}, {content_length} bytes received')
except Exception as e:
    print(f'  HTTP request: {e}')

time.sleep(5)

# Check if backend started on port 8000
print('\nChecking if uvicorn started on port 8000...')
port_check = run('ss -tlnp 2>/dev/null | grep 8000 || echo "Port 8000 not yet open"')
print(port_check)

# Also check for Node.js process
print('Checking if Node.js started...')
node_check = run('ss -tlnp 2>/dev/null | grep 3000 || pgrep -a node | head -3 || echo "No node process found"')
print(node_check)

# Check new log
print('\nNew console.log entries:')
print(run(f'strings {NODEJS}/console.log | tail -20'))

# ============================================================
print('\n=== Test backend directly ===')
# Start uvicorn briefly and test health endpoint
print('Testing uvicorn startup and health endpoint...')
test = run_long(
    f'cd {BACKEND} && '
    f'{VENV}/bin/uvicorn main:app --host 127.0.0.1 --port 8003 --log-level warning &'
    f' UVPID=$! && sleep 3 && '
    f'curl -s http://127.0.0.1:8003/health 2>&1 && '
    f'curl -s http://127.0.0.1:8003/blast/databases 2>&1 && '
    f'kill $UVPID 2>/dev/null && echo "UVICORN_TEST_DONE"',
    timeout=30
)
print('Backend test result:', test[:500])

sftp.close()
ssh.close()
print('\nDone!')
