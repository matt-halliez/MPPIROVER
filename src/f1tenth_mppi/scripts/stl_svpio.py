from functools import partial

import jax
import jax.numpy as jnp


class STLSVPIO:
    """STL-SVPIO for bounded F1TENTH control sequences."""

    def __init__(self, horizon, control_dim, n_particles=16, n_iterations=10,
                 step_size=5.0, temperature=1.0):
        self.horizon = int(horizon)
        self.control_dim = int(control_dim)
        self.n_particles = int(n_particles)
        self.n_iterations = int(n_iterations)
        self.step_size = float(step_size)
        self.temperature = float(temperature)
        self.flat_dim = self.horizon * self.control_dim

        self.previous_controls = jnp.zeros(
            (self.horizon, self.control_dim),
            dtype=jnp.float32,
        )


    def _svgd_step(self, env, particles, state, reference, traffic):
        def particle_robustness(control_sequence):
            states = env.rollout(state, control_sequence)
            return env.stl_robustness(states, reference, traffic)

        grad_rho = jax.vmap(jax.grad(particle_robustness))(particles)
        flat_particles = particles.reshape(self.n_particles, self.flat_dim)
        flat_score = (grad_rho / self.temperature).reshape(
            self.n_particles, self.flat_dim
        )

        differences = flat_particles[:, None, :] - flat_particles[None, :, :]
        squared_distances = (
            jnp.sum(differences * differences, axis=-1) / float(self.flat_dim)
        )
        bandwidth = jnp.maximum(
            jnp.median(squared_distances) / jnp.log(self.n_particles + 1.0),
            1e-6,
        )
        kernel = jnp.exp(-squared_distances / bandwidth)
        kernel_gradient = (
            -2.0
            / (bandwidth * float(self.flat_dim))
            * differences
            * kernel[:, :, None]
        )
        direction = (
            kernel @ flat_score + jnp.sum(kernel_gradient, axis=0)
        ) / float(self.n_particles)

        particles = particles + self.step_size * direction.reshape(particles.shape)
        return jnp.clip(particles, -1.0, 1.0)

    def _evaluate(self, env, particles, state, reference, traffic):
        def evaluate_particle(control_sequence):
            states = env.rollout(state, control_sequence)
            return env.stl_robustness(states, reference, traffic), states

        return jax.vmap(evaluate_particle)(particles)


    @partial(jax.jit, static_argnums=(0, 1))
    def _optimize(self, env, state, reference, traffic, rng, previous_controls,):
        noise = jax.random.normal(
            rng,
            shape=(
                self.n_particles,
                self.horizon,
                self.control_dim,
            ),
        )

        particles = jnp.clip(
            previous_controls[None, :, :] + 0.35 * noise,
            -1.0,
            1.0,
        )

        def optimization_step(_, current_particles):
            return self._svgd_step(
                env,
                current_particles,
                state,
                reference,
                traffic,
            )

        particles = jax.lax.fori_loop(
            0,
            self.n_iterations,
            optimization_step,
            particles,
        )

        robustness, trajectories = self._evaluate(
            env, particles, state, reference, traffic
        )
        best_index = jnp.argmax(robustness)
        return particles[best_index], trajectories[best_index], robustness[best_index]


    def update(self, env, state, reference, traffic, rng):
        best_controls, best_states, robustness = self._optimize(
            env,
            state,
            reference,
            traffic,
            rng,
            self.previous_controls,
        )

        self.previous_controls = jnp.concatenate(
            (best_controls[1:], best_controls[-1:]),
            axis=0,
        )

        return best_controls, best_states, robustness