# LoongArch Virtual Machine Firmware 
[简体中文](README_CN.md)

LoongArch virtual machine firmware is compiled based on the tianocore community source code, which is located at :  
https://github.com/tianocore/edk2  

You can download, modify and compile the source code by yourself, if you want to compile it by yourself, you can refer to:  
https://github.com/tianocore/edk2/tree/master/OvmfPkg/LoongArchVirt#readme

Of course, if you don't want to compile you can just use the current virtual machine firmware we compiled:  
QEMU_EFI.fd:UEFI code image for UEFI execution.  
QEMU_VARS.fd:UEFI flash image for non-volatile variables.  

### Instructions for use
Use the install script to place the bios in the specified location:
./install-loongarch-virt-firmware.sh

When booting the virtual machine, specify the virtual machine firmware you want to use with the -bios parameter e.g:  
```   
qemu-system-loongarch64 -m 8G -smp 4 -cpu la464 \
-machine virt  \
-bios /usr/share/edk2/loongarch64/QEMU_EFI.fd  \
-serial stdio   \
-device virtio-gpu-pci   \
-device nec-usb-xhci,id=xhci,addr=0x1b \
-device usb-tablet,id=tablet,bus=xhci.0,port=1 \
-device usb-kbd,id=keyboard,bus=xhci.0,port=2 \
-drive id=test,file=./archlinux.qcow2,if=none 
```   
When starting a virtual machine, specify the flash image to use through pflash, for example:
```
qemu-system-loongarch64 -m 8G -smp 4 -cpu la464 \
-blockdev '{"driver":"file","filename":"/usr/share/edk2/loongarch64/QEMU_EFI.fd","node-name":"libvirt-pflash0-storage","auto-read-only":true,"discard":"unmap"}' \
-blockdev '{"node-name":"libvirt-pflash0-format","read-only":true,"driver":"raw","file":"libvirt-pflash0-storage"}' \
-blockdev '{"driver":"file","filename":"/usr/share/edk2/loongarch64/QEMU_VARS.fd","node-name":"libvirt-pflash1-storage","read-only":false}' \
-machine virt,pflash0=libvirt-pflash0-format,pflash1=libvirt-pflash1-storage \
-serial stdio   \
-device virtio-gpu-pci   \
-device nec-usb-xhci,id=xhci,addr=0x1b \
-device usb-tablet,id=tablet,bus=xhci.0,port=1 \
-device usb-kbd,id=keyboard,bus=xhci.0,port=2 \
-drive id=test,file=./archlinux.qcow2,if=none
```  

### <font color=red>Notice</font>
<font color=red>**This virtual machine firmware is not available for qemu 4.2 and qemu 6.2, please go to the qemu website to download the latest qemu source code to compile and install.**</font>

If you have any questions，you can connect us:  
* Virtual Machine: maobibo@loongson.cn & lixianglai@loongson.cn
