# psp-converter (upf to psp8)
A python script for converting pseudopotentials from upf to psp8. For more information about the upf and psp8 formats see
[1](http://pseudopotentials.quantum-espresso.org/home/unified-pseudopotential-format), [2](https://esl.cecam.org/data/upf/), and [3](https://docs.abinit.org/developers/psp8_info/).


### Usage
Download `to_psp8.py` into your working directory, and run
```
python to_psp8.py path/to/psp.upf
```
To convert multiple files, e.g. 3
```
python to_psp8.py path/to/psp1.upf path/to/psp2.upf path/to/psp3.upf
```
In a python script
```
import to_psp8
to_psp8.convert(path/to/psp.upf)
```
The converted output files are generated in the same directory as the corresponding input files and have the same names but psp8 file extension.

### Requirements
 - python 3.6 or higher
 - numpy

### Limitation
The current code does not support pseudopotentials with nonlinear core correction. This will be added.
