import pefile

def dump_version_info(filename):
    print(f"\n--- Identifying {filename} ---")
    try:
        pe = pefile.PE(filename)
        if hasattr(pe, 'VS_VERSIONINFO'):
            for fileinfo in pe.FileInfo[0]:
                if fileinfo.name == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            if entry[0] in ['OriginalFilename', 'InternalName', 'FileDescription']:
                                print(f"{entry[0]}: {entry[1]}")
        else:
            print("[-] No VS_VERSIONINFO block found.")
            
        # Fallback check just in case Export directory exists
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            print(f"Export Name: {pe.DIRECTORY_ENTRY_EXPORT.name.decode('utf-8')}")
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")

dump_version_info('decrypted_object.bin')
dump_version_info('decrypted_captcha.bin')