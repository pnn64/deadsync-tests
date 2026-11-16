"""Build a small CLI directly from the pinned ITGmania bundled Lua sources."""
import hashlib,json,pathlib,subprocess
ROOT=pathlib.Path('/opt/song-lua-audit');OUT=ROOT/'pass3-gc-probe';OUT.mkdir(exist_ok=True)
SRC=ROOT/'harness/vendor/itgmania/extern/lua-5.1/src'
driver=OUT/'driver.c'
driver.write_text('''#include <stdio.h>
#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"
int main(int argc, char **argv) {
 lua_State *L = luaL_newstate();
 if (!L || argc != 2) return 2;
 luaL_openlibs(L);
 int code = luaL_loadfile(L, argv[1]);
 if (!code) code = lua_pcall(L, 0, LUA_MULTRET, 0);
 if (code) fprintf(stderr, "%s\\n", lua_tostring(L, -1));
 lua_close(L); return code;
}
''')
sources=sorted(p for p in SRC.glob('*.c') if p.name not in ['lua.c','luac.c','print.c'])
command=['gcc','-O2','-I',str(SRC),str(driver),*map(str,sources),'-lm','-ldl','-o',str(OUT/'lua51-reference')]
subprocess.run(command,check=True)
script=ROOT/'gc-dead-key-probe.lua'
result=subprocess.check_output([str(OUT/'lua51-reference'),str(script)],text=True)
(OUT/'native-output.txt').write_text(result)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/'native-provenance.json').write_text(json.dumps({'native_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SRC,text=True).strip(),
 'sources':{p.name:sha(p) for p in sources},'driver_sha256':sha(driver),'script_sha256':sha(script),
 'binary_sha256':sha(OUT/'lua51-reference'),'command':command,'output':result},indent=2)+'\n')
print(result,flush=True)
