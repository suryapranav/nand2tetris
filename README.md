# nand2tetris
The following is my attempt at creating a rudimentary 16-bit single-cycle processor. This follows the textbook "The Elements of Computing Systems: Building a Modern Computer from First Principles."

You can demo the computer using the [Computer](Physical%20Design/Computer.dig) file on [Digital](https://github.com/hneemann/Digital).

If you have a hack `.asm` file, use [this python script](Physical%20Design/generator.py) to convert it to an Intel Hex file which can be stored in the ROM modules to simulate program execution.

The computer is built up from first principles. In the physical simulation, ICs are only used for rudimentary gates and storage elements (RAM modules for memory, and EEPROMs for the instructions). All other components are built up from scratch.
