{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (ps: with ps; [
      matplotlib
      numpy
      pillow
      angr
      pyzbar
      segno
    ]))
    pkgs.zbar
  ];
}
