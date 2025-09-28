{ pkgs, lib, config, inputs, ... }:

{
  env.ARM_SUBSCRIPTION_ID="5e41688b-b047-4bc9-8a66-e8d2c7a07d92";
  env.ARM_TENANT_ID="354a4aae-0bba-4b49-9ae5-1f1240579503";
  env.PULUMI_CONFIG_PASSPHRASE="";

  packages = [
    pkgs.marp-cli
    pkgs.azure-cli
  ];

  languages.python = {
    enable = true;
    version = "3.12";
    uv = {
      enable = true;
      sync = {
        enable = true;
      };
    };
  };

  scripts.lab.exec = "uv run jupyter lab --ServerApp.token='totototo' --ServerApp.allow_remote_access=True";
  scripts.marp_html.exec = "marp presentation.md --html";
  scripts.nb-txt.exec = "uv run jupytext --to py:percent notebook.ipynb";
  scripts.txt-nb.exec = "uv run jupytext --to notebook notebook.py";
  scripts.lab-sync.exec = "uv run jupytext --sync notebook.ipynb";
  scripts.deploy.exec = "./script/deploy.sh";
  scripts.destroy.exec = "./script/destroy.sh";

  enterShell = ''
    ./script/ensure-project-name.sh
  '';

  processes = {
    uvicorn.exec = "poetry run uvicorn app.main:app --reload --reload-include '.env*' --reload-include '.env' --reload-include '*.yaml'";
  };
}
