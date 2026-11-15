import hashlib,json,pathlib,re,shutil,subprocess
root=pathlib.Path('/opt/song-lua-audit');src=root/'Songs/DS ULTIMATE LUA TEST';dest=root/'Songs/__audit_controls/ultimate-comma-layout'
shutil.copytree(src,dest,dirs_exist_ok=True)
path=dest/'DS ULTIMATE LUA TEST.sm';text=path.read_text()
normalized,count=re.subn(r'(?m)^([01234MLFK]+),\r?$',r'\1\n,',text)
assert count>0;path.write_text(normalized)
out=subprocess.run([str(root/'bin/chart-metadata-diagnostic'),str(path)],capture_output=True,text=True,check=True)
source=pathlib.Path('/home/parity/.cargo/git/checkouts/rssp-823189340b1bed13/da616e3')
print(json.dumps({'purpose':'Read-only parser diagnosis using a copy with measure delimiters moved to their own lines; no original corpus or product code changed.','changed_delimiter_lines':count,'original_sha256':hashlib.sha256((src/path.name).read_bytes()).hexdigest(),'normalized_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rssp_revision':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'parser_output':out.stdout}))
