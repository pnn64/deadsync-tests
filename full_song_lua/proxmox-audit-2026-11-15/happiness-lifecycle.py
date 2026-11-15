import json,pathlib,tarfile
import ijson,zstandard
case=pathlib.Path('/opt/song-lua-audit/results/715ba44e314f2f6e')
out=[]
with (case/'native-diagnostics.tar.zst').open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z,tarfile.open(fileobj=z,mode='r|') as tar:
    for member in tar:
        if not member.isfile() or not member.name.endswith('song-lua-trace.json'):continue
        for event in ijson.items(tar.extractfile(member),'events.item',use_float=True):
            if 'diva/diva.lua' not in event.get('source',''):continue
            if event.get('operation')=='command.begin' and event.get('line') in (992,1014,1063,1068,1071,1075,1080,1084,1088,1094):out.append(event)
print(json.dumps(out))
