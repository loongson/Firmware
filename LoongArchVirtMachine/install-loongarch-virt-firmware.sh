#!/usr/bin/bash

mkdir -pv /usr/share/qemu/firmware
cp ./50-edk2-loongarch64.json /usr/share/qemu/firmware
mkdir -pv /usr/share/edk2/loongarch64
cp ./QEMU_EFI.fd  /usr/share/edk2/loongarch64
cp ./QEMU_VARS.fd /usr/share/edk2/loongarch64
