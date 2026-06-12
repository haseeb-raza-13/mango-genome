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

print('=== OS ===')
print(run('cat /etc/os-release | head -4'))

print('\n=== Python ===')
print(run('python3 --version 2>&1; which python3 2>&1'))

print('\n=== pip ===')
print(run('pip3 --version 2>&1'))

print('\n=== Node / npm / pm2 ===')
print(run('node --version 2>&1; npm --version 2>&1; pm2 --version 2>&1'))

print('\n=== BLAST+ ===')
print(run('which blastn 2>&1; blastn -version 2>&1 | head -1'))

print('\n=== Clustal Omega ===')
print(run('which clustalo 2>&1; clustalo --version 2>&1'))

print('\n=== Home directory ===')
print(run('ls -la ~'))

print('\n=== public_html ===')
print(run('ls ~/public_html 2>&1 | head -20'))

print('\n=== Disk space ===')
print(run('df -h ~ | tail -1'))

print('\n=== RAM ===')
print(run('free -h | grep Mem'))

ssh.close()
