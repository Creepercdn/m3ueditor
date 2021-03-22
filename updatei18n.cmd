:: update18n.cmd <UI File> <Output File>
SET PYUIC=pyuic5
SET PYLUPDATE=pylupdate5
%PYUIC% -o "%TEMP%\%~n1.py" "%~f1"
%PYLUPDATE% -noobsolete -verbose "%TEMP%\%~n1.py" -ts "%~f2"
echo done