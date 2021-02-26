# m3ueditor
An editor to edit simple M3U(8) playlist.

## Files tree:
```
.
├── i18n
|   ├── untitled.en_US.qt.ts # Translate file for en_US
|   └── untitled.zh_CN.qt.ts # Translate file for zh_CN
├── aboutdiag.ui # About Dialog form
├── diagwrapper.py # About Dialog wrapper
├── m3u8wrapper.py # m3u8 parser
├── __main__.py # Main program
├── mainwindow.py # Main Window wrapper
├── res.qrc # resource
├── compilei18n.py # i18n translate files auto compiler for make/nmake
└── untitled.ui Main Window form
```

## How to compile files:
Need PyQt5 to run.
Need PyQt5-tools to compile or delevop.

nmake:
```
nmake -f nmakefile
```
clean:
```
nmake -f nmakefile clean
```

GNU make: # May don't work
```
make
```
clean:
```
make clean
```

## How to run:
```
python __main__.py
```
