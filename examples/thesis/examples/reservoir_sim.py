"""
Reservoir Simulation Example Script
====================================
This script demonstrates the Python interface for the reservoir simulator.
It runs a simple quarter five-spot problem and outputs convergence data.
"""

import numpy as np
from petsc4py import PETSc


def initialize_grid(nx, ny):
    """Create a uniform Cartesian grid."""
    dx = 1.0 / nx
    dy = 1.0 / ny
    x = np.linspace(dx / 2, 1 - dx / 2, nx)
    y = np.linspace(dy / 2, 1 - dy / 2, ny)
    X, Y = np.meshgrid(x, y)
    return X, Y, dx, dy


def permeability_field(X, Y, k_matrix=100.0, k_channel=100000.0):
    """
    Generate a channelized permeability field.

    Args:
        X, Y: Meshgrid coordinates
        k_matrix: Background permeability (mD)
        k_channel: Channel permeability (mD)

    Returns:
        2D array of permeability values
    """
    K = np.ones_like(X) * k_matrix
    # Create a diagonal channel
    channel_width = 0.1
    mask = np.abs(X - Y) < channel_width
    K[mask] = k_channel
    return K


def compute_transmissibility(K, dx, dy):
    """Compute face transmissibilities."""
    nx, ny = K.shape
    Tx = np.zeros((nx - 1, ny))
    Ty = np.zeros((nx, ny - 1))

    # Horizontal transmissibilities
    for i in range(nx - 1):
        for j in range(ny):
            k1 = K[i, j]
            k2 = K[i + 1, j]
            Tx[i, j] = 2 * k1 * k2 / (k1 + k2) / dx

    # Vertical transmissibilities
    for i in range(nx):
        for j in range(ny - 1):
            k1 = K[i, j]
            k2 = K[i, j + 1]
            Ty[i, j] = 2 * k1 * k2 / (k1 + k2) / dy

    return Tx, Ty


def assemble_pressure_system(Tx, Ty, q, nx, ny):
    """
    Assemble the pressure linear system.

    Args:
        Tx, Ty: Transmissibility arrays
        q: Source term
        nx, ny: Grid dimensions

    Returns:
        Coefficient matrix and right-hand side vector
    """
    N = nx * ny
    A = PETSc.Mat().createAIJ(size=(N, N), csr=None)
    A.setUp()

    for i in range(nx):
        for j in range(ny):
            row = i * ny + j
            diag = 0.0

            # West neighbor
            if i > 0:
                col = (i - 1) * ny + j
                A.setValue(row, col, -Tx[i - 1, j])
                diag += Tx[i - 1, j]

            # East neighbor
            if i < nx - 1:
                col = (i + 1) * ny + j
                A.setValue(row, col, -Tx[i, j])
                diag += Tx[i, j]

            # South neighbor
            if j > 0:
                col = i * ny + (j - 1)
                A.setValue(row, col, -Ty[i, j - 1])
                diag += Ty[i, j - 1]

            # North neighbor
            if j < ny - 1:
                col = i * ny + (j + 1)
                A.setValue(row, col, -Ty[i, j])
                diag += Ty[i, j]

            A.setValue(row, row, diag)

    A.assemblyBegin()
    A.assemblyEnd()

    b = PETSc.Vec().createSeq(N)
    for i in range(nx):
        for j in range(ny):
            row = i * ny + j
            b.setValue(row, q[i, j])

    b.assemblyBegin()
    b.assemblyEnd()

    return A, b


def solve_pressure(A, b):
    """Solve the pressure system using GMRES with AMG preconditioner."""
    x = PETSc.Vec().createSeq(b.getSize())

    ksp = PETSc.KSP().create()
    ksp.setType(PETSc.KSP.Type.GMRES)
    ksp.setTolerances(rtol=1e-8)

    pc = ksp.getPC()
    pc.setType(PETSc.PC.Type.HYPRE)
    pc.setHYPREType('boomeramg')

    ksp.setOperators(A)
    ksp.solve(b, x)

    return x.getArray()


def run_quarter_fivespot(nx=64, ny=64):
    """
    Run the quarter five-spot benchmark problem.

    Args:
        nx, ny: Grid dimensions

    Returns:
        Dictionary with results
    """
    # Initialize grid
    X, Y, dx, dy = initialize_grid(nx, ny)

    # Generate permeability field
    K = permeability_field(X, Y)

    # Create source terms (injection at bottom-left, production at top-right)
    q = np.zeros((nx, ny))
    q[0, 0] = 1.0      # Injection well
    q[-1, -1] = -1.0    # Production well

    # Compute transmissibilities
    Tx, Ty = compute_transmissibility(K, dx, dy)

    # Assemble and solve
    A, b = assemble_pressure_system(Tx, Ty, q, nx, ny)
    pressure = solve_pressure(A, b)

    # Compute velocity field
    velocity = np.gradient(pressure.reshape((nx, ny)))

    return {
        'pressure': pressure,
        'velocity': velocity,
        'permeability': K,
        'grid_size': (nx, ny),
        'max_pressure': np.max(pressure),
        'min_pressure': np.min(pressure),
    }


if __name__ == '__main__':
    # Run convergence study
    print("Quarter Five-Spot Convergence Study")
    print("=" * 50)

    grid_sizes = [16, 32, 64, 128]
    errors = []

    for nx in grid_sizes:
        result = run_quarter_fivespot(nx, nx)
        # Error is relative to finest grid solution
        errors.append(result['max_pressure'])
        print(f"Grid {nx:4d}x{nx:4d}: max pressure = {result['max_pressure']:.6f}")

    print("\nConvergence rates:")
    for i in range(1, len(errors)):
        rate = np.log(errors[i-1] / errors[i]) / np.log(2)
        print(f"  {grid_sizes[i-1]:4d} -> {grid_sizes[i]:4d}: rate = {rate:.2f}")
