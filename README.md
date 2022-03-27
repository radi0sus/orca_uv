# orca-uv
A Python 3 script for (hassle-free) plotting of absorption spectra from [ORCA](https://orcaforum.kofo.mpg.de) 
output files with peak dectection and annotation.
It combines the stick spectrum with the convoluted spectrum (gaussian line shape).
The script supports energy (wave number, cm<sup>-1</sup>) and wavelength (λ, nm) plots.
The full spectrum or parts of the spectrum can be plotted.

## External modules
 `re` 
 `numpy` 
 `matplotlib`
 `scipy`  
 
## Quick start
 Start the script with:
```console
python3 orca-uv.py filename
```
it will save the plot as PNG bitmap:
`filename-abs.png`

## Command-line options
- `filename` , required: filename
- `-s` , optional: shows the `matplotlib` window
- `-n` , optional: do not save the spectrum
- `-e` , optional: export the line spectrum in a csv-like fashion; filename of the export is input filename + "-mod.dat"
- `-pwn` , optional: plot the wave numer (energy, cm<sup>-1</sup>) spectrum
- `-wnm` `N` , optional: line width of the gaussian for the nm scale (default is `N = 20`)
- `-wwn` `N` , optional: line width of the gaussian for the cm<sup>-1</sup> scale (default is `N = 1000`)
- `-x0`  `N` , optional: start spectrum at N nm or N cm<sup>-1</sup> (`x0 => 0`)
- `-x1`  `N` , optional: end spectrum at N nm or N cm<sup>-1</sup> (`x1 => 0`)

## Script options
There are numerous ways to configure the spectrum in the script:
Check `# plot config section - configure here` in the script. 
You can even configure the script to plot of the single gaussian functions.

The delimiter for the line spectrum export can be changed by changing the value of `export_delim =`.

## Code options
Colors, line thickness, line styles, level of peak detection and 
more can be changed in the code directly.

## Remarks
The PNG file will be replaced everytime you start the script with the same output file. 
If you want to keep the file, you have to rename it. 
The data are taken from the section "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS".

## Examples:
![show](/examples/show-use3.gif)
![Example 1](/examples/example1.png)
![Example 2](/examples/example2.png)
![Example 3](/examples/example3.png)
