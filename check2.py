import paramiko, sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('82.112.232.168', port=65002, username='u666137017',
            key_filename=r'C:\Users\star\.ssh\mangodb_deploy', timeout=20)

def run(cmd, timeout=20):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    out.channel.recv_exit_status()
    o = out.read().decode(errors='replace').strip()
    e = err.read().decode(errors='replace').strip()
    return o + ('\nSTDERR: ' + e if e else '')

NODE = '/home/u666137017/domains/mangodb.cloud/nodejs'

print('=== API routes in .next build ===')
print(run(f'ls {NODE}/.next/server/pages/api/ 2>&1'))

print('\n=== node_modules (all 14) ===')
print(run(f'ls {NODE}/node_modules/'))

print('\n=== console.log (ASCII-safe) ===')
print(run(f"strings {NODE}/console.log 2>&1 | head -30"))

print('\n=== stderr.log ===')
print(run(f"cat {NODE}/stderr.log"))

print('\n=== .env.local? ===')
print(run(f"cat {NODE}/.env.local 2>&1"))

print('\n=== .next/server/app dir (static pages) ===')
print(run(f'ls {NODE}/.next/server/app/ 2>&1 | head -20'))

print('\n=== .next/server/pages dir ===')
print(run(f'ls {NODE}/.next/server/pages/ 2>&1'))

print('\n=== public_html/.builds/ ===')
print(run('ls ~/domains/mangodb.cloud/public_html/.builds/ 2>&1'))

print('\n=== public_html .htaccess ===')
print(run('cat ~/domains/mangodb.cloud/public_html/.htaccess'))

print('\n=== Any process on port 8000? ===')
print(run('ss -tlnp 2>/dev/null | grep 8000 || echo "Nothing on 8000"'))

print('\n=== Any process on port 3000? ===')
print(run('ss -tlnp 2>/dev/null | grep 3000 || echo "Nothing on 3000"'))

print('\n=== pip3.11 version ===')
print(run('/opt/alt/python311/bin/pip3.11 --version 2>&1'))

print('\n=== Does backend dir exist? ===')
print(run('ls ~/domains/mangodb.cloud/backend/ 2>&1'))

print('\n=== tools dir? ===')
print(run('ls ~/tools/ 2>&1'))

ssh.close()
