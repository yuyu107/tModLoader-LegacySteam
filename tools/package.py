"""Generate a distribution containing only scripts and sparse patches."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from delta import make_patch,apply_patch
VERSION='0.1.0-test'

def package(original_root,modified_root,output,manifest):
    root=Path(__file__).resolve().parent.parent
    destination=output/'package'
    if destination.exists():shutil.rmtree(destination)
    shutil.copytree(root/'runtime',destination)
    (destination/'LegacySteam/patches').mkdir(exist_ok=True)
    entries=[]
    for n,item in enumerate(manifest):
        original=(original_root/item['path']).read_bytes()
        target=(modified_root/item['path']).read_bytes()
        assert hashlib.sha256(original).hexdigest()==item['original']
        assert hashlib.sha256(target).hexdigest()==item['patched']
        patch=make_patch(original,target)
        assert apply_patch(original,patch)==target
        name=f'{n:02d}.lsp'
        (destination/'LegacySteam/patches'/name).write_bytes(patch)
        entries.append(dict(item,patch_file='patches/'+name,patch_hash=hashlib.sha256(patch).hexdigest(),patch_bytes=len(patch)))
    lines=["$LegacySteamVersion = '"+VERSION+"'",'$LegacySteamTargets = @(']
    for n,e in enumerate(entries):
        vals={'Path':e['path'].replace('/','\\'),'Original':e['original'],'Patched':e['patched'],'PatchFile':e['patch_file'].replace('/','\\'),'PatchHash':e['patch_hash']}
        lines.append(' @{ '+ '; '.join(k+"='"+v+"'" for k,v in vals.items())+' }'+(',' if n<len(entries)-1 else ''))
    lines.append(')')
    (destination/'LegacySteam/manifest.ps1').write_bytes(('\r\n'.join(lines)+'\r\n').encode('utf-8-sig'))
    (output/'manifest.json').write_text(json.dumps({'version':VERSION,'targets':entries},indent=2)+'\n')
    shutil.copy(root/'README.md',destination/'README.md')
    archive=output/f'tML-Win7-LegacySteam-v{VERSION}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in destination.rglob('*'):
            if file.is_file():z.write(file,file.relative_to(destination))
    print('Package:',archive,'bytes=',archive.stat().st_size)
