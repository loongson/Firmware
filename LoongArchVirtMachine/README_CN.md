# LoongArch虚拟机固件  

LoongArch虚拟机固件是基于tianocore社区源码进行编译的,源码的位置为:  
https://github.com/tianocore/edk2  
https://github.com/tianocore/edk2-platform  

你可以自行下载、修改、编译源码,如果您想要自行编译，你可以参考:  
https://github.com/tianocore/edk2-platforms/tree/master/Platform/Loongson/LoongArchQemuPkg/Readme.md  

当然，如果您不想编译你可以直接使用当前我们编译好的虚拟机固件:edk2-loongarch64-code.fd  

### 使用说明  
在启动虚拟机时，通过-bios参数指定你所要使用的虚拟机固件例如：  
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

### <font color=red>注意</font>  
<font color=red>**本虚拟机固件暂时不适用于qemu 4.2 和 qemu 6.2， 请前往qemu官网下载最新qemu源码编译安装。**</font>  


如果有问题，请联系我们:  
* 虚拟机: maobibo@loongson.cn & lixianglai@loongson.cn  
