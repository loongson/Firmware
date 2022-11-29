# LoongArch Virtual Machine Firmware 
[简体中文](https://github.com/loongson/Firmware/LoongArchVirtMachine/README_CN.md)

LoongArch virtual machine firmware is compiled based on the tianocore community source code, which is located at :  
https://github.com/tianocore/edk2  
https://github.com/tianocore/edk2-platform  

You can download, modify and compile the source code by yourself, if you want to compile it by yourself, you can refer to:  
https://github.com/tianocore/edk2-platforms/tree/master/Platform/Loongson/LoongArchQemuPkg/Readme.md  

Of course, if you don't want to compile you can just use the current virtual machine firmware we compiled:edk2-loongarch64-code.fd   

### Instructions for use
When booting the virtual machine, specify the virtual machine firmware you want to use with the -bios parameter e.g:  
```   
qemu-system-loongarch64 -m 8G -smp 4 --cpu la464 --machine virt  \
-bios ./edk2-loongarch64-code.fd  \
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
