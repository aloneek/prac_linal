"""Независимая проверка спектров, решений, энергии и устойчивых ветвей ЛР4.3."""
from pathlib import Path
import importlib.util
import sys
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
import sympy as sp

path = Path(__file__).resolve().parents[1] / "code/task3.py"
spec = importlib.util.spec_from_file_location("task3", path)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def main():
    lam = sp.symbols('lambda')
    expected = {
        't3_1': [-2*sp.I, 2*sp.I],
        't3_2': [-1-sp.sqrt(3)*sp.I, -1+sp.sqrt(3)*sp.I],
        't3_3': [-2, 2], 't3_4': [-4, 1],
        't3_2c': [-2, -2], 't3_2o': [-4, -1],
    }
    for case in m.CASES:
        A = sp.Matrix([[0, 1], [case.a, case.b]])
        assert sp.expand(A.charpoly(lam).as_expr() -
                         (lam**2-case.b*lam-case.a)) == 0
        for root in expected[case.key]:
            assert sp.simplify((A-root*sp.eye(2))*sp.Matrix([1, root])) == sp.zeros(2, 1)
        if case.key == 't3_2c':
            assert A.eigenvals() == {-2: 2}
            assert (A+2*sp.eye(2)).rank() == 1
            assert (A+2*sp.eye(2))*sp.Matrix([0, 1]) == sp.Matrix([1, -2])
        ts = np.linspace(0, case.duration, 101)
        F = m.fundamental(case.a, case.b, ts)
        reference = np.array([expm(case.matrix*t) for t in ts])
        np.testing.assert_allclose(F, reference, rtol=2e-10, atol=2e-11)
        values = m.trajectories(case, ts)
        np.testing.assert_allclose(values[:, 0], m.INITIAL, atol=1e-15)
        for initial, trajectory in zip(m.INITIAL, values):
            sol = solve_ivp(lambda t, x: case.matrix@x, (0, case.duration), initial,
                            t_eval=ts, rtol=1e-10, atol=1e-12)
            assert sol.success
            np.testing.assert_allclose(trajectory, sol.y.T, rtol=3e-7, atol=2e-10)
        # H' = b*x2². Проверяем отдельно от формулы решения.
        q, u = sp.symbols('q u', real=True)
        H = (u*u-case.a*q*q)/2
        assert sp.expand(sp.diff(H, q)*u + sp.diff(H, u)*(case.a*q+case.b*u)
                         - case.b*u*u) == 0
        if case.a < 0:
            Ht = (values[:, :, 1]**2-case.a*values[:, :, 0]**2)/2
            if case.b == 0:
                np.testing.assert_allclose(Ht, np.broadcast_to(Ht[:, :1], Ht.shape),
                                           rtol=1e-12, atol=1e-14)
            else:
                assert np.diff(Ht, axis=1).max() < 1e-12
                assert np.linalg.norm(values[:, -1], axis=1).max() < .001
        if case.stable_lambda is not None:
            v = np.array([1., case.stable_lambda])
            np.testing.assert_allclose(case.matrix@v, case.stable_lambda*v)
            exact = np.exp(case.stable_lambda*ts)[:, None]*v
            np.testing.assert_allclose(np.einsum('tij,j->ti', F, v), exact,
                                       rtol=1e-7, atol=2e-12)
            # Положительная мода действительно увеличивается.
            positive = max(float(sp.re(z)) for z in expected[case.key])
            assert positive > 0
        print(f'{case.key}: спектр, векторы, expm, solve_ivp, энергия — OK')
    print('Все проверки задания 3 пройдены.')


if __name__ == '__main__':
    main()
