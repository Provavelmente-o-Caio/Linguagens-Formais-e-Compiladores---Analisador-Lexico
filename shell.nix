{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages(p: with p; [
      # Packages go here :)
      pytest
      python-lsp-server
    ]))
  ];
}
