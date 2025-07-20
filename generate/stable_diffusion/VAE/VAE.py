from torch import nn

from generate.stable_diffusion.VAE.VAEDecoder import VAEDecoder
from generate.stable_diffusion.VAE.VAEEncoder import VAEEncoder


class VAE(nn.Module):
    def __init__(self, in_channels, latent_dim, out_channels):
        super(VAE, self).__init__()
        self.encoder = VAEEncoder(in_channels, latent_dim)
        self.decoder = VAEDecoder(latent_dim, out_channels)

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed
