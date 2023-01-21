python3 -m esptool -p COM6 -b 115200 erase_flash
python3 -m esptool -p COM6 -b 115200 write_flash -fs=detect -fm dout 0x00000 ./esp8266-1m-20220618-v1.19.1.bin
pause