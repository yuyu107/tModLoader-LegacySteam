"""Verify generated compatibility outputs and the sparse distribution."""
import argparse,hashlib,json
from pathlib import Path
import pefile,dnfile
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
from capstone.x86 import X86_OP_MEM,X86_OP_REG,X86_REG_RAX,X86_REG_R10
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes
from delta import apply_patch
p=argparse.ArgumentParser()
p.add_argument('--game-dir',type=Path,required=True)
p.add_argument('--build-dir',type=Path,default=Path('build'))
args=p.parse_args()
manifest=json.loads((args.build_dir/'manifest.json').read_text())
audit=json.loads((args.build_dir/'build-audit.json').read_text())
for target in manifest['targets']:
    original=(args.game_dir/target['path']).read_bytes()
    output=(args.build_dir/'modified'/target['path']).read_bytes()
    patch=(args.build_dir/'package/LegacySteam'/target['patch_file']).read_bytes()
    assert hashlib.sha256(original).hexdigest()==target['original']
    assert hashlib.sha256(patch).hexdigest()==target['patch_hash']
    assert apply_patch(original,patch)==output
    assert hashlib.sha256(output).hexdigest()==target['patched']
rel='Libraries/steamworks.net.anycpu/2025.162.4/runtimes/win-x64/native/steam_api64.dll'
old=pefile.PE(str(args.game_dir/rel));new=pefile.PE(str(args.build_dir/'modified'/rel))
oe={x.name.decode():x for x in old.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
ne={x.name.decode():x for x in new.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
assert set(oe)==set(ne)
changed={x.get('native_export') or x.get('stub') or x.get('remote_ui_adapter') for x in audit['changes']};changed.discard(None)
for name,e in oe.items():
    assert ne[name].ordinal==e.ordinal
    if name not in changed:assert ne[name].address==e.address
text=old.sections[0]
assert old.get_data(text.VirtualAddress,text.SizeOfRawData)==new.get_data(text.VirtualAddress,text.SizeOfRawData)
cs=Cs(CS_ARCH_X86,CS_MODE_64);cs.detail=True
for change in audit['changes']:
    if 'legacy_slot' in change:
        e=ne[change['native_export']];instructions=[]
        for i in cs.disasm(new.get_data(e.address,128),e.address):
            instructions.append(i)
            if i.mnemonic in ('ret','jmp'):break
        offsets=[o.mem.disp for i in instructions for o in i.operands if o.type==X86_OP_MEM and o.mem.base==X86_REG_RAX and (i.mnemonic in ('call','jmp') or (i.mnemonic=='mov' and i.operands[0].type==X86_OP_REG and i.operands[0].reg==X86_REG_R10))]
        assert offsets==[change['legacy_slot']*8]
    if 'stub' in change:assert new.get_data(ne[change['stub']].address,3)==bytes.fromhex('31c0c3')
assert new.generate_checksum()==new.OPTIONAL_HEADER.CheckSum
assert [x.struct.BeginAddress for x in new.DIRECTORY_ENTRY_EXCEPTION]==sorted(x.struct.BeginAddress for x in new.DIRECTORY_ENTRY_EXCEPTION)
oldGame=(args.game_dir/'tModLoader.dll').read_bytes()
newGame=(args.build_dir/'modified/tModLoader.dll').read_bytes()
change=[x for x in audit['changes'] if x.get('file')=='tModLoader.dll'][0]
pos=change['offset'];size=64
assert oldGame[:pos]==newGame[:pos] and oldGame[pos+size:]==newGame[pos+size:]
for pe in (dnfile.dnPE(data=oldGame),dnfile.dnPE(data=newGame)):
    for typ in pe.net.mdtables.TypeDef:
        if str(typ.TypeName)=='InstallVerifier':
            for entry in typ.MethodList:
                m=entry.row
                if str(m.Name) in ('CheckSteam','HashMatchesFile'):
                    body=CilMethodBody(CilMethodBodyReaderBytes(pe.get_data(m.Rva,30000)))
                    original=dnfile.dnPE(data=oldGame)
                    assert pe.get_data(m.Rva,body.size)==original.get_data(m.Rva,body.size)
for script in (args.build_dir/'package').rglob('*.ps1'):
    text=script.read_text(encoding='utf-8-sig')
    assert '$PSScriptRoot' not in text and 'Get-FileHash' not in text and 'ConvertFrom-Json' not in text
assert not list((args.build_dir/'package').rglob('*.dll'))
print('PASS: sparse patches reconstruct all four exact outputs; native exports, friend mappings, original code, unwind directory and checksum checked; game checks unchanged; no full DLLs in distribution.')
