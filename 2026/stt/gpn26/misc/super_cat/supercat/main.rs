use std::fs;
use std::os::unix::fs::MetadataExt;
use std::os::unix::fs::PermissionsExt;
use std::path::Path;

#[derive(Debug)]
struct Permissions {
    uid: u32,
    gid: u32,
    groups: Vec<u32>,
}

fn parse_u32_line(line: &str) -> Vec<u32> {
    /*parses eg
    uid: <num> <num>*/
    line.split_whitespace()
        .skip(1) //name
        .filter_map(|v| v.parse::<u32>().ok())
        .collect()
}

fn get_permissions() -> Permissions {
    let status = std::fs::read_to_string(format!("/proc/{}/status", std::process::id()))
        .expect("could not read own perms");
    let mut uid: u32 = 0;
    let mut gid: u32 = 0;
    let mut groups: Vec<u32> = vec![];
    // format is real effective safed fs for uid an gid
    // we want real
    for l in status.lines() {
        if l.starts_with("Uid") {
            uid = *(parse_u32_line(l).get(0).expect("could not get uid"));
        }
        if l.starts_with("Gid") {
            gid = *(parse_u32_line(l).get(0).expect("could not get gid"));
        }
        if l.starts_with("Groups") {
            groups = parse_u32_line(l);
        }
    }
    Permissions { uid, gid, groups }
}

fn grant_read(file: &Path) {
    let content = fs::read_to_string(file).expect("Could not read file as string");
    print!("{}", content);
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <file>", args[0]);
        std::process::exit(1);
    }
    let file = Path::new(&args[1]);
    let file_meta = std::fs::metadata(file).expect("could not get file info");
    // hail to unix
    let fs_mode = file_meta.permissions().mode();
    let user_perms = get_permissions();
    //same user
    if (user_perms.uid == file_meta.uid() && (fs_mode & 0o400) != 0) {
        grant_read(file);
    }
    if (user_perms.gid == file_meta.gid()) && (fs_mode & 0o040) != 0 {
        grant_read(file);
    }
    //check other groups
    if user_perms.groups.contains(&(file_meta.gid())) && (fs_mode & 0o040) != 0 {
        grant_read(file)
    }
    if (fs_mode & 0o004) != 0 {
        grant_read(file)
    }
    println!("this super cat wont be tricked by your pesky bribery attempts. Maybe next time try gourmet treats instead of  dog food");
}
