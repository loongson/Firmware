# LoongArch虚拟机固件  

LoongArch虚拟机固件是基于tianocore社区源码进行编译的,源码的位置为:  
https://github.com/tianocore/edk2

你可以自行下载、修改、编译源码,如果您想要自行编译，你可以参考:  
https://github.com/tianocore/edk2/tree/master/OvmfPkg/LoongArchVirt#readme

当然，如果您不想编译你可以直接使用当前我们编译好的虚拟机固件:  
QEMU_EFI.fd:UEFI代码镜像,用于UEFI的执行.  
QEMU_VARS.fd:UEFI flash镜像,用于保存非易失变量.  

### 使用说明  
使用安装脚本将固件放在指定位置:
./install-loongarch-virt-firmware.sh

在启动虚拟机时，通过-bios参数指定你所要使用的虚拟机固件例如：  
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
在启动虚拟机时，通过pflash指定所要使用flash镜像例如:
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

### <font color=red>注意</font>  
<font color=red>**本虚拟机固件不适用于qemu 4.2 和 qemu 6.2， 请前往qemu官网下载最新qemu源码编译安装。**</font>  

如果有问题，请联系我们:
* 虚拟机: maobibo@loongson.cn & lixianglai@loongson.cn  
