SURF
Spectroscopy User and Research Framework: open-source Python software to operate and automate cavity (Fabry-Perot) Fourier-transform microwave (FTMW) spectroscopy.

SURF is research software developed in the Gurusinghe Research Lab (GruLab) at Tennessee Tech University. It controls the cavity subsystem of the lab's L-shaped FTMW spectrometer. A companion manuscript describing SURF is in preparation for the Journal of Molecular Spectroscopy.

<img width="1275" height="510" alt="SURF Graphical abstract" src="https://github.com/user-attachments/assets/fb08b762-6374-4c18-8e0f-7ecfbaa885bb" />

Overview
SURF is a graphical framework that drives a resonant-cavity FTMW spectrometer end to end. It coordinates the microwave source, the tunable Fabry-Perot cavity, waveform generation, signal digitization, and gated detection, then displays and stores the resulting free-induction decays (FIDs) and spectra. The interface is built for day-to-day experimental work, such as locating cavity modes, running automated frequency surveys, and inspecting spectra, while a modular back end keeps the code adaptable to other cavity FTMW instruments.

The architecture separates three concerns: device communication (one controller module per instrument), instrument coordination (a spectrometer layer that sequences the devices), and experimental execution (the GUI panels that run cavity maps, scans, and analysis). Because each instrument is isolated behind its own controller, adapting SURF to a different synthesizer, actuator, or digitizer usually means editing a single module rather than the whole application.

Features
Automated cavity mode mapping, for both continuous and pulsed detection schemes
Automated frequency scanning with automatic cavity retuning at each point
Manual, panel-based control of every instrument
Live plotting of FIDs and spectra
Spectral analysis of saved data, and CSV export
Human-readable TOML configuration with restorable defaults; light and dark themes
Supported hardware

<img width="975" height="642" alt="Fig 1" src="https://github.com/user-attachments/assets/a1677d4d-ba87-443e-8709-5b87e6571851" />
<img width="976" height="798" alt="Fig 2" src="https://github.com/user-attachments/assets/23593693-4311-41b7-b030-8f34491378db" />
<img width="1436" height="776" alt="Fig 3" src="https://github.com/user-attachments/assets/142cdbed-6bd4-4a94-8e99-3e9a92cc6081" />
<img width="1133" height="722" alt="Fig 4" src="https://github.com/user-attachments/assets/829843c5-d2dd-4f11-9e86-208346ae3f9b" />
<img width="975" height="528" alt="Fig 5" src="https://github.com/user-attachments/assets/077a182b-2f23-417c-8f4d-3b79f39cf9d3" />

SURF talks to each instrument through a dedicated controller module, using VISA, serial, the Zaber Motion library, and .NET drivers as appropriate:

Microwave synthesizer (Valon): cavity excitation and LO source
Linear actuator (Zaber): Fabry-Perot cavity tuning
Arbitrary waveform generator: pulse and waveform generation
Oscilloscope: FID digitization and averaging
Digital delay/pulse generator: experiment timing
RF switch: signal routing

The instrument these modules were written for is described in Design and performance of an L-shaped Fourier transform microwave spectrometer (L-FTMW): Fabry-Perot cavity spectrometer setup, Rev. Sci. Instrum. 97, 024704 (2026), doi:10.1063/5.0311736.

Installation

Running

Documentation
See the docs folder for development setup and help. More about the lab: https://sites.tntech.edu/grulab/

Citing SURF

Contributing
Contributions, bug reports, and feature requests are welcome via GitHub Issues and Pull Requests.

License
A license for SURF is being finalized.
