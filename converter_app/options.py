DATA_TYPES = (
    'AIF', # Must be extened
    'CIRCULAR DICHROISM SPECTROSCOPY',
    'CONTINUOUS MASS SPECTRUM',
    'CYCLIC VOLTAMMETRY',
    'DLS ACF',
    'DLS intensity',
    'Emissions', ## to be checked
    'GEL PERMEATION CHROMATOGRAPHY',
    'HPLC UV-VIS',
    'INFRARED INTERFEROGRAM',
    'INFRARED PEAK TABLE',
    'INFRARED SPECTRUM',
    'INFRARED TRANSFERED SPECTRUM',
    'MASS SPECTRUM',
    'NMP PEAK ASSIGNMENTS',
    'NMR FID',
    'NMR PEAK TABLE',
    'NMR SPECTRUM',
    'RAMAN SPECTRUM',
    'SINGLE CRYSTAL X-RAY DIFFRACTION',
    'SIZE EXCLUSION CHROMATOGRAPHY',
    'SORPTION-DESORPTION MEASUREMENT',
    'TENSIOMETRY',
    'THERMOGRAVIMETRIC ANALYSIS',
    'UV-VIS',
    'X-RAY DIFFRACTION',
)

DATA_CLASSES = (
    'XYPOINTS',
    'XYDATA',
    'PEAK TABLE',
    'NTUPLES',
)

XUNITS = (
    '%',
    '1/CM',
    '2Theta',
    'DEGREES CELSIUS',
    'G/MOL',
    'HZ',
    'KILOGRAM',
    'kPa',
    'Lag time (microseconds)',
    'm/z',
    'MICROMETERS',
    'MILIMETERS',
    'MILLILITERS',
    'MINUTES',
    'MOLECULAR MASS / DA',
    'NANOMETERS',
    'p/p0', # Normalaized dimension
    'SECONDS',
    'Voltage vs Ref',
    'wavelength (nm)',
)

YUNITS = (
    'ABSORBANCE',
    'ACF (a.u.)',
    'Ampere',
    'ARBITRARY UNITS',
    'COUNTS',
    'DERIVATIVE WEIGHT',
    'ellipticity (deg cm2/dmol)',
    'Intensity',
    'KUBELKA-MUNK',
    'mAU',
    'ml/g',
    'mmol/g',
    'Molar Extinction (cm2/mmol) ',
    'Newton',
    'N/M2',
    'REFLECTANCE',
    'relative intensity (%)',
    'SIGNAL',
    'TRANSMITTANCE',
    'WEIGHT',
)

OPTIONS = {
    'DATA TYPE': DATA_TYPES,
    'DATA CLASS': DATA_CLASSES,
    'XUNITS': XUNITS,
    'YUNITS': YUNITS,
}
