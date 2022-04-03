# psp-converter (upf to psp8)
This repository provides a python script for converting pseudopotentials from upf to psp8. For more information about the upf and psp8 format see
[1](http://pseudopotentials.quantum-espresso.org/home/unified-pseudopotential-format), [2](https://esl.cecam.org/data/upf/), and [3](https://docs.abinit.org/developers/psp8_info/).

### Installation:
Use the following command to simply download `to_psp8.py` into your working directory
```
wget https://raw.githubusercontent.com/mostafa-sh/psp-converter/main/to_psp8.py
```

### Usage:
Run the code in terminal by
```
python to_psp8.py psp.upf

```
where `psp.upf` is the path to the pseudopotential file in upf format. For multiple files (let's say 3), use
```
python to_psp8.py psp1.upf psp2.upf psp3.upf
```
To use in a python script, include
```
import to_psp8
to_psp8.convert(psp.upf)
```
The converted output files are generated in the same directory as the corresponding input files and have the same name but psp8 file extension. 

### Requirements:
 - python 3.6 or higher
 - numpy

### Limitation:
The current code does not support pseudopotentials with nonlinear core correction. This will be added.
 
