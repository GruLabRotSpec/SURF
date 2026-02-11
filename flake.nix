{
  description = "Gru Spec GUI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  }: let
    inherit (nixpkgs) lib;

    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };

    python = pkgs.python313;
  in {
    devShell.x86_64-linux = pkgs.mkShell {
      packages = with pkgs; [
        python
        black
        uv

        qt6.qtbase
        qt6.qtdeclarative
        qt6.qttools
        qt6.qtsvg
        qt6.qtwayland
      ];

      env = {
        UV_PYTHON_DOWNLOADS = "never";
        UV_PYTHON = python.interpreter;
        LD_LIBRARY_PATH = lib.makeLibraryPath (
          pkgs.pythonManylinuxPackages.manylinux1
          ++ (with pkgs; [
            dbus
            mono
            zstd
            libGL
            libxcb
            libxkbcommon
            fontconfig
            freetype
            libX11
            libXcursor
            libXrandr
            wayland
            wayland-protocols
          ])
        );
      };
    };
  };
}
