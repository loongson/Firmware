# Firmware

[![简体中文](https://img.shields.io/badge/lang-中文-red.svg)](README_CN.md)

### Downloads Hub
For your convenience, GitHub Pages hosts a downloads index to make web searching for specific model/version firmware easier.
- 👉 [https://loongson.github.io/Firmware/](https://loongson.github.io/Firmware/)
The page is deployed automatically on pushes to `main` via GitHub Actions.

### Firmware Of LoongArch Machines
LoongArch machines firmware binary repository, where you can find firmware for almost machine types, including Qemu binaries. It will become more and more complete.
The firewares are all based EDK2, the boot logo is Loongson logo, EDKII style setup UI, **adapt upstream linux kernel, support EfiStub**.

### <font color=red>Notice</font>
<font color=red>**There firmwares have not yet adapted to the UOS and Kylin OS current versions, we only recommend developer. Unless you are a developer or familiar for LoongArch, do not try update the firmware easily.** </font>

### Prepare to update  
* Back up current firmware. We recommend that you need a burner, and read the contents of the SPI flash through the burner and save it.  
* Download the firmware that matches your machine type or motherboard. The information of machine can be obtained through machine appearance, motherboard appearance or the SMBIOS type0-type3.
* Check integrity of the downloaded firmware image against the provided `SHA256SUMS.txt` with `sha256sum` or any other equivalent tool.
* It is better to put the new firmware into a U disk formatted as fat32.

### Update  
* ZD class can be update through setup UI. You can find the update item on the "Security" page, select U disk devcie you inseted, and find the new firmware to update.
* Loongson class, there are two ways can update the firmware:  
  * The first way, update through setup UI. You can find the update item on the "Security" page, select U disk devcie you inseted, and find the new firmware to update.  
  * The second way, you can use "spi -u FileName" command in the EDKII shell to update, use "help spi" command for more help.
    * Tip: Switching the file system partition fs0:\fs1:\fs2: in Shell to search for FileName, refer to the instance:
      * [Step1](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step1.png): Enter EFI Shell to view partition;
      * [Step2](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step2.png): Use fs0:\fs1:\fs2 etc to enter directory and search for FileName;
      * [Step3](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step3.png): Use cmd[spi -u FileName] to update firmware;
* **The general update method is to update through burner, this method is recommended, which is safer.**  

If you have any questions，you can connect us:  
* Physical machines: lichao@loongson.cn && qiandongyan@loongson.cn  
* Qemu: lixianglai@loongson.cn
