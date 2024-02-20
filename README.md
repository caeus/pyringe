# ASD
ASD is a build system for monorepos. It emerges from the need to address these pain points:

* Poor monorepo support for very mainstream languages like JS, Python.
* No Turing complete languages to declare builds (TOML, YAML, JSON). Which makes it a pain in the ass to DRY builds.
* Bazel's frustratringly complex model, and how bad it plays with others.

ASD also draws inspiration from other build systems, especially those which model tasks and dependencies as DAG (Bazel (I KNOW), Gradle, SBT, Pants, Makefile).

## Why ASD?

Because it's super fast to write! But if you whish I can make it stand for Aggregated Source Director.

## Philosphy

Reproducible, isolated, hermetic, deterministic builds! NO! Man, that's important, sure, but not as important as allowing developers to progressively adopt it. So ASD lets you use whatever traditional dependency manager you are used to (pip, poetry, yarn, npm, gradle, sbt who cares?), while it provides the toolkit to organize task execution over your monorepo.

### Terminology
As such, and trying no to make it super difficult to learn, we use a language inspired in all those tools.

Our unit of work is a Task, and a Task is an implementation, and a set of dependencies (references to other tasks)

Task reference is determined by its location, which takes us to a module. A module is a collection of tasks. Multiple modules inhabit a project.

A project is a collection of modules, and it's bound to a folder inside the workspace. Projects are declared in files named `__project__.py`.

The workspace is but the root of the monorepo, and it's declared using the file `<monorepo_root>/__workspace__.toml`.

Similar to Bazel, but simpler! no toolchains, no remote repositories, none of that.


## Getting started (Hello world)

Install asd globally by running `pip install git+https://github.com/caeus/asd`, that's it. It uses python 3.12 or higher, so beware!


Start your monorepo by creating a `__workspace__.toml` file at the root of it and include this content:
```toml
[venv]
```
Yep, that simple. the `venv` table has two fields:
1. `at`, which tells ASD where to install the virtual environment (defaults to `.venv`)
2. `installs`, a list of PEP508 strings (dependencies) that your build will use. If you want write your own extensions, you can use a reference to a project inside the monorepo. It needs to be a `pyproject.toml` or `setup.py` python project. (defaults to a `[]`, a dependency to ASD is always included).

Now write at the root of the monorepo (or anywhere inside) a `__project__.py` file with this content:
```python
from asd.dsl import *
def main(ctx:ModuleCtx)->None:
    @ctx.task()
    async def hello_world(ctx:TaskCtx)->None:
        print("Hello world")
```

Now you can just run `asd run '<root relative path to folder with __project__.py file>:main:hello_world'` (ie `asd run :main:hello_world`, notice the colon at the begginning), and you are done!

Moreless... the coolest part of ASD is the execution model (a DAG (a structure I'm obsessed with)), so let's check it.

Now change your `__project__.py` file content to this:

```python
from asd.dsl import *
def main(ctx:ModuleCtx)->None:
    @ctx.task("say_hello")
    async def say_world(ctx:TaskCtx)->None:
        print("World!!!")
    
    @ctx.task()
    async def say_hello(ctx:TaskCtx)->None:
        print("Hello...")

```

and run `asd run :main:say_world`, and you'll notice that `Hello...` happens before `World!!!`

# pyringe
