# 固件  

### LoongArch平台固件    

LoongArch平台固件二进制仓库，在这里可以找到尽可能多的主机类型，包括虚拟机二进制。我们会越来越完善该仓库。  
所有固件均基于UDK2018版本，启动logo为龙芯logo，EDKII风格setup UI，**适配上游linux内核，支持EfiStub启动**  

### <font color=red>注意</font>  
<font color=red>**本仓库固件暂时不适用现有版本UOS和麒麟OS系统，我们只推荐开发者或者对LoongArch架构非常熟悉的人员更新固件，否则不要轻易尝试。**</font>  

### Prepare to update  
* 备份当前固件，推荐使用烧录器读取SPI flash里面的内容并且保存。
* 下载相应机型或者主板的固件。可以通过SMBIOS type0-type3来获取主机或者主板的信息。
* 用 `sha256sum` 或其他合适工具软件，对着提供的 `SHA256SUMS.txt` 校验下载的固件映像的完整性。
* 推荐使用fat32格式的U盘存放下载的固件。

### Update  
* 昆仑固件可以通过UI界面来升级；通常在“安全”页面下可以找到升级选项；找到插入的fat32格式U盘，并找到相应文件回车选择后开始升级。
* 龙芯固件可以通过两种方式升级：
  * 第一种，通过UI界面升级，同样是在"Security"页面找到升级的入口，选择插入的U盘并且找到相应文件进行升级。
  * 第二种，通过Shell命令行升级，在UEFI shell界面下通过"spi -u FileName" 命令升级；如果需要更多帮助，请执行"help spi"命令获取。
    * 提示: 在Shell下通过切换文件系统分区 fs0:\fs1:\fs2: ... 来查找FileName，实例参考:
      * [步骤一](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step1.png): 进去EFI Shell去查看分区;
      * [步骤二](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step2.png): 使用fs0:\fs1:\fs2: 等进入对应分区系统目录并查找烧录文件;
      * [步骤三](https://github.com/loongson/Firmware/blob/main/Image/spi_u_step3.png): 使用命令[spi -u FileName]来更新固件;
* **推荐使用烧录器升级，这种方式最安全**  

如果有问题，请联系我们:
* 物理机: lichao@loongson.cn && qiandongyan@loongson.cn  
* 虚拟机: lixianglai@loongson.cn
