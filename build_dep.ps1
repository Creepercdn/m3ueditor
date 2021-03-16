Write-Output "Start build..."

Write-Output "Build i18n translate files..."
python .\compilei18n.py $LRELEASE "./i18n/"
Move-Item -Force .\i18n\m3ueditor.*.qm .\

Write-Output "Build resoure file..."
& $PYRCC -compress 12 -threshold 1 -o res.py res.qrc

Write-Output "Build UI files..."
& $PYUIC -o m3ueditor.py m3ueditor.ui
& $PYUIC -o aboutdiag.py aboutdiag.ui

Write-Output "███╗   ███╗██████╗ ██╗   ██╗███████╗██████╗ ██╗████████╗ ██████╗ ██████╗ "
Write-Output "████╗ ████║╚════██╗██║   ██║██╔════╝██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗"
Write-Output "██╔████╔██║ █████╔╝██║   ██║█████╗  ██║  ██║██║   ██║   ██║   ██║██████╔╝"
Write-Output "██║╚██╔╝██║ ╚═══██╗██║   ██║██╔══╝  ██║  ██║██║   ██║   ██║   ██║██╔══██╗"
Write-Output "██║ ╚═╝ ██║██████╔╝╚██████╔╝███████╗██████╔╝██║   ██║   ╚██████╔╝██║  ██║"
Write-Output "╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝"
Write-Output "`n"
Write-Output "Build complete!"
Write-Output "Run __main__.py to open this app!"