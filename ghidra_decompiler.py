# export_decompiled_all.py
# Jython script for Ghidra to export decompiled C for all functions to a single file.
# Usage: run from Script Manager while program is open.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.symbol import SourceType
from java.io import FileWriter, BufferedWriter, PrintWriter

# Ask user for an output path
output_path = askString("Output file", "Path to save full decompiled output (absolute path):")

if not output_path:
    popup("No output path provided; exiting.")
    exit()

decomp = DecompInterface()
monitor = ConsoleTaskMonitor()
if not decomp.openProgram(currentProgram):
    popup("Failed to open decompiler for program: " + str(currentProgram))
    exit()

try:
    pw = PrintWriter(BufferedWriter(FileWriter(output_path)))
    pw.println("/* Decompiled output for: %s */\n" % currentProgram.getName())
    funcManager = currentProgram.getFunctionManager()
    functions = list(funcManager.getFunctions(True))
    total = len(functions)
    count = 0

    for f in functions:
        count += 1
        monitor.setMessage("Decompiling %d/%d : %s" % (count, total, f.getName()))
        res = decomp.decompileFunction(f, 60, monitor)  # 60 sec timeout
        pw.println("/* ------------------------------------------------------------ */")
        pw.println("/* Function %d/%d : %s @ %s */" % (count, total, f.getName(), f.getEntryPoint()))
        if res.decompiledFunction is None:
            pw.println("/* FAILED to decompile function: %s */\n" % f.getName())
            # fallback: print the listing / prototype
            try:
                pw.println("/* Prototype: %s */\n" % f.getSignature())
            except:
                pass
        else:
            # write the decompiled C
            ccode = res.getDecompiledFunction().getC()
            pw.println(ccode)
        pw.println("\n")
    pw.flush()
    popup("Decompiled output saved to:\n" + output_path)
finally:
    try:
        pw.close()
    except:
        pass
    decomp.dispose()
