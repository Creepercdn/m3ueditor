# m3ueditor
An editor to edit simple M3U(8) playlist.

## Files tree:
```
.
├── aboutdiag.ui # About Dialog form
├── diagwrapper.py # About Dialog wrapper
├── m3u8wrapper.py # m3u8 parser
├── __main__.py # Main program
├── mainwindow.py # Main Window wrapper
├── res.qrc # resource
├── untitled.en_US.qt.ts # Translate file for en_US
├── untitled.ui Main Window form
└── untitled.zh_CN.qt.ts # Translate file for zh_CN
```

## How to compile files:
nmake:
```
nmake -f nmakefile
```
clean:
```
nmake -f nmakefile clean
```

GNU make:
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
