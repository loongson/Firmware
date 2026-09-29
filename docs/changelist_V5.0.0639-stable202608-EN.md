# Loongson UEFI Firmware Binaries for the Community (V5.0.0639-stable202608)

## 1. Overview

This version contains primarily updates to key hardware support components, such as PHY, MRC, SMC, PCIe, and IPMI, etc. Also updated are SPI/Variable, ACPI/SMBIOS, Boot Manager, User Interface, and Platform support components.

Speaking from a high-level perspective, the 202608 release improves stability for multi-node/multi-processor systems, device identificaiton and initialization, boot performance, and peripheral compatibility:

- **Core component updates:** Updated key components, improving support for Loongson 2K3000/3B6000M, 3A5000, 3A6000, 3B6000, 3C6000/S/D/Q, and 7A2000-based platforms.
- **Platform support improvements:** Added support for TD612D0 (single-processor Loongson 3C6000/D workstation motherboard).
- **Functionality enhancements:** Introduced support for eMMC device information querying, default password, PCIe device serial detection, and Secure Engine-based hardware random number generator, as well as automatic to ESP boot entry naming, and improvements to the display initialisation interface.
- **Stability and compatibility:** Resolved a series of issues found in EFI variable handling, SPI flash, PXE, GRUB exits, Secure Boot configuration, ACPI, SMBIOS, display, newtorking, and storage, as well as stability and startup speed optimisation for multi-node/processor systems and systems with complex PCIe topology.

## 2. Key Component Updates

Please note that detailed changes and versions for some key components are not listed for public changelos.

| Component | Version Update | Changes |
|---|---|---|
| Loongson-FwSdk | Updated to V5.0.0639-stable202608 | Includes updates and improvements for platforms and devices based on Loongson 2K3000/3B6000M/3A6000/3B6000/3C6000/S/D/Q and 7A2000 |
| IPMI Support Module | - | Fixed several interface issues, such as configuration errors, user password lengths, SMBIOS/FRU update on the BMC end, and issues with AC power cycle stability |
| Filesystem and Emulator Modules | - | Updated the Ext2 filesystem driver, with workaround for data read issues with certain closed-source RAID drivers |
| EDK II (public code) | stable202602 | Enhanced usage for upstream implementation in modules such as HiiDatabaseDxe, VariableRuntimeDxe, and VariablePolicyProtocol, etc., reducing code redundancy and improving consistency with upstream interfaces |

## 3. Support for Chips and Platforms

### 3.1 2K3000/3B6000M-based Platforms

- Added the ability to replace EDID for 2K3000/3B6000M-based laptops, allowing different eDP screen configurations based on product designs.
- Added the ability to keep the DC (Display Controller) working as a display output when GPU is disabled.
- Improved ACPI events, GPIO, and memory reset handling.
- Improved DisplayPort AUX packet processing, fixing compatibility with some eDP adapters/convertors.
- Updated the VBIOS display configuration for the X2K30B0 motherboard, ensuring functionality for single-channel DP/HDMI interfaces.
- Enabled description for LPC nodes in the ACPI.DSDT table.
- Fixed SMC chip type identification.
- Fixed intermitten EDID read failure over DisplayPort.
- Fixed incorrect I²C bus frequency calculation.
- Fixed voltage regulation logic on reboots, eliminating unexpected voltage regulation.

### 3.2 3A6000-baed Platforms

- Refactored I²C voltage regulation, improving maintainability and log output.
- Optimized SMC data access policy in several scenarios, ensuring both stability and efficient execution.
- Optimized platform-specific voltage configuration defaults and logging for unexpected inputs.
- Optimized several atomic operations.
- Fixed SPI dual-wire mode configuration and incomplete register recovery on parameter fallback.

### 3.3 3B6000- and 3C6000-based Platforms

- Enabled HPTW (Hardware PageTable Walk) - please note that this feature is suggested for use with Loongnix Server 23.3 (Linux 6.6.52-1.12) or mainline kernels of version 7.1.5 or higher.
- Added support for the TD612D0 motherboard, adapting it to latest SMC and build system enhancements.
- Added detection and identification support for lower-frequency 3B6000 and 3C6000 SKUs.
- Optimized slave node reset and cross-node access stability during reboot on multi-node/processor 3C6000 systems.
- Optimized link initialization stability during power on.
- Optimized memory parameters for 3C6000/D, lowering likelihood for ECC errors.
- Optimized several atomic operations.
- Improved ACPI SRAT handling (except for dual 3C6000/S), making sure that processor descriptors were generated from real core indices.
- Optimized PCIe parameter saving and link configuration when training is disabled, eliminating unwanted interference from inappropriate parameters.
- Fixed incorrect memory temperature and CPU count display on the BMC's Web interface on multi-node 3C6000/S and 3C6000/D servers.
- Fixed incorrect maximum-frequency display after enabling DVFS on 3B6000-based systems.

### 3.4 7A2000 Bridge Chip

- Improved GPIO handling interface, adding configurability to multi-bitwidth access, input state, and interrupt polarity features.
- Optimized AHCI sequential write performance when using the bridge chip with a PCIe uplink.
- Fixed PCIe port initialization control, where GEN1 speed configuration could fail to apply.

### 3.5 Motherboards and Peripherals

- **[IMPORTANT] Fixed a severe issue where the I²C voltage regulation channel would set an exceedingly high core voltage on the XA612A0 motherboard, users currently running the stable202602/05 firmware are strongly recommended to update.**
- Added eMMC information querying, display in the firmware setup interface, and a dedicated boot-entry type; also improved eMMC boot-entry naming and handling when no eMMC device is present.
- Improved filesystem driver for Ext2, fixing path access issue on controller removal.
- Optimized network interface initialization, PXE toggle, and network protocol exit routines.
- Optimized device detection, disabling, and enabling for some PCIe devices, NVMe controller, and complex PCIe topologies..
- Fixed non-stopping beep during boot-up on the QC622D1 (dual 3C6000/S) motheboard.

## 4. General Enhancements and Optimizations

### 4.1 New Features

- Improved naming logic for ESP boot entries, introducing the ability to identify operating systems by known bootloader paths, supporting Loongnix, UOS, Kylin, openEuler, deepin, Anolis, Arch Linux, AOSC OS, and other operating systems and Linux distros.
- Added or improved ACPI ThermalZone `_STR` descriptors, adding support for nodes on 3A6000/7A2000.
- Added processor thread count display in the system information page.
- Added configurable default administrator password (defaults to empty or no password).
- Added EDAC memory controller indices and per-node controller count properties in the ACPI table, making it easier for Linux kernel driver to detect the relationship between the controller and processor node(s).
- Added LoongArch PE/COFF image parser to the Secure Boot configuration module.
- Added the ability to read PCIe device serial number(s), which could be used to improve the level of details in SMBIOS information.
- Added VID/DID debug information during PCI initialization, easing debugging and troubleshooting.
- Added optional platform-specific policy to continue searching for PCI Function 1-7 when Function 0 does not exist.
- Added BaseRngLib implementation based on the Loongson Secure Engine - when the Secure Engine is not available, a CPU-based fallback is available.
- Added available Proximity Domain and NUMA topology description to the ACPI IOVT table, enhancing SR-IOV scheduling performance.
- Enabled Reset Notificaiton Protocol support in the ResetRuntimeDxe module, allowing NVMe and other controllers to perform necessary shutdown procedures during system reboot/reset.
- Added support for Serial Flash Discoverable Parameters (SFDP) parsing and page-based write optimization, improving UEFI firmware update speeds (a fallback path is reserved for devices that do not support SFDP).

### 4.2 Improvements and Adjustments

- Optimized ACPI PCI I/O resource descriptors for multi-node/processor platforms, allowing each node to allocate an appropriate amount of I/O space.
- Improved status initialization for Secure Engine in device mode.
- Refactored EFI variable read/write and management mode implementation, making use of upstream VariableRuntimeDxe, FaultTolerantWriteDxe, and VariablePolicyProtocol module implementation from the upstream, improving variable area and fault tolerance write area management.
- Disabled NVMe OptionRom loading, preventing conflict between x86 emulation and native drivers.
- Optimized boot-up timeout handling when reverting to default configurations - the firmware will now use the platform default timeout.
- Optimized LoongArch64 firmware segment alignment, allowing PE/COFF images to fit page alignment requirements.
- Optimized boot-up progress display for Denglin's AI accelerator card, reducing screen refreshed and lowering start-up times on systems with complex PCIe topologies.
- Optimized help information for administrator password, making it consistent with the actual length limit and adding notification when the password exceeds that length.
- Removed the no-longer-supported virtual/physical address switching mode from the Legacy Boot option, the legacy BPI interface specification is no longer supported.
- Updated PCI ID database to 2026-08-11 and added information for several non-upstream device IDs.

## 5. General Bugfixes

### 5.1 Bugfixes

- Fixed an issue where the SMC configuration could not be changed in Release firmware.
- Fixed an issue where randomly generated MAC addresses were overwritten during reboots by making the randomly generated addresses non-volatile.
- Fixed an issue where the PXE/HTTP options were disabled (greyed-out) after pressing the F9/F10 hotkeys.
- Fixed an issue where the PXE switch no longer works after the option was enabled.
- Fixed an issue that prevented the PXE driver from initializing.
- Fixed an issue where the boot paths stopped working after the UEFI Shell was moved to another Firmware Volume.
- Fixed an issue where the system may hang after executing `exit` from the GRUB command line.
- Fixed residual displays after toggling between Chinese and English interfaces, also improved Chinese translation.
- Fixed an issue where the system time could not be saved after loading factory CMOS defaults when the administrator password is enabled.
- Fixed incorrect memory device count in SMBIOS information, as well as issues with missing NVMe device information and registration sequences.
- Fixed an issue where the BMC user password length limit was inconsistent with that specified in the help information.
- Fixed various issues with SMC parameter table length checks, frequency calibration, power consumption limits, temperature displays, and BMC function toggles.
- Fixed IPMI BMC display configruation access could cause assertion errors during boot-up, resulting in boot failures.
- Fixed an issue where invalid configuration dependencies in the Secure Engine's "empty" implementation could cause assertion errors during boot-up, resulting in boot failures.
- Fixed SPI flash parameter parsing errors, causing potential heap memory and UEFI variable storage corruption.
- Fixed incorrect usage of `Exclusive`/`Shared` ACPI interrupt resources properties.
- Fixed display offsets in graphical output.
- Fixed warning caused by recursive use of looped delays in network interface delay logic.
- Fixed consecutive errors when calling the UNDI interface on some network interface controllers.
- Fixed an issue where the save confirmation result passing did not match EDK II's interface.
- Fixed freeing of uninitialized pointers and memory leak in the callback path in the Secure Boot configuration module.
- Fixed multiple memory leaks and invalid dependencies in driver and platform libraries.

### 5.3 Update Statistics

|Area|№ of Issues Fixed|№ of New Features and Funtionalities|№ of Optimizations and Adjustments|Subtotals|
|---|---|---|---|---|
|2K3000 / 3B6000M| 	4|	3|	3|	10|
|3A6000|	2|	0|	4|	6|
|3B6000 / 3C6000/S/D/Q|  	2|	3|	6|	11|
|7A2000|        1|	1|	1|	3|
|Motherboards & Peripherals|	1|	1|	2|	4|
|General Features|	22|	12|	11|	45|
|Totals|32|	20|	27|	79|

## 6. Notes

- After setting a default administrator password and expiration date, should the device be shipped after that date, the user would see a notification regarding password expiration.
- The EDID replacement functionality for 2K3000/3B6000M requires that valid EDID data could be read from the target channel.
- PCI function scanning with missing Function 0 is an optional platform-specific policy.
- HPTW on 3B6000/3C6000 is only recommended with Loongnix Server 23.3 (Linux 6.6.52-1.12) or mainline kernels of version 7.1.5 or higher.
- PC platform runs a mandated memory resource detection routine after the first reboot following a firmare update - however, the routine may trigger a reboot, making it appear as though the system unexpectedly rebooted twice - we will attempt to find a solution to this issue before the next release.
- Firmware with support for mainline DVFS (Dynamic CPU/SoC Voltage Frequency Scaling) - this functionality is still considered community preview, firmware binaries with the `_mainline-dvfs` suffix (e.g., `[...]_mainline-dvfs.fd`) has this preview feature enabled - though please note that the BIOS setup does not show this version identifier.

## 7. References

- EDK II - A case of migration to VariablePolicyProtocol from VariableLockProtocol, https://github.com/tianocore/edk2/pull/1128
- EDK II - An example fix for boot-up failure when the Shell is located in a different Firmware Volume, https://github.com/tianocore/edk2/pull/4377
- EDK II - An example issue for NIC-related errors during ExitBootServices, https://github.com/tianocore/edk2/issues/8063
- EDK II - Discussion for scanning other PCI Functions when Function 0 is missing, https://github.com/tianocore/edk2/pull/12572
- EDK II - LoongArch PE/OFF parsing support for Secure Boot, https://github.com/tianocore/edk2/pull/12709
- PCI ID database, https://github.com/pciutils/pciids
