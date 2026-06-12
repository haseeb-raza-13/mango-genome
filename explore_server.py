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

print('=== domains/ structure ===')
print(run('find ~/domains -maxdepth 3 | head -40'))

print('\n=== .cl.selector contents ===')
print(run('ls -la ~/.cl.selector/; cat ~/.cl.selector/* 2>&1 | head -30'))

print('\n=== .profile ===')
print(run('cat ~/.profile'))

print('\n=== .config/ ===')
print(run('ls -la ~/.config/; ls -la ~/.config/*/ 2>&1'))

print('\n=== Available node versions ===')
print(run('ls /opt/alt/node* 2>&1 | head -20; ls /opt/nodejs* 2>&1 | head -10'))

print('\n=== Available python versions ===')
print(run('ls /opt/alt/python* 2>&1 | head -10; ls /usr/local/bin/python* 2>&1'))

print('\n=== PATH in profile ===')
print(run('source ~/.profile 2>&1; echo $PATH'))

print('\n=== npm .config ===')
print(run('ls ~/.npm/; cat ~/.npmrc 2>&1'))

ssh.close()
