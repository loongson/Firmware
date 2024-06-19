# Memtest86+ For LoongArch

Memtest86+ for LoongArch, this build is based on [memtest](https://github.com/memtest86plus/memtest86plus) commitID: 3f86696.
This is a beta test version, it has been tested on 3A5000, 3A6000, 3C5000, 3D5000 platforms. LoongArch branch [repo](https://github.com/kilaterlee/memtest86plus/tree/SubmitLoongArch) and the [PR](https://github.com/memtest86plus/memtest86plus/pull/410). In the future, all of build will beased this PR.

### <font color=red>Notice</font>
<font color=red>**You can not build this code now, because the binutils missed the `-b binary` option, the demo compuler will upload later, and this feature will support in next binutils version.** </font>
<font color=red>**Make sure `Legacy Boot Mode` is turned off.** </font>

## Useage
* memtest.efi: Copy the memtest.efi into a disk or removable device, run it in shell.
* memtest.iso: Make the iso as boot image, and choose this image in setup.

## Feature
LoongArch version supports most of the features of memtest86+, you can get the detailed informations from [memtest86+ main page](https://memtest.org/).
If you need open the UART, you can run with: `memtest.efi console=mmio,0x1fe001e0`
![image](https://github.com/loongson/Firmware/blob/main/Image/Memtest86+.jpg)
