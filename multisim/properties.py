from math import pi, sqrt

epsilon0 = 8.85e-12
mu0 = 4e-7*pi
c0 = 1/sqrt(epsilon0*mu0)
Z0 = sqrt(mu0/epsilon0)

class material:
    def __init__(self, eps_r, mu_r, sigma, magnetic_loss, name):
        self.eps_r = eps_r
        self.mu_r = mu_r
        self.sigma = sigma
        self.magnetic_loss = magnetic_loss
        self.name = name

        self.eps = eps_r * epsilon0
        self.mu = mu_r * mu0

    def get_string(self):
        string0 = "material: " + str(self.eps_r) + " " + str(self.mu_r) + " " + str(self.sigma) + " " + str(self.magnetic_loss) + "\n"
        return string0