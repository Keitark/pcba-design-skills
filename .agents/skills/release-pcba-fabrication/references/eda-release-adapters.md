# EDA release adapters

Use the authoritative EDA's native output job or CLI. Record tool/version,
source revision, origin, units, side/rotation convention, layer mapping, and
every command or job configuration needed to reproduce the release.

- **KiCad:** native Gerber/drill/position/BOM/STEP/PDF exports; pair board and
  project files because rules and stackup may live outside the board.
- **Altium:** controlled OutputJob for Gerber/ODB++/IPC-2581, NC drill, BOM,
  pick-and-place, assembly drawing, and 3D evidence.
- **EasyEDA Standard/Pro:** use the matching edition's fabrication and assembly
  export; verify origins and rotations independently.
- **EAGLE/Fusion:** use CAM processor/manufacturing outputs plus native BOM/CPL;
  preserve the exact CAM configuration.
- **ODB++/IPC-2581:** may replace several loose files when the manufacturer
  accepts them, but still include BOM/assembly and a manifest of the delivered
  package.

If only derived fabrication files exist, audit and package them but mark native
source traceability BLOCKED or USER_REVIEW. Never reconstruct a release revision
from filenames alone.
