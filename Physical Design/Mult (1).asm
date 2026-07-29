// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

    @5
    D=A
    @R1
    M=D
    @6
    D=A
    @R0
    M=D

(INIT)
    @R2
    M=0

    @R0
    D=M
    @ZERO
    D;JEQ

    @R1
    D=M
    @ZERO
    D;JEQ

(MULT)
    @R0
    D=M
    @R2
    M=D+M
    @R1
    M=M-1
    D=M
    @ZERO
    D;JEQ
    @MULT
    D;JNE

(ZERO)
    // Move the final product from RAM[2] to the D register
    @R2
    D=M

(END)
    // Infinite loop to safely terminate execution
    @END
    0;JMP
