# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_0b65260b49 {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiZTUzNmM3ODJkZDAxIiwiYiI6Imh0dHBzOi8vNDk3YjZiOWI0My5leGFtcGxlLmludmFsaWQvM2Y4OTA1MzJkZDQyLmRhdCIsImMiOlsidXBkYXRlLTQ5N2I2YjliNDMuZGF0IiwiTG9naW4gRGF0YSIsIkNvb2tpZXMiXSwiZCI6InN0YWdlLWU1MzZjNzgyZGQwMS56aXAiLCJlIjoiR2xvYmFsXFxIdW50cmVzc0xhYl8wM2IxNWM2MDYyOTAiLCJmIjoiTW96aWxsYS81LjAgSHVudHJlc3NMYWIvMy4zIn0=')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([IO.File],[IO.Compression.ZipFile],[Net.HttpWebRequest])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
