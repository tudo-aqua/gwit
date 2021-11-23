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

## How GWIT works

GWIT validates violation witnesses by weaving the assumptions made explicit in
a witness into the original program under analysis and checks the modified program 
with dynamic symbolic execution (i.e., DSE+SPouT).

GWIT relies on the provided ```Witness``` class (part of ```verifier-stub```) for 
providing the infrastructure for checking assumptions in the code of a program:

```java
public class Witness {

	private static int[] counters = new int[1];

	private static void ensureIndexExists(int i) {
		if (i < counters.length) {
			return;
		}
		int[] newCounters = new int[i+1];
		System.arraycopy(counters, 0, newCounters, 0, counters.length);
		counters = newCounters;
	}

	public static void assume(int id, boolean ... assumptions) {
		ensureIndexExists(id);
		int idx = counters[id];
		counters[id]++;
		Verifier.assume(assumptions[idx]);
	}
}
```

For a witness that makes multiple assumptions ```a, b, c``` on one line of code,
GWIT will weave a call 

```java
Witness.assume(0, a, b, c);
```

into the code of the original program after the line on which assumptions were made.
The calls to ```Verifier.assume(...)``` limit the number of paths that have to explored
by dynamic symbolic execution.

This approach works under a couple of assumptuions:

- Assumptions are made on lines in the code that surrounded by proper blocks 
- Code blocks are not clodes on the same line
- Assumptions are not on values that go intto method calls (at least not on 
  the line of the method call) 









