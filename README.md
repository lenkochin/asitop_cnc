# asitop_cnc

Forked version of `asitop`. The suffix 'cnc' stands for Core Name Compatible.

![](images/asitop.png)

---

## What is different from the original version?

### Core Name Compatibility
Apple changed the cores in M5 Pro/Max chips to P cores and S cores, instead of E cores and P cores.
The original asitop cannot parse this layout, so this version adds compatibility for it.

### Optimized Disk Writes
The original workflow of writing plist data first and then reading it back for parsing has been changed, so long-running sessions no longer consume disk writes.

### Modified Core Usage Calculation Logic
Calculates the average active ratio of cores instead of the cluster ratio.
