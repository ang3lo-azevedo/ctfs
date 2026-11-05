{ pkgs ? import <nixpkgs> {} }:

let
  sstv-tool = pkgs.python3Packages.buildPythonPackage rec {
    pname = "sstv";
    version = "master";
    format = "setuptools"; 

    src = pkgs.fetchFromGitHub {
      owner = "colaclanth";
      repo = "sstv";
      rev = "master";
      sha256 = "sha256-s+G3MUVxEL/CwLaLk2nFcTFfRqq4Hrbj6qa/GhhzFMc=";
    };

    nativeBuildInputs = [ pkgs.python3Packages.setuptools ];

    propagatedBuildInputs = with pkgs.python3Packages; [
      numpy
      pillow
      scipy
      pyaudio
      pysoundfile # A peça que faltava!
    ];

    doCheck = false;
  };
in
pkgs.mkShell {
  buildInputs = [ 
    sstv-tool 
    pkgs.sox 
  ];
}