using System;
using System.IO;
using System.Text;
public static class LegacyGameFingerprint {
 static int U16(byte[] b,int p) { return BitConverter.ToUInt16(b,p); }
 static int U32(byte[] b,int p) { uint n=BitConverter.ToUInt32(b,p); if(n>Int32.MaxValue) throw new InvalidDataException("Oversized metadata"); return (int)n; }
 static int Rva(byte[] b,int sections,int count,int rva) {
  for(int i=0;i<count;i++) { int p=sections+i*40, va=U32(b,p+12), size=U32(b,p+16);
   if(rva>=va && rva-va<size) { int pos=checked(U32(b,p+20)+rva-va); if(pos>=b.Length) break; return pos; }
  } throw new InvalidDataException("Unmapped metadata RVA");
 }
 public static byte[] Apply(byte[] input,string oldHash,string newHash) {
  if(oldHash.Length!=32 || newHash.Length!=32) throw new InvalidDataException("Invalid fingerprint");
  byte[] b=(byte[])input.Clone();
  if(U16(b,0)!=0x5a4d) throw new InvalidDataException("Not a PE file");
  int pe=U32(b,60); if(U32(b,pe)!=0x4550) throw new InvalidDataException("Not a PE file");
  int opt=pe+24, magic=U16(b,opt), dirs=magic==0x10b?96:magic==0x20b?112:0;
  if(dirs==0) throw new InvalidDataException("Unknown PE layout");
  int sections=opt+U16(b,pe+20), count=U16(b,pe+6);
  int cli=Rva(b,sections,count,U32(b,opt+dirs+14*8));
  if(U32(b,cli+36)!=0) throw new InvalidDataException("Strong named game assembly unsupported");
  int meta=Rva(b,sections,count,U32(b,cli+8));
  if(U32(b,meta)!=0x424a5342) throw new InvalidDataException("Invalid CLR metadata");
  int at=checked(meta+16+U32(b,meta+12)); at=(at+3)&~3;
  int streams=U16(b,at+2); at+=4; int heap=-1, heapSize=0;
  for(int i=0;i<streams;i++) {
   int offset=U32(b,at), size=U32(b,at+4), start=at+8, end=start;
   while(end<b.Length && b[end]!=0) end++;
   if(end==b.Length || end-start>32) throw new InvalidDataException("Invalid stream name");
   string name=Encoding.ASCII.GetString(b,start,end-start); at=(end+4)&~3;
   if(name=="#US") { if(heap!=-1) throw new InvalidDataException("Duplicate user-string heap"); heap=checked(meta+offset); heapSize=size; }
  }
  if(heap<0 || heapSize<=1 || heap>b.Length-heapSize) throw new InvalidDataException("Missing user-string heap");
  int limit=heap+heapSize, hits=0, match=-1;
  for(int pos=heap+1;pos<limit;) {
   int first=b[pos++], length;
   if(first<128) length=first;
   else if((first&192)==128) { if(pos>=limit) throw new InvalidDataException("Truncated string"); length=((first&63)<<8)|b[pos++]; }
   else if((first&224)==192) { if(pos>limit-3) throw new InvalidDataException("Truncated string"); length=((first&31)<<24)|(b[pos]<<16)|(b[pos+1]<<8)|b[pos+2]; pos+=3; }
   else throw new InvalidDataException("Invalid string length");
   if(length>limit-pos) throw new InvalidDataException("String exceeds heap");
   if(length==65 && Encoding.Unicode.GetString(b,pos,64)==oldHash) { hits++; match=pos; }
   pos+=length;
  }
  if(hits!=1) throw new InvalidDataException("Expected API fingerprint must occur in exactly one CLR user-string entry");
  Array.Copy(Encoding.Unicode.GetBytes(newHash),0,b,match,64);
  return b;
 }
}
