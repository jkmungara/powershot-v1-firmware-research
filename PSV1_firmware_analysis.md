# PowerShot V1 firmware analysis

## Input

- File: `PSV11200.FIR`
- Size: 65,038,928 bytes (`0x03e06a50`)
- SHA-256: `047f7c36ec9376690ccf8be48c55d23e7b0bb82e3776387847da690dcbe1a8ed`
- Header model ID: `0x80000497`
- Header version: `1.2.0.5.7.5`

## Parsed header

- Stored checksum field at `0x20`: `0x11b3a8f1`
- Updater header offset: `0x00000100`
- Encrypted updater payload offset: `0x00000120`
- Second updater: `0xffffffff`, indicating no second updater in the legacy interpretation
- Firmware header offset: `0x004c3a60`
- File-size field: `0x03e06a50`, exactly matching the file length

The layout is consistent with Canon's documented FIR family, but the updater and firmware payloads remain opaque. Sampled 64 KiB windows produce entropy near 7.997 bits per byte. That is consistent with encryption or strong compression, so incidental gzip and bzip signatures are not treated as embedded archives.

## Hardware and project direction

Canon identifies the PowerShot V1 as a DIGIC X camera. Existing CHDK documentation recommends an in-camera firmware dump for new ports, usually through Canon Basic where supported. Magic Lantern documents AES-protected Canon FIR generations and uses SD-card-loaded add-ons rather than replacing stock firmware.

No PowerShot V1 CHDK or Magic Lantern target was identified. The safest development target is therefore a read-only dump or RAM-loaded proof of concept, not a modified Canon updater.

## Next experiment on physical hardware

1. Use a spare SD card and a fully charged battery.
2. Verify whether the camera recognizes Canon Basic scripts without enabling any persistent boot flag.
3. If supported, run only a known read-only dumper that writes ROM ranges to the SD card.
4. Hash the dump twice and require identical SHA-256 values before analysis.
5. Determine architecture and memory map in Ghidra, then identify task names, property tables, gyro code, optical IS control, Movie Digital IS, crop limits, and video-frame processing.
6. Prototype telemetry logging in RAM. Do not alter internal flash or lens actuator commands.

## Stop conditions

Stop if the camera freezes repeatedly, the script requires a persistent boot flag, the dump differs between identical runs, or the only available route requires bypassing signature checks and flashing unverified code. Optical IS actuator changes can damage the lens assembly, while malformed firmware can make the camera unbootable.
