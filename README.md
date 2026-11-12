# PowerShot V1 firmware research

Read-only research notes and tooling for Canon PowerShot V1 firmware version 1.2.0.5.7.5.

## Repository contents

- `PSV1_firmware_analysis.md`: findings, parsed offsets, constraints, and safe next experiments.
- `inspect_psv1_fir.py`: read-only header and entropy inspector.

## Firmware sample

The Canon firmware binary is intentionally excluded. Obtain `PSV11200.FIR` from Canon and verify:

```text
SHA-256: 047f7c36ec9376690ccf8be48c55d23e7b0bb82e3776387847da690dcbe1a8ed
Size: 65038928 bytes
```

Run the inspector:

```bash
python3 inspect_psv1_fir.py PSV11200.FIR
```

## Current status

The FIR header is parseable, but the updater and firmware payloads appear encrypted or strongly packed. No patching or flashing code is included. The next useful artifact is a repeatable, read-only ROM dump from physical hardware or a lawful decryption path for this exact firmware generation.

## Safety

Do not flash modified firmware or alter optical image-stabilizer actuator commands without a verified recovery method. Work first with SD-card-loaded, RAM-only diagnostics.
