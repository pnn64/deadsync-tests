"""Pass scripts directly through SSH stdin, avoiding shell interpolation."""
import pathlib,subprocess,sys
WORK=pathlib.Path(__file__).resolve().parent
def ssh(ip='192.168.1.34',user='parity'):
    return ['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2','-o','StrictHostKeyChecking=accept-new',
            '-o','UserKnownHostsFile='+str(WORK/'known_hosts'),user+'@'+ip]
def run(script,ip='192.168.1.34',user='parity',language='python3',**kwargs):
    try:
        return subprocess.run(ssh(ip,user)+[language,'-' if language=='python3' else '-s'],
                              input=script,text=True,encoding='utf-8',check=True,**kwargs)
    except subprocess.CalledProcessError as error:
        if error.stderr:print(error.stderr,file=sys.stderr)
        raise
if __name__=='__main__':
    run(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'),
        ip=sys.argv[2] if len(sys.argv)>2 else '192.168.1.34',
        user=sys.argv[3] if len(sys.argv)>3 else 'parity',
        language=sys.argv[4] if len(sys.argv)>4 else 'python3')
