{
  description = "AugustaLabs CTF Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: 
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        torch
        transformers
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pythonEnv
        ];
        shellHook = ''
          echo "Environment for AugustaLabs CTF loaded."
        '';
      };

      packages.${system}.default = pkgs.writeShellScriptBin "solve" ''
        ${pythonEnv}/bin/python ./solve.py
      '';
    };
}
