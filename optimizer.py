import math
from typing import Callable, Iterable, Tuple

import torch
from torch.optim import Optimizer


class AdamW(Optimizer):
    def __init__(
            self,
            params: Iterable[torch.nn.parameter.Parameter],
            lr: float = 1e-3,
            betas: Tuple[float, float] = (0.9, 0.999),
            eps: float = 1e-6,
            weight_decay: float = 0.0,
            correct_bias: bool = True,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {} - should be >= 0.0".format(eps))
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, correct_bias=correct_bias)
        super().__init__(params, defaults)

    def step(self, closure: Callable = None):
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")

                # # State should be stored in this dictionary
                # state = self.state[p]
                #
                # # Initialize state if it doesn't exist
                # if len(state) == 0:
                #     state['step'] = 0
                #     state['exp_avg'] = torch.zeros_like(p.data)
                #     state['exp_avg_sq'] = torch.zeros_like(p.data)
                #
                # exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                # beta1, beta2 = group['betas']
                #
                # state['step'] += 1
                #
                # # Update first and second moments of the gradients
                # exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                # exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
                #
                # # Bias correction
                # bias_correction1 = 1 - beta1 ** state['step']
                # bias_correction2 = 1 - beta2 ** state['step']
                #
                # # Compute the denominator
                # denom = (exp_avg_sq.sqrt() / math.sqrt(bias_correction2)).add_(group['eps'])
                #
                # alpha = group["lr"]
                # # Compute the step size
                # step_size = alpha / bias_correction1
                #
                # # Update parameters
                # p.data.addcdiv_(exp_avg, denom, value=-step_size)
                #
                # # Add weight decay after the main gradient-based updates
                # if group['weight_decay'] > 0.0:
                #     p.data.add_(p.data, alpha=-group['lr'] * group['weight_decay'])
                # Access hyperparameters from the `group` dictionary

                # Update first and second moments of the gradients

                # Bias correction
                # Please note that we are using the "efficient version" given in
                # https://arxiv.org/abs/1412.6980

                # Update parameters

                # Add weight decay after the main gradient-based updates.
                # Please note that the learning rate should be incorporated into this update.

                state = self.state[p]
                # initialization of optimizer parameters
                if 'm' not in state or 'v' not in state:
                    state['step'] = torch.tensor(0).requires_grad_(False)
                    state['m'] = torch.zeros_like(p.data)
                    state['v'] = torch.zeros_like(p.data)

                # Access hyperparameters from the `group` dictionary
                alpha = group["lr"]
                beta1, beta2 = group["betas"]
                eps = group["eps"]
                weight_decay = group["weight_decay"]

                # Update the step counter
                state['step'] += 1

                # Update first and second moments of the gradients
                state['m'] = beta1 * state['m'] + (1 - beta1) * grad
                state['v'] = beta2 * state['v'] + (1 - beta2) * torch.pow(grad, 2)

                # Bias correction
                # Please note that we are using the "efficient version" given in
                # https://arxiv.org/abs/1412.6980
                alpha_t = alpha * torch.sqrt(1 - torch.pow(beta2, state['step'])) / (1 - torch.pow(beta1, state['step']))

                # Update parameters
                p.data = p.data - alpha_t * (state['m'] / (state['v'].sqrt() + eps))

                # Add weight decay after the main gradient-based updates.
                # Please note that the learning rate should be incorporated into this update.
                p.data = p.data - alpha * weight_decay * p.data

        return loss

