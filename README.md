# 👩‍💻 Toehold Switch Creator 🧬
[![Anaconda-Server Badge](https://anaconda.org/bioconda/primedrpa/badges/license.svg)]() [![GitHub version](https://badge.fury.io/gh/Naereen%2FStrapDown.js.svg)](https://github.com/iGEM-Tec-Monterrey/ToeholdSwitchCreator)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/iGEM-Tec-Monterrey/ToeholdSwitchCreator)

-----
## 💡 Tabla de contenido
- [👩‍💻 Toehold Switch Creator](#-toehold-switch-creator)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Key input files](#key-input-files)
  - [Key output files](#key-output-files)
  - [Software dependencies](#software-dependencies)
  - [Authors](#authors)
  - [Contact us](#-contact-us-on-social-media)
------
## Overview
🐍 **Toehold Switch Creator** is an open source software based on python for the in silico design of the riboswitches called “Toehold switches”, we aimed to made an straightforward software in response to the dispersion of the bioinformatic tools used generally for designing these  constructs, we originally made TSC for the development of our **iGEM project: Diagnosgene** a phytopathogenic detection system based on these biosensors.
 
## Installation
After forking this repository you will need to perform the installation of the software dependencies, these installations are made with Anaconda, for a detailed explanation on the step-by-step installation for your specific OS visit our wiki information.

[🍎 MacOS]()

[🐧 Linux / 🌊 Windows]()


## Key input files

It is required 3 input files for the software to work: the first is a parameters file, containing the data PrimedRPA needs to compute to generate the RPA primers, secondly we require a FASTA file which is of  crucial importance and contains the sequence to be detected and used by the program to compute the toehold switches as well as the primers, thirdly and lastly we need the energetic range wich will be used to calculate the suboptimal structures of the RNA toehold switches. On this repository you will find a template for the PrimedRPA parameters files as well as examples of each of these documents embedded within the [Validations](https://github.com/iGEM-Tec-Monterrey/ToeholdSwitchCreator/tree/main/Applied%20Cases) section, section, an example of the files could be as follows:

```bash
Tequilena_PrimedRPA_Parameters.txt
atequilena-sst1.fasta
```
## Key output files
After computing the output file is an easy to employ .csv file that contains the toehold sequences generated for each primer pair, the sequences of the toeholds are arranged in score order, being the first structures the best switches assembled, however it is strongly recommended to employ a secondary structure visualization tool such as a NUPACK for a better understanding of the RNA structures, it is also recommended to select the structures with less suboptimal structures for being employed on the experimental validation.

<img src="https://github.com/DonOrtiz/Bio_course/blob/main/excel.png" alt="excel_image" width="650" height="300">



## Software dependencies
The RPA primers are generated with [PrimedRPA](https://github.com/MatthewHiggins2017/bioconda-PrimedRPA) developed by Mathew Higgings, also the thermodynamic calculations employ [ViennaRNA](https://github.com/ViennaRNA/ViennaRNA) developed by Lorenz et al, the downloading of these dependencies are well described on the step by step guide provided on the Installation section.



## Authors

This software was developed by [Emiliano González Castañón](https://github.com/emilianocastanon), [Juan Antonio Alfaro Almaguer](https://github.com/Juan-500Antonio) and [Emilio Fabian Ortiz](https://github.com/DonOrtiz).


## 📫 Contact us on Social Media

[Facebook](https://www.facebook.com/iGEMTec) | [Instagram](https://www.instagram.com/igemtecmty/) | [Twitter](https://twitter.com/igemtecmty) | Feel Free to 💬 [Contact Us](igemtecmonterrey@gmail.com) about Anything!


<img src="https://media.giphy.com/media/LnQjpWaON8nhr21vNW/giphy.gif" width="60"> <em><b>We love connecting with different people</b> so if you want to say <b>hi, We'll be happy to meet you more!</b> :)</em>
