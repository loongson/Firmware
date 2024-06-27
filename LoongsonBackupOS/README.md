# BACKUPOS

[简体中文](https://github.com/loongson/Firmware/blob/main/LoongsonBackupOS/README_CN.md)

Loongson BACKUPOS operations show as follows:

```
1.Prepare two USB drives and other storage devices. Format one USB drive as Fat32 and 
  use it as a boot disk. Create a new EFI file (file name is not case sensitive) and 
  copy BACKUPLOONGARCH64.EFI into it. Use one USB drive in ext3/ext4 format as a backup 
  device for the system, with a capacity greater than the required backup file size.
2.Connect two USB drives to the host, power on, and press F4 on the progress bar to 
  access the function. As shown in Figure.
```
The picture is as follows:
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-F4.jpg)

```
3.After press F4 can show the function it mainly includes backup and restore.
```
The picture is as follows:
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-show.jpg)

```
4.In backup function, select the drive letter where the system is located for 
  the source storage device, and select the drive letter where the backup files 
  are located for the target storage device. A backup directory name will be
  automatically assigned, as shown in figure. After selection, click on Start Backup.
```
The picture is as follows:
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-back.jpg)

```
5.In restore function, select the system disk for the device that needs to be restored, 
  select the storage disk for storing the original data, and name a file for it, this tool 
  can name a default file as shown in Figure 4. After selecting, choose to start restoring.
```
The picture is as follows:
![image](https://github.com/loongson/Firmware/blob/main/Image/BACKUP-restore.jpg)
