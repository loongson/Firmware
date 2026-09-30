# EVB

The 3B6000-7A2000-EVB SMBIOS **Type 1** system information may be as follows:
```
System Information
	Manufacturer: Loongson
	Product Name: Loongson-3B6000-7A2000-1w-V0.1-EVB
	Version: Not Specified
	Serial Number: Not Specified
	UUID: Not Present
	Wake-up Type: Power Switch
	SKU Number: Not Specified
	Family: Not Specified
```

## Notes for XB612B0\_V1.1

This folder contains firmware specifically released for XB612B0\_V1.1 **with BA-stepping 3B6000 processors**, which are not compatible with those released for XB612B0\_V1.0/1.2. Firmware marked as V1.1-8 are for 8-core models, and those marked with V1.1-12 are for 12-core models.

To identify the stepping of your 3B6000 processor, please remove the heatsink assembly and identify the lettering marked in red - "AA" means AA stepping and "BA" means BA stepping. **Do not use these firmware binaries if your processor is marked with "AA", use the XB612B0_V1.2 firmware instead!**
![image](https://github.com/loongson/Firmware/blob/main/Image/3B6000-step.jpg)

The picture of motherboard is as follows:
![image](https://loongfans.cn/images/devices/loongson-xb612b0-v1.1.webp)
