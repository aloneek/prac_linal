import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


v1 = np.array([1.0, 4.0])
v2 = np.array([4.0, 1.0])

P  = np.column_stack([v1, v2])
Pinv = np.linalg.inv(P)

B = {
    1: np.array([[-1.0, 0.0],
                 [ 0.0, -3.0]]),
    2: np.array([[ 1.0, 1.0],
                 [ 0.0, 1.0]]),
    3: np.array([[-2/3, 0.0],
                 [ 0.0, 5/2]]),
    4: np.array([[-1/3, 7/4],
                 [-7/4, -1/3]]),
    5: np.array([[ 3/5, 4/3],
                 [-4/3, 3/5]]),
    6: np.array([[ 0.0, 5/3],
                 [-5/3, 0.0]]),
}

A = {k: P @ Bm @ Pinv for k, Bm in B.items()}


x0_list = [
    v1,                   
    v2,                    
    np.array([1.0,  0.0]),
    np.array([2.0, -1.0]),
    np.array([-1.0, 3.0]),
]
labels = [
    r"$x(0)=v_1=(1,4)$",
    r"$x(0)=v_2=(4,1)$",
    r"$x(0)=(1,0)$",
    r"$x(0)=(2,-1)$",
    r"$x(0)=(-1,3)$",
]


t_max = {1: 12, 2: 3, 3: 3, 4: 15, 5: 6, 6: 25}
colors = ["tab:red", "tab:blue", "tab:green", "tab:orange", "tab:purple"]

def matrix_title(k, Amat):
    return (
        f"Система {k}:   "
        f"A = [[{Amat[0,0]:.3g}, {Amat[0,1]:.3g}], "
        f"[{Amat[1,0]:.3g}, {Amat[1,1]:.3g}]]"
    )

for k in range(1, 7):
    Amat = A[k]
    T = t_max[k]
    t_span = (0.0, T)
    t_eval = np.linspace(*t_span, 2000)

    fig, axes = plt.subplots(5, 3, figsize=(14, 20))
    fig.suptitle(matrix_title(k, Amat), fontsize=14, y=0.995)


    for i, (x0, lab) in enumerate(zip(x0_list, labels)):
        sol = solve_ivp(lambda t, x: Amat @ x, t_span, x0,
                        t_eval=t_eval, rtol=1e-9, atol=1e-12)
        x1, x2 = sol.y[0], sol.y[1]
        c = colors[i]

        ax = axes[i, 0]
        ax.plot(sol.t, x1, color=c)
        ax.set_title(lab + "  —  $x_1(t)$")
        ax.set_xlabel("t"); ax.set_ylabel("$x_1$")
        ax.grid(True)

        ax = axes[i, 1]
        ax.plot(sol.t, x2, color=c)
        ax.set_title(lab + "  —  $x_2(t)$")
        ax.set_xlabel("t"); ax.set_ylabel("$x_2$")
        ax.grid(True)

        ax = axes[i, 2]
        ax.plot(x1, x2, color=c, label=lab)
        ax.plot(x0[0], x0[1], "o", color=c, ms=6)
        ax.plot(0, 0, "k+", ms=8)
        ax.set_title(lab + "  —  фазовая траектория")
        ax.set_xlabel("$x_1$"); ax.set_ylabel("$x_2$")
        ax.grid(True); ax.set_aspect("equal", adjustable="datalim")
        ax.legend(loc="best", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.985])
    plt.savefig(f"system_{k}.pdf", bbox_inches="tight")
    plt.savefig(f"system_{k}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"system {k}: saved.")

print("\n--- проверка собственных векторов/значений ---")
for k, Amat in A.items():
    lam, vec = np.linalg.eig(Amat)
    print(f"\nA_{k} =\n{Amat}")
    print("  eigenvalues:", lam)
    print("  A_k v1   =", Amat @ v1, "  (v1 =", v1, ")")
    print("  A_k v2   =", Amat @ v2, "  (v2 =", v2, ")")
    
    w = v1 + 1j * v2
    lhs = Amat @ w
    rhs = lam[0] * w
    
    for L in lam:
        if np.allclose(Amat @ w, L * w):
            print(f"  A_k (v1 + i v2) = ({L:.4g}) (v1 + i v2)")
            break