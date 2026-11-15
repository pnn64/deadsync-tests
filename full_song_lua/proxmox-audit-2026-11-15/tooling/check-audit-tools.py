import subprocess
from remote import WORK,ssh
for name in ['test_worker.py','categories.py','analyze-reports.py']:
 subprocess.run(['scp','-o','BatchMode=yes','-o','UserKnownHostsFile='+str(WORK/'known_hosts'),str(WORK/name),'parity@192.168.1.49:/opt/song-lua-audit/'+name],check=True)
subprocess.run(ssh('192.168.1.49')+['python3','/opt/song-lua-audit/test_worker.py'],check=True)
