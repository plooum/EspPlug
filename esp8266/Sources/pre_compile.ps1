#python3 -m pip install mpy-cross

$files = Get-ChildItem *.py
foreach($file in $files)
{
	python3 -m mpy_cross $file
}

Get-Item -Path "./*.mpy" | Move-Item -Force -Destination "../Bin"