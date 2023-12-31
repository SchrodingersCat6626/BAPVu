# BAPVu

Linux instructions:

By default the eDAQ device will be owned by root. Therefore, it would not be possible to run this program without sudo privileges. As a workaround you should add yourself to a user group which owns the device.

To check who owns one of the devices run the following (ttyACM0 in this case):

```
ls -ld /dev/ttyACM0
```

You will likely see this output:

```
crw-rw---- 1 root dialout 166, 0 May 21 13:30 /dev/ttyACM0
```

It can be seen that the device is owned by root. You must add yourself to the dialout usergroup to read and write from this device.

```
sudo usermod -aG dialout <user>
```


