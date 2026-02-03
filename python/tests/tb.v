/*
    This is a simple Verilog testbench for the basic module.
*/

module tb;

    reg clk;
    reg [7:0] cycle;
    initial begin
        clk = 1;
        cycle = 0;
    end

    always #1 clk = ~clk;
    always @(posedge clk) begin
        cycle = cycle + 1;
    end

    // Run for 30 clock cycles
    initial begin
        #30 $finish;
    end

    initial begin
        $dumpfile("basic.vcd");
        $dumpvars(0, tb);
    end
endmodule