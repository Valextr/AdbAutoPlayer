# 📝 TODO List

## 🚀 Go
- **Self Updater**
  _Waiting for Wails v3 release_
    - [Wails v3 Status](https://v3alpha.wails.io/status/)
    - [GitHub Issue #1178](https://github.com/wailsapp/wails/issues/1178)

## 🎨 Frontend
- Yules - Group Buttons I'm thinking just some [Accordion](https://next.skeleton.dev/docs/components/accordion/svelte#multiple) solution 

## 🐍 Python
- Support for running multiple bots/configs (Yules: Can't find the motivation to do this because I personally have no use for it at the moment.)
- GFL2 Daily automation
- Refactor backend second pass

## General
- Yules - Refactor Config logic
  - Patch: Don't ship config files
  - Go 
    - saves configs
    - passes config data, config form data and path to FE
    - remove all main config specific logic and structs
  - Python
    - reads configs
    - define main config
    - use defaults defined in code when config not found
    - default path for config will be same path as in distributed app
    - pass config data, config form data and path to Go
