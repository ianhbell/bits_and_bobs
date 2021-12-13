import graphene
import pandas, io

import typing 

df = pandas.read_csv(io.StringIO("""number symbol name mass
1    H    Hydrogen    1.00797
2    He    Helium    4.00260
3    Li    Lithium    6.941
4    Be    Beryllium    9.01218
5    B    Boron    10.81
6    C    Carbon    12.011
7    N    Nitrogen    14.0067
8    O    Oxygen    15.9994
9    F    Fluorine    18.998403
10    Ne    Neon    20.179
11    Na    Sodium    22.98977
12    Mg    Magnesium    24.305
13    Al    Aluminum    26.98154
14    Si    Silicon    28.0855
15    P    Phosphorus    30.97376
16    S    Sulfur    32.06
17    Cl    Chlorine    35.453
19    K    Potassium    39.0983
18    Ar    Argon    39.948
20    Ca    Calcium    40.08
21    Sc    Scandium    44.9559
22    Ti    Titanium    47.90
23    V    Vanadium    50.9415
24    Cr    Chromium    51.996
25    Mn    Manganese    54.9380
26    Fe    Iron    55.847
28    Ni    Nickel    58.70
27    Co    Cobalt    58.9332
29    Cu    Copper    63.546
30    Zn    Zinc    65.38
31    Ga    Gallium    69.72
32    Ge    Germanium    72.59
33    As    Arsenic    74.9216
34    Se    Selenium    78.96
35    Br    Bromine    79.904
36    Kr    Krypton    83.80
37    Rb    Rubidium    85.4678
38    Sr    Strontium    87.62
39    Y    Yttrium    88.9059
40    Zr    Zirconium    91.22
41    Nb    Niobium    92.9064
42    Mo    Molybdenum    95.94
43    Tc    Technetium    98
44    Ru    Ruthenium    101.07
45    Rh    Rhodium    102.9055
46    Pd    Palladium    106.4
47    Ag    Silver    107.868
48    Cd    Cadmium    112.41
49    In    Indium    114.82
50    Sn    Tin    118.69
51    Sb    Antimony    121.75
53    I    Iodine    126.9045
52    Te    Tellurium    127.60
54    Xe    Xenon    131.30
55    Cs    Cesium    132.9054
56    Ba    Barium    137.33
57    La    Lanthanum    138.9055
58    Ce    Cerium    140.12
59    Pr    Praseodymium    140.9077
60    Nd    Neodymium    144.24
61    Pm    Promethium    145
62    Sm    Samarium    150.4
63    Eu    Europium    151.96
64    Gd    Gadolinium    157.25
65    Tb    Terbium    158.9254
66    Dy    Dysprosium    162.50
67    Ho    Holmium    164.9304
68    Er    Erbium    167.26
69    Tm    Thulium    168.9342
70    Yb    Ytterbium    173.04
71    Lu    Lutetium    174.967
72    Hf    Hafnium    178.49
73    Ta    Tantalum    180.9479
74    W    Tungsten    183.85"""
), sep=r'\s+', engine='python', index_col='symbol')

# Build the enumeration of symbols (conveniently all atom symbols are valid Python variable names)
AtomEnum = graphene.Enum('AtomEnum', [(symbol, symbol) for symbol in df.index])

ATOM_QUERY_ARGS = dict(
  symbol=graphene.Argument(AtomEnum, required=True),
)

class AtomImpl:
    """ Actual implementation of the atom, holds fields, accessed by attribute """
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, 'm_'+k, v)

    @property
    def name(self):
        return self.m_name

    @property
    def symbol(self):
        return self.m_symbol

    @property
    def atomic_mass(self):
        return self.m_mass

    @property
    def atomic_number(self):
        return self.m_number

def create_atom(symbol: str) -> AtomImpl:
    fields = df.loc[symbol].copy()
    fields['symbol'] = symbol
    return AtomImpl(**fields)

class Atom(graphene.ObjectType):
    """ The Schema for an Atom. Paired with AtomImpl """
    symbol = graphene.String(description="Symbol.")
    name = graphene.String(description="Name.")
    atomic_mass = graphene.Float(description="Atomic mass.")
    atomic_number = graphene.Float(description="Atomic number.")

class Query(graphene.ObjectType):

    atom = graphene.Field(
        Atom,
        **ATOM_QUERY_ARGS,
    )

    def resolve_atom(root, info, symbol: str) -> AtomImpl:
        return create_atom(symbol)

    atoms = graphene.List(
        Atom
    )

    def resolve_atoms(root, info) -> typing.List[AtomImpl]:
        return [create_atom(symbol) for symbol in df.index]

schema = graphene.Schema(query=Query)