# 龙芯备份还原操作系统

龙芯备份还原操作系统操作流程如下：

```
1.准备两个U盘等存储设备，将一个U盘格式化为Fat32，作为引导盘，新建EFI文件（文件名不区分大小写），放入文件
  BACKUPLOONGARCH64.EFI，一个U盘为ext等文件格式，作为用于备份系统的设备，容量需要大于所需备份文件大小。
2.将两个U盘接入主机中，开机，进度条界面按F4即可进入功能。如图所示。
```
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-F4.jpg)

```
3.进入后，可以看到如图界面。主要包含备份和还原两个功能。
```
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-show.jpg)

```
4.选择备份功能。源存储设备选择系统所在盘符，目标存储设备选择备份文件所在盘符。会自动分配一个备份目录名字，
  如图所示。选好后，点击开始备份。
```
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-back.jpg)

```
5.选择还原功能。需要还原的设备选择系统盘，存放原始数据设备选择备份时的存储盘，在还原数据中选择需要还原的文件，如图。选好后，选择开始还原。
```
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-restore.jpg)
