python3 -m esptool -p COM6 -b 115200 erase_flash
python3 -m esptool -p COM6 -b 115200 write_flash -fs=detect -fm dout 0x00000 ./EspPlugMicropython_SONOFF.bin
pause