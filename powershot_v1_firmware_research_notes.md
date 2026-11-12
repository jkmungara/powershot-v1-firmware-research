# Canon PowerShot V1 firmware research notes

## Purpose

This document captures the firmware-analysis work completed in this chat before moving to the next stage. The working goal is to investigate whether the Canon PowerShot V1 video stabilization pipeline can be adjusted, especially the digital stabilization behavior described as edge jitter, wobble, or a "gooey" warp effect.

No modified firmware has been flashed. All work so far has been read-only parsing and signature verification.

## Camera and firmware files

- Camera: Canon PowerShot V1
- Model ID: `0x80000497`
- Decimal model ID: `2147484823`
- Processor generation selected by the verifier: DIGIC 10
- Firmware 1.1.0 file: `PSV11100.FIR`
- Firmware 1.2.0 file: `PSV11200.FIR`

Local paths used on macOS:

```text
/Users/INE12398085/Downloads/psv1-v110-win/PSV11100.FIR
/Users/INE12398085/Downloads/psv1-v120-win/PSV11200.FIR
/Users/INE12398085/Downloads/d8_oracle-main
```

A previous path using `psv1-v112-win` was a typo and caused a file-not-found error. The correct 1.2.0 directory is `psv1-v120-win`.

## Research objective

The proposed workflow is:

1. Parse both FIR packages with `fir_tool2.py`.
2. Verify the signature format and authenticated regions with `d810_verif.py`.
3. Compare parsed records rather than raw encrypted bytes.
4. Assess whether `d8_oracle.py` can be adapted for the PowerShot V1 FIR format and model header.
5. Obtain a lawful, permissioned DIGIC X or DIGIC 10 ROM dump from an owner or researcher.
6. Prefer a ROM from the PowerShot V1 or a close relative such as the PowerShot R50 V. Treat EOS R5 or EOS R6 ROMs only as unverified research references.
7. If decryption succeeds, load `ROM0.bin` and `ROM1.bin` into Ghidra and search for tasks, event procedures, strings, and functions related to `IS`, `MovieIS`, gyro processing, lens stabilization, electronic crop, and frame transforms.

## Current stabilization hypothesis

The camera provides optical or lens stabilization plus Movie Digital IS. The visible wobble may come from the digital warp or electronic crop stage rather than from lens IS alone.

Potential firmware targets, if lawful decryption and analysis become possible:

- Gyro sampling and calibration
- Lens IS commands
- Movie Digital IS gain
- Temporal smoothing constants
- Motion-vector filtering
- Electronic crop-window movement
- Rolling-shutter compensation
- Frame transform or warp functions

A sensible research target would be a RAM-only runtime change that preserves optical IS while disabling or reducing the digital warp stage. Repacking and flashing a modified FIR is not currently viable because both packages are signed, and no Canon private signing key is available.

## `fir_tool2.py` results

Parser version reported:

```text
Fir_tool 0.6 (Oct2025)
```

### Firmware 1.1.0

```text
fileLen = 0x3dfb980

FIR header
0x000: modelId = 0x80000497
0x010: version = b'1.1.0'
0x020: checksum = 0x120f6f8f
0x024: updater1 header = 0x100
0x028: updater1 offset = 0x120
0x02c: updater2 offset = 0xffffffff
0x030: firmware offset = 0x4bfb20
0x034: updater3 offset = 0xffffffff
0x038: filesize = 0x3dfb980
0x03c: 0x0
0x040: sha1 seed = 0x0
0x044: 0x4 0x0 0x20 0x24 0x44 0x100 0x4bfa20 0x4bfb20 0x393be60

0x068: 20 38b480df72e12196240e2e211dbf85a086a0f130f373e2ccc50345d297654980
0x08c: 20 bb577b9a48df251993b22f48414d4c021009019de086af5234b9b85c27316499
0x0b0: 20 67cadf13f5bc23a52aff2ac1bd123473f71135214bd1a47fd4e51b47251693da
0x0d4: 20 cc505993c565f24006ccf68916b69dcdcc0212a1b7f0b84922314c352d5ce874

Updater 1 header
0x100: encrypted length = 0x4bfa00
0x104: 0x4bf9f8
0x108: IV = 2000000030be93030000000030be9303
0x120: updater1 ciphertext begins

Firmware header
0x4bfb20: offset to decryption data = 0x10
0x4bfb24: offset to encrypted data = 0x30
0x4bfb28: total firmware length = 0x393be60
0x4bfb30: encrypted length = 0x393be30
0x4bfb34: 0x393be28
0x4bfb38: IV = 0000000000000000bce5dcffc03c7a53
0x4bfb50: encrypted firmware begins
0x3dfb980: encrypted firmware ends
```

### Firmware 1.2.0

```text
fileLen = 0x3e06a50

FIR header
0x000: modelId = 0x80000497
0x010: version = b'1.2.0'
0x020: checksum = 0x11b3a8f1
0x024: updater1 header = 0x100
0x028: updater1 offset = 0x120
0x02c: updater2 offset = 0xffffffff
0x030: firmware offset = 0x4c3a60
0x034: updater3 offset = 0xffffffff
0x038: filesize = 0x3e06a50
0x03c: 0x0
0x040: sha1 seed = 0x0
0x044: 0x4 0x0 0x20 0x24 0x44 0x100 0x4c3960 0x4c3a60 0x3942ff0

0x068: 20 2147d8d523496d01270ff5b088fea9af971b5603b573267b73dd610ccc5aea48
0x08c: 20 32bc380c87e5627d2f35cea706dd5d4ce731fe953b1cb0f6b1995fb5d8d3b8b5
0x0b0: 20 125669b6d099a5f5bb065fe134bca1d0a024c0fc97376a2d81463f327afb59e8
0x0d4: 20 efdfc10770e6cced03a773705291ca66f6047b21010ea8f3e5a3b14f2dc8ec0e

Updater 1 header
0x100: encrypted length = 0x4c3940
0x104: 0x4c3940
0x108: IV = 20000000c02f940300000000c02f9403
0x120: updater1 ciphertext begins

Firmware header
0x4c3a60: offset to decryption data = 0x10
0x4c3a64: offset to encrypted data = 0x30
0x4c3a68: total firmware length = 0x3942ff0
0x4c3a70: encrypted length = 0x3942fc0
0x4c3a74: 0x3942fc0
0x4c3a78: IV = 0000000000000000dce284ff108c1f42
0x4c3a90: encrypted firmware begins
0x3e06a50: encrypted firmware ends
```

## Parsed comparison

| Field | 1.1.0 | 1.2.0 | Change |
|---|---:|---:|---:|
| Model ID | `0x80000497` | `0x80000497` | Same |
| File size | `0x3DFB980` | `0x3E06A50` | `+0xB0D0`, 45,264 bytes |
| Updater offset | `0x120` | `0x120` | Unchanged |
| Updater encrypted length | `0x4BFA00` | `0x4C3940` | `+0x3F40`, 16,192 bytes |
| Firmware offset | `0x4BFB20` | `0x4C3A60` | `+0x3F40`, 16,192 bytes |
| Firmware total length | `0x393BE60` | `0x3942FF0` | `+0x7190`, 29,072 bytes |
| Firmware encrypted length | `0x393BE30` | `0x3942FC0` | `+0x7190`, 29,072 bytes |
| Firmware payload header | `0x30` bytes | `0x30` bytes | Unchanged |
| Updater 2 and 3 | Absent | Absent | Unchanged |

The size arithmetic closes exactly:

```text
0x3F40 + 0x7190 = 0xB0D0
updater growth + firmware growth = total FIR growth
```

This supports the parser's interpretation of the main package boundaries.

## Authentication-record observation

The parser prints `20` before each value at offsets `0x068`, `0x08C`, `0x0B0`, and `0x0D4`, while each displayed value has 64 hexadecimal characters, or 32 bytes.

The records are spaced by `0x24`, suggesting a structure similar to:

```c
struct auth_record {
    uint32_t length;   /* likely 0x20 */
    uint8_t value[32];
};
```

These values are consistent in size with SHA-256 digests or 256-bit signature components. The parser label `sha1 seed` may be legacy terminology and should not be treated as proof that SHA-1 protects these packages.

## `d810_verif.py` results

Environment:

```text
pycryptodome 4.4.0
Python virtual environment under ./.venv
```

Both packages verified successfully with the script selecting the DIGIC 10 key.

### Firmware 1.1.0 verification

```json
{
  "model_id": 2147484823,
  "digic": 10,
  "version": "1.1.0",
  "checksum": 303001487,
  "l1": 32,
  "r1": 25648441440021737747958245982573697364005054246012126589942521428175915141504,
  "l2": 32,
  "s1": 84737071454013257539493199553625794289744508199611284070899165476982615008409,
  "l3": 32,
  "r2": 46946666138714900061213188620762342972871428325880510784108704551878014702554,
  "l4": 32,
  "s2": 92413787115494098135532023090580757522715766479344050391633455391990691457140,
  "h1": "02c16726fde3279601d904c32693b3fdd83830fdb3bb4b4517301428319e2149",
  "h2": "ca80fde1d2c992cd4478c94691b5daba2a65217cca4dfbb21792319f03485a3e",
  "v1": true,
  "v2": true
}
```

### Firmware 1.2.0 verification

```json
{
  "model_id": 2147484823,
  "digic": 10,
  "version": "1.2.0",
  "checksum": 296986865,
  "l1": 32,
  "r1": 15053266668242738798636818945651522101956713459962079341512455238346482575944,
  "l2": 32,
  "s1": 22948196512967958726893145732566475487994962028887988663837496147938167208117,
  "l3": 32,
  "r2": 8294309734114606377308617831618499947281396993616177826137332308254429764072,
  "l4": 32,
  "s2": 108498109944500726257635115875858329060367377842116606603500430985589099654158,
  "h1": "d34c6fefd1fea01e4fd32ff70a757c1be2ca9638a83c6cfc9d924af5f2b65327",
  "h2": "eddb5c76282257021c5bfe51c54222d1535bb3973198762b0862c2c622d1a48f",
  "v1": true,
  "v2": true
}
```

### Verification conclusions

- Both FIR files are recognized.
- Both use model ID `0x80000497`.
- The verifier selects DIGIC 10.
- All four signature-component lengths are 32 bytes.
- Both signatures validate for firmware 1.1.0.
- Both signatures validate for firmware 1.2.0.
- The calculated digests differ between firmware releases, as expected.
- Verification proves package authenticity and integrity under the known public key.
- Verification does not provide Canon's private signing key.
- Verification does not decrypt either payload.
- A modified FIR would still require a valid signature unless the camera's verification path were lawfully bypassed for research.

## Signed-region work still required

The current verifier reports `h1` and `h2`, but the chat has not yet established the exact byte slices used to calculate them.

The next source-inspection command is:

```bash
grep -nE 'SHA256|sha256|h1|h2|digest' d810_verif.py
grep -nE -B 12 -A 20 'h1.*=|h2.*=' d810_verif.py
```

The verifier should eventually log each authenticated range to `stderr` while leaving JSON on `stdout`, for example:

```python
print(
    f"h1_region=0x{start1:x}:0x{end1:x} "
    f"length=0x{end1 - start1:x}",
    file=sys.stderr,
)
```

Do not invent `start1`, `end1`, `start2`, or `end2`. Use the actual expressions and variables from the verifier source.

Suggested output capture:

```bash
python3 d810_verif.py "$FIR110" \
  > PSV11100-verification.json \
  2> PSV11100-regions.txt

python3 d810_verif.py "$FIR120" \
  > PSV11200-verification.json \
  2> PSV11200-regions.txt

python3 -m json.tool PSV11100-verification.json >/dev/null &&
python3 -m json.tool PSV11200-verification.json >/dev/null &&
echo "Both JSON files are valid"
```

## `d8_oracle.py` compatibility findings

The source inspection found these assumptions:

```text
Emulating cipher.bin at 0x200000
Code copied from ROM address 0xE0039000
ARM CPU model set to UC_CPU_ARM_CORTEX_A7
Updater verification marker: V&D Firmware V5
Firmware decryption is performed through code inside decrypted updater1
```

Relevant source locations observed:

```text
Line 160: cipher_bin = rom0[cipher_offset:cipher_offset+CIPHER_ROM_SIZE]
Line 167: mu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_A7)
Line 170: model and version are unpacked from FIR offset 0
Line 187: cipher code is written to CIPHER_ADDRESS
Line 234: decrypted updater is checked for b'V&D Firmware V5'
Line 262: firmware header fields are unpacked
Line 267: decryption seed2 is written to R3
Line 271 onward: firmware ciphertext is mapped and decrypted
```

The attempted commands were:

```bash
python3 ./d8_oracle.py -s "$FIR110"
python3 ./d8_oracle.py -s "$FIR120"
```

Both stopped with:

```text
default ROM is missing
```

The source also emitted a `SyntaxWarning` because an example path in its docstring used `fir\EOSRP160.FIR` without a raw string.

### Oracle conclusion

`d8_oracle.py` requires a ROM even for the attempted signature mode. More importantly, the current oracle contains fixed architectural assumptions that have not been verified for the PowerShot V1 or DIGIC 10:

- Fixed ROM cipher address `0xE0039000`
- Fixed emulation address `0x200000`
- ARM Cortex-A7 Unicorn model
- Existing memory map and aliases
- Existing code pattern for locating updater decryption
- `V&D Firmware V5` marker
- Existing register ABI and seed locations

Adding only model ID `0x80000497` would not prove compatibility. Running code from an unverified ROM address could produce misleading output or an emulator fault.

## ROM requirements

A lawful, permissioned ROM dump is still required. Record the following with any supplied dump:

- Exact camera model
- Firmware version
- Dump method
- Owner or research permission
- File names
- File sizes
- SHA-256 hashes
- Expected ROM base address

Preferred order:

1. PowerShot V1
2. PowerShot R50 V, if its architecture is confirmed sufficiently close
3. EOS R5 or EOS R6 only as exploratory references

Before adapting the oracle, establish:

```text
ROM base address
ROM0 size and SHA-256
CPU architecture and appropriate Unicorn CPU model
cipher routine location and size
load address and aliases
required ROM data tables
updater load address
updater decrypt-call pattern
firmware decrypt function ABI
expected decrypted updater marker
```

## Suggested safe code changes

### Add explicit model recognition

Where the verifier or parser maps model IDs:

```python
0x80000497: 10,  # Canon PowerShot V1
```

Use the repository's existing table structure rather than forcing this exact value shape.

### Add bounds checking around ROM cipher extraction

The current logic should validate that `CIPHER_ROM_ADDR - base_addr` is non-negative and that the requested region fits inside the supplied ROM before slicing it.

### Add a compatibility guard

Until the CPU, ROM map, cipher address, and updater format are confirmed, the oracle should stop before emulation for DIGIC 10 rather than silently applying known DIGIC 8 assumptions.

### Keep original files unchanged

Create separate working copies such as:

```text
d810_verif-psv1.py
d8_oracle-psv1.py
```

Keep hash records for original and modified scripts.

## Useful commands

### Set firmware paths

```bash
FIR110=$(find ~/Downloads/psv1-v110-win -type f -iname 'PSV11100.FIR' -print -quit)
FIR120=$(find ~/Downloads/psv1-v120-win -type f -iname 'PSV11200.FIR' -print -quit)
printf '%s\n%s\n' "$FIR110" "$FIR120"
```

### Parse both FIR files

```bash
cd ~/Downloads/d8_oracle-main
python3 ml_scripts/fir_tool2.py "$FIR110"
python3 ml_scripts/fir_tool2.py "$FIR120"
```

### Verify both FIR files

```bash
python3 d810_verif.py "$FIR110"
python3 d810_verif.py "$FIR120"
```

### Record firmware hashes before further work

```bash
shasum -a 256 "$FIR110" "$FIR120" | tee PSV1-firmware-sha256.txt
shasum -a 1 "$FIR110" "$FIR120" | tee PSV1-firmware-sha1.txt
```

SHA-1 is included only as an additional file identifier. SHA-256 should be the primary integrity record.

### Extract encrypted updater payloads

```bash
dd if="$FIR110" of=PSV11100-updater.enc bs=1 \
  skip=$((0x120)) count=$((0x4BFA00))

dd if="$FIR120" of=PSV11200-updater.enc bs=1 \
  skip=$((0x120)) count=$((0x4C3940))
```

### Extract encrypted firmware payloads

```bash
dd if="$FIR110" of=PSV11100-firmware.enc bs=1 \
  skip=$((0x4BFB50)) count=$((0x393BE30))

dd if="$FIR120" of=PSV11200-firmware.enc bs=1 \
  skip=$((0x4C3A90)) count=$((0x3942FC0))
```

### Inspect oracle arguments and constants

```bash
python3 d8_oracle.py --help
sed -n '1,320p' d8_oracle.py

grep -nE \
'ArgumentParser|add_argument|ROM_BASE|CIPHER_ROM|CIPHER_ADDRESS|FIR_ADDRESS|EMU_|UC_CPU|code_pattern|V&D' \
d8_oracle.py
```

## Safety and research boundaries

- Do not flash a modified FIR based only on successful parsing or decryption.
- Keep the original FIR packages unchanged.
- Work on copies and record SHA-256 hashes.
- Treat a successful decrypt as an analysis milestone, not proof that a repacked image is safe or installable.
- Do not assume a ROM from another Canon model has compatible addresses, keys, tables, or calling conventions.
- Use only ROM dumps that were lawfully obtained and shared with permission.
- Prefer RAM-only experiments or emulation over persistent flash modification.
- Keep recovery options and hardware risk in mind. An invalid signed package may be rejected, while a deeper boot or flash modification can brick the camera.

## Current status

| Work item | Status |
|---|---|
| Obtain FIR 1.1.0 and 1.2.0 | Complete |
| Parse both FIR headers | Complete |
| Compare parsed package records | Complete |
| Identify model ID | Complete: `0x80000497` |
| Identify verifier generation | Complete: DIGIC 10 |
| Verify signature 1 on both files | Complete, valid |
| Verify signature 2 on both files | Complete, valid |
| Map exact signed byte ranges | Pending source instrumentation |
| Decrypt updater1 | Blocked by compatible ROM and verified oracle assumptions |
| Decrypt firmware payload | Blocked by updater decryption and compatible ROM |
| Obtain lawful PowerShot V1 ROM | Pending |
| Ghidra analysis | Pending successful extraction or dump |
| Locate stabilization functions | Pending Ghidra analysis |
| Produce modified FIR | Not attempted and not presently feasible due to signing |
| Flash camera | Not attempted |

## Immediate next steps

1. Inspect the exact `h1` and `h2` calculations in `d810_verif.py`.
2. Add signed-region reporting to `stderr` without changing verification behavior.
3. Save JSON verification results and region maps for both versions.
4. Hash the FIR files and all scripts used.
5. Obtain a lawful PowerShot V1 ROM dump, with model and firmware metadata.
6. Determine the PowerShot V1 ROM base, CPU model, cipher-code location, and updater marker before enabling `d8_oracle.py` emulation.
7. If decryption succeeds, verify plaintext using expected headers, markers, internal checksums, and repeatable hashes before importing it into Ghidra.
8. In Ghidra, search first for `IS`, `MovieIS`, `gyro`, lens-control tasks, crop-window logic, frame transforms, and event procedures.

## Files and links mentioned

Source files (`PSV11100.FIR`, `PSV11200.FIR`, `d8_oracle-main.zip`) were provided during the chat via corporate SharePoint links, now redacted. They required corporate authentication and could not be downloaded in the analysis environment.
## Bottom line

The PowerShot V1 FIR format is parseable with the available tooling, and both official packages contain two valid signatures verified with the DIGIC 10 public key. The updater and firmware payloads remain encrypted. The existing `d8_oracle.py` cannot yet be treated as PowerShot V1 compatible because it depends on a ROM and contains fixed DIGIC 8-era architectural assumptions. The next defensible step is to document exact signed regions and obtain a lawful PowerShot V1 ROM dump before attempting oracle adaptation or Ghidra analysis.
