from pathlib import Path
import dnfile,pefile,re,struct,json,hashlib
from capstone import *
from capstone.x86 import *
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBytes
import argparse
parser=argparse.ArgumentParser(description='Build exact-version tModLoader legacy Steam compatibility patches')
parser.add_argument('--game-dir', required=True, type=Path, help='Pristine tModLoader folder or extracted original input archive')
parser.add_argument('--output', type=Path, default=Path('build'))
args=parser.parse_args()
root=args.game_dir; out=args.output; payload=out/'modified';payload.mkdir(parents=True,exist_ok=True)
layouts=json.loads(Path(__file__).with_name('interface_layouts.json').read_text())
manifest=[]; audit=[]
replacements={'SteamFriends018':'SteamFriends017','STEAMREMOTEPLAY_INTERFACE_VERSION003':'STEAMREMOTEPLAY_INTERFACE_VERSION002','STEAMUGC_INTERFACE_VERSION021':'STEAMUGC_INTERFACE_VERSION020'}
for rel in ['Libraries/steamworks.net.anycpu/2025.162.4/lib/net8.0/Steamworks.NET.dll','Libraries/steamworks.net.anycpu/2025.162.4/runtimes/win/lib/net8.0/Steamworks.NET.dll']:
 original=(root/rel).read_bytes();b=bytearray(original);p=dnfile.dnPE(data=original)
 assert p.net.struct.StrongNameSignatureSize==0,'Strong named DLL unsupported'
 for old,new in replacements.items():
  a=old.encode('utf-16le');z=new.encode('utf-16le'); count=b.count(a);assert count>=1
  b=b.replace(a,z);audit.append({'file':rel,'replace':old,'with':new,'count':count})
 found=False
 for t in p.net.mdtables.TypeDef:
  if str(t.TypeName)=='CSteamAPIContext':
   for mi in t.MethodList:
    m=mi.row
    if str(m.Name)=='Init':
     body=CilMethodBody(CilMethodBodyReaderBytes(p.get_data(m.Rva,12000)));ins=body.instructions
     for n,i in enumerate(ins):
      if i.opcode.name=='ldsfld' and n+4<len(ins) and [x.opcode.name for x in ins[n:n+5]]==['ldsfld','ldsfld','bne.un.s','ldc.i4.0','ret']:
       fld=p.net.mdtables.Field.rows[i.operand.rid-1]
       if str(fld.Name)=='m_pSteamTimeline':
        start=i.offset;end=ins[n+5].offset;assert end-start==14
        pos=p.get_offset_from_rva(m.Rva)+start;b[pos:pos+14]=b'\x00'*14;found=True
        audit.append({'file':rel,'timeline_null_check_removed_at':pos})
 assert found or rel.endswith("/lib/net8.0/Steamworks.NET.dll") and "/runtimes/" not in rel
 dst=payload/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
 manifest.append({'path':rel,'original':hashlib.sha256(original).hexdigest(),'patched':hashlib.sha256(b).hexdigest()})
 # reparse and inspect instructions, retaining successful return and valid method metadata
 q=dnfile.dnPE(data=bytes(b));assert len(q.net.mdtables.MethodDef.rows)==len(p.net.mdtables.MethodDef.rows)

rel='Libraries/steamworks.net.anycpu/2025.162.4/runtimes/win-x64/native/steam_api64.dll';orig=(root/rel).read_bytes();b=bytearray(orig);p=pefile.PE(data=orig)
def align(n,a):return (n+a-1)//a*a
newrva=align(max(s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData) for s in p.sections),p.OPTIONAL_HEADER.SectionAlignment)
newraw=align(len(b),p.OPTIONAL_HEADER.FileAlignment)
code=bytearray();newruntime=[];md=Cs(CS_ARCH_X86,CS_MODE_64);md.detail=True
exports={e.name.decode():e for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
def add_code(blob,oldrva=None,oldsize=None):
 while len(code)%16:code.append(0xcc)
 rva=newrva+len(code);code.extend(blob)
 if oldrva is not None:
  entries=[x.struct for x in p.DIRECTORY_ENTRY_EXCEPTION if x.struct.BeginAddress==oldrva]
  assert len(entries)<=1
  if entries:
   ent=entries[0];assert p.get_data(ent.UnwindData,1)[0] >> 3 == 0;newruntime.append((rva,rva+len(blob),ent.UnwindData))
 return rva
def route(name,rva):
 e=exports[name];idx=e.ordinal-p.DIRECTORY_ENTRY_EXPORT.struct.Base
 pos=p.get_offset_from_rva(p.DIRECTORY_ENTRY_EXPORT.struct.AddressOfFunctions+idx*4)
 struct.pack_into('<I',b,pos,rva)
old=layouts['friends160'];new=layouts['friends162']
assert len(old)==len(new)+2 and set(old)-set(new)=={'SetPersonaName','GetUserRestrictions'}
for name,e in exports.items():
 if not name.startswith('SteamAPI_ISteamFriends_'):continue
 method=name.removeprefix('SteamAPI_ISteamFriends_'); assert method in new
 oldslot=old.index(method)*8;newslot=new.index(method)*8
 if oldslot==newslot:continue
 instr=[]
 for i in md.disasm(p.get_data(e.address,128),e.address):
  instr.append(i)
  if i.mnemonic in ('ret','jmp'):break
 assert instr[-1].mnemonic in ('ret','jmp')
 result=bytearray();patched=0
 for i in instr:
  bb=bytearray(i.bytes)
  mem=[o.mem for o in i.operands if o.type==X86_OP_MEM and o.mem.base==X86_REG_RAX]
  isdispatch=(i.mnemonic in ('call','jmp') and mem) or (i.mnemonic=='mov' and len(i.operands)>0 and i.operands[0].type==X86_OP_REG and i.operands[0].reg==X86_REG_R10 and mem)
  if isdispatch:
   assert len(mem)==1 and mem[0].disp==newslot,(method,i.op_str,newslot)
   # Re-encode ModRM displacement, allowing 8-bit -> 32-bit expansion.
   modpos=i.modrm_offset;tailpos=modpos+1
   assert (bb[modpos]&7)==0
   bb=bb[:tailpos]+(bb[tailpos+i.disp_size:] if i.disp_size else bb[tailpos:])
   if oldslot<=127:
    bb[modpos]=(bb[modpos]&0x3f)|0x40;bb[tailpos:tailpos]=struct.pack('<b',oldslot)
   else:
    bb[modpos]=(bb[modpos]&0x3f)|0x80;bb[tailpos:tailpos]=struct.pack('<i',oldslot)
   patched+=1
  # These wrappers contain no relative control flow or RIP-relative addresses.
  assert not any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in i.operands)
  assert not (i.mnemonic in ('call','jmp') and i.operands and i.operands[0].type==X86_OP_IMM)
  result.extend(bb)
 assert patched==1
 rva=add_code(result,e.address,sum(i.size for i in instr));route(name,rva)
 audit.append({'native_export':name,'new_slot':newslot//8,'legacy_slot':oldslot//8,'rva':rva})
 # Verify generated code dispatch exactly to old slot
 ds=list(md.disasm(bytes(result),rva));assert sum(i.size for i in ds)==len(result)
 assert any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RAX and o.mem.disp==oldslot for i in ds for o in i.operands)
# Unsupported new functionality returns zero/false or is a no-op; redirect only named EAT entries.
stub=add_code(b'\x31\xc0\xc3')
remoteold=layouts['remoteplay160']
for name,e in exports.items():
 if name.startswith('SteamAPI_ISteamTimeline_'):route(name,stub);audit.append({'stub':name})
 elif name.startswith('SteamAPI_ISteamRemotePlay_'):
  method=name.removeprefix('SteamAPI_ISteamRemotePlay_')
  if method=='ShowRemotePlayTogetherUI':
   # Legacy slot 6 takes bool bShowOverlay; force true in EDX.
   assert remoteold.index('BStartRemotePlayTogether')==6
   rva=add_code(bytes.fromhex('ba01000000488b0148ff6030'));route(name,rva);audit.append({'remote_ui_adapter':name})
  elif method not in remoteold:route(name,stub);audit.append({'stub':name})
 elif name in ('SteamAPI_ISteamUGC_SetItemsDisabledLocally','SteamAPI_ISteamUGC_SetSubscriptionsLoadOrder'):
  route(name,stub);audit.append({'stub':name})
for oldstr,newstr in replacements.items():
 a=oldstr.encode()+b'\0';z=newstr.encode()+b'\0';n=b.count(a);assert n>=1;b=b.replace(a,z);audit.append({'native_string':oldstr,'replace':newstr,'count':n})
# Relocated functions with stack frames retain their original unwind info.
while len(code)%4:code.append(0)
runtime_rva=newrva+len(code)
runtimes=[(x.struct.BeginAddress,x.struct.EndAddress,x.struct.UnwindData) for x in p.DIRECTORY_ENTRY_EXCEPTION]+newruntime
runtimes.sort()
for item in runtimes:code.extend(struct.pack('<III',*item))
rawsize=align(len(code),p.OPTIONAL_HEADER.FileAlignment)
secpos=p.sections[-1].get_file_offset()+40;assert secpos+40<=p.OPTIONAL_HEADER.SizeOfHeaders and not any(b[secpos:secpos+40])
b.extend(b'\0'*(newraw-len(b)));b.extend(code);b.extend(b'\0'*(rawsize-len(code)))
struct.pack_into('<8sIIIIIIHHI',b,secpos,b'.legacy\0',len(code),newrva,rawsize,newraw,0,0,0,0,0x60000020)
struct.pack_into('<H',b,p.FILE_HEADER.get_field_absolute_offset('NumberOfSections'),p.FILE_HEADER.NumberOfSections+1)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfImage'),align(newrva+len(code),p.OPTIONAL_HEADER.SectionAlignment))
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('SizeOfCode'),p.OPTIONAL_HEADER.SizeOfCode+rawsize)
struct.pack_into('<II',b,p.OPTIONAL_HEADER.DATA_DIRECTORY[3].get_file_offset(),runtime_rva,len(runtimes)*12)
# Authenticode is no longer valid after modification; remove the certificate directory.
struct.pack_into('<II',b,p.OPTIONAL_HEADER.DATA_DIRECTORY[4].get_file_offset(),0,0)
struct.pack_into('<I',b,p.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),0)
q=pefile.PE(data=bytes(b));struct.pack_into('<I',b,q.OPTIONAL_HEADER.get_field_absolute_offset('CheckSum'),q.generate_checksum())
q=pefile.PE(data=bytes(b));assert q.FILE_HEADER.NumberOfSections==7
assert len(q.DIRECTORY_ENTRY_EXPORT.symbols)==len(p.DIRECTORY_ENTRY_EXPORT.symbols)
assert all(x.address+3 <= len(q.get_memory_mapped_image()) for x in q.DIRECTORY_ENTRY_EXPORT.symbols if x.name and x.address)
dst=payload/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(b)
manifest.append({'path':rel,'original':hashlib.sha256(orig).hexdigest(),'patched':hashlib.sha256(b).hexdigest()})
# Update only the precise expected Windows x64 API fingerprint; retain all check methods.
game_original=(root/'tModLoader.dll').read_bytes()
expected='3bae3a5ecad22eec751e154f68e09361'
assert hashlib.md5(orig).hexdigest()==expected
assert hashlib.sha256(game_original).hexdigest() == 'fcc6a9624b12191be4a15d714a3675440911feb8c1d374642ab1fd686f0da0a5'
needle=expected.encode('utf-16le');assert game_original.count(needle)==1
fingerprint=hashlib.md5(bytes(b)).hexdigest()
game_patched=game_original.replace(needle,fingerprint.encode('utf-16le'))
(payload/'tModLoader.dll').write_bytes(game_patched)
manifest.append({'path':'tModLoader.dll','original':hashlib.sha256(game_original).hexdigest(),'patched':hashlib.sha256(game_patched).hexdigest()})
audit.append({'file':'tModLoader.dll','expected_api_md5':fingerprint,'offset':game_original.index(needle)})
(out/'build-audit.json').write_text(json.dumps({'manifest':manifest,'changes':audit},indent=2)+'\n')
from package import package
package(root,payload,out,manifest)
print('Built and verified exact-version delta package:',out)
