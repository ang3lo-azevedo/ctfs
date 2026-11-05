# Huntress Script Triage -- inert composite-analysis fixture (windows_powershell_5_1)
function artifact_6ad60457ad {
  $encodedMaterial = [Convert]::FromBase64String('eyJhIjoiYTg4YmZkYTcyZGJlIiwiYiI6Imh0dHBzOi8vY2RuLTAzY2UzMjY5NDguZXhhbXBsZS5pbnZhbGlkLzNlNTkwOTRiMjRlMi5iaW4iLCJjIjoid2FsbGV0X2QzMjdiYzExMTRhOTA3NTg5YWY4MWJiYTcxMjI2Yjc3IiwiZCI6InVwZGF0ZS0wM2NlMzI2OTQ4LmRhdCIsImUiOiJIS0NVXFxTb2Z0d2FyZVxcSHVudHJlc3NMYWJcXFJ1blxcMDNjZTMyNjk0OCIsImYiOiJNb3ppbGxhLzUuMCBIdW50cmVzc0xhYi8zLjYiLCJnIjo2NCwiaCI6Ikdsb2JhbFxcSHVudHJlc3NMYWJfNjQ2MGI0ZjZhYTcyIn0=')
  $reconstruct = {
    param([byte[]]$candidateBytes)
    return [byte[]]$candidateBytes
  }
  [byte[]]$plainMaterial = @(& $reconstruct $encodedMaterial)
  $decodedText = [Text.Encoding]::UTF8.GetString($plainMaterial)
  $descriptor = $decodedText | ConvertFrom-Json
  $record = $descriptor
  $nativeTypes = @([Diagnostics.Process],[Microsoft.Win32.Registry],[Net.WebClient])
  [pscustomobject]@{ A = $record.a; B = $record.b; C = $record.c; D = $record.d; Native = $nativeTypes }
}
