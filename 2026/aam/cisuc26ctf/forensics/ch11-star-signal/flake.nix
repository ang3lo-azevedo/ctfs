{
  description = "A flake for findaes";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Systems to support
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      # Helper to generate an attrset '{ x86_64-linux = f "x86_64-linux"; ... }'
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Nixpkgs instantiated for each system
      nixpkgsFor = forAllSystems (system: import nixpkgs { inherit system; });
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          default = pkgs.stdenv.mkDerivation {
            pname = "findaes";
            version = "1.0.2";

            src = pkgs.fetchzip {
              url = "mirror://sourceforge/project/findaes/findaes-1.2.zip";
              sha256 = "1356qxw0ws62w68dhhpa1y9a0s1bfvyrnr1v2vhd4635xmjgl45q";
            };

            # If the zip contains source code that needs compiling, 
            # nix will try to run 'make' automatically. 
            # If it's a pre-compiled binary, this installPhase is correct.
            installPhase = ''
              install -Dm555 -t $out/bin findaes
            '';
          };
        });

      devShells = forAllSystems (system:
        let
          pkgs = nixpkgsFor.${system};
        in
        {
          default = pkgs.mkShell {
            # This puts findaes in your PATH when you enter the shell
            buildInputs = [ self.packages.${system}.default ];

            shellHook = ''
              echo "findaes shell environment loaded"
              findaes --help || true
            '';
          };
        });
    };
}