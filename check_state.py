import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('82.112.232.168', port=65002, username='u666137017',
            key_filename=r'C:\Users\star\.ssh\mangodb_deploy', timeout=20)

def run(cmd):
    _, out, err = ssh.exec_command(cmd, timeout=15)
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    return (o + (' | ERR: ' + e if e else ''))

print('=== nodejs dir ===')
print(run('ls -la ~/domains/mangodb.cloud/nodejs/'))

print('\n=== .next present? ===')
print(run('ls ~/domains/mangodb.cloud/nodejs/.next/ | head -10'))

print('\n=== package.json ===')
print(run('cat ~/domains/mangodb.cloud/nodejs/package.json'))

print('\n=== server.js ===')
print(run('cat ~/domains/mangodb.cloud/nodejs/server.js'))

print('\n=== node config.json ===')
print(run('cat ~/.config/nextjs-nodejs/config.json'))

print('\n=== public_html .htaccess ===')
print(run('cat ~/domains/mangodb.cloud/public_html/.htaccess'))

print('\n=== Python 3.11 available ===')
print(run('/opt/alt/python311/bin/python3.11 --version 2>&1'))
print(run('/opt/alt/python311/bin/pip3.11 --version 2>&1'))

print('\n=== Can spawn subprocesses? ===')
print(run('/opt/alt/python311/bin/python3.11 -c "import subprocess; r = subprocess.run([\'echo\', \'hello\'], capture_output=True, text=True); print(r.stdout)"'))

print('\n=== stderr and console logs ===')
print(run('cat ~/domains/mangodb.cloud/nodejs/stderr.log 2>&1 | tail -20'))
print(run('cat ~/domains/mangodb.cloud/nodejs/console.log 2>&1 | tail -20'))

ssh.close()
