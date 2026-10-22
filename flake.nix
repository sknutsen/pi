{
  description = "Pi user-config: CLI plus installer for ~/.pi/agent";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pi.url = "github:earendil-works/pi/stable";
    pi.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      nixpkgs,
      pi,
      ...
    }:
    let
      # nixpkgs-unstable dropped x86_64-darwin; Pi's own flake still supports it.
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: import nixpkgs { inherit system; };

      # Always run against a working checkout. Linking ~/.pi/agent into the
      # nix store would make config read-only and GC-fragile.
      mkInstallApp =
        pkgs: action:
        let
          name =
            {
              install = "pi-config-install";
              uninstall = "pi-config-uninstall";
              status = "pi-config-status";
            }
            .${action};
          extraArgs =
            {
              install = "";
              uninstall = " --uninstall";
              status = " --status";
            }
            .${action};
        in
        {
          type = "app";
          program = "${
            pkgs.writeShellApplication {
              inherit name;
              runtimeInputs = [ pkgs.python3 ];
              text = ''
                repo="''${PI_CONFIG_REPO:-}"
                if [[ -z "$repo" && -f "''${PWD}/scripts/install.py" && -f "''${PWD}/settings.json" ]]; then
                  repo="$PWD"
                fi
                if [[ -z "$repo" ]]; then
                  echo "pi-config: run from a checkout of this repo, or set PI_CONFIG_REPO" >&2
                  echo "Example: git clone <this-repo> ~/Code/pi && cd ~/Code/pi && nix run .#${action}" >&2
                  exit 1
                fi
                exec python3 "$repo/scripts/install.py" --repo "$repo"${extraArgs} "$@"
              '';
            }
          }/bin/${name}";
          meta.description =
            {
              install = "Link this checkout into ~/.pi/agent";
              uninstall = "Remove this repo's links from ~/.pi/agent";
              status = "Show whether ~/.pi/agent points at this checkout";
            }
            .${action};
        };
    in
    {
      packages = forAllSystems (system: {
        default = pi.packages.${system}.default;
        pi = pi.packages.${system}.default;
      });

      apps = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pi.apps.${system}.default;
          pi = pi.apps.${system}.default;
          install = mkInstallApp pkgs "install";
          uninstall = mkInstallApp pkgs "uninstall";
          status = mkInstallApp pkgs "status";
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pi.packages.${system}.default
              pkgs.python3
              pkgs.git
            ];
            shellHook = ''
              echo "Pi user-config shell — $(pi --version 2>/dev/null || echo pi)"
              echo "  nix run .#install    # link this checkout to ~/.pi/agent"
              echo "  nix run .#status"
              echo "  python3 scripts/install.py --status"
            '';
          };
        }
      );

      formatter = forAllSystems (system: (pkgsFor system).nixfmt);

      # Import from home-manager. repo must be a checkout path string, not a
      # Nix path (those copy into the store).
      homeModules.default =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          cfg = config.programs.pi-user-config;
          system = pkgs.stdenv.hostPlatform.system;
        in
        {
          options.programs.pi-user-config = {
            enable = lib.mkEnableOption "Pi CLI and this user-config checkout";
            repo = lib.mkOption {
              type = lib.types.str;
              default =
                "${config.home.homeDirectory}/"
                + (if pkgs.stdenv.hostPlatform.isDarwin then "Code/pi" else "code/pi");
              defaultText = lib.literalExpression ''
                if pkgs.stdenv.hostPlatform.isDarwin
                then "''${config.home.homeDirectory}/Code/pi"
                else "''${config.home.homeDirectory}/code/pi"
              '';
              description = ''
                Working checkout of this repo. Defaults to ~/Code/pi on
                Darwin and ~/code/pi on Linux/WSL. Must be a string, not a
                Nix path — those copy into the store.
              '';
            };
            installPi = lib.mkOption {
              type = lib.types.bool;
              default = true;
              description = "Install the Pi CLI from github:earendil-works/pi/stable.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = lib.mkIf cfg.installPi [ pi.packages.${system}.default ];
            home.activation.piUserConfig = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
              repo="${cfg.repo}"
              repo="''${repo/#\~/${config.home.homeDirectory}}"
              if [[ ! -f "$repo/scripts/install.py" ]]; then
                echo "pi-user-config: skipping, clone missing at $repo"
              else
                ${lib.getExe pkgs.python3} "$repo/scripts/install.py" --repo "$repo"
              fi
            '';
          };
        };
    };
}
