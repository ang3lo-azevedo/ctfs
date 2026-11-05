# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_e2bdc3275e {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiNzg1MjQ0YzdmZGY1IiwiYiI6Ii5sb2NrZWQtMWQ2ODUiLCJjIjoiUkVDT1ZFUlktMWQ2ODU4Yjc3Ny50eHQiLCJkIjoiaHR0cHM6Ly8xZDY4NThiNzc3LmV4YW1wbGUuaW52YWxpZC9hMGUyMDIwNGVkMTcuZGF0IiwiZSI6WyJ1cGRhdGUtMWQ2ODU4Yjc3Ny5kYXQiLCJMb2dpbiBEYXRhIiwiQ29va2llcyJdLCJmIjoiR2xvYmFsXFxIdW50cmVzc0xhYl9iMmUyNTdhNGVhMGYifQ==')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[Security.Cryptography.Aes],[IO.DirectoryInfo])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
