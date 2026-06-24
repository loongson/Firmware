### Loongson UEFI RC V5.0.0529-stable202605 FOR COMMUNITY

## 1. 版本概述

本版更新主要包含 DDR.MRC、PCIe.PHY、SMC、IPMI、EDK II (edk2) 基础代码及平台适配的相关更新，并优化了平台稳定性、外设兼容性、启动流程及固件更新等功能：

- **基础模块升级**：持续迭代 DDR.MRC、PCIe.PHY 及 SMC 等基础模块，提升内存初始化、链路训练、功耗控制和异常场景处理能力；
- **平台支持增强**：完善龙芯 2K3000/3B6000M、3A6000、3B6000、3C6000/S/D/Q、及 7A2000 等平台的支持；
- **功能增强**：新增固件备份恢复、ACPI FPDT 启动性能测量表及 ACPI I/O 虚拟化表 (IOVT) 等新功能，增强 SMBIOS 信息及 2K3000 多项平台能力；
- **稳定性与兼容性优化**：优化 PCIe 链路训练、DMA 传输可靠性、ACPI S3 睡眠、VBIOS、PCIe Option ROM 及 LoongGPU 的驱动兼容性，并增强了外设兼容性；

## 2. 部分基础模块升级变更如下：

| 模块 | 旧版本 | 新版本 | 主要变化 |
|---|---:|---:|---|
| Loongson-FwSdk | V5.0.0431-stable202602 | V5.0.0529-stable202605 | 涵盖 2K/3B/C/6000/S/D/Q 7A 芯片与平台适配 |
| EDK II（edk2 公共代码） | stable202505 | stable202602 | 同步 EDK II stable202602 公共基线中的新功能和问题修复 |

## 3. 芯片与平台适配

### 3.1 2K3000/3B6000M 平台

- 新增 2K3000 及 3B6000/M 相关定义及动态开启相应设备功能；
- 新增 3B6000M/4 平台功耗封顶功能, 界面选项可配置；
- 新增 2K3000 系列平台多端口 PCIe 控制界面配置选项；
- 新增 2K3000/3B6000M 平台高级设置界面中的 4KiB 页模式配置选项以更好地支持二进制翻译等特定应用场景；
- 优化 2K3000/3B6000M 平台部分位域控制、帧缓存操作及 HDMI 像素时钟频率算法及内存复位延时等初始化体验行为；
- 优化 2K3000/3B6000M 平台的预分配内存池机制，提升开机体验；
- 完善 2K3000/3B6000M 平台 DP 接口的热插拔探测功能；
- 优化 2K3000/3B6000M 平台 DP 获取 EDID 时设置包字节大小；
- 优化 2K3000/3B6000M 温度传感器获取及温度算法；
- 优化 2K3000/3B6000M 平台 PCIe 训练机制；
- 去除 2K3000/3B6000M 平台固件设置界面中残留无用 IOMMU 及 SR-IOV 配置选项的问题；
- 修复 2K3000/3B6000M/4 平台特定场景下休眠唤醒时返回数据异常；
- 修复 2K3000/3B6000M 平台固件快速启动失效问题；

### 3.2 3B6000/3C6000 平台

- 优化 3B/C6000 平台 PCIe 相关配置，提升链路稳定性及外设兼容性；
- 完善 3B6000 平台 ACPI EDAC 功能及 RDIMM 内存自检支持；
- 校准 3B6000/3C6000 平台温度传感器数据读取；
- 修复 3C6000 特定平台无内存在位时的 EDAC 误报问题；
- 优化 SMC 异常场景处理，降低主控异常挂起风险；
- 集成 BMC 功耗封顶控制命令机制；

### 3.3 7A2000 平台

- 优化在低温等特定环境下的初始化稳定性；
- 修复无法关闭远程 USB 唤醒的问题；
- 修复固件设置界面下 7A2000 SATA 端口配置无效的问题；

### 3.4 板卡与外设

- 适配迈络思 (Mellanox) ConnectX-4 系列 25GbE/100GbE 网卡，以及部分 PMC 等 PCIe 网络及存储设备；
- 升级部分 EFI 外设驱动: 如华瑞 RAID 可提升稳定性。

以上详情细节描述此处不再展开；

## 4. 通用（公共层）功能增强

- 更新 EDK II (edk2) 基础代码至 stable202602 版本，包含大量普适性新功能和修复；
- 新增 ACPI I/O 虚拟化表 (IOVT)，可更好地兼容主线 Linux 内核的 IOMMU 虚拟化功能；
- 新增 ACPI 固件性能数据表 (FPDT)，可支持 `systemd-analyze(1)` 等程序测量固件及引导器耗时等信息；
- 新增 SMBIOS 中数个 DRAM 厂商的 ID 对应名称，包括 Ramaxel、Micron 等；
- 新增 SMBIOS Type 17 设备（内存设备）信息根据 DDR 配置自动填入贴片内存或内存模组 SPD 信息的功能；
- 新增 ACPI S3 低端地址存储内存校验支持；
- 新增固件备份及恢复功能；
- 新增重入解析 VBIOS 机制，便于固件自适应调整 VBIOS 数据；
- 更新 PCI ID 数据库到 2026.05.12 的版本，并增补部分尚未登记的 PCI 厂商和设备信息；
- 调整 PCIe 资源分配策略，将 Above 4G 可支持空间由小于 512GiB 扩展至 720GiB，以兼容更多大 BAR 计算加速卡。

其中，本次同时发布的公测固件 V5.0.0532 主要为了兼容社区主线 Linux 内核中已有的动态调频调压及睿频 (Boost) 功能。

## 5. 通用（公共层）功能优化与问题修复

- 新增 MultiArchUefiPkg Watchdog Timer (WDT) 规避机制，避免模拟初始化个别网卡 Option ROM 时出现的断言 (Assert) 错误；
- 增强部分 PCIe Option ROM 中宽窄字符混用情况的的兼容性，避免部分非标设备设置界面乱码，抑或在切换固件配置界面语言时卡死的问题；
- 优化 ACPI EDAC 表，现可根据内存模组 (DIMM) 的 ECC 状态动态导出配置，其中 EDAC 编号可按 DIMM 识别顺序排列；
- 完善 SMBIOS 内存类型字段中对 LPDDR4 的识别逻辑，并修正部分信息；
- 完善 UEFI Shell 中的 pcietest 命令（供主板厂商SI测试使用），以支持 3C6000 平台的拓扑结构；
- 完善 UEFI Shell 中的 i2c 命令，支持特定板卡板载 EEPROM 读写操作；
- 修复驱动卸载时 UninstallMultipleProtocolInterfaces 的调用错误；
- 修复无显卡情况下无法操作固件图形化更新界面 (UI.UpdateFw) 的问题；
- 修复因 EDK II (edk2) 网络栈升级导致的 HTTP 引导类型错误；
- 修复重启过程中可能因 RTC 频繁读写导致精度受损的问题；
- 修复部分文件路径错误；
- 优化 SMBIOS 部分字段，并在必要时做拆分操作，避免长行问题；
- 优化解压缩数据时的部分打印信息；
- 重构部分 ACPI ASL 及 ACPI 相关配置信息中的 OEM ID 字段；
- 规范依赖 RTC 位域寄存器功能的掩码；

## 6. 注意事项与已知问题

- 2K3000/3B6000M 平台 DisplayPort 热插拔探测功能仅支持 20250206 或更新版本的 LoongGPU 驱动；
- 固件备份及恢复功能需要管理员权限且须提供可写存储设备，默认备份路径为 \LsFwBackup\lsfw.bin；
- ACPI FPDT 表用于引导性能测量；当前固件结合设备实际场景去除了 DB.Support 相关数据；

## 7. 参考链接

- EDK II (edk2) stable202602 版本发行说明：https://github.com/tianocore/edk2/releases/tag/edk2-stable202602
- ACPI IOVT 表参考提交：https://github.com/tianocore/edk2/commit/0e6f016032ed6c51a44cee684e4e0b0c65667cbd
- UninstallMultipleProtocolInterfaces 修复参考：https://github.com/tianocore/edk2/commit/9388c6b1c17af9c8a9f451a42c066b3ae7d81fda
- PCI ID 数据库来源：https://github.com/pciutils/pciids
