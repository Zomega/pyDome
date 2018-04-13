#    pyDome:  A geodesic dome calculator
#    Copyright (C) 2013  Daniel Williams
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



#
# load useful modules
#
import numpy as np
import click

#
# load pyDome modules
#
from Polyhedral import Face, Chord, Vertex, Polyhedron, Octahedron, Icosahedron
from SymmetryTriangle import SymmetryTriangle, ClassOneMethodOneSymmetryTriangle
from GeodesicSphere import GeodesicSphere
from Output import OutputDXF, OutputFaceVRML, OutputWireframeVRML
from Truncation import truncate
from BillOfMaterials import get_bill_of_materials

@click.command(
  help='A geodesic dome calculator. Copyright 2013 by Daniel Williams'
)
@click.option(
  '--output', '-o', type=str, required=True,
  help='Path to output file(s). Extensions will be added. '
       + 'Generates DXF and WRL files by default, but only WRL file when '
       + '"-F" option is active. Example:  "-o output/test" produces files '
       + 'output/test.wrl and output/test.dxf.'
)
@click.option(
  '--radius', '-r', type=float, default=1.0,
  help='Radius of generated dome. Default 1.0'
)
@click.option(
  '--polyhedral', '-p',
  type=click.Choice(['octahedron', 'icosahedron']),
  default='icosahedron',
  help='Default icosahedron.'
)
@click.option(
  '--frequency', '-f', type=int, default=4,
  help='Frequency of generated dome. Default 4.'
)
@click.option(
  '--bom-rounding', '-b', type=int, default=5,
  help='The number of decimal places to round chord length output in the generated Bill of Materials. Default 5.'
)
@click.option(
  '--face', '-F', is_flag=True, default=False,
  help='Flag specifying whether to generate face output in WRL file. Cancels DXF file output and cannot be used with truncation.'
)
@click.option(
  '--vthreshold', '-v', type=float, default=0.0000001,
  help='Distance required to consider two vertices equal. Default 0.0000001.'
)
@click.option(
  '--truncation', '-t', type=float,
  help='Distance (ratio) from the bottom to truncate. I advise using only 0.499999 or 0.333333.'
)
def main(radius, frequency, polyhedral, vthreshold, truncation, bom_rounding, face, output):

  # This section contains various casts and checks to maintain compatability with
  # the old getopt version.
  radius = np.float64(radius)

  if polyhedral == 'icosahedron':
    polyhedral = Icosahedron()
  else:
    polyhedral = Octahedron()

  vertex_equal_threshold = vthreshold
  bom_rounding_precision = bom_rounding
  face_output = face
  truncation_amount = truncation
  run_truncate=truncation is not None
  output_path = output

  #
  # check for mutually exclusive options
  #
  if face_output and run_truncate:
    print 'Truncation does not work with face output at this time. Use either -t or -F but not both.'
    exit(-1)

  #
  # generate geodesic sphere
  #
  symmetry_triangle = ClassOneMethodOneSymmetryTriangle(frequency, polyhedral)
  sphere = GeodesicSphere(polyhedral, symmetry_triangle, vertex_equal_threshold, radius)
  C_sphere = sphere.non_duplicate_chords
  F_sphere = sphere.non_duplicate_face_nodes
  V_sphere = sphere.sphere_vertices

  #
  # truncate
  #
  V = V_sphere
  C = C_sphere
  if run_truncate:
    V, C = truncate(V_sphere, C_sphere, truncation_amount)

  #
  # write model output
  #
  if face_output:
    OutputFaceVRML(V, F_sphere, output_path + '.wrl')
  else:
    OutputWireframeVRML(V, C, output_path + '.wrl')
    OutputDXF(V, C, output_path + '.dxf')

  #
  # bill of materials
  #
  get_bill_of_materials(V, C, bom_rounding_precision)

#
# run the main function
#
if __name__ == "__main__":
  main()
