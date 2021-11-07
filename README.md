# The GWIT tool

GWIT (as in *guess what I am thinking* or as in *GDart witness validator*) 
is a witness validator for SVCOMP witnesses for Java programs,
based on the *GDart* tool ensemble.

It consists of four components:
- DSE a generic dynamic symbolic execution (https://github.com/tudo-aqua/dse)
- SPouT: Symbolic Path Recording During Testing (https://github.com/tudo-aqua/spout)
- JConstraints: A meta solving library for SMT problems (https://github.com/tudo-aqua/jconstraints)
- Verifier-Stub: A set of stubs for the verifier (https://github.com/tudo-aqua/verifier-stub)

To validate a witness, just call the ./run-gwit.sh script:
`./run-gwit.sh property-file witness-file`

GDart runs on MacOS and Ubuntu 20.04. Windows is currently not supported.
