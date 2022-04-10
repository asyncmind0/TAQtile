# TAQtile - Tactical Advanced Qtile Config 

![TAQtile Operator](ghost-in-the-shell-fingers.jpg)

This is a multi head qtile config designed for switching focus between
predefined screens, windows and workspaces with special keybinds.


# How to use:

This is an advanced configuration for ![Qtile](https://github.com/qtile)

- Extra window and group actions 
- Customized widgets
- More dmenu intgration.
- Mostly things that worked for @jagguli


Uses ![suckless](https://suckless.org) tools by default

- st
- surf
- dmenu

## Key binds

For full binding list see `taqtile/keys.py`

| Key  | Action  |
|:--|:--|
| F1   | Switch/Toggle Browser Group |
| F11  | Switch/Toggle Open Termial1 |
| F12  | Switch/Toggle Open Termial2 |
| Super-0..9  | Switch/Toggle Group n |
| XF86Launch5  | Switch/Toggle Open Termial3 |
| Ctrl-Space  | Dmenu Run |
| Ctrl-Meta-V | Clipboard history |
| Super-P | Dmenu password store (insert using xdotool)|
| Super-G | Dmenu browser history and `st` instance list (experimental)|



**TODO**
- highligh currently focused screen taskbar
- dmenu browser profile selector
- bring window to monitor dmenu option
