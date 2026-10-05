"""Generate a distribution containing only scripts and sparse patches."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from delta import make_patch,apply_patch
VERSION='0.2.0-test2'

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
    shutil.copy(root/'LICENSE',destination/'LICENSE')
    archive=output/f'tML-Win7-LegacySteam-v{VERSION}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for file in destination.rglob('*'):
            if file.is_file():z.write(file,file.relative_to(destination))
    print('Package:',archive,'bytes=',archive.stat().st_size)


def package_existing(patch_root, output):
    """Package published, hash-checked deltas without requiring game DLLs."""
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((patch_root / 'manifest.json').read_text())
    assert manifest['version'] == '0.1.0', 'Patch data version mismatch'
    destination = output / 'package'
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(root / 'runtime', destination)
    runtime_manifest = destination / 'LegacySteam/manifest.ps1'
    runtime_manifest.write_text(runtime_manifest.read_text(encoding='utf-8-sig').replace("$LegacySteamVersion = '0.1.0'", "$LegacySteamVersion = '" + VERSION + "'"), encoding='utf-8-sig')
    patch_dir = destination / 'LegacySteam/patches'
    patch_dir.mkdir(exist_ok=True)
    for item in manifest['targets']:
        name = Path(item['patch_file']).name
        data = (patch_root / name).read_bytes()
        assert len(data) == item['patch_bytes']
        assert hashlib.sha256(data).hexdigest() == item['patch_hash']
        (patch_dir / name).write_bytes(data)
    for name in ('README.md', 'LICENSE'):
        shutil.copy(root / name, destination / name)
    shutil.copy(root / 'docs/CHANGELOG.md', destination / 'CHANGELOG.md')
    shutil.copy(patch_root / 'manifest.json', destination / 'LegacySteam/manifest.json')
    archive = output / f'tML-Win7-LegacySteam-v{VERSION}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in sorted(destination.rglob('*')):
            if file.is_file():
                z.write(file, file.relative_to(destination))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.sha256.txt').write_text(digest + '  ' + archive.name + '\n')
    print('Package:', archive, 'bytes=', archive.stat().st_size)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--patch-dir', type=Path, default=Path('patches/2026.8.3.0'))
    parser.add_argument('--output', type=Path, default=Path('build/release'))
    args = parser.parse_args()
    package_existing(args.patch_dir, args.output)
