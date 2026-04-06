# GDB OCD-interface

Tool for managing on-chip debugger interfaces/servers from within GDB


Normally, when developing for embedded devices, like ARM Cortex-M
microcontrollers, it is required for setting up a debugging session to:

- Start two terminals
- In terminal 1 - start ocd interface, for example `openocd`
- In terminal 2 - start gdb instance, for example `gdb-multiarch`
- In terminal 2 - Connect to openocd, using `target remote localhost:1234`, or
  variant thereof

Then on every reset, it may be required to reconnect to the OCD instance

This makes a lot of overhead for each update and reprogramming.

This tool manages the OCD sessions as subprocesses from within `gdb` itself,
and also has convenience macros for rebuilding and reprogramming automatically.


## Install

Install `gdb-ocdif`, so it's available from gdb environment.

### Install from pypi:
```sh
pip install --user gdb-ocdif
```
Make sure the install path, usually `~/.local` is available for python search
path

### Install from git:
pick a directory to clone this repo from
```sh
git clone https://github.com/pengi/gdb_ocdif.git /path/to/where/to/put/gdb_ocdif
```

In your normal environment, or before starting gdb, update `PYTHONPATH`
environment variable

Run, or add to `~/.bashrc`, `~/.zshrc` or similar:
```sh
export PYTHONPATH=/path/to/where/to/put/gdb_ocdif:$PYTHONPATH
```

### Configure gdb

It is recommended to autoload gdb_ocdif into gdb on each startup, and also add
default configuration and aliases

Add following to `~/.gdbinit`, and update to your liking.

None of the lines below will affect the target, but only setup the enviornment
```ini

# Load gdb_ocdif
python import gdb_ocdif

# Define available probes
#
# `ocdif openocd` - command to register an openocd probe
# `nrf1`          - defines the name of the probe within gdb_ocdif
# `jlink`         - the interface to use in openocd.
#                   Loads the interface file interface/jlink.cfg
# `nrf52`         - the target to use in openocd.
#                   Loads the interface file target/nrf52.cfg
# `123456789`     - Serial number of the probe, to identify multiple. Optional.
# `swd`           - Transport to use, `swd` or `jtag`, defaults to `swd`
#
# can be followed by an integer defining debug_level for openocd, defaults to 1
#
# Note that this does not actually connect to the probes. To connect, use
#  - `ocdif connect nrf1`
# or:
#  - `ocdif select nrf1`
#  - `ocdif connect`
ocdif openocd nrf1 jlink nrf52 123456789 swd
ocdif openocd nrf2 jlink nrf52 123456790 swd

# To make connection to the probe more convenient, it is trecommended to add
# aliases to select the current probe
alias nrf1    = ocdif select nrf1
alias nrf2    = ocdif select nrf2

# Two convenience commands are recommended to make more accessible:
#  - ocdif reset  - Reset the target to a halted state, using the command
#                   specified by the probe implementation. For example
#                   `monitor reset halt`
#  - ocdif reload - Reconnects to target, builds application with make, loads
#                   and resets target
alias reload  = ocdif reload
alias res     = ocdif reset
```

## Usage

When configured as above, recompiling and reloading can be done within gdb:

### Selection and connecting

To use gdb_ocdif only to manage OCD connections, but don't invoke make, it is
possible to use, given configuration above:
 - `(gdb) nrf1`
 - `(gdb) ocdif connect`

(Output is cut down for clarity)

```sh
$ gdb-multiarch myapp.elf
GNU gdb (Ubuntu 15.1-1ubuntu1~24.04.1) 15.1


Reading symbols from myapp.elf...
(gdb) nrf1
(gdb) ocdif connect 
Reset_Handler () at vendor/nrf/nrfx/bsp/stable/mdk/gcc_startup_nrf52840.S:231
231	    ldr r1, =__data_start
openocd   Calling:
openocd      openocd
openocd      -c 'debug_level 1'
openocd      -c 'source [find interface/jlink.cfg]'
openocd      -c 'transport select swd'
openocd      -c 'source [find target/nrf52.cfg]'
openocd      -c 'gdb_port 15618'
openocd      -c 'tcl_port disabled'
openocd      -c 'telnet_port disabled'
openocd      -c '$_TARGETNAME configure -rtos auto'
openocd      -c 'echo "session started"'
openocd      -c 'adapter serial 683479168'
openocd > Open On-Chip Debugger 0.12.0
openocd > Licensed under GNU GPL v2
openocd > For bug reports, read
openocd > 	http://openocd.org/doc/doxygen/bugs.html
openocd > debug_level: 1
openocd > 
openocd > swd
openocd # session started
openocd > undefined debug reason 8 - target needs reset
(nrf1 gdb) 
```

Resuling in `openocd` started in background, and gdb is connected.

Port number is randomized, to manage multiple debugging instances in paralell
to different boards.


### reload - automatic rebuilds and reprogramming

It is also, and recommended, to use ocdif to trigger rebuilds and reloads. This
makes it possible to keep breakpoints and state between rebuilds.

This requires the target (in this case `myapp.elf`) to be build using `make` as:
`make myapp.elf`

If that is possible (which is recommeneded), it is possible to:

 - select target - `(gdb) ocdif select nrf1`
 - rebuild, reload and reset - `(gdb) ocdif reload`

`(gdb) ocdif reload` can then be repeated on code change.

...or use the aliases defined in `.gdbinit`:
 - `(gdb) nrf1`
 - `(gdb) reload`

for example:

```sh
$ gdb-multiarch myapp.elf 
GNU gdb (Ubuntu 15.1-1ubuntu1~24.04.1) 15.1

[...]

Reading symbols from myapp.elf...


(gdb) nrf1


(gdb) reload
make   Calling:
make      make
make      -j32 myapp.elf
make > 
make >   ... proper make output cut out from example output ...
make >   LINK     myapp.elf
make > 
make   Process 'make' exited with code 0
Reset_Handler () at vendor/nrf/nrfx/bsp/stable/mdk/gcc_startup_nrf52840.S:231
231	    ldr r1, =__data_start
[nrf52.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x00003e48 msp: 0x20004008
Loading section .vectors, size 0x200 lma 0x0
Loading section .rodata, size 0x118 lma 0x200
Loading section .ARM.exidx, size 0x8 lma 0x318
Loading section .text, size 0x4690 lma 0x320
Loading section .copy.table, size 0x30 lma 0x49b0
Loading section .zero.table, size 0x18 lma 0x49e0
Loading section .data, size 0x8 lma 0x49f8
Start address 0x00003e48, load size 18944
Transfer rate: 9 KB/sec, 2368 bytes/write.
[nrf52.cpu] halted due to debug-request, current mode: Thread 
xPSR: 0x01000000 pc: 0x00003e48 msp: 0x20004008
make   closed
openocd   Calling:
openocd      openocd
openocd      -c 'debug_level 1'
openocd      -c 'source [find interface/jlink.cfg]'
openocd      -c 'transport select swd'
openocd      -c 'source [find target/nrf52.cfg]'
openocd      -c 'gdb_port 11047'
openocd      -c 'tcl_port disabled'
openocd      -c 'telnet_port disabled'
openocd      -c '$_TARGETNAME configure -rtos auto'
openocd      -c 'echo "session started"'
openocd      -c 'adapter serial 123456789'
openocd > Open On-Chip Debugger 0.12.0
openocd > Licensed under GNU GPL v2
openocd > For bug reports, read
openocd > 	http://openocd.org/doc/doxygen/bugs.html
openocd > debug_level: 1
openocd > 
openocd > swd
openocd # session started
openocd > undefined debug reason 8 - target needs reset
openocd > [nrf52.cpu] halted due to debug-request, current mode: Thread
openocd > xPSR: 0x01000000 pc: 0x00003e48 msp: 0x20004008
openocd > [nrf52.cpu] halted due to debug-request, current mode: Thread
openocd > xPSR: 0x01000000 pc: 0x00003e48 msp: 0x20004008
openocd > [nrf52.cpu] halted due to debug-request, current mode: Thread
openocd > xPSR: 0x01000000 pc: 0x00003e48 msp: 0x20004008
openocd > [nrf52.cpu] halted due to debug-request, current mode: Thread
(nrf1 gdb) continue
...
```

When connected, current probe name is shown in the prompt
